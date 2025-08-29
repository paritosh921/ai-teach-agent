"""
LLM-Powered Text to JSON Book Converter

This module uses LLM intelligence to robustly convert any plain text educational
content to the rich JSON format, handling formatting issues and extracting
educational elements with high accuracy.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import asdict

from ..schemas.book_schema import (
    JsonBook, Chapter, Section, ContentBlock, ContentBlockType,
    EducationalElements, VideoGenerationHints, LearningObjective,
    BookMetadata, SubjectArea, DifficultyLevel
)


class LLMTextToJsonConverter:
    """Enhanced LLM-powered converter for robust text-to-JSON conversion"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required for LLM-powered conversion")
        
        # Initialize OpenAI client
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
    
    def convert_text_to_json(self, text_content: str, book_title: str, 
                           output_path: Optional[str] = None) -> JsonBook:
        """
        Convert plain text educational content to rich JSON format using LLM
        
        Args:
            text_content: Raw text content of the educational book
            book_title: Title of the book
            output_path: Optional path to save the JSON file
            
        Returns:
            JsonBook object with rich educational structure
        """
        print(f"[LLM] CONVERSION: Starting intelligent conversion of '{book_title}'")
        print("[ANALYSIS] LLM analyzing content structure and educational elements...")
        
        # Step 1: Analyze overall book structure and metadata
        metadata = self._extract_metadata_with_llm(text_content, book_title)
        print(f"[METADATA] Detected subject: {metadata.subject}, level: {metadata.level}")
        
        # Step 2: Extract chapter structure using LLM
        chapters_data = self._extract_chapters_with_llm(text_content)
        print(f"[STRUCTURE] Identified {len(chapters_data)} chapters")
        
        # Step 3: Process each chapter with detailed LLM analysis
        json_chapters = []
        for i, chapter_data in enumerate(chapters_data, 1):
            print(f"[PROCESSING] Chapter {i}/{len(chapters_data)}: {chapter_data.get('title', 'Unknown')}")
            json_chapter = self._process_chapter_with_llm(chapter_data, i)
            json_chapters.append(json_chapter)
        
        # Step 4: Create the complete JSON book
        json_book = JsonBook(
            metadata=metadata,
            chapters=json_chapters
        )
        
        # Step 5: Save if output path provided
        if output_path:
            json_book.save_json(output_path)
            print(f"[SAVED] Enhanced JSON book saved to {output_path}")
        
        print("[SUCCESS] LLM CONVERSION: Complete! Generated rich educational structure")
        return json_book
    
    def _extract_metadata_with_llm(self, text_content: str, book_title: str) -> BookMetadata:
        """Use LLM to extract intelligent metadata from text"""
        
        # Take first 2000 characters for analysis
        sample_content = text_content[:2000]
        
        system_prompt = """You are an educational content analyzer. Analyze the provided text and extract metadata in JSON format.

Return a JSON object with these fields:
- "subject": one of ["mathematics", "physics", "chemistry", "computer_science", "engineering", "biology", "economics", "general"]
- "level": one of ["elementary", "middle_school", "high_school", "undergraduate", "graduate"] 
- "description": brief description of the book's content and scope
- "tags": array of 3-5 relevant topic tags

Be precise and base your analysis on the actual content patterns, terminology, and complexity."""

        user_prompt = f"""Book Title: {book_title}

Sample Content:
{sample_content}

Analyze this educational content and provide metadata in JSON format."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
            
            metadata_dict = json.loads(result_text)
            
            return BookMetadata(
                title=book_title,
                subject=SubjectArea(metadata_dict.get("subject", "general")),
                level=metadata_dict.get("level", "undergraduate"),
                description=metadata_dict.get("description", ""),
                tags=metadata_dict.get("tags", [])
            )
            
        except Exception as e:
            print(f"[WARNING] LLM metadata extraction failed: {e}")
            # Fallback to basic metadata
            return BookMetadata(
                title=book_title,
                subject=SubjectArea.GENERAL,
                level="undergraduate",
                description=f"Educational content from {book_title}"
            )
    
    def _extract_chapters_with_llm(self, text_content: str) -> List[Dict[str, Any]]:
        """Use LLM to intelligently extract chapter structure"""
        
        system_prompt = """You are an educational content parser. Analyze the provided text and extract the chapter structure.

