"""
LLM-Powered Book Processor for Intelligent Content Analysis

This module uses AI to intelligently process any text format, extracting educational
content, structuring it for video generation, and handling various writing styles.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from openai import OpenAI
from datetime import datetime


@dataclass
class EducationalConcept:
    """Represents a key educational concept extracted from text"""
    name: str
    definition: str
    examples: List[str]
    formulas: List[str]
    importance: str
    difficulty_level: str  # beginner, intermediate, advanced


@dataclass
class LearningObjective:
    """Represents a learning objective for a section"""
    objective: str
    success_criteria: List[str]
    prerequisite_knowledge: List[str]


@dataclass
class LLMTextSection:
    """LLM-processed educational section"""
    title: str
    content: str
    level: int  # 1=chapter, 2=section, 3=subsection
    section_number: str
    educational_concepts: List[EducationalConcept]
    learning_objectives: List[LearningObjective]
    key_formulas: List[str]
    visual_elements: List[str]
    difficulty_level: str
    estimated_duration_minutes: int
    prerequisites: List[str]


@dataclass
class LLMParsedBook:
    """Complete book processed by LLM"""
    title: str
    filepath: str
    chapters: List[LLMTextSection]
    sections: List[LLMTextSection]
    total_sections: int
    overall_difficulty: str
    target_audience: str
    recommended_sequence: List[str]


class LLMBookProcessor:
    """
    LLM-powered book processor that intelligently extracts and structures
    educational content from any text format
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)

    def process_book_file(self, book_path: str, topic_name: str = None) -> LLMParsedBook:
        """
        Process a book file using LLM for intelligent content extraction

        Args:
            book_path: Path to the book file
            topic_name: Optional topic name (defaults to filename)
        """
        # Read the book content
        with open(book_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        if not topic_name:
            topic_name = Path(book_path).stem

        # Process with LLM
        print(f"LLM: Processing {len(raw_content)} characters from {book_path}")
        return self._process_content_with_llm(raw_content, topic_name, book_path)

    def process_raw_content(self, content: str, topic_name: str) -> LLMParsedBook:
        """
        Process raw text content directly using LLM

        Args:
            content: Raw text content
            topic_name: Topic name for the content
        """
        return self._process_content_with_llm(content, topic_name, "raw_content")

    def _process_content_with_llm(self, content: str, topic_name: str, filepath: str) -> LLMParsedBook:
        """Main LLM processing pipeline"""

        print(f"LLM: Starting processing pipeline for '{topic_name}'")

        # Step 1: Extract overall book structure and metadata
        print(f"LLM: Step 1 - Extracting metadata...")
        book_metadata = self._extract_book_metadata(content, topic_name)
        print(f"LLM: Metadata extracted - Title: '{book_metadata['title']}', Difficulty: {book_metadata['difficulty']}")

        # Step 2: Identify main sections and chapters
        print(f"LLM: Step 2 - Identifying sections...")
        sections_data = self._identify_sections(content)
        print(f"LLM: Found {len(sections_data)} sections")

        if not sections_data:
            print("LLM: No sections found, using fallback processing")
            sections_data = self._fallback_section_identification(content)

        # Step 3: Process each section in detail
        print(f"LLM: Step 3 - Processing {len(sections_data)} sections in detail...")
        processed_sections = []
        for i, section_data in enumerate(sections_data, 1):
            print(f"LLM: Processing section {i}/{len(sections_data)}: '{section_data['title']}'")
            processed_section = self._process_section_detail(
                section_data['content'],
                section_data['title'],
                section_data['level'],
                section_data['section_number']
            )
            if processed_section:
                processed_sections.append(processed_section)
            else:
                print(f"LLM: Warning - Section {i} processing returned None")

        print(f"LLM: Successfully processed {len(processed_sections)} sections")

        # Step 4: Convert to dictionaries for merging, then back to objects
        section_dicts = []
        for section in processed_sections:
            if hasattr(section, '__dict__'):
                # Convert dataclass to dict
                section_dict = {
                    'title': section.title,
                    'content': section.content,
                    'level': section.level,
                    'section_number': section.section_number,
                    'estimated_duration': getattr(section, 'estimated_duration_minutes', 15)
                }
                section_dicts.append(section_dict)
            else:
                section_dicts.append(section)

        # Post-process sections to merge small fragments
        merged_dicts = self._merge_small_sections(section_dicts)

        # Convert back to LLMTextSection objects
        processed_sections = []
        for section_dict in merged_dicts:
            section_obj = LLMTextSection(
                title=section_dict['title'],
                content=section_dict['content'],
                level=section_dict['level'],
                section_number=section_dict['section_number'],
                educational_concepts=[],  # Will be filled by LLM processing
                learning_objectives=[],
                key_formulas=[],
                visual_elements=[],
                difficulty_level='intermediate',
                estimated_duration_minutes=section_dict['estimated_duration'],
                prerequisites=[]
            )
            processed_sections.append(section_obj)

        # Step 5: Organize into chapters and sections
        chapters = [s for s in processed_sections if s.level == 1]
        all_sections = processed_sections

        result = LLMParsedBook(
            title=book_metadata['title'],
            filepath=filepath,
            chapters=chapters,
            sections=all_sections,
            total_sections=len(all_sections),
            overall_difficulty=book_metadata['difficulty'],
            target_audience=book_metadata['audience'],
            recommended_sequence=[s.title for s in processed_sections]
        )

        print(f"LLM: Processing complete - {result.total_sections} sections, {len(result.chapters)} chapters")
        return result

    def _extract_book_metadata(self, content: str, topic_name: str) -> Dict[str, Any]:
        """Extract overall book metadata using LLM"""

        prompt = f"""
        Analyze this educational text about "{topic_name}" and extract key metadata:

        TEXT CONTENT:
        {content[:2000]}...  # First 2000 characters for overview

        Provide a JSON response with:
        {{
            "title": "Full book title",
            "difficulty": "beginner/intermediate/advanced",
            "audience": "high_school/undergraduate/graduate/professional",
            "main_topics": ["topic1", "topic2", "topic3"],
            "prerequisites": ["prereq1", "prereq2"],
            "learning_goals": ["goal1", "goal2"]
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educational content analyzer. Extract accurate metadata from educational texts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Error extracting metadata: {e}")
            # Fallback metadata
            return {
                "title": topic_name.replace('_', ' ').title(),
                "difficulty": "intermediate",
                "audience": "undergraduate",
                "main_topics": [topic_name],
                "prerequisites": [],
                "learning_goals": [f"Understand {topic_name} concepts"]
            }

    def _identify_sections(self, content: str) -> List[Dict[str, Any]]:
        """Identify and extract sections from the text using LLM"""

        prompt = f"""
        Analyze this educational text and identify all the main sections, chapters, and subsections.
        Break down the content into logical educational units.

        TEXT CONTENT:
        {content}

        Provide a JSON response as an array of sections:
        [
            {{
                "title": "Section Title",
                "level": 1,  // 1=chapter, 2=section, 3=subsection
                "section_number": "1.2",
                "content": "Full content of this section",
                "estimated_duration": 15  // minutes
            }}
        ]

        Focus on educational structure, not just headings. Group related content together.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at structuring educational content. Identify logical sections and chapters from any text format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Handle different response formats
            if isinstance(result, dict) and 'sections' in result:
                return result['sections']
            elif isinstance(result, list):
                return result
            else:
                return []

        except Exception as e:
            print(f"Error identifying sections: {e}")
            # Fallback: split by common patterns
            return self._fallback_section_identification(content)

    def _process_section_detail(self, section_content: str, title: str, level: int, section_number: str) -> LLMTextSection:
        """Process a single section in detail using LLM"""

        prompt = f"""
        Analyze this educational section and extract detailed educational information:

        SECTION TITLE: {title}
        SECTION CONTENT:
        {section_content}

        Provide a JSON response with:
        {{
            "educational_concepts": [
                {{
                    "name": "Concept Name",
                    "definition": "Clear definition",
                    "examples": ["example1", "example2"],
                    "formulas": ["formula1", "formula2"],
                    "importance": "Why this matters",
                    "difficulty_level": "beginner/intermediate/advanced"
                }}
            ],
            "learning_objectives": [
                {{
                    "objective": "What students should learn",
                    "success_criteria": ["criterion1", "criterion2"],
                    "prerequisite_knowledge": ["prereq1", "prereq2"]
                }}
            ],
            "key_formulas": ["formula1", "formula2"],
            "visual_elements": ["visual1", "visual2"],
            "difficulty_level": "beginner/intermediate/advanced",
            "estimated_duration_minutes": 15,
            "prerequisites": ["prereq1", "prereq2"]
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educational content analyst. Extract detailed pedagogical information from educational text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Create educational concepts
            concepts = []
            for concept_data in result.get('educational_concepts', []):
                concepts.append(EducationalConcept(**concept_data))

            # Create learning objectives
            objectives = []
            for obj_data in result.get('learning_objectives', []):
                objectives.append(LearningObjective(**obj_data))

            return LLMTextSection(
                title=title,
                content=section_content,
                level=level,
                section_number=section_number,
                educational_concepts=concepts,
                learning_objectives=objectives,
                key_formulas=result.get('key_formulas', []),
                visual_elements=result.get('visual_elements', []),
                difficulty_level=result.get('difficulty_level', 'intermediate'),
                estimated_duration_minutes=result.get('estimated_duration_minutes', 15),
                prerequisites=result.get('prerequisites', [])
            )

        except Exception as e:
            print(f"Error processing section '{title}': {e}")
            # Fallback section
            return LLMTextSection(
                title=title,
                content=section_content,
                level=level,
                section_number=section_number,
                educational_concepts=[],
                learning_objectives=[],
                key_formulas=[],
                visual_elements=[],
                difficulty_level='intermediate',
                estimated_duration_minutes=15,
                prerequisites=[]
            )

    def _fallback_section_identification(self, content: str) -> List[Dict[str, Any]]:
        """Fallback method to identify sections when LLM fails"""

        # Simple pattern-based section identification
        lines = content.split('\n')
        sections = []
        current_section = None
        current_section_number = ''
        current_content = []

        # Patterns to match section headers with numbers
        chapter_pattern = re.compile(r'^(#+\s+)?Chapter\s+(\d+)', re.IGNORECASE)
        section_pattern = re.compile(r'^(#+\s+)?Section\s+([\d.]+)', re.IGNORECASE)
        numbered_pattern = re.compile(r'^(#+\s+)?(\d+(?:\.\d+)*)[\.\s]*(.+)$')

        for line in lines:
            line = line.strip()

            # Extract section number and title
            section_number = ''
            title = line

            # Try different patterns to extract section numbers
            if chapter_pattern.match(line):
                match = chapter_pattern.match(line)
                section_number = match.group(2)
                title = line.replace(match.group(0), '').strip() or f"Chapter {section_number}"
            elif section_pattern.match(line):
                match = section_pattern.match(line)
                section_number = match.group(2)
                title = line.replace(match.group(0), '').strip() or f"Section {section_number}"
            elif numbered_pattern.match(line):
                match = numbered_pattern.match(line)
                section_number = match.group(2)
                title = match.group(3).strip() if match.group(3) else f"Section {section_number}"

            # Check if this is a section header (be more specific to avoid false positives)
            is_section_header = (
                chapter_pattern.match(line) or
                section_pattern.match(line) or
                numbered_pattern.match(line) or
                line.startswith(('## ', '### ', '#### ')) or
                # Only treat as section header if it's clearly a structural element
                (re.match(r'^(#+\s+)?[A-Z][a-zA-Z\s]+.*:$', line) and
                 not line.endswith('?') and  # Avoid questions
                 len(line.split()) <= 6 and  # Shorter titles only
                 not any(word in line.lower() for word in ['the', 'and', 'for', 'with', 'from', 'this', 'that']))  # Avoid descriptive phrases
            )

            if is_section_header:
                # Save previous section
                if current_section and current_content:
                    sections.append({
                        'title': current_section,
                        'level': 2,
                        'section_number': current_section_number,
                        'content': '\n'.join(current_content),
                        'estimated_duration': max(10, len(current_content) // 50)
                    })

                # Clean up the title
                title = title.strip()
                if title.startswith(':'):
                    title = title[1:].strip()
                if not title:
                    title = f"Section {section_number}" if section_number else "Unnamed Section"

                # Start new section
                current_section = title
                current_section_number = section_number
                current_content = []

            elif current_section:
                current_content.append(line)

        # Add final section
        if current_section and current_content:
            sections.append({
                'title': current_section,
                'level': 2,
                'section_number': current_section_number,
                'content': '\n'.join(current_content),
                'estimated_duration': max(10, len(current_content) // 50)
            })

        return sections if sections else [{
            'title': 'Main Content',
            'level': 1,
            'section_number': '1',
            'content': content,
            'estimated_duration': max(15, len(content) // 100)
        }]

    def _merge_small_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge small sections together to create more substantial content units"""
        if not sections:
            return sections

        merged_sections = []
        current_group = []
        current_content_length = 0
        min_content_length = 800  # Minimum characters for a meaningful section

        for section in sections:
            section_content_length = len(section['content'])

            # If this is a very short section (likely a fragment), add it to current group
            if section_content_length < 200 or section['title'].startswith(('## ', '### ', '#### ')):
                current_group.append(section)
                current_content_length += section_content_length
            else:
                # This is a substantial section
                if current_group:
                    # Merge the accumulated small sections
                    merged_section = self._merge_section_group(current_group)
                    if merged_section:
                        merged_sections.append(merged_section)
                    current_group = []
                    current_content_length = 0

                # Add this substantial section
                merged_sections.append(section)

        # Merge any remaining small sections
        if current_group:
            merged_section = self._merge_section_group(current_group)
            if merged_section:
                merged_sections.append(merged_section)

        # Final pass: merge any remaining sections that are still too small
        final_sections = []
        i = 0
        while i < len(merged_sections):
            current_section = merged_sections[i]

            # If this section is too small and there are more sections, merge with next
            if (len(current_section['content']) < min_content_length and
                i + 1 < len(merged_sections) and
                not current_section['title'].startswith('Chapter')):

                next_section = merged_sections[i + 1]
                merged_content = current_section['content'] + '\n\n' + next_section['content']
                merged_title = current_section['title']

                # If next section has a more meaningful title, use it
                if (len(next_section['title']) > len(current_section['title']) and
                    not next_section['title'].startswith(('## ', '### '))):
                    merged_title = next_section['title']

                merged_section = {
                    'title': merged_title,
                    'level': min(current_section['level'], next_section['level']),
                    'section_number': current_section['section_number'] or next_section['section_number'],
                    'content': merged_content,
                    'estimated_duration': max(10, len(merged_content) // 100)
                }

                final_sections.append(merged_section)
                i += 2  # Skip the next section since we merged it
            else:
                final_sections.append(current_section)
                i += 1

        return final_sections

    def _merge_section_group(self, section_group: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Merge a group of small sections into one larger section"""
        if not section_group:
            return None

        # Find the most appropriate title (prefer chapter/section headers over subheaders)
        best_title = None
        best_level = 999
        section_number = ''

        merged_content_parts = []

        for section in section_group:
            merged_content_parts.append(f"## {section['title']}")
            merged_content_parts.append(section['content'])

            # Choose the best title (highest level = most important)
            if section['level'] < best_level:
                best_title = section['title']
                best_level = section['level']
                section_number = section['section_number']

        # If no good title found, create a generic one
        if not best_title:
            best_title = "Combined Content"

        merged_content = '\n\n'.join(merged_content_parts)

        return {
            'title': best_title,
            'level': best_level,
            'section_number': section_number,
            'content': merged_content,
            'estimated_duration': max(10, len(merged_content) // 100)
        }

    def save_processed_book(self, parsed_book: LLMParsedBook, output_path: str):
        """Save processed book to JSON file"""

        # Convert dataclasses to dictionaries
        book_dict = asdict(parsed_book)

        # Convert datetime objects if any
        book_dict['processed_at'] = datetime.now().isoformat()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(book_dict, f, indent=2, ensure_ascii=False)

    def load_processed_book(self, input_path: str) -> LLMParsedBook:
        """Load processed book from JSON file"""

        with open(input_path, 'r', encoding='utf-8') as f:
            book_dict = json.load(f)

        # Convert back to dataclasses
        chapters = []
        for chapter_dict in book_dict['chapters']:
            concepts = [EducationalConcept(**c) for c in chapter_dict['educational_concepts']]
            objectives = [LearningObjective(**o) for o in chapter_dict['learning_objectives']]
            chapter_dict['educational_concepts'] = concepts
            chapter_dict['learning_objectives'] = objectives
            chapters.append(LLMTextSection(**chapter_dict))

        sections = []
        for section_dict in book_dict['sections']:
            concepts = [EducationalConcept(**c) for c in section_dict['educational_concepts']]
            objectives = [LearningObjective(**o) for o in section_dict['learning_objectives']]
            section_dict['educational_concepts'] = concepts
            section_dict['learning_objectives'] = objectives
            sections.append(LLMTextSection(**section_dict))

        return LLMParsedBook(
            title=book_dict['title'],
            filepath=book_dict['filepath'],
            chapters=chapters,
            sections=sections,
            total_sections=book_dict['total_sections'],
            overall_difficulty=book_dict['overall_difficulty'],
            target_audience=book_dict['target_audience'],
            recommended_sequence=book_dict['recommended_sequence']
        )
