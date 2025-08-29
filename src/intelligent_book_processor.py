"""
Intelligent Book Processor with LLM-Powered Content Analysis

This module uses Large Language Models to intelligently parse and understand
educational content regardless of formatting, structure, or style. It replaces
rigid pattern matching with semantic content understanding.
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from openai import OpenAI

# Import existing structures for compatibility
from .book_processor import TextSection, BookContent


@dataclass
class ContentStructure:
    """LLM-analyzed content structure"""
    document_type: str  # textbook, paper, manual, etc.
    subject_area: str   # mathematics, physics, chemistry, etc.
    educational_level: str  # elementary, high_school, undergraduate, graduate
    total_chapters: int
    total_sections: int
    structure_confidence: float  # 0.0-1.0 confidence in analysis
    formatting_style: str  # markdown, plain_text, academic, etc.


@dataclass
class SemanticSection:
    """Semantically understood section with LLM analysis"""
    title: str
    content: str
    level: int
    section_number: str
    semantic_type: str  # introduction, theory, examples, applications, summary
    educational_elements: Dict[str, List[str]]
    prerequisite_concepts: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    difficulty_level: float = 0.5  # 0.0-1.0 scale
    estimated_duration: int = 10   # minutes


@dataclass
class IntelligentBookContent:
    """Enhanced book content with semantic understanding"""
    title: str
    filepath: str
    structure: ContentStructure
    chapters: List[SemanticSection]
    sections: List[SemanticSection]
    total_sections: int
    content_analysis: Dict[str, Any] = field(default_factory=dict)
    
    def to_book_content(self) -> BookContent:
        """Convert to legacy BookContent for compatibility"""
        # Convert SemanticSections to TextSections
        legacy_chapters = []
        legacy_sections = []
        
        for chapter in self.chapters:
            legacy_chapters.append(TextSection(
                title=chapter.title,
                content=chapter.content,
                level=chapter.level,
                section_number=chapter.section_number,
                educational_elements=chapter.educational_elements
            ))
        
        for section in self.sections:
            legacy_sections.append(TextSection(
                title=section.title,
                content=section.content,
                level=section.level,
                section_number=section.section_number,
                educational_elements=section.educational_elements
            ))
        
        return BookContent(
            title=self.title,
            filepath=self.filepath,
            chapters=legacy_chapters,
            sections=legacy_sections,
            total_sections=self.total_sections
        )


class IntelligentBookProcessor:
    """
    LLM-powered book processor that understands content semantically
    
    This processor can handle any educational text format:
    - Plain text files with any structure
    - Markdown files (any variant)
    - Poorly formatted or unstructured content
    - Mixed formatting styles
    - Missing section numbers or headers
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, books_dir: str = "books", model: str = "gpt-4o-mini"):
        self.books_dir = Path(books_dir)
        self.books_dir.mkdir(exist_ok=True)
        
        # Initialize OpenAI client (optional for fallback mode)
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            self.client = None
        self.model = model
        
        # Content analysis cache
        self.analysis_cache = {}
        self.cache_file = Path("temp/content_analysis_cache.json")
        self.cache_file.parent.mkdir(exist_ok=True)
        self._load_cache()
    
    def _load_cache(self):
        """Load analysis cache from file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.analysis_cache = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load analysis cache: {e}")
            self.analysis_cache = {}
    
    def _save_cache(self):
        """Save analysis cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save analysis cache: {e}")
    
    def load_book(self, topic_name: str) -> IntelligentBookContent:
        """
        Load and intelligently parse any educational content
        
        Args:
            topic_name: Name of the book file (without extension)
            
        Returns:
            IntelligentBookContent with semantic understanding
        """
        print(f"INTELLIGENT: Loading book '{topic_name}' with LLM-powered analysis...")
        
        # Try different file extensions
        possible_files = [
            self.books_dir / f"{topic_name}.txt",
            self.books_dir / f"{topic_name}.md",
            self.books_dir / f"{topic_name}.markdown"
        ]
        
        book_path = None
        for path in possible_files:
            if path.exists():
                book_path = path
                break
        
        if not book_path:
            raise FileNotFoundError(f"Book '{topic_name}' not found. Tried: {[str(p) for p in possible_files]}")
        
        # Load content
        with open(book_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        print(f"INTELLIGENT: Loaded {len(raw_content)} characters from {book_path}")
        
        # Check cache first
        content_hash = str(hash(raw_content))
        if content_hash in self.analysis_cache:
            print("INTELLIGENT: Using cached analysis...")
            cached_data = self.analysis_cache[content_hash]
            return self._reconstruct_from_cache(cached_data, str(book_path))
        
        # Analyze content structure with LLM
        print("INTELLIGENT: Analyzing content structure with LLM...")
        structure = self._analyze_content_structure(raw_content)
        
        # Extract sections semantically
        print("INTELLIGENT: Extracting sections semantically...")
        sections = self._extract_sections_semantically(raw_content, structure)
        
        # Generate section numbers if missing
        print("INTELLIGENT: Generating section numbers...")
        numbered_sections = self._generate_section_numbers(sections, structure)
        
        # Enhance sections with educational analysis
        print("INTELLIGENT: Analyzing educational elements...")
        enhanced_sections = self._enhance_sections_with_analysis(numbered_sections)
        
        # Create book content
        book_content = self._create_book_content(
            topic_name, str(book_path), structure, enhanced_sections
        )
        
        # Cache the analysis
        self._cache_analysis(content_hash, book_content)
        
        print(f"INTELLIGENT: Analysis complete - found {len(book_content.sections)} sections")
        return book_content
    
    def _analyze_content_structure(self, content: str) -> ContentStructure:
        """Use LLM to analyze overall content structure"""
        
        # Truncate very long content for initial analysis
        analysis_content = content[:8000] if len(content) > 8000 else content
        
        prompt = f"""Analyze this educational content and determine its structure. 
        
CONTENT TO ANALYZE:
{analysis_content}

Provide a JSON response with this exact structure:
{{
    "document_type": "textbook|paper|manual|notes|other",
    "subject_area": "mathematics|physics|chemistry|biology|computer_science|other",
    "educational_level": "elementary|high_school|undergraduate|graduate",
    "total_chapters": <estimated number of major chapters>,
    "total_sections": <estimated number of sections/subsections>,
    "structure_confidence": <confidence 0.0-1.0>,
    "formatting_style": "markdown|plain_text|academic|mixed"
}}

Focus on identifying the educational content's organization and structure patterns."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing educational content structure. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text.replace('```json', '').replace('```', '')
            
            analysis_data = json.loads(analysis_text)
            
            return ContentStructure(
                document_type=analysis_data.get('document_type', 'textbook'),
                subject_area=analysis_data.get('subject_area', 'other'),
                educational_level=analysis_data.get('educational_level', 'undergraduate'),
                total_chapters=analysis_data.get('total_chapters', 1),
                total_sections=analysis_data.get('total_sections', 5),
                structure_confidence=analysis_data.get('structure_confidence', 0.8),
                formatting_style=analysis_data.get('formatting_style', 'plain_text')
            )
            
        except Exception as e:
            print(f"Warning: Structure analysis failed: {e}")
            # Return default structure
            return ContentStructure(
                document_type='textbook',
                subject_area='other', 
                educational_level='undergraduate',
                total_chapters=1,
                total_sections=5,
                structure_confidence=0.5,
                formatting_style='plain_text'
            )
    
    def _extract_sections_semantically(self, content: str, structure: ContentStructure) -> List[Dict[str, Any]]:
        """Use LLM to extract sections based on semantic understanding"""
        
        # Split content into chunks for processing
        chunks = self._split_content_for_analysis(content, max_chunk_size=6000)
        all_sections = []
        
        for i, chunk in enumerate(chunks):
            print(f"INTELLIGENT: Analyzing chunk {i+1}/{len(chunks)}...")
            
            prompt = f"""Analyze this educational content chunk and identify distinct sections or topics.

CONTENT CHUNK:
{chunk}

CONTEXT:
- Document type: {structure.document_type}
- Subject: {structure.subject_area}
- Level: {structure.educational_level}

Identify logical sections and provide a JSON array with this structure:
[
    {{
        "title": "Clear, descriptive title for this section",
        "content": "The actual content text for this section",
        "level": 2 or 3,  // 2=chapter/major section, 3=subsection
        "semantic_type": "introduction|theory|examples|applications|summary|other",
        "boundary_confidence": <confidence 0.0-1.0>,
        "key_topics": ["list", "of", "main", "topics"]
    }}
]

Guidelines:
- Each section should be a coherent educational unit
- Look for natural topic transitions, not just formatting
- Include the full content text for each section
- Sections should be substantial enough for a video (at least 100 words)
- Identify the semantic purpose of each section"""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert educational content analyst. Always respond with valid JSON arrays."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=3000
                )
                
                sections_text = response.choices[0].message.content.strip()
                
                # Clean JSON response
                if sections_text.startswith('```json'):
                    sections_text = sections_text.replace('```json', '').replace('```', '')
                
                chunk_sections = json.loads(sections_text)
                
                # Validate and add to all sections
                for section in chunk_sections:
                    if (section.get('title') and 
                        section.get('content') and 
                        len(section['content'].strip()) >= 50):  # Minimum content length
                        all_sections.append(section)
                        
            except Exception as e:
                print(f"Warning: Chunk analysis failed: {e}")
                # Fallback: treat entire chunk as one section
                all_sections.append({
                    'title': f"Content Section {i+1}",
                    'content': chunk,
                    'level': 2,
                    'semantic_type': 'other',
                    'boundary_confidence': 0.3,
                    'key_topics': []
                })
        
        # Merge overlapping or very short sections
        merged_sections = self._merge_small_sections(all_sections)
        
        return merged_sections
    
    def _split_content_for_analysis(self, content: str, max_chunk_size: int = 6000) -> List[str]:
        """Split content into chunks for LLM analysis"""
        if len(content) <= max_chunk_size:
            return [content]
        
        # Try to split at natural boundaries
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph exceeds chunk size, start new chunk
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _merge_small_sections(self, sections: List[Dict[str, Any]], min_words: int = 50) -> List[Dict[str, Any]]:
        """Merge sections that are too small to be useful"""
        merged = []
        i = 0
        
        while i < len(sections):
            current_section = sections[i]
            word_count = len(current_section['content'].split())
            
            # If section is too small, try to merge with next
            if word_count < min_words and i < len(sections) - 1:
                next_section = sections[i + 1]
                
                # Merge sections
                merged_section = {
                    'title': f"{current_section['title']} & {next_section['title']}",
                    'content': current_section['content'] + "\n\n" + next_section['content'],
                    'level': min(current_section['level'], next_section['level']),
                    'semantic_type': 'combined',
                    'boundary_confidence': min(
                        current_section.get('boundary_confidence', 0.5),
                        next_section.get('boundary_confidence', 0.5)
                    ),
                    'key_topics': current_section.get('key_topics', []) + next_section.get('key_topics', [])
                }
                
                merged.append(merged_section)
                i += 2  # Skip both sections
            else:
                merged.append(current_section)
                i += 1
        
        return merged
    
    def _generate_section_numbers(self, sections: List[Dict[str, Any]], 
                                 structure: ContentStructure) -> List[Dict[str, Any]]:
        """Generate appropriate section numbers for content"""
        
        numbered_sections = []
        chapter_count = 1
        section_count = 1
        
        for section in sections:
            level = section.get('level', 2)
            
            if level == 2:  # Chapter level
                section_number = str(chapter_count)
                chapter_count += 1
                section_count = 1  # Reset section count for new chapter
            else:  # Section level
                section_number = f"{chapter_count-1}.{section_count}"
                section_count += 1
            
            # Add section number to section data
            section['section_number'] = section_number
            numbered_sections.append(section)
        
        return numbered_sections
    
    def _enhance_sections_with_analysis(self, sections: List[Dict[str, Any]]) -> List[SemanticSection]:
        """Enhance sections with detailed educational analysis"""
        
        enhanced_sections = []
        
        for section_data in sections:
            print(f"INTELLIGENT: Analyzing '{section_data['title'][:50]}...'")
            
            # Extract educational elements using LLM
            educational_elements = self._extract_educational_elements_llm(section_data['content'])
            
            # Analyze learning aspects
            learning_analysis = self._analyze_learning_aspects(section_data['content'])
            
            # Create semantic section
            semantic_section = SemanticSection(
                title=section_data['title'],
                content=section_data['content'],
                level=section_data['level'],
                section_number=section_data['section_number'],
                semantic_type=section_data.get('semantic_type', 'other'),
                educational_elements=educational_elements,
                prerequisite_concepts=learning_analysis.get('prerequisites', []),
                learning_objectives=learning_analysis.get('objectives', []),
                key_concepts=learning_analysis.get('key_concepts', []),
                difficulty_level=learning_analysis.get('difficulty', 0.5),
                estimated_duration=self._estimate_duration(section_data['content'])
            )
            
            enhanced_sections.append(semantic_section)
        
        return enhanced_sections
    
    def _extract_educational_elements_llm(self, content: str) -> Dict[str, List[str]]:
        """Use LLM to extract educational elements semantically"""
        
        # Truncate very long content
        analysis_content = content[:4000] if len(content) > 4000 else content
        
        prompt = f"""Analyze this educational content and extract key educational elements.

CONTENT:
{analysis_content}

Extract and categorize educational elements into this JSON structure:
{{
    "definitions": ["list of definitions or key terms explained"],
    "formulas": ["mathematical formulas, equations, or expressions"],
    "examples": ["examples, worked problems, or illustrations"],
    "theorems": ["theorems, laws, principles, or rules"],
    "applications": ["real-world applications or practical uses"],
    "key_concepts": ["important concepts or ideas"]
}}

Guidelines:
- Extract actual text snippets, not just titles
- Focus on educational content that would be important for learning
- Include mathematical expressions as they appear
- Capture examples with enough context to be useful"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying educational elements in academic content. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            elements_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if elements_text.startswith('```json'):
                elements_text = elements_text.replace('```json', '').replace('```', '')
            
            return json.loads(elements_text)
            
        except Exception as e:
            print(f"Warning: Educational elements extraction failed: {e}")
            # Fallback to basic pattern matching
            return self._extract_educational_elements_fallback(content)
    
    def _extract_sections_fallback(self, content: str) -> List[Dict[str, Any]]:
        """Extract sections using pattern-based fallback when LLM is unavailable"""
        sections = []
        lines = content.split('\n')
        current_section = None
        
        # Enhanced patterns to catch various section formats
        import re
        section_patterns = [
            (r'^#{1,4}\s*(.+)', 'header'),  # # Header, ## Header, etc.
            (r'^Chapter\s+(\d+)[:\s]*(.+)', 'chapter'),  # Chapter X: Title
            (r'^Section\s+([0-9.]+)[:\s]*(.+)', 'section'),  # Section X.Y: Title  
            (r'^([0-9]+\.(?:[0-9]+\.)*[0-9]*)\s*[-:]?\s*(.+)', 'numbered'),  # X.Y Title or X.Y: Title
            (r'^([A-Z][^.!?]*[.!?])\s*$', 'statement'),  # Statement-like lines
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            matched = False
            for pattern, section_type in section_patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous section if exists
                    if current_section:
                        sections.append(current_section)
                    
                    # Determine level and title based on pattern type
                    if section_type == 'header':
                        level = min(line.count('#'), 3)
                        title = match.group(1).strip()
                    elif section_type == 'chapter':
                        level = 2
                        title = f"Chapter {match.group(1)}: {match.group(2).strip()}"
                    elif section_type == 'section':
                        level = 3
                        title = match.group(2).strip()
                    elif section_type == 'numbered':
                        level = 3
                        title = match.group(2).strip()
                    else:
                        level = 2
                        title = line
                    
                    current_section = {
                        'title': title,
                        'content': line,
                        'level': level,
                        'line_start': i,
                        'line_end': i
                    }
                    matched = True
                    break
            
            # Add content to current section
            if not matched and current_section:
                current_section['content'] += '\n' + line
                current_section['line_end'] = i
        
        # Add final section
        if current_section:
            sections.append(current_section)
            
        return sections
    
    def _search_sections_by_content(self, sections: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Search sections by content with scoring"""
        import re
        
        query_lower = query.lower()
        matches = []
        
        for section in sections:
            title = section.get('title', '').lower()
            content = section.get('content', '').lower()
            
            # Exact number match gets highest score
            if re.search(rf'\b{re.escape(query)}\b', title + ' ' + content):
                score = 1.0
            elif query_lower in title:
                score = 0.8
            elif query_lower in content:
                score = 0.6
            else:
                # Fuzzy matching for partial matches
                score = 0.0
                for word in query.split():
                    if word.lower() in title or word.lower() in content:
                        score += 0.2
            
            if score > 0:
                matches.append({
                    **section,
                    'score': score
                })
        
        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches

    def _extract_educational_elements_fallback(self, content: str) -> Dict[str, List[str]]:
        """Fallback educational element extraction using patterns"""
        elements = {
            'definitions': [],
            'formulas': [],
            'examples': [],
            'theorems': [],
            'applications': [],
            'key_concepts': []
        }
        
        # Simple pattern-based extraction as fallback
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for definitions
            if any(keyword in line.lower() for keyword in ['define', 'definition', 'is called', 'refers to']):
                elements['definitions'].append(line)
            
            # Look for examples
            elif any(keyword in line.lower() for keyword in ['example', 'for instance', 'consider']):
                elements['examples'].append(line)
            
            # Look for formulas (simple heuristic)
            elif '=' in line and any(char in line for char in ['x', 'y', 'f', '(', ')', '+', '-']):
                elements['formulas'].append(line)
            
            # Look for important concepts (bold or capitalized)
            elif '**' in line or line.isupper():
                elements['key_concepts'].append(line.replace('**', ''))
        
        return elements
    
    def _analyze_learning_aspects(self, content: str) -> Dict[str, Any]:
        """Analyze learning objectives and prerequisites"""
        
        # Simple analysis for now - can be enhanced with more sophisticated LLM prompts
        analysis = {
            'prerequisites': [],
            'objectives': [],
            'key_concepts': [],
            'difficulty': 0.5
        }
        
        # Estimate difficulty based on content complexity
        complexity_indicators = [
            'theorem', 'proof', 'lemma', 'corollary', 'integral', 'derivative',
            'matrix', 'eigenvalue', 'transformation', 'convergence'
        ]
        
        complexity_count = sum(1 for indicator in complexity_indicators 
                             if indicator in content.lower())
        
        analysis['difficulty'] = min(1.0, complexity_count * 0.1 + 0.3)
        
        return analysis
    
    def _estimate_duration(self, content: str) -> int:
        """Estimate video duration in minutes"""
        # Rough estimation: 150 words per minute for narration
        word_count = len(content.split())
        base_duration = max(5, word_count // 150)
        
        # Adjust for mathematical content (slower)
        formula_count = content.count('=') + content.count('∫') + content.count('∑')
        math_adjustment = formula_count * 0.5
        
        return int(base_duration + math_adjustment)
    
    def _create_book_content(self, title: str, filepath: str, 
                           structure: ContentStructure,
                           sections: List[SemanticSection]) -> IntelligentBookContent:
        """Create final intelligent book content structure"""
        
        # Separate chapters and sections
        chapters = [s for s in sections if s.level == 2]
        all_sections = sections  # Include all levels
        
        return IntelligentBookContent(
            title=title,
            filepath=filepath,
            structure=structure,
            chapters=chapters,
            sections=all_sections,
            total_sections=len(all_sections),
            content_analysis={
                'processing_method': 'llm_semantic',
                'confidence': structure.structure_confidence,
                'sections_analyzed': len(sections),
                'average_duration': sum(s.estimated_duration for s in sections) / len(sections) if sections else 0
            }
        )
    
    def _cache_analysis(self, content_hash: str, book_content: IntelligentBookContent):
        """Cache analysis results for future use"""
        try:
            # Convert to serializable format
            cache_data = {
                'title': book_content.title,
                'structure': book_content.structure.__dict__,
                'sections': [
                    {
                        'title': s.title,
                        'content': s.content,
                        'level': s.level,
                        'section_number': s.section_number,
                        'semantic_type': s.semantic_type,
                        'educational_elements': s.educational_elements,
                        'estimated_duration': s.estimated_duration
                    }
                    for s in book_content.sections
                ]
            }
            
            self.analysis_cache[content_hash] = cache_data
            self._save_cache()
            
        except Exception as e:
            print(f"Warning: Could not cache analysis: {e}")
    
    def _reconstruct_from_cache(self, cache_data: Dict[str, Any], filepath: str) -> IntelligentBookContent:
        """Reconstruct book content from cache"""
        
        # Reconstruct structure
        structure = ContentStructure(**cache_data['structure'])
        
        # Reconstruct sections
        sections = []
        for section_data in cache_data['sections']:
            section = SemanticSection(
                title=section_data['title'],
                content=section_data['content'],
                level=section_data['level'],
                section_number=section_data['section_number'],
                semantic_type=section_data['semantic_type'],
                educational_elements=section_data['educational_elements'],
                estimated_duration=section_data['estimated_duration']
            )
            sections.append(section)
        
        return self._create_book_content(cache_data['title'], filepath, structure, sections)
    
    def find_section_by_number(self, book_content: IntelligentBookContent, 
                              section_number: str) -> Optional[SemanticSection]:
        """Find section by number with flexible matching"""
        
        # Try exact match first
        for section in book_content.sections:
            if section.section_number == section_number:
                return section
        
        # Try partial matches
        for section in book_content.sections:
            if section.section_number.startswith(section_number) or section_number in section.section_number:
                return section
        
        # Try semantic search in titles
        search_terms = section_number.replace('.', ' ').split()
        for section in book_content.sections:
            title_lower = section.title.lower()
            if any(term in title_lower for term in search_terms):
                return section
        
        return None
    
    def list_available_sections(self, book_content: IntelligentBookContent) -> List[Tuple[str, str]]:
        """List all available sections with numbers and titles"""
        return [(section.section_number, section.title) for section in book_content.sections]
    
    def get_content_summary(self, book_content: IntelligentBookContent) -> str:
        """Get a summary of the book content"""
        summary = f"Book: {book_content.title}\n"
        summary += f"Type: {book_content.structure.document_type}\n"
        summary += f"Subject: {book_content.structure.subject_area}\n"
        summary += f"Level: {book_content.structure.educational_level}\n"
        summary += f"Total sections: {book_content.total_sections}\n"
        summary += f"Processing confidence: {book_content.structure.structure_confidence:.2f}\n\n"
        
        summary += "Available sections:\n"
        for section in book_content.sections:
            duration = section.estimated_duration
            summary += f"  {section.section_number}: {section.title} ({duration}min)\n"
        
        return summary


# Convenience function for integration
def create_intelligent_book_processor(openai_api_key: str) -> IntelligentBookProcessor:
    """Factory function to create intelligent book processor"""
    return IntelligentBookProcessor(openai_api_key)