Return a JSON array where each chapter is an object with:
- "number": chapter number (integer)
- "title": chapter title (string)
- "content": the full text content of this chapter (string)
- "description": brief description of chapter content (string)

IMPORTANT: 
- Include ALL text content for each chapter, don't truncate
- Handle any formatting inconsistencies gracefully
- If no clear chapters exist, create logical groupings
- Preserve all mathematical formulas and educational content exactly"""

        user_prompt = f"""Extract chapter structure from this educational text:

{text_content}

Return chapter information in JSON format."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
            
            chapters_data = json.loads(result_text)
            
            # Validate structure
            if not isinstance(chapters_data, list):
                raise ValueError("Expected array of chapters")
            
            return chapters_data
            
        except Exception as e:
            print(f"[WARNING] LLM chapter extraction failed: {e}")
            # Fallback: treat entire content as single chapter
            return [{
                "number": 1,
                "title": "Main Content",
                "content": text_content,
                "description": "Educational content"
            }]
    
    def _process_chapter_with_llm(self, chapter_data: Dict[str, Any], chapter_number: int) -> Chapter:
        """Process individual chapter with detailed LLM analysis"""
        
        chapter_content = chapter_data.get("content", "")
        chapter_title = chapter_data.get("title", f"Chapter {chapter_number}")
        
        # Extract sections within the chapter
        sections_data = self._extract_sections_with_llm(chapter_content, chapter_number)
        
        # Process each section
        json_sections = []
        for section_data in sections_data:
            json_section = self._process_section_with_llm(section_data, chapter_number)
            json_sections.append(json_section)
        
        # Extract chapter learning objectives
        learning_objectives = self._extract_learning_objectives_with_llm(chapter_content)
        
        return Chapter(
            id=f"chapter_{chapter_number}",
            number=chapter_number,
            title=chapter_title,
            description=chapter_data.get("description", ""),
            learning_objectives=learning_objectives,
            sections=json_sections
        )
    
    def _extract_sections_with_llm(self, chapter_content: str, chapter_number: int) -> List[Dict[str, Any]]:
        """Extract sections within a chapter using LLM"""
        
        system_prompt = """You are an educational content parser. Analyze the chapter content and extract logical sections.

Return a JSON array where each section is an object with:
- "number": section number (e.g., "1.1", "1.2") 
- "title": section title (string)
- "content": the full text content of this section (string)
- "difficulty": one of ["beginner", "intermediate", "advanced"]

IMPORTANT:
- Create logical sections even if not explicitly marked
- Include ALL content, don't truncate
- Preserve mathematical formulas exactly
- If no clear sections, create meaningful topic-based groupings"""

        user_prompt = f"""Extract section structure from this chapter content:

{chapter_content[:3000]}...

Create logical sections and return in JSON format."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
            
            sections_data = json.loads(result_text)
            
            # Validate structure
            if not isinstance(sections_data, list):
                raise ValueError("Expected array of sections")
            
            return sections_data
            
        except Exception as e:
            print(f"[WARNING] LLM section extraction failed: {e}")
            # Fallback: treat entire chapter as single section
            return [{
                "number": f"{chapter_number}.1",
                "title": "Main Content",
                "content": chapter_content,
                "difficulty": "intermediate"
            }]
    
    def _process_section_with_llm(self, section_data: Dict[str, Any], chapter_number: int) -> Section:
        """Process individual section with comprehensive LLM analysis"""
        
        section_content = section_data.get("content", "")
        section_title = section_data.get("title", "Section")
        section_number = section_data.get("number", f"{chapter_number}.1")
        
        # Extract structured content blocks using LLM
        content_blocks = self._extract_content_blocks_with_llm(section_content)
        
        # Extract educational elements using LLM
        educational_elements = self._extract_educational_elements_with_llm(section_content)
        
        # Extract learning objectives for this section
        learning_objectives = self._extract_learning_objectives_with_llm(section_content)
        
        # Generate video hints using LLM
        video_hints = self._generate_video_hints_with_llm(section_content, content_blocks)
        
        # Determine difficulty
        difficulty_str = section_data.get("difficulty", "intermediate")
        try:
            difficulty = DifficultyLevel(difficulty_str)
        except ValueError:
            difficulty = DifficultyLevel.INTERMEDIATE
        
        return Section(
            id=f"section_{section_number.replace('.', '_')}",
            number=section_number,
            title=section_title,
            difficulty=difficulty,
            estimated_duration=self._estimate_duration(section_content),
            content_blocks=content_blocks,
            learning_objectives=learning_objectives,
            educational_elements=educational_elements,
            video_hints=video_hints
        )
    
    def _extract_content_blocks_with_llm(self, content: str) -> List[ContentBlock]:
        """Extract structured content blocks using LLM"""
        
        system_prompt = """You are an educational content analyzer. Break down the provided content into structured blocks.

