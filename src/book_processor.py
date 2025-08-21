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
    """Processes textbook files into structured educational content"""
    
    def __init__(self, books_dir: str = "books"):
        self.books_dir = Path(books_dir)
        if not self.books_dir.exists():
            raise FileNotFoundError(f"Books directory not found: {books_dir}")
    
    def load_book(self, topic_name: str) -> BookContent:
        """Load and process a book file into structured content"""
        book_path = self.books_dir / f"{topic_name}.txt"
        
        if not book_path.exists():
            raise FileNotFoundError(f"Book file not found: {book_path}")
        
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
        
        # Generic heading fallback
        if line.startswith('###'):
            return {
                'level': 3,
                'section_number': '',
                'title': line[3:].strip()
            }
        elif line.startswith('##'):
            return {
                'level': 2,
                'section_number': '',
                'title': line[2:].strip()
            }
        
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
            r'(∫.+dx)',  # integrals
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
    
    def get_available_books(self) -> List[str]:
        """Get list of available book topics"""
        if not self.books_dir.exists():
            return []
        
        books = []
        for file in self.books_dir.glob("*.txt"):
            books.append(file.stem)
        
        return sorted(books)
    
    def get_section_by_number(self, book: BookContent, section_number: str) -> Optional[TextSection]:
        """Get a specific section by its number (e.g., '1.2')"""
        for section in book.sections:
            if section.section_number == section_number:
                return section
        return None
    
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