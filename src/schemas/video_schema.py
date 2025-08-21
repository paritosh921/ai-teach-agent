"""
Video Schema Validation for Builder LLM

This module defines and validates the strict YAML schema used by the Builder LLM
for deterministic video generation. It ensures all generated YAML specs conform
to the required structure for layout safety and proper code generation.
"""

import yaml
from typing import Dict, Any, List, Union, Optional
from dataclasses import dataclass
from enum import Enum


class ElementType(Enum):
    """Supported element types in the Builder LLM system"""
    TEXT = "Text"
    MATHTEX = "MathTex"
    AXESPLOT = "AxesPlot"
    TABLE = "Table"
    IMAGE = "Image"


class ColumnPosition(Enum):
    """Column positions for layout templates"""
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class LayoutTemplate(Enum):
    """Supported layout templates"""
    SINGLE = "single"
    TWO_COLUMN = "two_column"
    THREE_COLUMN = "three_column"


class AnimationType(Enum):
    """Animation types for element entrance/exit"""
    WRITE = "Write"
    FADE_IN = "FadeIn"
    FADE_OUT = "FadeOut"
    CREATE = "Create"
    GROW_FROM_CENTER = "GrowFromCenter"
    SHRINK_TO_CENTER = "ShrinkToCenter"
    TRANSFORM = "Transform"


@dataclass
class StyleSpec:
    """Element style specifications"""
    font_size: Optional[int] = None
    weight: Optional[str] = None
    color: Optional[str] = None


@dataclass
class WrapSpec:
    """Text wrapping specifications"""
    max_chars: Optional[int] = None
    max_lines: Optional[int] = None


@dataclass
class ScaleFitSpec:
    """Element scaling specifications"""
    max_width_pct: Optional[float] = None
    max_height_pct: Optional[float] = None


@dataclass
class AnimationSpec:
    """Animation timing specifications"""
    anim: str  # Animation type
    at: float  # Time in seconds


@dataclass
class ElementSpec:
    """Individual element specification"""
    key: str
    type: str  # ElementType
    column: str  # ColumnPosition
    content: Optional[str] = None  # For Text/MathTex
    tex: Optional[str] = None      # For MathTex
    path: Optional[str] = None     # For Image
    fn: Optional[str] = None       # For AxesPlot function
    style: Optional[StyleSpec] = None
    wrap: Optional[WrapSpec] = None
    scale_fit: Optional[ScaleFitSpec] = None
    z_index: Optional[int] = None
    enter: Optional[AnimationSpec] = None
    exit: Optional[AnimationSpec] = None


@dataclass
class LayoutSpec:
    """Layout specification for a scene"""
    template: str  # LayoutTemplate
    elements: List[ElementSpec]


@dataclass
class ChecksSpec:
    """Validation checks for a scene"""
    require_no_overlap: bool = True
    require_in_frame: bool = True


@dataclass
class SceneSpec:
    """Individual scene specification"""
    id: str
    goal: str
    time_budget_s: int
    narration: str
    layout: LayoutSpec
    checks: ChecksSpec


@dataclass
class StyleConfig:
    """Video style configuration"""
    voice: str = "professional"
    pace_wpm: int = 150
    theme: str = "3blue1brown"


@dataclass
class GridSpec:
    """Grid template specification"""
    template: str
    config: Dict[str, Any] = None


@dataclass
class GlobalConfig:
    """Global video configuration"""
    safe_margin_pct: float = 0.06
    default_font_size: int = 42
    max_width_pct: float = 0.92
    grid: Optional[GridSpec] = None


@dataclass
class VideoSpec:
    """Complete video specification"""
    topic: str
    audience: str
    style: StyleConfig
    global_config: GlobalConfig
    scenes: List[SceneSpec]