Return a JSON array where each block is an object with:
- "type": one of ["introduction", "definition", "theorem", "proof", "example", "exercise", "application", "summary", "text", "formula"]
- "content": the text content of this block
- "title": optional title for the block (for definitions, examples, etc.)
- "formula": optional mathematical formula (for formula blocks)
- "problem": optional problem statement (for example/exercise blocks)
- "solution_steps": optional array of solution steps (for example blocks)
- "answer": optional final answer (for example blocks)

IMPORTANT:
- Preserve ALL mathematical content exactly
- Identify educational elements precisely (definitions, theorems, examples)
- Don't lose any content in the conversion
- Create logical content blocks that make sense for video generation"""

        user_prompt = f"""Analyze this educational content and extract structured content blocks:

{content}

Return content blocks in JSON format."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
            
            blocks_data = json.loads(result_text)
            
            # Convert to ContentBlock objects
            content_blocks = []
            for block_data in blocks_data:
                try:
                    block_type = ContentBlockType(block_data.get("type", "text"))
                    content_block = ContentBlock(
                        type=block_type,
                        content=block_data.get("content", ""),
                        title=block_data.get("title"),
                        formula=block_data.get("formula"),
                        problem=block_data.get("problem"),
                        solution_steps=block_data.get("solution_steps", []),
                        answer=block_data.get("answer")
                    )
                    content_blocks.append(content_block)
                except Exception as e:
                    print(f"[WARNING] Invalid content block: {e}")
                    continue
            
            return content_blocks if content_blocks else [ContentBlock(
                type=ContentBlockType.TEXT,
                content=content
            )]
            
        except Exception as e:
            print(f"[WARNING] LLM content block extraction failed: {e}")
            # Fallback: create single text block
            return [ContentBlock(type=ContentBlockType.TEXT, content=content)]
    
    def _extract_educational_elements_with_llm(self, content: str) -> EducationalElements:
        """Extract educational elements using LLM intelligence"""
        
        system_prompt = """You are an educational content analyzer. Extract key educational elements from the content.

Return a JSON object with these arrays:
- "key_concepts": important concepts and terminology
- "formulas": mathematical formulas and equations
- "definitions": formal definitions 
- "examples": example problems or demonstrations
- "applications": real-world applications or use cases
- "prerequisites": prerequisite knowledge needed
- "common_mistakes": common student errors or misconceptions

IMPORTANT: 
- Extract actual content, not placeholders
- Preserve mathematical notation exactly
- Be comprehensive but precise"""

        user_prompt = f"""Extract educational elements from this content:

{content}

Return educational elements in JSON format."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
            
            elements_data = json.loads(result_text)
            
            return EducationalElements(
                key_concepts=elements_data.get("key_concepts", []),
                formulas=elements_data.get("formulas", []),
                definitions=elements_data.get("definitions", []),
                examples=elements_data.get("examples", []),
                applications=elements_data.get("applications", []),
                prerequisites=elements_data.get("prerequisites", []),
                common_mistakes=elements_data.get("common_mistakes", [])
            )
            
        except Exception as e:
            print(f"[WARNING] LLM educational elements extraction failed: {e}")
            return EducationalElements()
    
    def _extract_learning_objectives_with_llm(self, content: str) -> List[LearningObjective]:
        """Extract learning objectives using LLM"""
        
        system_prompt = """You are an educational content analyzer. Extract or infer learning objectives from the content.

Return a JSON array where each objective is an object with:
- "objective": clear learning objective statement (what students should be able to do)
- "bloom_level": one of ["remember", "understand", "apply", "analyze", "evaluate", "create"]

Create 3-5 specific, measurable learning objectives based on the content."""

        user_prompt = f"""Extract learning objectives from this educational content:

{content[:1500]}...

