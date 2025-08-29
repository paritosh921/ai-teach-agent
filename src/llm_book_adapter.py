"""
LLM Book Processor Adapter

This module provides backward compatibility with the existing book processing system
while using the new LLM-powered content extraction under the hood.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from .llm_book_processor import LLMBookProcessor, LLMParsedBook, LLMTextSection
from .book_processor import BookProcessor, BookContent, TextSection


class LLMBasedBookProcessor(BookProcessor):
    """
    Enhanced BookProcessor that uses LLM for intelligent content processing
    while maintaining full backward compatibility with existing code.
    """

    def __init__(self, books_dir: str = "books", json_books_dir: str = "books_json",
                 use_llm: bool = True, api_key: Optional[str] = None):
        super().__init__(books_dir, json_books_dir)
        self.use_llm = use_llm
        self.llm_processor = None

        if use_llm:
            try:
                self.llm_processor = LLMBookProcessor(api_key)
                print("✅ LLM-powered book processing enabled")
            except Exception as e:
                print(f"⚠️ LLM processor unavailable: {e}")
                print("Falling back to traditional text processing")
                self.use_llm = False

    def load_book(self, topic_name: str, format_hint: Optional[str] = None) -> BookContent:
        """
        Enhanced load_book that uses LLM processing when available
        """

        # First try the traditional approach
        try:
            # Check if we have a processed LLM version
            llm_cache_path = self._get_llm_cache_path(topic_name)
            if self.use_llm and llm_cache_path.exists():
                print(f"Loading cached LLM-processed book: {topic_name}")
                return self._load_cached_llm_book(llm_cache_path)

            # Try traditional loading first
            traditional_book = super().load_book(topic_name, format_hint)

            # If LLM is available and we don't have a cached version, process with LLM
            if self.use_llm and self.llm_processor:
                print(f"Processing '{topic_name}' with LLM for enhanced content extraction...")
                try:
                    llm_book = self._process_with_llm(topic_name)

                    # Verify that LLM processing produced valid results
                    if llm_book and llm_book.sections and len(llm_book.sections) > 0:
                        self._cache_llm_book(llm_book, llm_cache_path)
                        converted_book = self._convert_llm_to_traditional(llm_book)

                        # Double-check that conversion worked
                        if converted_book and converted_book.sections and len(converted_book.sections) > 0:
                            return converted_book
                        else:
                            print(f"LLM conversion failed, falling back to traditional parsing")
                            return traditional_book
                    else:
                        print(f"LLM processing returned empty results, using traditional parsing")
                        return traditional_book

                except Exception as e:
                    print(f"LLM processing failed ({e}), using traditional parsing")
                    return traditional_book
            else:
                return traditional_book

        except Exception as e:
            # If traditional loading fails and LLM is available, try LLM-only approach
            if self.use_llm and self.llm_processor:
                print(f"Traditional parsing failed, trying LLM-only processing: {e}")
                try:
                    return self._llm_fallback_processing(topic_name)
                except Exception as e2:
                    raise Exception(f"Both traditional and LLM processing failed: {e} | {e2}")
            else:
                raise e

    def _process_with_llm(self, topic_name: str) -> LLMParsedBook:
        """Process a book using LLM"""

        # Try different file formats
        book_path = None

        # Check JSON format first
        json_path = self.json_books_dir / f"{topic_name}.json"
        if json_path.exists():
            # For JSON files, we might want to enhance them with LLM processing
            # For now, just use the text content from the traditional processor
            pass

        # Check text format
        text_path = self.books_dir / f"{topic_name}.txt"
        if text_path.exists():
            book_path = text_path

        if not book_path:
            raise FileNotFoundError(f"No book file found for '{topic_name}'")

        # Process with LLM
        return self.llm_processor.process_book_file(str(book_path), topic_name)

    def _convert_llm_to_traditional(self, llm_book: LLMParsedBook) -> BookContent:
        """Convert LLM-processed book to traditional BookContent format"""

        # Convert LLM sections to traditional TextSections
        traditional_sections = []
        for llm_section in llm_book.sections:
            # Extract educational elements for compatibility
            educational_elements = self._extract_elements_from_llm_section(llm_section)

            traditional_section = TextSection(
                title=llm_section.title,
                content=llm_section.content,
                level=llm_section.level,
                section_number=llm_section.section_number,
                educational_elements=educational_elements
            )
            traditional_sections.append(traditional_section)

        # Separate chapters (level 1 or 2 in LLM system)
        chapters = [s for s in traditional_sections if s.level <= 2]

        return BookContent(
            title=llm_book.title,
            filepath=llm_book.filepath,
            chapters=chapters,
            sections=traditional_sections,
            total_sections=len(traditional_sections)
        )

    def _extract_elements_from_llm_section(self, llm_section: LLMTextSection) -> Dict[str, List[str]]:
        """Extract educational elements from LLM section for backward compatibility"""

        elements = {
            'formulas': llm_section.key_formulas.copy(),
            'definitions': [],
            'examples': [],
            'key_concepts': [],
            'equations': []
        }

        # Extract from educational concepts
        for concept in llm_section.educational_concepts:
            if concept.name:
                elements['key_concepts'].append(concept.name)
            if concept.definition:
                elements['definitions'].append(f"{concept.name}: {concept.definition}")
            elements['examples'].extend(concept.examples)
            elements['formulas'].extend(concept.formulas)

        # Extract from learning objectives
        for objective in llm_section.learning_objectives:
            elements['key_concepts'].append(objective.objective)

        return elements

    def _get_llm_cache_path(self, topic_name: str) -> Path:
        """Get path for LLM-processed cache"""
        cache_dir = Path("cache") / "llm_books"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"{topic_name}_llm.json"

    def _cache_llm_book(self, llm_book: LLMParsedBook, cache_path: Path):
        """Cache LLM-processed book"""
        try:
            self.llm_processor.save_processed_book(llm_book, str(cache_path))
        except Exception as e:
            print(f"Warning: Failed to cache LLM book: {e}")

    def _load_cached_llm_book(self, cache_path: Path) -> BookContent:
        """Load cached LLM book and convert to traditional format"""
        try:
            llm_book = self.llm_processor.load_processed_book(str(cache_path))
            return self._convert_llm_to_traditional(llm_book)
        except Exception as e:
            print(f"Warning: Failed to load cached LLM book: {e}")
            raise e

    def _llm_fallback_processing(self, topic_name: str) -> BookContent:
        """Fallback LLM processing when traditional methods fail"""

        # Try to find any file with the topic name
        for ext in ['.txt', '.md', '.rst']:
            potential_path = self.books_dir / f"{topic_name}{ext}"
            if potential_path.exists():
                llm_book = self.llm_processor.process_book_file(str(potential_path), topic_name)
                return self._convert_llm_to_traditional(llm_book)

        # Try to find files containing the topic name
        for file_path in self.books_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if topic_name.lower() in content.lower():
                        llm_book = self.llm_processor.process_raw_content(content, topic_name)
                        return self._convert_llm_to_traditional(llm_book)
            except Exception:
                continue

        raise FileNotFoundError(f"No suitable content found for topic '{topic_name}'")

    def get_book_info_enhanced(self, topic_name: str) -> Dict[str, Any]:
        """Get enhanced book information using LLM processing"""

        if not self.use_llm or not self.llm_processor:
            return super().get_book_info(topic_name)

        try:
            llm_book = self._process_with_llm(topic_name)

            return {
                'title': llm_book.title,
                'total_sections': llm_book.total_sections,
                'difficulty': llm_book.overall_difficulty,
                'audience': llm_book.target_audience,
                'chapters': [ch.title for ch in llm_book.chapters],
                'sections': [s.title for s in llm_book.sections],
                'prerequisites': list(set(
                    prereq for section in llm_book.sections
                    for prereq in section.prerequisites
                )),
                'estimated_duration': sum(
                    s.estimated_duration_minutes for s in llm_book.sections
                ),
                'processing_method': 'llm_enhanced'
            }

        except Exception as e:
            print(f"Enhanced info unavailable: {e}")
            return super().get_book_info(topic_name)

    def list_books_with_llm_info(self) -> Dict[str, Dict[str, Any]]:
        """List all books with LLM-enhanced information"""
        books = {}

        # Get traditional book info
        traditional_books = self.list_books_with_details()

        for book_name, info in traditional_books.items():
            books[book_name] = info.copy()

            # Try to add LLM-enhanced info
            try:
                enhanced_info = self.get_book_info_enhanced(book_name)
                books[book_name].update({
                    'llm_enhanced': True,
                    'difficulty': enhanced_info.get('difficulty', 'unknown'),
                    'audience': enhanced_info.get('audience', 'unknown'),
                    'estimated_duration': enhanced_info.get('estimated_duration', 0)
                })
            except Exception:
                books[book_name]['llm_enhanced'] = False

        return books