class VideoSchemaValidator:
    """Validator for video YAML specifications"""
    
    def __init__(self):
        """Initialize the validator with required fields and constraints"""
        self.required_fields = {
            'video_spec': ['topic', 'audience', 'style', 'global', 'scenes'],
            'style': ['voice', 'pace_wpm', 'theme'],
            'global': ['safe_margin_pct', 'default_font_size', 'max_width_pct'],
            'scene': ['id', 'goal', 'time_budget_s', 'narration', 'layout', 'checks'],
            'layout': ['template', 'elements'],
            'element': ['key', 'type', 'column'],
            'animation': ['anim', 'at']
        }
        
        self.valid_enums = {
            'element_type': [e.value for e in ElementType],
            'column_position': [e.value for e in ColumnPosition],
            'layout_template': [e.value for e in LayoutTemplate],
            'animation_type': [e.value for e in AnimationType]
        }
    
    def validate_yaml_spec(self, yaml_spec: Dict[str, Any]) -> bool:
        """
        Validate a complete YAML specification
        
        Args:
            yaml_spec: Dictionary from parsed YAML
            
        Returns:
            True if valid, raises ValidationError if invalid
        """
        try:
            self._validate_video_spec(yaml_spec)
            return True
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Unexpected validation error: {e}")
    
    def _validate_video_spec(self, spec: Dict[str, Any]) -> None:
        """Validate top-level video specification"""
        self._check_required_fields(spec, 'video_spec')
        
        # Validate topic and audience
        if not isinstance(spec['topic'], str) or not spec['topic'].strip():
            raise ValidationError("topic must be a non-empty string")
        
        if not isinstance(spec['audience'], str) or not spec['audience'].strip():
            raise ValidationError("audience must be a non-empty string")
        
        # Validate style
        self._validate_style(spec['style'])
        
        # Validate global config
        self._validate_global_config(spec['global'])
        
        # Validate scenes
        if not isinstance(spec['scenes'], list) or len(spec['scenes']) == 0:
            raise ValidationError("scenes must be a non-empty list")
        
        for i, scene in enumerate(spec['scenes']):
            try:
                self._validate_scene(scene)
            except ValidationError as e:
                raise ValidationError(f"Scene {i}: {e}")
    
    def _validate_style(self, style: Dict[str, Any]) -> None:
        """Validate style configuration"""
        self._check_required_fields(style, 'style')
        
        if not isinstance(style['voice'], str):
            raise ValidationError("style.voice must be a string")
        
        if not isinstance(style['pace_wpm'], int) or style['pace_wpm'] <= 0:
            raise ValidationError("style.pace_wpm must be a positive integer")
        
        if not isinstance(style['theme'], str):
            raise ValidationError("style.theme must be a string")
    
    def _validate_global_config(self, global_config: Dict[str, Any]) -> None:
        """Validate global configuration"""
        self._check_required_fields(global_config, 'global')
        
        # Validate safe_margin_pct
        margin = global_config['safe_margin_pct']
        if not isinstance(margin, (int, float)) or margin < 0.01 or margin > 0.2:
            raise ValidationError("safe_margin_pct must be between 0.01 and 0.2")
        
        # Validate default_font_size
        font_size = global_config['default_font_size']
        if not isinstance(font_size, int) or font_size < 12 or font_size > 120:
            raise ValidationError("default_font_size must be between 12 and 120")
        
        # Validate max_width_pct
        max_width = global_config['max_width_pct']
        if not isinstance(max_width, (int, float)) or max_width < 0.5 or max_width > 1.0:
            raise ValidationError("max_width_pct must be between 0.5 and 1.0")
    
    def _validate_scene(self, scene: Dict[str, Any]) -> None:
        """Validate individual scene specification"""
        self._check_required_fields(scene, 'scene')
        
        # Validate scene ID
        if not isinstance(scene['id'], str) or not scene['id'].strip():
            raise ValidationError("scene.id must be a non-empty string")
        
        # Validate goal
        if not isinstance(scene['goal'], str) or not scene['goal'].strip():
            raise ValidationError("scene.goal must be a non-empty string")
        
        # Validate time budget
        if not isinstance(scene['time_budget_s'], int) or scene['time_budget_s'] <= 0:
            raise ValidationError("scene.time_budget_s must be a positive integer")
        
        # Validate narration
        if not isinstance(scene['narration'], str) or not scene['narration'].strip():
            raise ValidationError("scene.narration must be a non-empty string")
        
        # Validate layout
        self._validate_layout(scene['layout'])
        
        # Validate checks
        self._validate_checks(scene['checks'])
    
    def _validate_layout(self, layout: Dict[str, Any]) -> None:
        """Validate layout specification"""
        self._check_required_fields(layout, 'layout')
        
        # Validate template
        template_value = layout['template']
        if template_value not in self.valid_enums['layout_template']:
            raise ValidationError(f"layout.template '{template_value}' must be one of: {self.valid_enums['layout_template']}")
        
        # Validate elements
        if not isinstance(layout['elements'], list) or len(layout['elements']) == 0:
            raise ValidationError("layout.elements must be a non-empty list")
        
        element_keys = set()
        for i, element in enumerate(layout['elements']):
            try:
                self._validate_element(element)
                # Check for duplicate keys
                if element['key'] in element_keys:
                    raise ValidationError(f"Duplicate element key: {element['key']}")
                element_keys.add(element['key'])
            except ValidationError as e:
                raise ValidationError(f"Element {i} ({element.get('key', 'unknown')}): {e}")
    
    def _validate_element(self, element: Dict[str, Any]) -> None:
        """Validate individual element specification"""
        self._check_required_fields(element, 'element')
        
        # Validate key
        if not isinstance(element['key'], str) or not element['key'].strip():
            raise ValidationError("element.key must be a non-empty string")
        
        # Validate type
        if element['type'] not in self.valid_enums['element_type']:
            raise ValidationError(f"element.type must be one of: {self.valid_enums['element_type']}")
        
        # Validate column
        if element['column'] not in self.valid_enums['column_position']:
            raise ValidationError(f"element.column must be one of: {self.valid_enums['column_position']}")
        
        # Validate content based on type
        element_type = element['type']
        if element_type in ['Text', 'MathTex']:
            # Accept 'content', 'tex', or 'text' fields (text is alias for content)
            if not any(field in element for field in ['content', 'tex', 'text']):
                raise ValidationError(f"{element_type} element must have 'content', 'tex', or 'text' field")
        elif element_type == 'Image':
            if 'path' not in element:
                raise ValidationError("Image element must have 'path' field")
        elif element_type == 'AxesPlot':
            if 'fn' not in element:
                raise ValidationError("AxesPlot element must have 'fn' field")
        
        # Validate optional fields
        if 'z_index' in element:
            if not isinstance(element['z_index'], int):
                raise ValidationError("element.z_index must be an integer")
        
        if 'enter' in element:
            self._validate_animation(element['enter'])
        
        if 'exit' in element:
            self._validate_animation(element['exit'])
    
    def _validate_animation(self, animation: Dict[str, Any]) -> None:
        """Validate animation specification"""
        self._check_required_fields(animation, 'animation')
        
        # Validate animation type
        if animation['anim'] not in self.valid_enums['animation_type']:
            raise ValidationError(f"animation.anim must be one of: {self.valid_enums['animation_type']}")
        
        # Validate timing
        if not isinstance(animation['at'], (int, float)) or animation['at'] < 0:
            raise ValidationError("animation.at must be a non-negative number")
    
    def _validate_checks(self, checks: Dict[str, Any]) -> None:
        """Validate checks specification"""
        if 'require_no_overlap' in checks:
            if not isinstance(checks['require_no_overlap'], bool):
                raise ValidationError("checks.require_no_overlap must be a boolean")
        
        if 'require_in_frame' in checks:
            if not isinstance(checks['require_in_frame'], bool):
                raise ValidationError("checks.require_in_frame must be a boolean")
    
    def _check_required_fields(self, obj: Dict[str, Any], obj_type: str) -> None:
        """Check that all required fields are present"""
        required = self.required_fields.get(obj_type, [])
        missing = [field for field in required if field not in obj]
        if missing:
            raise ValidationError(f"Missing required fields for {obj_type}: {missing}")