Return learning objectives in JSON format."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
            
            objectives_data = json.loads(result_text)
            
            learning_objectives = []
            for obj_data in objectives_data:
                learning_obj = LearningObjective(
                    objective=obj_data.get("objective", ""),
                    bloom_level=obj_data.get("bloom_level", "understand")
                )
                learning_objectives.append(learning_obj)
            
            return learning_objectives
            
        except Exception as e:
            print(f"[WARNING] LLM learning objectives extraction failed: {e}")
            return []
    
    def _generate_video_hints_with_llm(self, content: str, content_blocks: List[ContentBlock]) -> VideoGenerationHints:
        """Generate intelligent video hints using LLM"""
        
        # Count content block types
        block_types = [block.type.value for block in content_blocks]
        block_summary = f"Content blocks: {', '.join(set(block_types))}"
        
        system_prompt = """You are an educational video production advisor. Analyze the content and provide video generation hints.

Return a JSON object with:
- "suggested_duration": estimated minutes for video (integer)
- "subdivision_strategy": one of ["auto", "by_type", "by_length", "by_concept"]
- "focus_areas": array of focus areas like ["definitions", "examples", "applications", "theory"]
- "visual_emphasis": array of elements needing visual attention
- "pace": one of ["slow", "moderate", "fast"]
- "complexity_score": complexity rating from 0.0 to 1.0

Consider content complexity, mathematical elements, and educational effectiveness."""

        user_prompt = f"""Analyze this educational content for video production:

Content length: {len(content)} characters
{block_summary}

Content preview:
{content[:800]}...

Provide video generation hints in JSON format."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
            
            hints_data = json.loads(result_text)
            
            return VideoGenerationHints(
                suggested_duration=hints_data.get("suggested_duration", self._estimate_duration(content)),
                subdivision_strategy=hints_data.get("subdivision_strategy", "auto"),
                focus_areas=hints_data.get("focus_areas", []),
                visual_emphasis=hints_data.get("visual_emphasis", []),
                pace=hints_data.get("pace", "moderate"),
                complexity_score=hints_data.get("complexity_score", 0.5)
            )
            
        except Exception as e:
            print(f"[WARNING] LLM video hints generation failed: {e}")
            return VideoGenerationHints(
                suggested_duration=self._estimate_duration(content),
                subdivision_strategy="auto",
                pace="moderate",
                complexity_score=0.5
            )
    
    def _estimate_duration(self, content: str) -> int:
        """Estimate video duration in minutes"""
        char_count = len(content)
        word_count = char_count / 5  # Rough estimation
        duration_minutes = max(1, int(word_count / 150))  # 150 words per minute
        return min(duration_minutes, 30)  # Cap at 30 minutes
    
    def validate_json_output(self, json_book: JsonBook) -> List[str]:
        """Validate the generated JSON book structure"""
        errors = []
        
        try:
            # Basic structure validation
            if not json_book.chapters:
                errors.append("No chapters found in generated JSON")
            
            for i, chapter in enumerate(json_book.chapters):
                if not chapter.sections:
                    errors.append(f"Chapter {i+1} has no sections")
                
                for j, section in enumerate(chapter.sections):
                    if not section.content_blocks:
                        errors.append(f"Chapter {i+1}, Section {j+1} has no content blocks")
                    
                    if len(section.content_blocks) == 1 and section.content_blocks[0].type == ContentBlockType.TEXT:
                        # Check if it's just a fallback text block
                        if len(section.content_blocks[0].content) < 100:
                            errors.append(f"Chapter {i+1}, Section {j+1} has minimal content")
        
        except Exception as e:
            errors.append(f"JSON structure validation error: {e}")
        
        return errors


def main():
    """Test the LLM-powered converter"""
    converter = LLMTextToJsonConverter()
    
    # Test with sample content
    sample_text = """
    # Introduction to Calculus
    
    ## Chapter 1: Limits
    
    ### Understanding Limits
    
    A limit describes the behavior of a function as its input approaches a particular value.
    
    **Definition**: The limit of f(x) as x approaches a is L if we can make f(x) arbitrarily close to L.
    
    Example: Find the limit of f(x) = x² as x approaches 2.
    Solution: lim(x→2) x² = 4
    """
    
    try:
        json_book = converter.convert_text_to_json(sample_text, "Test Book")
        print("[SUCCESS] LLM conversion successful!")
        print(f"Generated {len(json_book.chapters)} chapters")
        
        # Validate
        errors = converter.validate_json_output(json_book)
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("[SUCCESS] Validation passed!")
            
    except Exception as e:
        print(f"[ERROR] LLM conversion failed: {e}")


if __name__ == "__main__":
    main()