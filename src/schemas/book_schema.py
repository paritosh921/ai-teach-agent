"""
JSON Schema Definition for Educational Books

This module defines the comprehensive JSON schema for educational books,
providing rich metadata and flexible content structures for video generation.
"""

from typing import Dict, List, Optional, Union, Literal, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class DifficultyLevel(str, Enum):
    """Educational difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"  
    ADVANCED = "advanced"
    EXPERT = "expert"


class ContentBlockType(str, Enum):
    """Types of educational content blocks"""
    INTRODUCTION = "introduction"
    DEFINITION = "definition"
    THEOREM = "theorem"
    PROOF = "proof"
    EXAMPLE = "example"
    EXERCISE = "exercise"
    APPLICATION = "application"
    SUMMARY = "summary"
    TEXT = "text"
    FORMULA = "formula"
    DIAGRAM = "diagram"
    INTERACTIVE = "interactive"


class SubjectArea(str, Enum):
    """Academic subject areas"""
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    COMPUTER_SCIENCE = "computer_science"
    ENGINEERING = "engineering"
    BIOLOGY = "biology"
    ECONOMICS = "economics"
    GENERAL = "general"


@dataclass
class BookMetadata:
    """Metadata for the educational book"""
    title: str
    subject: SubjectArea
    level: str  # e.g., "undergraduate", "high_school", "graduate"
    language: str = "english"
    version: str = "1.0"
    authors: List[str] = field(default_factory=list)
    description: Optional[str] = None
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "subject": self.subject,
            "level": self.level,
            "language": self.language,
            "version": self.version,
            "authors": self.authors,
            "description": self.description,
            "isbn": self.isbn,
            "publication_year": self.publication_year,
            "tags": self.tags
        }


@dataclass
class LearningObjective:
    """Learning objective with assessment criteria"""
    objective: str
    bloom_level: str  # "remember", "understand", "apply", "analyze", "evaluate", "create"
    assessment_method: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.objective,
            "bloom_level": self.bloom_level,
            "assessment_method": self.assessment_method
        }


@dataclass
class ContentBlock:
    """Individual content block with rich metadata"""
    type: ContentBlockType
    content: str
    id: Optional[str] = None
    title: Optional[str] = None
    importance: Optional[str] = None  # "fundamental", "important", "supplementary"
    formula: Optional[str] = None
    diagram_description: Optional[str] = None
    interactive_type: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # For structured content like examples and exercises
    problem: Optional[str] = None
    solution_steps: List[str] = field(default_factory=list)
    answer: Optional[str] = None
    hints: List[str] = field(default_factory=list)
    
    # For proofs and theorems
    hypothesis: Optional[str] = None
    conclusion: Optional[str] = None
    proof_method: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "content": self.content,
            "id": self.id,
            "title": self.title,
            "importance": self.importance,
            "formula": self.formula,
            "diagram_description": self.diagram_description,
            "interactive_type": self.interactive_type,
            "tags": self.tags,
            "problem": self.problem,
            "solution_steps": self.solution_steps,
            "answer": self.answer,
            "hints": self.hints,
            "hypothesis": self.hypothesis,
            "conclusion": self.conclusion,
            "proof_method": self.proof_method
        }


@dataclass
class EducationalElements:
    """Rich educational element classification"""
    key_concepts: List[str] = field(default_factory=list)
    formulas: List[str] = field(default_factory=list)
    definitions: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    exercises: List[Dict[str, Any]] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    follow_up_topics: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_concepts": self.key_concepts,
            "formulas": self.formulas,
            "definitions": self.definitions,
            "examples": self.examples,
            "exercises": self.exercises,
            "applications": self.applications,
            "prerequisites": self.prerequisites,
            "follow_up_topics": self.follow_up_topics,
            "common_mistakes": self.common_mistakes
        }


@dataclass
class VideoGenerationHints:
    """Hints for video generation and subdivision"""
    suggested_duration: Optional[int] = None  # minutes
    subdivision_strategy: Optional[str] = None  # "auto", "by_type", "by_length", "by_concept"
    focus_areas: List[str] = field(default_factory=list)
    visual_emphasis: List[str] = field(default_factory=list)  # Elements that need visual attention
    pace: Optional[str] = None  # "slow", "moderate", "fast"
    complexity_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "suggested_duration": self.suggested_duration,
            "subdivision_strategy": self.subdivision_strategy,
            "focus_areas": self.focus_areas,
            "visual_emphasis": self.visual_emphasis,
            "pace": self.pace,
            "complexity_score": self.complexity_score
        }


@dataclass
class Section:
    """Rich section structure with flexible content"""
    id: str
    number: str  # e.g., "1.1", "2.3.1"
    title: str
    difficulty: DifficultyLevel
    estimated_duration: int  # minutes
    content_blocks: List[ContentBlock]
    learning_objectives: List[LearningObjective] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    educational_elements: Optional[EducationalElements] = None
    video_hints: Optional[VideoGenerationHints] = None
    notes: Optional[str] = None
    subsections: List['Section'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "difficulty": self.difficulty,
            "estimated_duration": self.estimated_duration,
            "content_blocks": [block.to_dict() for block in self.content_blocks],
            "learning_objectives": [obj.to_dict() for obj in self.learning_objectives],
            "prerequisites": self.prerequisites,
            "educational_elements": self.educational_elements.to_dict() if self.educational_elements else None,
            "video_hints": self.video_hints.to_dict() if self.video_hints else None,
            "notes": self.notes,
            "subsections": [sub.to_dict() for sub in self.subsections]
        }


@dataclass
class Chapter:
    """Rich chapter structure"""
    id: str
    number: int
    title: str
    description: Optional[str] = None
    learning_objectives: List[LearningObjective] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)
    estimated_total_duration: Optional[int] = None  # minutes
    difficulty_progression: Optional[str] = None  # "linear", "increasing", "mixed"
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "description": self.description,
            "learning_objectives": [obj.to_dict() for obj in self.learning_objectives],
            "sections": [section.to_dict() for section in self.sections],
            "estimated_total_duration": self.estimated_total_duration,
            "difficulty_progression": self.difficulty_progression,
            "notes": self.notes
        }


@dataclass
class JsonBook:
    """Complete JSON book structure"""
    metadata: BookMetadata
    chapters: List[Chapter]
    global_prerequisites: List[str] = field(default_factory=list)
    appendices: List[Section] = field(default_factory=list)
    glossary: Dict[str, str] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "chapters": [chapter.to_dict() for chapter in self.chapters],
            "global_prerequisites": self.global_prerequisites,
            "appendices": [appendix.to_dict() for appendix in self.appendices],
            "glossary": self.glossary,
            "references": self.references
        }
    
    def save_json(self, filepath: Union[str, Path]) -> None:
        """Save the book as JSON file"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_json(cls, filepath: Union[str, Path]) -> 'JsonBook':
        """Load book from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Parse metadata
        metadata_data = data["metadata"]
        metadata = BookMetadata(
            title=metadata_data["title"],
            subject=SubjectArea(metadata_data["subject"]),
            level=metadata_data["level"],
            language=metadata_data.get("language", "english"),
            version=metadata_data.get("version", "1.0"),
            authors=metadata_data.get("authors", []),
            description=metadata_data.get("description"),
            isbn=metadata_data.get("isbn"),
            publication_year=metadata_data.get("publication_year"),
            tags=metadata_data.get("tags", [])
        )
        
        # Parse chapters
        chapters = []
        for chapter_data in data["chapters"]:
            sections = []
            for section_data in chapter_data["sections"]:
                # Parse content blocks
                content_blocks = []
                for block_data in section_data["content_blocks"]:
                    content_block = ContentBlock(
                        type=ContentBlockType(block_data["type"]),
                        content=block_data["content"],
                        id=block_data.get("id"),
                        title=block_data.get("title"),
                        importance=block_data.get("importance"),
                        formula=block_data.get("formula"),
                        diagram_description=block_data.get("diagram_description"),
                        interactive_type=block_data.get("interactive_type"),
                        tags=block_data.get("tags", []),
                        problem=block_data.get("problem"),
                        solution_steps=block_data.get("solution_steps", []),
                        answer=block_data.get("answer"),
                        hints=block_data.get("hints", []),
                        hypothesis=block_data.get("hypothesis"),
                        conclusion=block_data.get("conclusion"),
                        proof_method=block_data.get("proof_method")
                    )
                    content_blocks.append(content_block)
                
                # Parse learning objectives
                learning_objectives = []
                for obj_data in section_data.get("learning_objectives", []):
                    learning_obj = LearningObjective(
                        objective=obj_data["objective"],
                        bloom_level=obj_data["bloom_level"],
                        assessment_method=obj_data.get("assessment_method")
                    )
                    learning_objectives.append(learning_obj)
                
                # Parse educational elements
                educational_elements = None
                if section_data.get("educational_elements"):
                    elem_data = section_data["educational_elements"]
                    educational_elements = EducationalElements(
                        key_concepts=elem_data.get("key_concepts", []),
                        formulas=elem_data.get("formulas", []),
                        definitions=elem_data.get("definitions", []),
                        examples=elem_data.get("examples", []),
                        exercises=elem_data.get("exercises", []),
                        applications=elem_data.get("applications", []),
                        prerequisites=elem_data.get("prerequisites", []),
                        follow_up_topics=elem_data.get("follow_up_topics", []),
                        common_mistakes=elem_data.get("common_mistakes", [])
                    )
                
                # Parse video hints
                video_hints = None
                if section_data.get("video_hints"):
                    hints_data = section_data["video_hints"]
                    video_hints = VideoGenerationHints(
                        suggested_duration=hints_data.get("suggested_duration"),
                        subdivision_strategy=hints_data.get("subdivision_strategy"),
                        focus_areas=hints_data.get("focus_areas", []),
                        visual_emphasis=hints_data.get("visual_emphasis", []),
                        pace=hints_data.get("pace"),
                        complexity_score=hints_data.get("complexity_score")
                    )
                
                section = Section(
                    id=section_data["id"],
                    number=section_data["number"],
                    title=section_data["title"],
                    difficulty=DifficultyLevel(section_data["difficulty"]),
                    estimated_duration=section_data["estimated_duration"],
                    content_blocks=content_blocks,
                    learning_objectives=learning_objectives,
                    prerequisites=section_data.get("prerequisites", []),
                    educational_elements=educational_elements,
                    video_hints=video_hints,
                    notes=section_data.get("notes")
                )
                sections.append(section)
            
            # Parse chapter learning objectives
            chapter_objectives = []
            for obj_data in chapter_data.get("learning_objectives", []):
                learning_obj = LearningObjective(
                    objective=obj_data["objective"],
                    bloom_level=obj_data["bloom_level"],
                    assessment_method=obj_data.get("assessment_method")
                )
                chapter_objectives.append(learning_obj)
            
            chapter = Chapter(
                id=chapter_data["id"],
                number=chapter_data["number"],
                title=chapter_data["title"],
                description=chapter_data.get("description"),
                learning_objectives=chapter_objectives,
                sections=sections,
                estimated_total_duration=chapter_data.get("estimated_total_duration"),
                difficulty_progression=chapter_data.get("difficulty_progression"),
                notes=chapter_data.get("notes")
            )
            chapters.append(chapter)
        
        return cls(
            metadata=metadata,
            chapters=chapters,
            global_prerequisites=data.get("global_prerequisites", []),
            appendices=[],  # TODO: Parse appendices if needed
            glossary=data.get("glossary", {}),
            references=data.get("references", [])
        )


class BookSchemaValidator:
    """Validator for JSON book schema"""
    
    @staticmethod
    def validate_content_block(block_data: Dict[str, Any]) -> List[str]:
        """Validate content block structure"""
        errors = []
        
        if "type" not in block_data:
            errors.append("Content block missing required 'type' field")
        elif block_data["type"] not in [t.value for t in ContentBlockType]:
            errors.append(f"Invalid content block type: {block_data['type']}")
        
        if "content" not in block_data:
            errors.append("Content block missing required 'content' field")
        
        # Validate specific block types
        block_type = block_data.get("type")
        if block_type == "example" and not (block_data.get("problem") or block_data.get("solution_steps")):
            errors.append("Example block should have 'problem' or 'solution_steps'")
        
        if block_type == "formula" and not block_data.get("formula"):
            errors.append("Formula block should have 'formula' field")
        
        return errors
    
    @staticmethod
    def validate_section(section_data: Dict[str, Any]) -> List[str]:
        """Validate section structure"""
        errors = []
        
        required_fields = ["id", "number", "title", "difficulty", "estimated_duration", "content_blocks"]
        for field in required_fields:
            if field not in section_data:
                errors.append(f"Section missing required field: {field}")
        
        # Validate difficulty level
        if "difficulty" in section_data and section_data["difficulty"] not in [d.value for d in DifficultyLevel]:
            errors.append(f"Invalid difficulty level: {section_data['difficulty']}")
        
        # Validate content blocks
        if "content_blocks" in section_data:
            for i, block in enumerate(section_data["content_blocks"]):
                block_errors = BookSchemaValidator.validate_content_block(block)
                for error in block_errors:
                    errors.append(f"Content block {i}: {error}")
        
        return errors
    
    @staticmethod
    def validate_book(book_data: Dict[str, Any]) -> List[str]:
        """Validate complete book structure"""
        errors = []
        
        # Validate top-level structure
        if "metadata" not in book_data:
            errors.append("Book missing required 'metadata' field")
        if "chapters" not in book_data:
            errors.append("Book missing required 'chapters' field")
        
        # Validate metadata
        if "metadata" in book_data:
            metadata = book_data["metadata"]
            required_meta_fields = ["title", "subject", "level"]
            for field in required_meta_fields:
                if field not in metadata:
                    errors.append(f"Metadata missing required field: {field}")
        
        # Validate chapters and sections
        if "chapters" in book_data:
            for i, chapter in enumerate(book_data["chapters"]):
                if "sections" not in chapter:
                    errors.append(f"Chapter {i} missing 'sections' field")
                    continue
                
                for j, section in enumerate(chapter["sections"]):
                    section_errors = BookSchemaValidator.validate_section(section)
                    for error in section_errors:
                        errors.append(f"Chapter {i}, Section {j}: {error}")
        
        return errors


# Example usage and schema documentation
EXAMPLE_JSON_STRUCTURE = {
    "metadata": {
        "title": "Introduction to Calculus",
        "subject": "mathematics",
        "level": "undergraduate",
        "language": "english",
        "version": "2.0",
        "authors": ["Dr. John Smith"],
        "description": "A comprehensive introduction to differential and integral calculus"
    },
    "chapters": [
        {
            "id": "chapter_1",
            "number": 1,
            "title": "Limits and Continuity", 
            "description": "Foundational concepts of limits",
            "sections": [
                {
                    "id": "section_1_1",
                    "number": "1.1",
                    "title": "Understanding Limits",
                    "difficulty": "beginner",
                    "estimated_duration": 20,
                    "content_blocks": [
                        {
                            "type": "introduction",
                            "content": "The concept of a limit is fundamental to calculus..."
                        },
                        {
                            "type": "definition",
                            "title": "Limit Definition",
                            "content": "A limit describes the behavior of a function as its input approaches a particular value.",
                            "formula": "lim(x→a) f(x) = L",
                            "importance": "fundamental"
                        },
                        {
                            "type": "example", 
                            "title": "Computing a Simple Limit",
                            "problem": "Find lim(x→2) x²",
                            "solution_steps": [
                                "Substitute x = 2 directly since x² is continuous",
                                "lim(x→2) x² = 2² = 4"
                            ],
                            "answer": "4"
                        }
                    ],
                    "learning_objectives": [
                        {
                            "objective": "Define the concept of a limit",
                            "bloom_level": "understand"
                        },
                        {
                            "objective": "Calculate basic limits using direct substitution",
                            "bloom_level": "apply"
                        }
                    ],
                    "educational_elements": {
                        "key_concepts": ["limit", "approaching", "continuous"],
                        "formulas": ["lim(x→a) f(x) = L"],
                        "examples": [
                            {
                                "type": "computation",
                                "difficulty": "basic",
                                "description": "Direct substitution limit"
                            }
                        ]
                    },
                    "video_hints": {
                        "suggested_duration": 15,
                        "subdivision_strategy": "by_type",
                        "focus_areas": ["definition", "examples"],
                        "visual_emphasis": ["limit notation", "graph approaching"],
                        "pace": "moderate"
                    }
                }
            ]
        }
    ]
}