"""
Topic Subdivider for Educational Content

This module intelligently subdivides complex educational sections into
multiple focused video topics for better learning progression.
"""

import re
import numpy as np
from typing import List, Dict, Optional, Tuple, Set, TYPE_CHECKING
from dataclasses import dataclass

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from .book_processor import TextSection


@dataclass
class VideoSubtopic:
    """Represents a subdivided topic for focused video generation"""
    title: str
    content: str
    focus_type: str  # 'definitions', 'examples', 'applications', 'theory', 'mixed'
    parent_section: str  # Original section number
    subtopic_index: str  # e.g., "1.1a", "1.1b"
    educational_elements: Dict[str, List[str]]
    complexity_score: float
    estimated_duration: int  # minutes
    
    def to_dict(self) -> dict:
        """Convert VideoSubtopic to JSON-serializable dictionary"""
        return {
            'title': self.title,
            'content': self.content,
            'focus_type': self.focus_type,
            'parent_section': self.parent_section,
            'subtopic_index': self.subtopic_index,
            'educational_elements': self.educational_elements,
            'complexity_score': self.complexity_score,
            'estimated_duration': self.estimated_duration
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VideoSubtopic':
        """Create VideoSubtopic from dictionary"""
        return cls(
            title=data['title'],
            content=data['content'],
            focus_type=data['focus_type'],
            parent_section=data['parent_section'],
            subtopic_index=data['subtopic_index'],
            educational_elements=data['educational_elements'],
            complexity_score=data['complexity_score'],
            estimated_duration=data['estimated_duration']
        )


class TopicSubdivider:
    """Intelligently subdivides educational content into focused video topics"""
    
    def __init__(self):
        # Content length thresholds for subdivision
        self.max_single_video_length = 2000  # characters
        self.min_subtopic_length = 300  # characters
        
        # Educational element density thresholds
        self.max_formulas_per_video = 5
        self.max_definitions_per_video = 3
        self.max_examples_per_video = 4
        
        # Focus type patterns
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
        
        self.application_patterns = [
            r'(?:Application|Problem|Exercise)\s*\d*:',
            r'In practice,',
            r'This\s+(?:is\s+)?(?:useful|applied|used)\s+(?:for|in|when)',
            r'Real-world\s+(?:example|application)',
            r'(?:Can|May)\s+be\s+used\s+to'
        ]
    
    def should_subdivide_section(self, section: 'TextSection') -> bool:
        """Determine if a section should be subdivided into multiple videos"""
        # Check content length
        if len(section.content) > self.max_single_video_length:
            return True
        
        # Check estimated duration
        estimated_duration = self._estimate_duration(section.content)
        if estimated_duration > 10:  # More than 10 minutes should be subdivided
            return True
        
        # Check educational element density
        elements = section.educational_elements
        if (len(elements.get('formulas', [])) > self.max_formulas_per_video or
            len(elements.get('definitions', [])) > self.max_definitions_per_video or
            len(elements.get('examples', [])) > self.max_examples_per_video):
            return True
        
        # Check complexity indicators
        complexity = self._calculate_complexity_score(section)
        return complexity > 0.7
    
    def subdivide_section(self, section: 'TextSection', 
                         subdivision_strategy: str = "auto") -> List[VideoSubtopic]:
        """
        Subdivide a section into multiple focused video topics optimized for 10-minute segments
        
        Args:
            section: The section to subdivide
            subdivision_strategy: 'auto', 'by_type', 'by_length', 'by_concept', 'optimal_10min'
        """
        if subdivision_strategy == "auto":
            return self._auto_subdivide(section)
        elif subdivision_strategy == "by_type":
            return self._subdivide_by_type(section)
        elif subdivision_strategy == "by_length":
            return self._subdivide_by_length(section)
        elif subdivision_strategy == "by_concept":
            return self._subdivide_by_concept(section)
        elif subdivision_strategy == "optimal_10min":
            return self._subdivide_optimal_10min(section)
        else:
            raise ValueError(f"Unknown subdivision strategy: {subdivision_strategy}")
    
    def generate_focused_videos(self, section: 'TextSection', 
                              focus_types: List[str]) -> List[VideoSubtopic]:
        """
        Generate focused videos for specific content types
        
        Args:
            focus_types: List of focus types like ['definitions', 'examples', 'applications']
        """
        subtopics = []
        
        for focus_type in focus_types:
            content = self._extract_focused_content(section, focus_type)
            if content.strip() and len(content) >= self.min_subtopic_length:
                subtopic = VideoSubtopic(
                    title=f"{section.title} - {focus_type.title()}",
                    content=content,
                    focus_type=focus_type,
                    parent_section=section.section_number,
                    subtopic_index=f"{section.section_number}_{focus_type[:3]}",
                    educational_elements=self._extract_focused_elements(section, focus_type),
                    complexity_score=self._calculate_content_complexity(content),
                    estimated_duration=self._estimate_duration(content)
                )
                subtopics.append(subtopic)
        
        return subtopics
    
    def _auto_subdivide(self, section: 'TextSection') -> List[VideoSubtopic]:
        """Automatically determine the best subdivision strategy"""
        # If heavy on different content types, subdivide by type
        elements = section.educational_elements
        type_counts = {
            'definitions': len(elements.get('definitions', [])),
            'examples': len(elements.get('examples', [])),
            'formulas': len(elements.get('formulas', [])),
            'key_concepts': len(elements.get('key_concepts', []))
        }
        
        # If multiple content types with high density, subdivide by type
        high_density_types = [t for t, count in type_counts.items() if count >= 3]
        if len(high_density_types) >= 2:
            return self._subdivide_by_type(section)
        
        # If very long content, subdivide by concept/natural breaks
        if len(section.content) > self.max_single_video_length * 1.5:
            return self._subdivide_by_concept(section)
        
        # Otherwise, subdivide by length
        return self._subdivide_by_length(section)
    
    def _subdivide_by_type(self, section: 'TextSection') -> List[VideoSubtopic]:
        """Subdivide based on content types (definitions, examples, etc.)"""
        subtopics = []
        content_types = ['definitions', 'examples', 'applications', 'theory']
        
        for i, content_type in enumerate(content_types):
            focused_content = self._extract_focused_content(section, content_type)
            if focused_content.strip() and len(focused_content) >= self.min_subtopic_length:
                subtopic = VideoSubtopic(
                    title=f"{section.title} - {content_type.title()}",
                    content=focused_content,
                    focus_type=content_type,
                    parent_section=section.section_number,
                    subtopic_index=f"{section.section_number}{chr(97+i)}",  # a, b, c, d
                    educational_elements=self._extract_focused_elements(section, content_type),
                    complexity_score=self._calculate_content_complexity(focused_content),
                    estimated_duration=self._estimate_duration(focused_content)
                )
                subtopics.append(subtopic)
        
        return subtopics
    
    def _subdivide_by_length(self, section: 'TextSection') -> List[VideoSubtopic]:
        """Subdivide based on content length into logical chunks"""
        subtopics = []
        content = section.content
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        current_chunk = []
        current_length = 0
        subtopic_index = 0
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed limit, save current chunk
            if (current_length + len(paragraph) > self.max_single_video_length and 
                current_chunk and current_length >= self.min_subtopic_length):
                
                chunk_content = '\n\n'.join(current_chunk)
                subtopic = VideoSubtopic(
                    title=f"{section.title} - Part {subtopic_index + 1}",
                    content=chunk_content,
                    focus_type='mixed',
                    parent_section=section.section_number,
                    subtopic_index=f"{section.section_number}{chr(97+subtopic_index)}",
                    educational_elements=self._extract_chunk_elements(chunk_content),
                    complexity_score=self._calculate_content_complexity(chunk_content),
                    estimated_duration=self._estimate_duration(chunk_content)
                )
                subtopics.append(subtopic)
                
                current_chunk = [paragraph]
                current_length = len(paragraph)
                subtopic_index += 1
            else:
                current_chunk.append(paragraph)
                current_length += len(paragraph) + 2  # +2 for \n\n
        
        # Add final chunk if it has content
        if current_chunk and current_length >= self.min_subtopic_length:
            chunk_content = '\n\n'.join(current_chunk)
            subtopic = VideoSubtopic(
                title=f"{section.title} - Part {subtopic_index + 1}",
                content=chunk_content,
                focus_type='mixed',
                parent_section=section.section_number,
                subtopic_index=f"{section.section_number}{chr(97+subtopic_index)}",
                educational_elements=self._extract_chunk_elements(chunk_content),
                complexity_score=self._calculate_content_complexity(chunk_content),
                estimated_duration=self._estimate_duration(chunk_content)
            )
            subtopics.append(subtopic)
        
        return subtopics
    
    def _subdivide_by_concept(self, section: 'TextSection') -> List[VideoSubtopic]:
        """Subdivide based on conceptual boundaries and natural breaks"""
        subtopics = []
        content = section.content
        
        # Look for concept boundaries
        concept_breaks = self._find_concept_boundaries(content)
        
        if not concept_breaks:
            # Fallback to length-based subdivision
            return self._subdivide_by_length(section)
        
        # Split content at concept boundaries
        sections_content = []
        last_pos = 0
        
        for break_pos, concept_title in concept_breaks:
            if break_pos > last_pos:
                sections_content.append({
                    'title': concept_title or f"Concept {len(sections_content) + 1}",
                    'content': content[last_pos:break_pos].strip()
                })
            last_pos = break_pos
        
        # Add final section
        if last_pos < len(content):
            final_content = content[last_pos:].strip()
            if final_content:
                sections_content.append({
                    'title': f"Concept {len(sections_content) + 1}",
                    'content': final_content
                })
        
        # Convert to VideoSubtopic objects
        for i, section_data in enumerate(sections_content):
            if len(section_data['content']) >= self.min_subtopic_length:
                subtopic = VideoSubtopic(
                    title=f"{section.title} - {section_data['title']}",
                    content=section_data['content'],
                    focus_type='mixed',
                    parent_section=section.section_number,
                    subtopic_index=f"{section.section_number}{chr(97+i)}",
                    educational_elements=self._extract_chunk_elements(section_data['content']),
                    complexity_score=self._calculate_content_complexity(section_data['content']),
                    estimated_duration=self._estimate_duration(section_data['content'])
                )
                subtopics.append(subtopic)
        
        return subtopics
    
    def _extract_focused_content(self, section: 'TextSection', focus_type: str) -> str:
        """Extract content focused on specific educational elements"""
        content = section.content
        lines = content.split('\n')
        focused_lines = []
        
        if focus_type == 'definitions':
            # Extract lines with definitions and surrounding context
            for i, line in enumerate(lines):
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.definition_patterns):
                    # Include context (previous and next few lines)
                    start_idx = max(0, i - 1)
                    end_idx = min(len(lines), i + 3)
                    focused_lines.extend(lines[start_idx:end_idx])
        
        elif focus_type == 'examples':
            # Extract example sections
            in_example = False
            for i, line in enumerate(lines):
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.example_patterns):
                    in_example = True
                    focused_lines.append(line)
                elif in_example:
                    if line.strip() == '' and i < len(lines) - 1 and lines[i+1].strip() == '':
                        in_example = False
                    focused_lines.append(line)
        
        elif focus_type == 'applications':
            # Extract application sections
            for i, line in enumerate(lines):
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.application_patterns):
                    # Include context for applications
                    start_idx = max(0, i - 1)
                    end_idx = min(len(lines), i + 4)
                    focused_lines.extend(lines[start_idx:end_idx])
        
        elif focus_type == 'theory':
            # Extract theoretical content (formulas, proofs, etc.)
            formulas = section.educational_elements.get('formulas', [])
            for formula in formulas:
                # Find lines containing this formula and add context
                for i, line in enumerate(lines):
                    if formula.replace('$', '').strip() in line:
                        start_idx = max(0, i - 2)
                        end_idx = min(len(lines), i + 3)
                        focused_lines.extend(lines[start_idx:end_idx])
        
        return '\n'.join(focused_lines).strip()
    
    def _extract_focused_elements(self, section: 'TextSection', focus_type: str) -> Dict[str, List[str]]:
        """Extract educational elements relevant to the focus type"""
        all_elements = section.educational_elements
        
        if focus_type == 'definitions':
            return {'definitions': all_elements.get('definitions', [])}
        elif focus_type == 'examples':
            return {'examples': all_elements.get('examples', [])}
        elif focus_type == 'applications':
            return {'applications': all_elements.get('applications', [])}
        elif focus_type == 'theory':
            return {
                'formulas': all_elements.get('formulas', []),
                'key_concepts': all_elements.get('key_concepts', [])
            }
        else:
            return all_elements
    
    def _extract_chunk_elements(self, content: str) -> Dict[str, List[str]]:
        """Extract educational elements from a content chunk"""
        # Simple extraction based on patterns
        elements = {
            'formulas': [],
            'definitions': [],
            'examples': [],
            'key_concepts': []
        }
        
        # Find formulas (content between $ symbols)
        formulas = re.findall(r'\$([^$]+)\$', content)
        elements['formulas'] = formulas
        
        # Find definitions (bold text followed by definition indicators)
        for pattern in self.definition_patterns:
            definitions = re.findall(pattern, content, re.IGNORECASE)
            elements['definitions'].extend(definitions)
        
        # Find examples
        example_sections = []
        for pattern in self.example_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                start = match.start()
                # Find end of example (next paragraph break)
                end = content.find('\n\n', start)
                if end == -1:
                    end = len(content)
                example_sections.append(content[start:end].strip())
        elements['examples'] = example_sections
        
        # Find key concepts (capitalized terms, bold text)
        key_concepts = re.findall(r'\*\*([^*]+)\*\*', content)
        elements['key_concepts'] = key_concepts
        
        return elements
    
    def _calculate_complexity_score(self, section: 'TextSection') -> float:
        """Calculate complexity score based on content characteristics"""
        content = section.content
        elements = section.educational_elements
        
        # Base complexity from content length
        length_score = min(len(content) / 2000, 1.0)
        
        # Educational element density
        total_elements = sum(len(vals) for vals in elements.values())
        element_density = min(total_elements / 20, 1.0)
        
        # Formula complexity
        formula_count = len(elements.get('formulas', []))
        formula_score = min(formula_count / 10, 1.0)
        
        # Mathematical complexity (Greek letters, complex notation)
        math_indicators = len(re.findall(r'[α-ωΑ-Ω]|∑|∫|∂|∇|√', content))
        math_score = min(math_indicators / 20, 1.0)
        
        # Weighted combination
        return (length_score * 0.3 + element_density * 0.4 + 
               formula_score * 0.2 + math_score * 0.1)
    
    def _calculate_content_complexity(self, content: str) -> float:
        """Calculate complexity score for a content chunk"""
        # Simplified version for content chunks
        length_score = min(len(content) / 1000, 1.0)
        formula_count = len(re.findall(r'\$([^$]+)\$', content))
        formula_score = min(formula_count / 5, 1.0)
        math_indicators = len(re.findall(r'[α-ωΑ-Ω]|∑|∫|∂|∇|√', content))
        math_score = min(math_indicators / 10, 1.0)
        
        return (length_score * 0.5 + formula_score * 0.3 + math_score * 0.2)
    
    def _estimate_duration(self, content: str) -> int:
        """Estimate video duration in minutes based on content"""
        # Rough estimation: 150 words per minute, average 5 chars per word
        char_count = len(content)
        word_count = char_count / 5
        duration_minutes = max(1, int(word_count / 150))
        
        # Adjust for mathematical content (slower delivery)
        formula_count = len(re.findall(r'\$([^$]+)\$', content))
        if formula_count > 0:
            duration_minutes += formula_count * 0.5
        
        return duration_minutes
    
    def _find_concept_boundaries(self, content: str) -> List[Tuple[int, Optional[str]]]:
        """Find natural concept boundaries in content"""
        boundaries = []
        
        # Look for section breaks, new concepts, etc.
        concept_indicators = [
            r'\n\n(?:Now|Next|Furthermore|Additionally|Moreover),',
            r'\n\n(?:Let\'s|We will|Consider|Suppose)',
            r'\n\n(?:\d+\.|\w+\.)\s+[A-Z]',  # Numbered or lettered lists
            r'\n\n[A-Z][^.!?]*(?:Theorem|Lemma|Corollary|Proposition)',
            r'\n\n(?:Definition|Example|Problem|Exercise)\s*\d*:'
        ]
        
        for pattern in concept_indicators:
            for match in re.finditer(pattern, content):
                # Extract concept title if possible
                title_match = re.search(r'(?:Definition|Example|Problem|Exercise|Theorem|Lemma)\s*\d*:?\s*([^\n]*)', 
                                      content[match.start():match.start()+100])
                title = title_match.group(1).strip() if title_match else None
                boundaries.append((match.start(), title))
        
        # Sort by position
        boundaries.sort(key=lambda x: x[0])
        
        return boundaries
    
    def _subdivide_optimal_10min(self, section: 'TextSection') -> List[VideoSubtopic]:
        """
        Subdivide section into optimal 10-minute segments with intelligent part numbering
        """
        content = section.content
        estimated_total_duration = self._estimate_duration(content)
        
        if estimated_total_duration <= 10:
            # Single video is sufficient
            return [VideoSubtopic(
                title=section.title,
                content=content,
                focus_type="comprehensive",
                parent_section=section.section_number,
                subtopic_index=f"{section.section_number}",
                educational_elements=section.educational_elements,
                complexity_score=self._calculate_complexity_score(section),
                estimated_duration=estimated_total_duration
            )]
        
        # Calculate optimal number of segments
        target_segments = max(2, int(np.ceil(estimated_total_duration / 10)))
        target_duration_per_segment = estimated_total_duration / target_segments
        
        print(f"SUBDIVISION: Target {target_segments} segments of ~{target_duration_per_segment:.1f} min each")
        
        # Use intelligent content splitting
        segments = self._create_intelligent_segments(
            section, target_segments, target_duration_per_segment
        )
        
        # Create video subtopics with proper part numbering
        subtopics = []
        for i, (segment_content, focus_type, title_suffix) in enumerate(segments):
            if len(segments) > 1:
                # Multi-part numbering
                if title_suffix:
                    title = f"{section.title} - {title_suffix}"
                else:
                    title = f"{section.title} - Part {i + 1}"
                subtopic_index = f"{section.section_number}.{i + 1}"
            else:
                title = section.title
                subtopic_index = section.section_number
            
            # Extract educational elements for this segment
            segment_elements = self._extract_segment_elements(segment_content)
            
            subtopic = VideoSubtopic(
                title=title,
                content=segment_content,
                focus_type=focus_type,
                parent_section=section.section_number,
                subtopic_index=subtopic_index,
                educational_elements=segment_elements,
                complexity_score=self._calculate_content_complexity(segment_content),
                estimated_duration=int(self._estimate_duration(segment_content))
            )
            subtopics.append(subtopic)
        
        return subtopics
    
    def _create_intelligent_segments(self, section: 'TextSection', 
                                   target_segments: int, 
                                   target_duration: float) -> List[Tuple[str, str, str]]:
        """Create intelligent content segments based on natural boundaries"""
        content = section.content
        
        # Find natural breakpoints
        concept_boundaries = self._find_concept_boundaries(content)
        paragraph_boundaries = self._find_paragraph_boundaries(content)
        
        # Combine all potential break points
        all_boundaries = set([0])  # Start
        all_boundaries.update([pos for pos, _ in concept_boundaries])
        all_boundaries.update(paragraph_boundaries)
        all_boundaries.add(len(content))  # End
        
        sorted_boundaries = sorted(all_boundaries)
        
        # Create segments using dynamic programming approach
        segments = self._optimize_segment_boundaries(
            content, sorted_boundaries, target_segments, target_duration
        )
        
        return segments
    
    def _find_paragraph_boundaries(self, content: str) -> List[int]:
        """Find paragraph boundaries for potential split points"""
        boundaries = []
        
        # Look for double newlines (paragraph breaks)
        for match in re.finditer(r'\n\n+', content):
            boundaries.append(match.end())
        
        return boundaries
    
    def _optimize_segment_boundaries(self, content: str, boundaries: List[int], 
                                   target_segments: int, target_duration: float) -> List[Tuple[str, str, str]]:
        """Optimize segment boundaries using content analysis"""
        if len(boundaries) < 2:
            return [(content, "comprehensive", "")]
        
        # Simple approach: divide content roughly equally with respect to boundaries
        content_length = len(content)
        segment_size = content_length // target_segments
        
        segments = []
        last_boundary = 0
        
        for seg_idx in range(target_segments):
            # Find ideal split point
            ideal_end = min(content_length, (seg_idx + 1) * segment_size)
            
            # Find nearest boundary
            if seg_idx == target_segments - 1:  # Last segment
                actual_end = content_length
            else:
                actual_end = self._find_nearest_boundary(boundaries, ideal_end)
            
            # Extract segment
            segment_content = content[last_boundary:actual_end].strip()
            
            if not segment_content:
                continue
            
            # Determine focus type and title suffix
            focus_type, title_suffix = self._analyze_segment_focus(
                segment_content, seg_idx, target_segments
            )
            
            segments.append((segment_content, focus_type, title_suffix))
            last_boundary = actual_end
        
        return segments
    
    def _find_nearest_boundary(self, boundaries: List[int], target_pos: int) -> int:
        """Find the boundary closest to target position"""
        if not boundaries:
            return target_pos
        
        # Find closest boundary
        closest_boundary = min(boundaries, key=lambda x: abs(x - target_pos))
        
        # Prefer boundaries that are not too far from target
        if abs(closest_boundary - target_pos) < len(boundaries) * 50:  # Reasonable threshold
            return closest_boundary
        
        return target_pos
    
    def _analyze_segment_focus(self, content: str, segment_idx: int, 
                             total_segments: int) -> Tuple[str, str]:
        """Analyze segment content to determine focus type and title"""
        
        # Count different types of content
        definition_count = len(re.findall(r'(?:Definition|defined as|refers to)', content, re.IGNORECASE))
        example_count = len(re.findall(r'(?:Example|For example|Consider)', content, re.IGNORECASE))
        formula_count = len(re.findall(r'\$([^$]+)\$', content))
        application_count = len(re.findall(r'(?:Application|used to|applies to)', content, re.IGNORECASE))
        
        # Determine primary focus
        focus_scores = {
            'definitions': definition_count * 2,
            'examples': example_count * 1.5,
            'theory': formula_count * 2,
            'applications': application_count * 1.8,
        }
        
        primary_focus = max(focus_scores.keys(), key=lambda k: focus_scores[k])
        
        # Generate title suffix based on content and position
        if total_segments <= 2:
            # Simple part numbering
            if segment_idx == 0:
                title_suffix = "Introduction & Theory" if primary_focus in ['definitions', 'theory'] else "Part 1"
            else:
                title_suffix = "Applications & Examples" if primary_focus in ['examples', 'applications'] else "Part 2"
        
        elif total_segments <= 4:
            # Descriptive part naming
            suffix_map = {
                0: "Fundamentals",
                1: "Theory & Methods" if primary_focus == 'theory' else "Core Concepts", 
                2: "Applications" if primary_focus == 'applications' else "Examples",
                3: "Advanced Topics"
            }
            title_suffix = suffix_map.get(segment_idx, f"Part {segment_idx + 1}")
        
        else:
            # Numbered parts for many segments
            title_suffix = f"Part {segment_idx + 1}"
        
        return primary_focus, title_suffix
    
    def _extract_segment_elements(self, content: str) -> Dict[str, List[str]]:
        """Extract educational elements from a content segment"""
        return self._extract_educational_elements(content)
    
    def create_chapter_video_series(self, chapter_sections: List['TextSection'], 
                                  target_video_duration: int = 10) -> List[VideoSubtopic]:
        """
        Create a complete video series for an entire chapter with optimal pacing
        
        Args:
            chapter_sections: List of sections in the chapter
            target_video_duration: Target duration per video in minutes
            
        Returns:
            List of VideoSubtopic objects with intelligent numbering
        """
        print(f"CHAPTER SERIES: Creating video series for {len(chapter_sections)} sections")
        
        all_videos = []
        video_counter = 1
        
        for section in chapter_sections:
            # Check if section needs subdivision
            if self.should_subdivide_section(section):
                # Use optimal 10-minute subdivision
                subtopics = self._subdivide_optimal_10min(section)
                
                # Renumber for chapter-wide consistency
                for subtopic in subtopics:
                    subtopic.subtopic_index = f"Video_{video_counter:02d}"
                    # Update title to include video number
                    if not subtopic.title.startswith("Video"):
                        subtopic.title = f"Video {video_counter}: {subtopic.title}"
                    video_counter += 1
                    
                all_videos.extend(subtopics)
            else:
                # Single video for this section
                subtopic = VideoSubtopic(
                    title=f"Video {video_counter}: {section.title}",
                    content=section.content,
                    focus_type="comprehensive",
                    parent_section=section.section_number,
                    subtopic_index=f"Video_{video_counter:02d}",
                    educational_elements=section.educational_elements,
                    complexity_score=self._calculate_complexity_score(section),
                    estimated_duration=self._estimate_duration(section.content)
                )
                all_videos.append(subtopic)
                video_counter += 1
        
        # Final optimization: merge very short videos or split very long ones
        optimized_videos = self._optimize_video_series(all_videos, target_video_duration)
        
        print(f"CHAPTER SERIES: Generated {len(optimized_videos)} videos from {len(chapter_sections)} sections")
        return optimized_videos
    
    def _optimize_video_series(self, videos: List[VideoSubtopic], 
                             target_duration: int) -> List[VideoSubtopic]:
        """Optimize video series by merging short videos and splitting long ones"""
        
        optimized = []
        i = 0
        
        while i < len(videos):
            current_video = videos[i]
            
            # If video is too short, try to merge with next
            if (current_video.estimated_duration < target_duration * 0.6 and 
                i < len(videos) - 1 and 
                videos[i + 1].estimated_duration < target_duration * 0.6):
                
                next_video = videos[i + 1]
                
                # Merge videos
                merged_video = VideoSubtopic(
                    title=f"{current_video.title.split(':')[0]}: {current_video.title.split(':', 1)[1]} & {next_video.title.split(':', 1)[1]}",
                    content=current_video.content + "\n\n" + next_video.content,
                    focus_type="combined",
                    parent_section=current_video.parent_section,
                    subtopic_index=current_video.subtopic_index,
                    educational_elements=self._merge_educational_elements(
                        current_video.educational_elements, 
                        next_video.educational_elements
                    ),
                    complexity_score=(current_video.complexity_score + next_video.complexity_score) / 2,
                    estimated_duration=current_video.estimated_duration + next_video.estimated_duration
                )
                
                optimized.append(merged_video)
                i += 2  # Skip next video as it's been merged
                
            # If video is too long, split it
            elif current_video.estimated_duration > target_duration * 1.5:
                # Split into parts
                split_videos = self._split_long_video(current_video, target_duration)
                optimized.extend(split_videos)
                i += 1
                
            else:
                # Video duration is acceptable
                optimized.append(current_video)
                i += 1
        
        # Renumber the optimized series
        for idx, video in enumerate(optimized, 1):
            video.subtopic_index = f"Video_{idx:02d}"
            # Update title numbering
            if "Video" in video.title:
                title_parts = video.title.split(":", 1)
                if len(title_parts) == 2:
                    video.title = f"Video {idx}: {title_parts[1].strip()}"
        
        return optimized
    
    def _split_long_video(self, video: VideoSubtopic, target_duration: int) -> List[VideoSubtopic]:
        """Split a long video into multiple parts"""
        content = video.content
        estimated_duration = video.estimated_duration
        
        # Calculate number of parts needed
        num_parts = max(2, int(np.ceil(estimated_duration / target_duration)))
        
        # Use intelligent segmentation
        section = type('Section', (), {
            'title': video.title,
            'content': content,
            'section_number': video.parent_section,
            'educational_elements': video.educational_elements
        })()
        
        segments = self._create_intelligent_segments(section, num_parts, target_duration)
        
        split_videos = []
        for i, (segment_content, focus_type, title_suffix) in enumerate(segments):
            split_title = f"{video.title} - Part {i + 1}"
            if title_suffix:
                split_title = f"{video.title} - {title_suffix}"
            
            split_video = VideoSubtopic(
                title=split_title,
                content=segment_content,
                focus_type=focus_type,
                parent_section=video.parent_section,
                subtopic_index=f"{video.subtopic_index}.{i + 1}",
                educational_elements=self._extract_segment_elements(segment_content),
                complexity_score=self._calculate_content_complexity(segment_content),
                estimated_duration=self._estimate_duration(segment_content)
            )
            split_videos.append(split_video)
        
        return split_videos
    
    def _merge_educational_elements(self, elements1: Dict[str, List[str]], 
                                  elements2: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Merge educational elements from two videos"""
        merged = {}
        all_keys = set(elements1.keys()) | set(elements2.keys())
        
        for key in all_keys:
            list1 = elements1.get(key, [])
            list2 = elements2.get(key, [])
            merged[key] = list1 + list2
        
        return merged
    
    def generate_video_file_names(self, subtopics: List[VideoSubtopic], 
                                 base_name: str = "video") -> List[str]:
        """
        Generate appropriate file names for video subtopics
        
        Args:
            subtopics: List of video subtopics
            base_name: Base name for the video files
            
        Returns:
            List of file names with proper part numbering
        """
        file_names = []
        
        for subtopic in subtopics:
            # Create safe file name
            title = subtopic.title.lower()
            title = re.sub(r'[^\w\s-]', '', title)  # Remove special characters
            title = re.sub(r'[-\s]+', '_', title)   # Replace spaces/hyphens with underscores
            title = title[:50]  # Limit length
            
            # Add part numbering if multiple videos from same parent section
            same_parent_videos = [s for s in subtopics if s.parent_section == subtopic.parent_section]
            
            if len(same_parent_videos) > 1:
                # Multiple parts - add part suffix
                part_number = same_parent_videos.index(subtopic) + 1
                file_name = f"{title}_part_{part_number}.mp4"
            else:
                # Single video
                file_name = f"{title}.mp4"
            
            file_names.append(file_name)
        
        return file_names