"""
JSON Book Processor for Educational Content

This module processes JSON-format educational books with rich metadata and
flexible content structures for enhanced video generation capabilities.
"""

import os
import json
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from dataclasses import dataclass

from .schemas.book_schema import (
    JsonBook, Chapter, Section, ContentBlock, ContentBlockType,
    EducationalElements, VideoGenerationHints, DifficultyLevel,
    BookSchemaValidator
)


@dataclass
class JsonTextSection:
    """Adapter class to maintain compatibility with existing TextSection interface"""
    title: str
    content: str
    level: int  # 1=book, 2=chapter, 3=section, 4=subsection
    section_number: str
    educational_elements: Dict[str, List[str]]
    
    # Extended JSON-specific properties
    difficulty: Optional[str] = None
    estimated_duration: Optional[int] = None
    content_blocks: Optional[List[ContentBlock]] = None
    learning_objectives: Optional[List[str]] = None
    video_hints: Optional[Dict[str, Any]] = None
    
    def get_content_by_type(self, content_type: str) -> str:
        """Extract content of specific type from content blocks"""
        if not self.content_blocks:
            return self.content
        
        filtered_blocks = [
            block for block in self.content_blocks 
            if block.type.value == content_type
        ]
        
        if not filtered_blocks:
            return ""
        
        return "\n\n".join(block.content for block in filtered_blocks)
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Get structured examples from content blocks"""
        if not self.content_blocks:
            return []
        
        examples = []
        for block in self.content_blocks:
            if block.type == ContentBlockType.EXAMPLE:
                example_dict = {
                    "title": block.title or "Example",
                    "content": block.content,
                    "problem": block.problem,
                    "solution_steps": block.solution_steps,
                    "answer": block.answer,
                    "hints": block.hints
                }
                examples.append(example_dict)
        
        return examples
    
    def get_formulas(self) -> List[str]:
        """Extract all formulas from content blocks"""
        if not self.content_blocks:
            # Fallback to legacy formula extraction
            return self.educational_elements.get('formulas', [])
        
        formulas = []
        for block in self.content_blocks:
            if block.formula:
                formulas.append(block.formula)
            if block.type == ContentBlockType.FORMULA:
                # Extract formulas from formula blocks
                formula_text = block.content.strip()
                if formula_text:
                    formulas.append(formula_text)
        
        return formulas
    
    def get_definitions(self) -> List[str]:
        """Extract all definitions from content blocks"""
        if not self.content_blocks:
            return self.educational_elements.get('definitions', [])
        
        definitions = []
        for block in self.content_blocks:
            if block.type == ContentBlockType.DEFINITION:
                def_text = f"{block.title}: {block.content}" if block.title else block.content
                definitions.append(def_text)
        
        return definitions


@dataclass
class JsonBookContent:
    """JSON book content structure compatible with existing BookContent interface"""
    title: str
    filepath: str
    chapters: List[JsonTextSection]
    sections: List[JsonTextSection]
    total_sections: int
    
    # Extended JSON-specific properties
    json_book: Optional[JsonBook] = None
    metadata: Optional[Dict[str, Any]] = None


class JsonBookProcessor:
    """Processes JSON-format educational books with rich content structures"""
    
    def __init__(self, books_dir: str = "books_json"):
        self.books_dir = Path(books_dir)
        self.books_dir.mkdir(exist_ok=True)
        
        # Fallback to regular books directory if JSON directory doesn't exist
        if not list(self.books_dir.glob("*.json")):
            self.fallback_books_dir = Path("books")
        else:
            self.fallback_books_dir = None
    
    def load_json_book(self, topic_name: str) -> JsonBookContent:
        """Load and process a JSON book file"""
        json_path = self.books_dir / f"{topic_name}.json"
        
        if not json_path.exists():
            raise FileNotFoundError(f"JSON book file not found: {json_path}")
        
        try:
            # Load and validate JSON book
            json_book = JsonBook.load_json(json_path)
            
            # Validate schema
            book_dict = json_book.to_dict()
            validation_errors = BookSchemaValidator.validate_book(book_dict)
            if validation_errors:
                print(f"WARNING: JSON book validation errors:")
                for error in validation_errors[:5]:  # Show first 5 errors
                    print(f"  - {error}")
                if len(validation_errors) > 5:
                    print(f"  ... and {len(validation_errors) - 5} more errors")
            
            return self._convert_json_to_book_content(json_book, str(json_path))
            
        except Exception as e:
            raise ValueError(f"Error loading JSON book '{topic_name}': {e}")
    
    def _convert_json_to_book_content(self, json_book: JsonBook, filepath: str) -> JsonBookContent:
        """Convert JsonBook to JsonBookContent for compatibility"""
        chapters = []
        all_sections = []
        
        for chapter in json_book.chapters:
            # Create chapter as a section (level 2)
            chapter_educational_elements = {
                'formulas': [],
                'definitions': [],
                'examples': [],
                'key_concepts': [],
                'equations': []
            }
            
            chapter_content = chapter.description or f"Chapter {chapter.number}: {chapter.title}"
            
            chapter_section = JsonTextSection(
                title=chapter.title,
                content=chapter_content,
                level=2,
                section_number=str(chapter.number),
                educational_elements=chapter_educational_elements,
                estimated_duration=chapter.estimated_total_duration
            )
            chapters.append(chapter_section)
            all_sections.append(chapter_section)
            
            # Process sections within the chapter
            for section in chapter.sections:
                section_content = self._extract_section_content(section)
                educational_elements = self._extract_educational_elements(section)
                
                json_section = JsonTextSection(
                    title=section.title,
                    content=section_content,
                    level=3,
                    section_number=section.number,
                    educational_elements=educational_elements,
                    difficulty=section.difficulty.value,
                    estimated_duration=section.estimated_duration,
                    content_blocks=section.content_blocks,
                    learning_objectives=[obj.objective for obj in section.learning_objectives],
                    video_hints=section.video_hints.to_dict() if section.video_hints else None
                )
                all_sections.append(json_section)
                
                # Process subsections if any
                for subsection in section.subsections:
                    subsection_content = self._extract_section_content(subsection)
                    subsection_educational_elements = self._extract_educational_elements(subsection)
                    
                    json_subsection = JsonTextSection(
                        title=subsection.title,
                        content=subsection_content,
                        level=4,
                        section_number=subsection.number,
                        educational_elements=subsection_educational_elements,
                        difficulty=subsection.difficulty.value,
                        estimated_duration=subsection.estimated_duration,
                        content_blocks=subsection.content_blocks
                    )
                    all_sections.append(json_subsection)
        
        return JsonBookContent(
            title=json_book.metadata.title,
            filepath=filepath,
            chapters=chapters,
            sections=all_sections,
            total_sections=len(all_sections),
            json_book=json_book,
            metadata=json_book.metadata.to_dict()
        )
    
    def _extract_section_content(self, section: Section) -> str:
        """Extract readable content from section content blocks"""
        content_parts = []
        
        for block in section.content_blocks:
            if block.title:
                if block.type == ContentBlockType.DEFINITION:
                    content_parts.append(f"**{block.title}**: {block.content}")
                elif block.type == ContentBlockType.EXAMPLE:
                    content_parts.append(f"**Example: {block.title}**")
                    content_parts.append(block.content)
                    if block.problem:
                        content_parts.append(f"Problem: {block.problem}")
                    if block.solution_steps:
                        content_parts.append("Solution:")
                        for i, step in enumerate(block.solution_steps, 1):
                            content_parts.append(f"{i}. {step}")
                    if block.answer:
                        content_parts.append(f"Answer: {block.answer}")
                elif block.type == ContentBlockType.THEOREM:
                    content_parts.append(f"**Theorem: {block.title}**")
                    content_parts.append(block.content)
                    if block.hypothesis:
                        content_parts.append(f"Hypothesis: {block.hypothesis}")
                    if block.conclusion:
                        content_parts.append(f"Conclusion: {block.conclusion}")
                else:
                    content_parts.append(f"**{block.title}**")
                    content_parts.append(block.content)
            else:
                content_parts.append(block.content)
            
            # Add formula if present
            if block.formula:
                content_parts.append(f"Formula: {block.formula}")
            
            content_parts.append("")  # Add spacing between blocks
        
        return "\n".join(content_parts).strip()
    
    def _extract_educational_elements(self, section: Section) -> Dict[str, List[str]]:
        """Extract educational elements from section content blocks"""
        if section.educational_elements:
            return {
                'formulas': section.educational_elements.formulas,
                'definitions': section.educational_elements.definitions,
                'examples': [str(ex) for ex in section.educational_elements.examples],
                'key_concepts': section.educational_elements.key_concepts,
                'equations': []  # Can be extended
            }
        
        # Extract from content blocks if no explicit educational elements
        elements = {
            'formulas': [],
            'definitions': [],
            'examples': [],
            'key_concepts': [],
            'equations': []
        }
        
        for block in section.content_blocks:
            if block.type == ContentBlockType.FORMULA and block.formula:
                elements['formulas'].append(block.formula)
            elif block.type == ContentBlockType.DEFINITION:
                def_text = f"{block.title}: {block.content}" if block.title else block.content
                elements['definitions'].append(def_text)
            elif block.type == ContentBlockType.EXAMPLE:
                example_text = block.title or "Example"
                elements['examples'].append(example_text)
            
            # Extract key concepts from tags
            if block.tags:
                elements['key_concepts'].extend(block.tags)
        
        return elements
    
    def get_available_books(self) -> List[str]:
        """Get list of available JSON book topics"""
        books = []
        
        # Check JSON books directory
        if self.books_dir.exists():
            for file in self.books_dir.glob("*.json"):
                books.append(file.stem)
        
        # Check fallback directory if needed
        if not books and self.fallback_books_dir and self.fallback_books_dir.exists():
            for file in self.fallback_books_dir.glob("*.txt"):
                books.append(f"{file.stem} (text format)")
        
        return sorted(books)
    
    def get_section_by_number(self, book: JsonBookContent, section_number: str) -> Optional[JsonTextSection]:
        """Get a specific section by its number"""
        for section in book.sections:
            if section.section_number == section_number:
                return section
        return None
    
    def get_chapter_sections(self, book: JsonBookContent, chapter_number: str) -> List[JsonTextSection]:
        """Get all sections belonging to a specific chapter"""
        sections = []
        for section in book.sections:
            if section.section_number.startswith(f"{chapter_number}."):
                sections.append(section)
        return sections
    
    def analyze_section_complexity(self, section: JsonTextSection) -> Dict[str, Any]:
        """Analyze section complexity with JSON-specific enhancements"""
        base_analysis = {
            'content_length': len(section.content),
            'estimated_duration_minutes': section.estimated_duration or self._estimate_duration(section.content),
            'difficulty': section.difficulty or "unknown",
            'educational_elements': {key: len(values) for key, values in section.educational_elements.items()}
        }
        
        # Enhanced analysis from JSON metadata
        if section.content_blocks:
            block_types = [block.type.value for block in section.content_blocks]
            base_analysis['content_block_types'] = block_types
            base_analysis['content_blocks_count'] = len(section.content_blocks)
            
            # Count specific educational content types
            base_analysis['examples_count'] = len([b for b in section.content_blocks if b.type == ContentBlockType.EXAMPLE])
            base_analysis['definitions_count'] = len([b for b in section.content_blocks if b.type == ContentBlockType.DEFINITION])
            base_analysis['formulas_count'] = len([b for b in section.content_blocks if b.type == ContentBlockType.FORMULA])
        
        if section.video_hints:
            base_analysis['suggested_subdivision_strategy'] = section.video_hints.get('subdivision_strategy', 'auto')
            base_analysis['suggested_focus_areas'] = section.video_hints.get('focus_areas', [])
            base_analysis['complexity_score'] = section.video_hints.get('complexity_score', 0.5)
        else:
            base_analysis['complexity_score'] = self._calculate_complexity_score(section)
        
        # Determine if subdivision is recommended
        base_analysis['should_subdivide'] = (
            base_analysis['complexity_score'] > 0.6 or
            base_analysis['content_length'] > 2000 or
            base_analysis.get('content_blocks_count', 0) > 6
        )
        
        return base_analysis
    
    def _estimate_duration(self, content: str) -> int:
        """Estimate video duration in minutes"""
        char_count = len(content)
        word_count = char_count / 5  # Rough estimation
        duration_minutes = max(1, int(word_count / 150))  # 150 words per minute
        return duration_minutes
    
    def _calculate_complexity_score(self, section: JsonTextSection) -> float:
        """Calculate complexity score for a section"""
        content_length = len(section.content)
        
        # Base complexity from content length
        length_score = min(content_length / 2000, 1.0)
        
        # Educational element density
        total_elements = sum(len(values) for values in section.educational_elements.values())
        element_density = min(total_elements / 20, 1.0)
        
        # Difficulty level scoring
        difficulty_scores = {
            'beginner': 0.2,
            'intermediate': 0.5,
            'advanced': 0.8,
            'expert': 1.0
        }
        difficulty_score = difficulty_scores.get(section.difficulty, 0.5)
        
        # Content block complexity
        block_complexity = 0.0
        if section.content_blocks:
            complex_types = [ContentBlockType.PROOF, ContentBlockType.THEOREM, ContentBlockType.EXERCISE]
            complex_blocks = len([b for b in section.content_blocks if b.type in complex_types])
            block_complexity = min(complex_blocks / 5, 1.0)
        
        # Weighted combination
        return (length_score * 0.3 + element_density * 0.3 + 
               difficulty_score * 0.2 + block_complexity * 0.2)
    
    def supports_subdivision_hints(self) -> bool:
        """Check if this processor supports subdivision hints"""
        return True
    
    def get_subdivision_recommendations(self, section: JsonTextSection) -> Dict[str, Any]:
        """Get subdivision recommendations specific to JSON format"""
        recommendations = {
            'strategies': ['auto', 'by_type', 'by_length', 'by_concept'],
            'recommended_strategy': 'auto'
        }
        
        if section.video_hints:
            hints = section.video_hints
            if hints.get('subdivision_strategy'):
                recommendations['recommended_strategy'] = hints['subdivision_strategy']
            if hints.get('focus_areas'):
                recommendations['focus_areas'] = hints['focus_areas']
        
        # Analyze content blocks for recommendations
        if section.content_blocks:
            block_types = [block.type.value for block in section.content_blocks]
            
            # If many different content types, recommend by_type
            unique_types = len(set(block_types))
            if unique_types >= 4:
                recommendations['recommended_strategy'] = 'by_type'
                recommendations['reason'] = f"Section contains {unique_types} different content types"
            
            # If very long content, recommend by_length
            elif len(section.content) > 3000:
                recommendations['recommended_strategy'] = 'by_length'
                recommendations['reason'] = "Section content is very long"
            
            # If complex educational elements, recommend by_concept
            elif any(block.type in [ContentBlockType.THEOREM, ContentBlockType.PROOF] for block in section.content_blocks):
                recommendations['recommended_strategy'] = 'by_concept'
                recommendations['reason'] = "Section contains complex theoretical content"
        
        return recommendations


def main():
    """Test the JSON book processor"""
    processor = JsonBookProcessor()
    
    # List available books
    books = processor.get_available_books()
    print(f"Available JSON books: {books}")
    
    if books:
        try:
            # Try to load first book
            book_name = books[0].replace(" (text format)", "")
            book = processor.load_json_book(book_name)
            print(f"\nLoaded JSON book: {book.title}")
            print(f"Total sections: {book.total_sections}")
            
            # Show first few sections
            for i, section in enumerate(book.sections[:3]):
                print(f"\n{i+1}. {section.title} (Level {section.level})")
                print(f"   Section: {section.section_number}")
                print(f"   Difficulty: {section.difficulty}")
                print(f"   Duration: {section.estimated_duration} minutes")
                if section.content_blocks:
                    print(f"   Content blocks: {len(section.content_blocks)}")
                    block_types = [block.type.value for block in section.content_blocks]
                    print(f"   Block types: {', '.join(set(block_types))}")
        except Exception as e:
            print(f"Error loading JSON book: {e}")


if __name__ == "__main__":
    main()