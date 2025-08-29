"""
Text to JSON Book Converter

This module converts existing text-format educational books to the new
rich JSON format with enhanced metadata and content structure analysis.
"""

import re
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from ..schemas.book_schema import (
    JsonBook, Chapter, Section, ContentBlock, ContentBlockType,
    EducationalElements, VideoGenerationHints, LearningObjective,
    BookMetadata, SubjectArea, DifficultyLevel
)
from ..book_processor import BookProcessor, TextSection


class TextToJsonConverter:
    """Converts text-format books to enhanced JSON format with LLM intelligence"""
    
    def __init__(self, use_llm: bool = True, api_key: Optional[str] = None):
        self.text_processor = BookProcessor()
        self.use_llm = use_llm
        
        # Initialize LLM converter if requested and API key available
        self.llm_converter = None
        if use_llm:
            try:
                from .llm_text_to_json import LLMTextToJsonConverter
                api_key = api_key or os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.llm_converter = LLMTextToJsonConverter(api_key)
                    print("[LLM] CONVERTER: Intelligent LLM-powered conversion enabled")
                else:
                    print("[WARNING] No OpenAI API key found. Falling back to rule-based conversion.")
                    self.use_llm = False
            except Exception as e:
                print(f"[WARNING] Failed to initialize LLM converter: {e}")
                print("[FALLBACK] Using rule-based conversion instead")
                self.use_llm = False
        
        # Content analysis patterns for intelligent classification
        self.definition_patterns = [
            r'\*\*(.*?)\*\*.*?(?:is|are|means|defined as|refers to)',
            r'(?:Definition|Def\.?):\s*(.*?)(?:\n|$)',
            r'We define\s+(.*?)\s+as',
            r'Let\s+(.*?)\s+be\s+(?:a|an|the)'
        ]
        
        self.example_patterns = [
            r'(?:Example|Ex\.?)\s*\d*:',
            r'For example,',
            r'Consider\s+(?:the\s+)?(?:following|case|example)',
            r'Let\'s\s+(?:look at|consider|examine)',
            r'Suppose\s+(?:that\s+)?we\s+have'
        ]
        
        self.theorem_patterns = [
            r'(?:Theorem|Thm\.?)\s*\d*:',
            r'(?:Lemma|Lem\.?)\s*\d*:',
            r'(?:Corollary|Cor\.?)\s*\d*:',
            r'(?:Proposition|Prop\.?)\s*\d*:'
        ]
        
        self.proof_patterns = [
            r'Proof:',
            r'Proof\.',
            r'We prove',
            r'To show',
            r'Q\.E\.D\.|QED'
        ]
        
        self.application_patterns = [
            r'(?:Application|Problem|Exercise)\s*\d*:',
            r'In practice,',
            r'This\s+(?:is\s+)?(?:useful|applied|used)\s+(?:for|in|when)',
            r'Real-world\s+(?:example|application)'
        ]
    
    def convert_book(self, text_book_path: str, output_path: Optional[str] = None,
                    enhance_content: bool = True, force_rule_based: bool = False) -> JsonBook:
        """
        Convert a text book to JSON format with intelligent content analysis
        
        Args:
            text_book_path: Path to the .txt book file
            output_path: Optional output path for JSON file
            enhance_content: Whether to apply intelligent content enhancement
            force_rule_based: Force use of rule-based conversion even if LLM available
        """
        text_path = Path(text_book_path)
        if not text_path.exists():
            raise FileNotFoundError(f"Text book not found: {text_book_path}")
        
        book_name = text_path.stem
        
        # Try LLM conversion first if available and not forced to use rule-based
        if self.use_llm and self.llm_converter and enhance_content and not force_rule_based:
            try:
                print(f"[LLM] CONVERSION: Converting '{book_name}' using LLM intelligence...")
                
                # Read raw text content
                with open(text_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                
                # Determine book title from content or filename
                title_match = re.search(r'^#\s*(.+)$', text_content, re.MULTILINE)
                book_title = title_match.group(1).strip() if title_match else book_name.replace('_', ' ').title()
                
                # Use LLM conversion
                json_book = self.llm_converter.convert_text_to_json(text_content, book_title, output_path)
                
                # Validate LLM output
                validation_errors = self.llm_converter.validate_json_output(json_book)
                if validation_errors:
                    print(f"[WARNING] LLM VALIDATION: Found {len(validation_errors)} issues, but proceeding:")
                    for error in validation_errors[:3]:  # Show first 3 errors
                        print(f"   - {error}")
                
                print("[SUCCESS] LLM CONVERSION: Successfully completed with intelligent parsing!")
                return json_book
                
            except Exception as e:
                print(f"[ERROR] LLM CONVERSION FAILED: {e}")
                print("[FALLBACK] Switching to rule-based conversion...")
        
        # Fallback to rule-based conversion
        print(f"[RULE-BASED] Converting '{book_name}' using rule-based parsing...")
        return self._convert_book_rule_based(text_book_path, output_path, enhance_content)
    
    def _convert_book_rule_based(self, text_book_path: str, output_path: Optional[str] = None,
                                enhance_content: bool = True) -> JsonBook:
        """Original rule-based conversion method as fallback"""
        text_path = Path(text_book_path)
        book_name = text_path.stem
        
        # Load using existing text processor
        text_book = self.text_processor.load_book(book_name)
        
        print(f"Converting '{text_book.title}' from text to JSON format...")
        
        # Create metadata
        metadata = self._create_metadata(text_book, text_path)
        
        # Convert chapters and sections
        json_chapters = []
        current_chapter = None
        
        for text_section in text_book.sections:
            if text_section.level == 2:  # Chapter
                if current_chapter:
                    json_chapters.append(current_chapter)
                
                current_chapter = self._create_chapter(text_section, enhance_content)
            
            elif text_section.level == 3 and current_chapter:  # Section
                json_section = self._create_section(text_section, enhance_content)
                current_chapter.sections.append(json_section)
        
        # Add final chapter
        if current_chapter:
            json_chapters.append(current_chapter)
        
        # Create JSON book
        json_book = JsonBook(
            metadata=metadata,
            chapters=json_chapters
        )
        
        # Save to file if output path specified
        if output_path:
            json_book.save_json(output_path)
            print(f"JSON book saved to: {output_path}")
        
        print(f"Conversion complete: {len(json_chapters)} chapters, "
             f"{sum(len(c.sections) for c in json_chapters)} sections")
        
        return json_book
    
    def _create_metadata(self, text_book, text_path: Path) -> BookMetadata:
        """Create metadata from text book"""
        # Intelligent subject detection
        subject = self._detect_subject(text_book.title, text_book.sections)
        
        # Detect level from content complexity
        level = self._detect_level(text_book.sections)
        
        return BookMetadata(
            title=text_book.title,
            subject=subject,
            level=level,
            description=f"Converted from text format: {text_path.name}",
            version="1.0"
        )
    
    def _detect_subject(self, title: str, sections: List[TextSection]) -> SubjectArea:
        """Intelligently detect subject area from content"""
        title_lower = title.lower()
        
        # Check title for subject keywords
        if any(word in title_lower for word in ['calculus', 'algebra', 'geometry', 'mathematics', 'math']):
            return SubjectArea.MATHEMATICS
        elif any(word in title_lower for word in ['physics', 'mechanics', 'thermodynamics', 'quantum']):
            return SubjectArea.PHYSICS
        elif any(word in title_lower for word in ['chemistry', 'organic', 'inorganic', 'biochemistry']):
            return SubjectArea.CHEMISTRY
        elif any(word in title_lower for word in ['computer', 'programming', 'algorithms', 'data']):
            return SubjectArea.COMPUTER_SCIENCE
        elif any(word in title_lower for word in ['engineering', 'mechanical', 'electrical', 'civil']):
            return SubjectArea.ENGINEERING
        elif any(word in title_lower for word in ['biology', 'genetics', 'anatomy', 'physiology']):
            return SubjectArea.BIOLOGY
        elif any(word in title_lower for word in ['economics', 'finance', 'market', 'trade']):
            return SubjectArea.ECONOMICS
        
        # Analyze section content for subject keywords
        all_content = " ".join(section.content.lower() for section in sections[:5])  # Check first 5 sections
        
        subject_scores = {
            SubjectArea.MATHEMATICS: len(re.findall(r'\b(?:equation|integral|derivative|limit|theorem|formula|function)\b', all_content)),
            SubjectArea.PHYSICS: len(re.findall(r'\b(?:velocity|acceleration|force|energy|momentum|wave|particle)\b', all_content)),
            SubjectArea.CHEMISTRY: len(re.findall(r'\b(?:molecule|atom|reaction|compound|element|bond|ion)\b', all_content)),
            SubjectArea.COMPUTER_SCIENCE: len(re.findall(r'\b(?:algorithm|data|structure|program|code|software|computer)\b', all_content)),
            SubjectArea.ENGINEERING: len(re.findall(r'\b(?:design|system|process|structure|material|analysis)\b', all_content))
        }
        
        # Return subject with highest score
        best_subject = max(subject_scores.items(), key=lambda x: x[1])
        return best_subject[0] if best_subject[1] > 0 else SubjectArea.GENERAL
    
    def _detect_level(self, sections: List[TextSection]) -> str:
        """Detect educational level from content complexity"""
        complexity_indicators = {
            'high_school': ['basic', 'introduction', 'simple', 'fundamental'],
            'undergraduate': ['calculus', 'advanced', 'theorem', 'analysis'],
            'graduate': ['research', 'advanced', 'complex', 'theoretical', 'proof']
        }
        
        all_content = " ".join(section.content.lower() for section in sections[:3])
        
        scores = {}
        for level, indicators in complexity_indicators.items():
            scores[level] = sum(all_content.count(indicator) for indicator in indicators)
        
        # Also consider mathematical complexity
        formula_count = len(re.findall(r'integral|sum|partial|nabla|\^[{\(]|lim|d/dx', all_content))
        if formula_count > 10:
            scores['graduate'] = scores.get('graduate', 0) + 5
        elif formula_count > 3:
            scores['undergraduate'] = scores.get('undergraduate', 0) + 3
        
        best_level = max(scores.items(), key=lambda x: x[1])
        return best_level[0] if best_level[1] > 0 else 'undergraduate'
    
    def _create_chapter(self, text_section: TextSection, enhance_content: bool) -> Chapter:
        """Create a JSON chapter from a text section"""
        chapter_number = int(text_section.section_number) if text_section.section_number.isdigit() else 1
        
        # Extract learning objectives from chapter content
        learning_objectives = []
        if enhance_content:
            objectives = self._extract_learning_objectives(text_section.content)
            learning_objectives = [
                LearningObjective(objective=obj, bloom_level="understand")
                for obj in objectives
            ]
        
        return Chapter(
            id=f"chapter_{chapter_number}",
            number=chapter_number,
            title=text_section.title,
            description=self._extract_chapter_description(text_section.content),
            learning_objectives=learning_objectives,
            sections=[]  # Will be populated later
        )
    
    def _create_section(self, text_section: TextSection, enhance_content: bool) -> Section:
        """Create a JSON section from a text section with intelligent content analysis"""
        # Determine difficulty level
        difficulty = self._analyze_difficulty(text_section)
        
        # Parse content into blocks
        content_blocks = []
        if enhance_content:
            content_blocks = self._parse_content_blocks(text_section.content)
        else:
            # Basic conversion: create a single text block
            content_blocks = [ContentBlock(
                type=ContentBlockType.TEXT,
                content=text_section.content
            )]
        
        # Extract learning objectives
        learning_objectives = []
        if enhance_content:
            objectives = self._extract_learning_objectives(text_section.content)
            learning_objectives = [
                LearningObjective(objective=obj, bloom_level=self._determine_bloom_level(obj))
                for obj in objectives
            ]
        
        # Create enhanced educational elements
        educational_elements = self._create_enhanced_educational_elements(text_section, content_blocks)
        
        # Generate video hints
        video_hints = None
        if enhance_content:
            video_hints = self._generate_video_hints(text_section, content_blocks, difficulty)
        
        return Section(
            id=f"section_{text_section.section_number.replace('.', '_')}",
            number=text_section.section_number,
            title=text_section.title,
            difficulty=difficulty,
            estimated_duration=self._estimate_duration(text_section.content),
            content_blocks=content_blocks,
            learning_objectives=learning_objectives,
            educational_elements=educational_elements,
            video_hints=video_hints
        )
    
    def _parse_content_blocks(self, content: str) -> List[ContentBlock]:
        """Intelligently parse content into structured blocks"""
        blocks = []
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        for i, paragraph in enumerate(paragraphs):
            block = self._classify_paragraph(paragraph, i)
            if block:
                blocks.append(block)
        
        return blocks if blocks else [ContentBlock(type=ContentBlockType.TEXT, content=content)]
    
    def _classify_paragraph(self, paragraph: str, index: int) -> Optional[ContentBlock]:
        """Classify a paragraph into an appropriate content block type"""
        paragraph_lower = paragraph.lower()
        
        # Check for definitions
        if any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in self.definition_patterns):
            # Extract title if available
            title_match = re.search(r'\*\*([^*]+)\*\*', paragraph)
            title = title_match.group(1) if title_match else None
            
            return ContentBlock(
                type=ContentBlockType.DEFINITION,
                title=title,
                content=paragraph,
                importance="fundamental"
            )
        
        # Check for examples
        if any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in self.example_patterns):
            # Try to extract problem and solution
            problem_match = re.search(r'(?:Find|Calculate|Determine|Solve)\s+(.+?)(?:\.|$)', paragraph)
            problem = problem_match.group(1) if problem_match else None
            
            return ContentBlock(
                type=ContentBlockType.EXAMPLE,
                title=f"Example {index + 1}",
                content=paragraph,
                problem=problem
            )
        
        # Check for theorems
        if any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in self.theorem_patterns):
            theorem_match = re.search(r'(?:Theorem|Lemma|Corollary|Proposition)\s*\d*:\s*(.+?)(?:\n|$)', paragraph)
            title = theorem_match.group(1) if theorem_match else None
            
            return ContentBlock(
                type=ContentBlockType.THEOREM,
                title=title,
                content=paragraph,
                importance="fundamental"
            )
        
        # Check for proofs
        if any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in self.proof_patterns):
            return ContentBlock(
                type=ContentBlockType.PROOF,
                title="Proof",
                content=paragraph,
                proof_method="direct"  # Default assumption
            )
        
        # Check for applications
        if any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in self.application_patterns):
            return ContentBlock(
                type=ContentBlockType.APPLICATION,
                title="Application",
                content=paragraph
            )
        
        # Check for formulas (lines with mathematical expressions)
        formula_indicators = ['=', 'integral', 'sum', 'partial', '->', 'lim', 'd/dx']
        if any(indicator in paragraph for indicator in formula_indicators) and len(paragraph) < 200:
            # Extract the formula
            formula = paragraph.strip()
            return ContentBlock(
                type=ContentBlockType.FORMULA,
                content=f"Mathematical formula: {formula}",
                formula=formula
            )
        
        # Check for introductory content (first few paragraphs or paragraphs with introduction keywords)
        if (index < 2 or 
            any(word in paragraph_lower for word in ['introduction', 'overview', 'concept', 'fundamental'])):
            return ContentBlock(
                type=ContentBlockType.INTRODUCTION,
                content=paragraph
            )
        
        # Default to text block
        return ContentBlock(
            type=ContentBlockType.TEXT,
            content=paragraph
        )
    
    def _analyze_difficulty(self, text_section: TextSection) -> DifficultyLevel:
        """Analyze content difficulty level"""
        content_lower = text_section.content.lower()
        
        # Count complexity indicators
        advanced_terms = ['theorem', 'proof', 'lemma', 'corollary', 'rigorous', 'abstract']
        intermediate_terms = ['derivative', 'integral', 'limit', 'function', 'equation']
        beginner_terms = ['basic', 'simple', 'introduction', 'fundamental', 'elementary']
        
        advanced_count = sum(content_lower.count(term) for term in advanced_terms)
        intermediate_count = sum(content_lower.count(term) for term in intermediate_terms)
        beginner_count = sum(content_lower.count(term) for term in beginner_terms)
        
        # Check mathematical complexity
        complex_math_count = len(re.findall(r'integral|sum|partial|nabla|\^[{\(]|lim|d/dx', content_lower))
        
        # Determine difficulty based on indicators
        if advanced_count > 2 or complex_math_count > 5:
            return DifficultyLevel.ADVANCED
        elif intermediate_count > 3 or complex_math_count > 2:
            return DifficultyLevel.INTERMEDIATE
        elif beginner_count > 1 or 'introduction' in text_section.title.lower():
            return DifficultyLevel.BEGINNER
        else:
            return DifficultyLevel.INTERMEDIATE
    
    def _create_enhanced_educational_elements(self, text_section: TextSection, 
                                            content_blocks: List[ContentBlock]) -> EducationalElements:
        """Create enhanced educational elements from content blocks"""
        elements = EducationalElements()
        
        # Start with existing elements from text processing
        elements.formulas = text_section.educational_elements.get('formulas', [])
        elements.key_concepts = text_section.educational_elements.get('key_concepts', [])
        
        # Extract from content blocks
        for block in content_blocks:
            if block.type == ContentBlockType.DEFINITION:
                def_text = f"{block.title}: {block.content}" if block.title else block.content
                elements.definitions.append(def_text)
            
            elif block.type == ContentBlockType.EXAMPLE:
                example_dict = {
                    "title": block.title or "Example",
                    "type": "worked_example",
                    "difficulty": "basic",
                    "problem": block.problem or "See content"
                }
                elements.examples.append(example_dict)
            
            elif block.type == ContentBlockType.FORMULA and block.formula:
                if block.formula not in elements.formulas:
                    elements.formulas.append(block.formula)
            
            elif block.type == ContentBlockType.APPLICATION:
                elements.applications.append(block.title or "Application")
            
            # Extract key concepts from tags
            if block.tags:
                elements.key_concepts.extend(block.tags)
        
        # Remove duplicates
        elements.key_concepts = list(set(elements.key_concepts))
        elements.formulas = list(set(elements.formulas))
        
        return elements
    
    def _generate_video_hints(self, text_section: TextSection, content_blocks: List[ContentBlock], 
                            difficulty: DifficultyLevel) -> VideoGenerationHints:
        """Generate intelligent video generation hints"""
        duration = self._estimate_duration(text_section.content)
        
        # Analyze content block types for subdivision strategy
        block_types = [block.type for block in content_blocks]
        unique_types = len(set(block_types))
        
        if unique_types >= 4:
            strategy = "by_type"
        elif len(text_section.content) > 3000:
            strategy = "by_length"
        elif any(bt in [ContentBlockType.THEOREM, ContentBlockType.PROOF] for bt in block_types):
            strategy = "by_concept"
        else:
            strategy = "auto"
        
        # Determine focus areas
        focus_areas = []
        if any(block.type == ContentBlockType.DEFINITION for block in content_blocks):
            focus_areas.append("definitions")
        if any(block.type == ContentBlockType.EXAMPLE for block in content_blocks):
            focus_areas.append("examples")
        if any(block.type == ContentBlockType.APPLICATION for block in content_blocks):
            focus_areas.append("applications")
        if any(block.type in [ContentBlockType.THEOREM, ContentBlockType.PROOF, ContentBlockType.FORMULA] 
               for block in content_blocks):
            focus_areas.append("theory")
        
        # Visual emphasis elements
        visual_emphasis = []
        for block in content_blocks:
            if block.formula:
                visual_emphasis.append("formula_notation")
            if block.type == ContentBlockType.EXAMPLE:
                visual_emphasis.append("step_by_step_solution")
            if block.type == ContentBlockType.THEOREM:
                visual_emphasis.append("theorem_statement")
        
        # Determine pace based on difficulty and content complexity
        pace = "moderate"
        if difficulty == DifficultyLevel.BEGINNER:
            pace = "slow"
        elif difficulty == DifficultyLevel.ADVANCED:
            pace = "moderate"  # Advanced content needs careful pacing
        
        return VideoGenerationHints(
            suggested_duration=duration,
            subdivision_strategy=strategy,
            focus_areas=focus_areas,
            visual_emphasis=list(set(visual_emphasis)),
            pace=pace,
            complexity_score=self._calculate_complexity_score(text_section)
        )
    
    def _extract_learning_objectives(self, content: str) -> List[str]:
        """Extract or infer learning objectives from content"""
        objectives = []
        
        # Look for explicit objectives
        objective_patterns = [
            r'(?:Learning objectives?|Objectives?|Goals?|By the end.*?you will)\s*:?\s*(.+?)(?:\n\n|$)',
            r'(?:Students? will|You will)\s+(?:be able to\s+)?(.+?)(?:\.|$)'
        ]
        
        for pattern in objective_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split on bullet points or numbers
                parts = re.split(r'\n\s*[-•\d+\.]\s*', match.strip())
                for part in parts:
                    if len(part.strip()) > 10:  # Filter out very short matches
                        objectives.append(part.strip())
        
        # If no explicit objectives found, infer from content structure
        if not objectives:
            objectives = self._infer_learning_objectives(content)
        
        return objectives[:5]  # Limit to 5 objectives
    
    def _infer_learning_objectives(self, content: str) -> List[str]:
        """Infer learning objectives from content analysis"""
        objectives = []
        
        # Check for definitions
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in self.definition_patterns):
            objectives.append("Understand key definitions and terminology")
        
        # Check for examples
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in self.example_patterns):
            objectives.append("Apply concepts through worked examples")
        
        # Check for formulas
        if re.search(r'integral|sum|partial|nabla|\^[{\(]|lim|d/dx|=', content):
            objectives.append("Use mathematical formulas and expressions")
        
        # Check for theorems
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in self.theorem_patterns):
            objectives.append("Understand and apply fundamental theorems")
        
        # Check for applications
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in self.application_patterns):
            objectives.append("Apply concepts to real-world problems")
        
        return objectives
    
    def _determine_bloom_level(self, objective: str) -> str:
        """Determine Bloom's taxonomy level for an objective"""
        objective_lower = objective.lower()
        
        # Bloom's taxonomy keywords
        bloom_keywords = {
            "remember": ["memorize", "recall", "list", "identify", "define", "recognize"],
            "understand": ["understand", "explain", "describe", "interpret", "summarize"],
            "apply": ["apply", "use", "demonstrate", "solve", "calculate", "implement"],
            "analyze": ["analyze", "compare", "contrast", "examine", "differentiate"],
            "evaluate": ["evaluate", "assess", "judge", "critique", "justify"],
            "create": ["create", "design", "construct", "develop", "formulate"]
        }
        
        for level, keywords in bloom_keywords.items():
            if any(keyword in objective_lower for keyword in keywords):
                return level
        
        return "understand"  # Default level
    
    def _extract_chapter_description(self, content: str) -> Optional[str]:
        """Extract or create chapter description"""
        # Take first sentence or paragraph as description
        sentences = content.split('.')
        if sentences and len(sentences[0]) < 200:
            return sentences[0].strip() + "."
        
        # Take first paragraph if sentence is too long
        paragraphs = content.split('\n\n')
        if paragraphs and len(paragraphs[0]) < 300:
            return paragraphs[0].strip()
        
        return None
    
    def _estimate_duration(self, content: str) -> int:
        """Estimate video duration in minutes"""
        char_count = len(content)
        word_count = char_count / 5  # Rough estimation: 5 chars per word
        duration_minutes = max(1, int(word_count / 150))  # 150 words per minute
        return min(duration_minutes, 30)  # Cap at 30 minutes
    
    def _calculate_complexity_score(self, text_section: TextSection) -> float:
        """Calculate complexity score for video generation hints"""
        content = text_section.content
        
        # Content length factor
        length_score = min(len(content) / 2000, 1.0)
        
        # Mathematical complexity
        math_indicators = len(re.findall(r'integral|sum|partial|nabla|\^[{\(]|lim|d/dx', content))
        math_score = min(math_indicators / 10, 1.0)
        
        # Educational element density
        total_elements = sum(len(values) for values in text_section.educational_elements.values())
        element_score = min(total_elements / 15, 1.0)
        
        # Advanced terminology
        advanced_terms = ['theorem', 'proof', 'lemma', 'corollary', 'rigorous']
        advanced_count = sum(content.lower().count(term) for term in advanced_terms)
        advanced_score = min(advanced_count / 5, 1.0)
        
        # Weighted combination
        return (length_score * 0.3 + math_score * 0.3 + 
                element_score * 0.2 + advanced_score * 0.2)
    
    def batch_convert_books(self, input_dir: str = "books", output_dir: str = "books_json"):
        """Convert all text books in a directory to JSON format"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            print(f"Input directory not found: {input_dir}")
            return
        
        output_path.mkdir(exist_ok=True)
        
        text_books = list(input_path.glob("*.txt"))
        if not text_books:
            print(f"No .txt books found in {input_dir}")
            return
        
        print(f"Converting {len(text_books)} books from {input_dir} to {output_dir}")
        
        for text_book in text_books:
            try:
                output_file = output_path / f"{text_book.stem}.json"
                print(f"\nConverting: {text_book.name}")
                
                json_book = self.convert_book(str(text_book), str(output_file))
                print(f"[SUCCESS] Successfully converted to {output_file.name}")
                
            except Exception as e:
                print(f"[ERROR] Failed to convert {text_book.name}: {e}")
        
        print(f"\nBatch conversion complete!")


def main():
    """Test the text-to-JSON converter"""
    converter = TextToJsonConverter()
    
    # Convert calculus.txt if it exists
    calculus_path = Path("books/calculus.txt")
    if calculus_path.exists():
        try:
            json_book = converter.convert_book(str(calculus_path), "books_json/calculus.json")
            print(f"\nConversion successful!")
            print(f"Chapters: {len(json_book.chapters)}")
            print(f"Total sections: {sum(len(ch.sections) for ch in json_book.chapters)}")
            
        except Exception as e:
            print(f"Conversion failed: {e}")
    else:
        print("calculus.txt not found in books/ directory")
        
        # Try batch conversion
        converter.batch_convert_books()


if __name__ == "__main__":
    main()