class ValidationError(Exception):
    """Custom exception for YAML validation errors"""
    pass


def validate_video_yaml(yaml_content: Union[str, Dict[str, Any]]) -> bool:
    """
    Validate a video YAML specification
    
    Args:
        yaml_content: Either YAML string or parsed dictionary
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    if isinstance(yaml_content, str):
        try:
            parsed = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValidationError(f"Invalid YAML syntax: {e}")
    else:
        parsed = yaml_content
    
    validator = VideoSchemaValidator()
    return validator.validate_yaml_spec(parsed)


def create_example_yaml() -> Dict[str, Any]:
    """Create an example valid YAML specification for testing"""
    return {
        'topic': 'Integration Basics',
        'audience': 'undergraduate',
        'style': {
            'voice': 'professional',
            'pace_wpm': 150,
            'theme': '3blue1brown'
        },
        'global': {
            'safe_margin_pct': 0.06,
            'default_font_size': 42,
            'max_width_pct': 0.92,
            'grid': {
                'template': 'single',
                'config': {}
            }
        },
        'scenes': [
            {
                'id': 'intro',
                'goal': 'Introduce the concept of integration',
                'time_budget_s': 30,
                'narration': 'Today we will explore integration, the process of finding areas under curves.',
                'layout': {
                    'template': 'single',
                    'elements': [
                        {
                            'key': 'title',
                            'type': 'Text',
                            'content': 'Integration Basics',
                            'column': 'center',
                            'style': {'font_size': 48},
                            'z_index': 2,
                            'enter': {'anim': 'Write', 'at': 0.5},
                            'exit': {'anim': 'FadeOut', 'at': 4.0}
                        }
                    ]
                },
                'checks': {
                    'require_no_overlap': True,
                    'require_in_frame': True
                }
            }
        ]
    }