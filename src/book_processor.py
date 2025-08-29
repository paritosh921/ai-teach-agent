"""
Book Text Processor for Educational Content Generation

This module processes textbook content from books/topic_name.txt files,
chunking them into logical educational sections for POML generation.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TextSection:
    """Represents a logical section of educational content"""
    title: str
    content: str
    level: int  # 1=chapter, 2=section, 3=subsection
    section_number: str  # e.g., "1.2.3"
    educational_elements: Dict[str, List[str]]  # formulas, definitions, examples


@dataclass
class BookContent:
    """Complete book structure with processed sections"""
    title: str
    filepath: str
    chapters: List[TextSection]
    sections: List[TextSection]
    total_sections: int


class BookProcessor:
    """Processes textbook files into structured educational content (text and JSON formats)"""
    
    def __init__(self, books_dir: str = "books", json_books_dir: str = "books_json"):
        self.books_dir = Path(books_dir)
        self.json_books_dir = Path(json_books_dir)
        
        # Create directories if they don't exist
        self.books_dir.mkdir(exist_ok=True)
        self.json_books_dir.mkdir(exist_ok=True)
        
        # Deferred import to avoid circular dependency
        self._subdivider = None
        self._json_processor = None
    
    def load_book(self, topic_name: str, format_hint: Optional[str] = None) -> BookContent:
        """
        Load and process a book file with automatic format detection
        
        Args:
            topic_name: Name of the book (without extension)
            format_hint: Optional format hint ('text', 'json', or None for auto-detection)
        """
        # Auto-detect format if not specified
        if format_hint is None:
            format_hint = self.detect_book_format(topic_name)
        
        if format_hint == "json":
            return self._load_json_book(topic_name)
        else:
            return self._load_text_book(topic_name)
    
    def detect_book_format(self, topic_name: str) -> str:
        """Detect whether book is in JSON or text format"""
        json_path = self.json_books_dir / f"{topic_name}.json"
        text_path = self.books_dir / f"{topic_name}.txt"
        
        # Check JSON first (preferred format)
        if json_path.exists():
            return "json"
        elif text_path.exists():
            return "text"
        else:
            raise FileNotFoundError(f"Book '{topic_name}' not found in either JSON (.json) or text (.txt) format")
    
    def _load_json_book(self, topic_name: str) -> BookContent:
        """Load JSON format book and convert to BookContent interface"""
        try:
            json_book_content = self.json_processor.load_json_book(topic_name)
            
            # Convert JsonBookContent to BookContent for compatibility
            return BookContent(
                title=json_book_content.title,
                filepath=json_book_content.filepath,
                chapters=json_book_content.chapters,  # JsonTextSection are compatible with TextSection
                sections=json_book_content.sections,
                total_sections=json_book_content.total_sections
            )
            
        except Exception as e:
            # Fallback to text format if JSON loading fails
            print(f"Warning: Failed to load JSON format for '{topic_name}': {e}")
            print("Falling back to text format...")
            return self._load_text_book(topic_name)
    
    def _load_text_book(self, topic_name: str) -> BookContent:
        """Load traditional text format book"""
        book_path = self.books_dir / f"{topic_name}.txt"
        
        if not book_path.exists():
            raise FileNotFoundError(f"Text book file not found: {book_path}")
        
        with open(book_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self._parse_book_content(content, str(book_path))
    
    def _parse_book_content(self, content: str, filepath: str) -> BookContent:
        """Parse raw book content into structured sections"""
        lines = content.strip().split('\n')
        
        # Extract book title (first # heading)
        title = "Untitled"
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        sections = []
        current_section = None
        current_content_lines = []
        
        for line in lines:
            # Detect headings
            heading_match = self._parse_heading(line)
            if heading_match:
                # Save previous section
                if current_section:
                    content_text = '\n'.join(current_content_lines).strip()
                    educational_elements = self._extract_educational_elements(content_text)
                    sections.append(TextSection(
                        title=current_section['title'],
                        content=content_text,
                        level=current_section['level'],
                        section_number=current_section['section_number'],
                        educational_elements=educational_elements
                    ))
                
                # Start new section
                current_section = heading_match
                current_content_lines = []
            else:
                # Accumulate content
                if current_section:  # Skip content before first heading
                    current_content_lines.append(line)
        
        # Save final section
        if current_section:
            content_text = '\n'.join(current_content_lines).strip()
            educational_elements = self._extract_educational_elements(content_text)
            sections.append(TextSection(
                title=current_section['title'],
                content=content_text,
                level=current_section['level'],
                section_number=current_section['section_number'],
                educational_elements=educational_elements
            ))
        
        # Separate chapters and sections
        chapters = [s for s in sections if s.level == 2]  # ## headings
        all_sections = [s for s in sections if s.level >= 2]  # ## and ### headings
        
        return BookContent(
            title=title,
            filepath=filepath,
            chapters=chapters,
            sections=all_sections,
            total_sections=len(all_sections)
        )
    
    def _parse_heading(self, line: str) -> Optional[Dict[str, any]]:
        """Parse heading line and extract level, title, and section number"""
        line = line.strip()
        
        # Match ## Chapter X: Title or ### Section X.Y: Title
        chapter_match = re.match(r'^##\s+Chapter\s+(\d+):\s*(.+)$', line)
        if chapter_match:
            return {
                'level': 2,
                'section_number': chapter_match.group(1),
                'title': chapter_match.group(2).strip()
            }
        
        section_match = re.match(r'^###\s+Section\s+([\d.]+):\s*(.+)$', line)
        if section_match:
            return {
                'level': 3,
                'section_number': section_match.group(1),
                'title': section_match.group(2).strip()
            }
        
        # Generic heading fallback - only recognize level 2 and 3 as section breaks
        # Level 4+ headings (####, #####, etc.) are treated as content, not section breaks
        if line.startswith('### ') and not line.startswith('#### '):
            return {
                'level': 3,
                'section_number': '',
                'title': line[3:].strip()
            }
        elif line.startswith('## ') and not line.startswith('### '):
            return {
                'level': 2,
                'section_number': '',
                'title': line[2:].strip()
            }
        
        # Level 4+ headings (####, #####, etc.) return None so they're treated as content
        return None
    
    def _extract_educational_elements(self, content: str) -> Dict[str, List[str]]:
        """Extract key educational elements from content"""
        elements = {
            'formulas': [],
            'definitions': [],
            'examples': [],
            'key_concepts': [],
            'equations': []
        }
        
        # Extract mathematical formulas and equations
        formula_patterns = [
            r'([a-zA-Z_][a-zA-Z0-9_]*\s*=.+)',  # variable = expression
            r'(integral.+dx)',  # integrals
            r'(lim\(.+\))',  # limits
            r'(d/dx\[.+\])',  # derivatives
            r'([A-Z_][a-zA-Z0-9_]*\s*=.+)',  # physics equations
        ]
        
        for pattern in formula_patterns:
            matches = re.findall(pattern, content)
            elements['formulas'].extend(matches)
        
        # Extract definitions (text following colons or marked with **)
        definition_patterns = [
            r'\*\*([^*]+)\*\*:\s*([^.]+\.)',  # **Term**: Definition.
            r'([A-Z][a-zA-Z\s]+):\s*([A-Z][^.]+\.)',  # Term: Definition.
        ]
        
        for pattern in definition_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    elements['definitions'].append(f"{match[0]}: {match[1]}")
        
        # Extract examples
        example_matches = re.findall(r'[Ee]xample[s]?:?\s*([^.]+\.)', content)
        elements['examples'].extend(example_matches)
        
        # Extract key concepts (words in **bold**)
        concept_matches = re.findall(r'\*\*([^*]+)\*\*', content)
        elements['key_concepts'].extend(concept_matches)
        
        # Extract numbered equations
        equation_matches = re.findall(r'^\s*\d+\.\s*(.+)', content, re.MULTILINE)
        elements['equations'].extend(equation_matches)
        
        return elements
    
    def get_available_books(self, include_format_info: bool = False) -> List[str]:
        """
        Get list of available book topics from both directories
        
        Args:
            include_format_info: Whether to include format information in the results
        """
        books = {}
        
        # Check JSON books directory
        if self.json_books_dir.exists():
            for file in self.json_books_dir.glob("*.json"):
                books[file.stem] = "json"
        
        # Check text books directory
        if self.books_dir.exists():
            for file in self.books_dir.glob("*.txt"):
                if file.stem not in books:  # JSON takes precedence
                    books[file.stem] = "text"
        
        if include_format_info:
            return [f"{name} ({format})" for name, format in sorted(books.items())]
        else:
            return sorted(books.keys())
    
    def list_books_with_details(self) -> Dict[str, Dict[str, str]]:
        """Get detailed information about available books"""
        books_info = {}
        
        # Check JSON books
        if self.json_books_dir.exists():
            for file in self.json_books_dir.glob("*.json"):
                books_info[file.stem] = {
                    "format": "json",
                    "path": str(file),
                    "enhanced": "yes"
                }
        
        # Check text books
        if self.books_dir.exists():
            for file in self.books_dir.glob("*.txt"):
                if file.stem not in books_info:  # Don't overwrite JSON info
                    books_info[file.stem] = {
                        "format": "text", 
                        "path": str(file),
                        "enhanced": "no"
                    }
        
        return books_info
    
    def get_section_by_number(self, book: BookContent, section_number: str) -> Optional[TextSection]:
        """Get a specific section by its number (e.g., '1.2') with flexible matching"""
        # First, try to find exact match
        exact_match = None
        for section in book.sections:
            if section.section_number == section_number:
                exact_match = section
                break

        # If we found an exact match and it has content, return it
        if exact_match and exact_match.content.strip():
            return exact_match

        # Try partial matches for subsection requests (e.g., "1.1" -> "1")
        if '.' in section_number:
            chapter_number = section_number.split('.')[0]
            # Look for the chapter
            for section in book.sections:
                if section.section_number == chapter_number:
                    print(f"INFO: Section {section_number} not found, using chapter {chapter_number}: '{section.title}'")
                    return section

        # If it's a single digit (chapter number), merge all subsections of that chapter
        if section_number.isdigit():
            merged = self._merge_chapter_content(book, section_number)
            if merged and merged.content.strip():
                return merged

        # Try to find any section that starts with the requested number
        for section in book.sections:
            if section.section_number and section.section_number.startswith(section_number):
                print(f"INFO: Found partial match for {section_number}: '{section.title}' (section {section.section_number})")
                return section

        # Last resort: return first section if it's a simple request
        if section_number in ['1', '1.1', '1.0'] and book.sections:
            first_section = book.sections[0]
            print(f"INFO: Using first available section: '{first_section.title}'")
            return first_section

        # Fallback to exact match even if it has no content (better than nothing)
        return exact_match
    
    def _merge_chapter_content(self, book: BookContent, chapter_number: str) -> Optional[TextSection]:
        """Merge all subsections of a chapter into a single TextSection"""
        # Get the chapter header
        chapter_section = None
        for section in book.sections:
            if section.section_number == chapter_number and section.level == 2:
                chapter_section = section
                break
        
        if not chapter_section:
            return None
        
        # Get all subsections
        subsections = self.get_chapter_sections(book, chapter_number)
        
        if not subsections:
            # If no subsections, return the chapter itself (even if it has minimal content)
            return chapter_section
        
        # Merge content from all subsections
        merged_content_parts = []
        merged_educational_elements = {
            'formulas': [],
            'definitions': [],
            'examples': [],
            'key_concepts': [],
            'equations': []
        }
        
        for subsection in subsections:
            # Add subsection header
            merged_content_parts.append(f"\n### {subsection.title}\n")
            merged_content_parts.append(subsection.content)
            
            # Merge educational elements
            for key, values in subsection.educational_elements.items():
                if key in merged_educational_elements:
                    merged_educational_elements[key].extend(values)
        
        # Create merged section
        merged_content = "\n".join(merged_content_parts).strip()
        
        return TextSection(
            title=chapter_section.title,
            content=merged_content,
            level=chapter_section.level,
            section_number=chapter_section.section_number,
            educational_elements=merged_educational_elements
        )
    
    def get_chapter_sections(self, book: BookContent, chapter_number: str) -> List[TextSection]:
        """Get all sections belonging to a specific chapter"""
        sections = []
        for section in book.sections:
            if section.section_number.startswith(f"{chapter_number}."):
                sections.append(section)
        return sections
    
    def filter_sections_by_keywords(self, book: BookContent, keywords: List[str]) -> List[TextSection]:
        """Filter sections containing specific keywords"""
        matching_sections = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for section in book.sections:
            content_lower = section.content.lower()
            title_lower = section.title.lower()
            
            if any(kw in content_lower or kw in title_lower for kw in keywords_lower):
                matching_sections.append(section)
        
        return matching_sections
    
    @property
    def subdivider(self):
        """Lazy-load the subdivider to avoid circular imports"""
        if self._subdivider is None:
            from .topic_subdivider import TopicSubdivider
            self._subdivider = TopicSubdivider()
        return self._subdivider
    
    @property
    def json_processor(self):
        """Lazy-load the JSON processor to avoid circular imports"""
        if self._json_processor is None:
            from .json_book_processor import JsonBookProcessor
            self._json_processor = JsonBookProcessor(str(self.json_books_dir))
        return self._json_processor
    
    def should_subdivide_section(self, section: TextSection) -> bool:
        """Check if a section should be subdivided into multiple videos"""
        return self.subdivider.should_subdivide_section(section)
    
    def get_subdivided_videos(self, section: TextSection, 
                             subdivision_strategy: str = "auto") -> List['VideoSubtopic']:
        """Get subdivided video topics from a section"""
        return self.subdivider.subdivide_section(section, subdivision_strategy)
    
    def get_focused_videos(self, section: TextSection, 
                          focus_types: List[str]) -> List['VideoSubtopic']:
        """Generate focused videos for specific content types"""
        return self.subdivider.generate_focused_videos(section, focus_types)
    
    def analyze_section_complexity(self, section: TextSection) -> Dict[str, any]:
        """Analyze section complexity and provide subdivision recommendations"""
        complexity = self.subdivider._calculate_complexity_score(section)
        should_subdivide = self.should_subdivide_section(section)
        
        # Count educational elements
        elements = section.educational_elements
        element_counts = {key: len(values) for key, values in elements.items()}
        
        # Estimate video duration for the full section
        estimated_duration = self.subdivider._estimate_duration(section.content)
        
        analysis = {
            'complexity_score': complexity,
            'should_subdivide': should_subdivide,
            'estimated_duration_minutes': estimated_duration,
            'content_length': len(section.content),
            'educational_elements': element_counts,
            'subdivision_recommendation': 'auto'
        }
        
        # Provide subdivision recommendations
        if complexity > 0.8:
            analysis['subdivision_recommendation'] = 'by_concept'
        elif sum(element_counts.values()) > 10:
            analysis['subdivision_recommendation'] = 'by_type'
        elif len(section.content) > 2500:
            analysis['subdivision_recommendation'] = 'by_length'
        
        return analysis
    
    def get_multi_video_breakdown(self, section: TextSection) -> Dict[str, any]:
        """Get a complete breakdown of how a section could be divided into multiple videos"""
        analysis = self.analyze_section_complexity(section)
        
        breakdown = {
            'original_section': {
                'title': section.title,
                'section_number': section.section_number,
                'analysis': analysis
            },
            'subdivision_options': {}
        }
        
        if analysis['should_subdivide']:
            # Get different subdivision strategies
            strategies = ['auto', 'by_type', 'by_length', 'by_concept']
            for strategy in strategies:
                try:
                    subtopics = self.get_subdivided_videos(section, strategy)
                    breakdown['subdivision_options'][strategy] = [
                        {
                            'title': st.title,
                            'subtopic_index': st.subtopic_index,
                            'focus_type': st.focus_type,
                            'estimated_duration': st.estimated_duration,
                            'complexity_score': st.complexity_score,
                            'content_length': len(st.content)
                        }
                        for st in subtopics
                    ]
                except Exception as e:
                    breakdown['subdivision_options'][strategy] = f'Error: {str(e)}'
            
            # Get focused video options
            focus_types = ['definitions', 'examples', 'applications', 'theory']
            try:
                focused_videos = self.get_focused_videos(section, focus_types)
                breakdown['focused_options'] = [
                    {
                        'title': fv.title,
                        'subtopic_index': fv.subtopic_index,
                        'focus_type': fv.focus_type,
                        'estimated_duration': fv.estimated_duration,
                        'content_length': len(fv.content)
                    }
                    for fv in focused_videos if len(fv.content.strip()) > 200
                ]
            except Exception as e:
                breakdown['focused_options'] = f'Error: {str(e)}'
        
        return breakdown
    
    def convert_text_to_json(self, topic_name: str, enhance_content: bool = True, 
                           use_llm: bool = True, api_key: Optional[str] = None) -> bool:
        """
        Convert a text book to JSON format with LLM intelligence
        
        Args:
            topic_name: Name of the book to convert
            enhance_content: Whether to apply intelligent content enhancement
            use_llm: Whether to use LLM-powered conversion
            api_key: Optional OpenAI API key for LLM conversion
            
        Returns:
            True if conversion successful, False otherwise
        """
        text_path = self.books_dir / f"{topic_name}.txt"
        if not text_path.exists():
            print(f"Text book '{topic_name}.txt' not found")
            return False
        
        try:
            from .converters.text_to_json import TextToJsonConverter
            
            # Initialize converter with LLM support
            converter = TextToJsonConverter(use_llm=use_llm, api_key=api_key)
            
            json_output_path = self.json_books_dir / f"{topic_name}.json"
            
            # Convert with LLM intelligence if available
            json_book = converter.convert_book(
                str(text_path), 
                str(json_output_path), 
                enhance_content=enhance_content,
                force_rule_based=not use_llm
            )
            
            print(f"Successfully converted '{topic_name}' to JSON format")
            conversion_method = "LLM-powered" if (use_llm and converter.llm_converter) else "rule-based"
            print(f"Conversion method: {conversion_method}")
            print(f"Enhanced features: {'enabled' if enhance_content else 'disabled'}")
            return True
            
        except Exception as e:
            print(f"Failed to convert '{topic_name}' to JSON: {e}")
            return False
    
    def get_book_format(self, topic_name: str) -> Optional[str]:
        """Get the format of a specific book"""
        try:
            return self.detect_book_format(topic_name)
        except FileNotFoundError:
            return None
    
    def has_json_version(self, topic_name: str) -> bool:
        """Check if a JSON version exists for a book"""
        json_path = self.json_books_dir / f"{topic_name}.json"
        return json_path.exists()
    
    def has_text_version(self, topic_name: str) -> bool:
        """Check if a text version exists for a book"""
        text_path = self.books_dir / f"{topic_name}.txt"
        return text_path.exists()


def main():
    """Test the book processor"""
    processor = BookProcessor()
    
    # List available books
    books = processor.get_available_books()
    print(f"Available books: {books}")
    
    if books:
        # Load first book
        book = processor.load_book(books[0])
        print(f"\nLoaded book: {book.title}")
        print(f"Total sections: {book.total_sections}")
        
        # Show first few sections
        for i, section in enumerate(book.sections[:3]):
            print(f"\n{i+1}. {section.title} (Level {section.level})")
            print(f"   Section: {section.section_number}")
            print(f"   Content length: {len(section.content)} chars")
            print(f"   Educational elements:")
            for key, values in section.educational_elements.items():
                if values:
                    print(f"     {key}: {len(values)} items")


if __name__ == "__main__":
    main()