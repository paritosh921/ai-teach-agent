"""
Smart Manim Code Generator for Builder LLM System

This module generates Manim code with strict adherence to layout safety rules:
- Helper utilities inline (safe_frame, scale_to_fit_pct, place_in_grid)
- Collision detection and auto-shrinking
- Z-index management and explicit exit/enter sequencing
- Template-based positioning with safety guarantees
"""

import os
import yaml
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from ..schemas.layout_templates import get_template_manager, get_template_positions, get_template_helpers
from ..layout.safe_layout_manager import create_safe_layout_manager
from ..layout.collision_detector import validate_layout_safety


@dataclass
class CodeGenerationConfig:
    """Configuration for code generation"""
    frame_width: float = 14.0
    frame_height: float = 8.0
    safe_margin_pct: float = 0.06
    default_font_size: int = 42
    min_font_size: int = 24
    buffer_distance: float = 0.2
    include_debug_helpers: bool = True
    use_modern_api: bool = True


class ManimCodeGenerator:
    """
    Generates Manim code from YAML specifications with safety guarantees
    
    Key features:
    - Template-based layout with collision avoidance
    - Inline helper utilities for safety checks
    - Modern Manim API usage
    - Z-index management and proper sequencing
    - Deterministic output with fixed seeds
    """
    
    def __init__(self, config: Optional[CodeGenerationConfig] = None):
        """Initialize code generator with configuration"""
        self.config = config or CodeGenerationConfig()
        
        # Initialize layout manager
        self.layout_manager = create_safe_layout_manager(
            self.config.frame_width, 
            self.config.frame_height
        )
        
        # Get template manager
        self.template_manager = get_template_manager()
        
        # Code generation state
        self.generated_elements: Dict[str, Dict[str, Any]] = {}
        self.scene_timeline: List[Tuple[float, str, str]] = []  # (time, action, element_key)
    
    def generate_code(self, yaml_spec: Dict[str, Any]) -> str:
        """
        Generate complete Manim code from YAML specification
        
        Args:
            yaml_spec: Validated YAML specification from Builder LLM
            
        Returns:
            Complete Python code ready for compilation
        """
        print("🔨 Generating Manim code from YAML specification...")
        
        # Reset state
        self.generated_elements = {}
        self.scene_timeline = []
        
        # Extract key information
        topic = yaml_spec.get('topic', 'Video')
        global_config = yaml_spec.get('global', {})
        scenes = yaml_spec.get('scenes', [])
        
        # Validate scenes and elements for safety
        self._validate_spec_safety(yaml_spec)
        
        # Generate code sections
        code_sections = [
            self._generate_imports(),
            self._generate_helper_utilities(global_config),
            self._generate_scene_class(topic, scenes, global_config),
        ]
        
        # Combine all sections
        full_code = '\n\n'.join(section for section in code_sections if section)
        
        print("OK: Code generation completed")
        print(f"CHART: Generated {len(scenes)} scenes with {len(self.generated_elements)} elements")
        
        return full_code
    
    def _validate_spec_safety(self, yaml_spec: Dict[str, Any]) -> None:
        """Validate YAML specification for layout safety"""
        scenes = yaml_spec.get('scenes', [])
        
        for scene in scenes:
            layout = scene.get('layout', {})
            elements = layout.get('elements', [])
            template = layout.get('template', 'single')
            
            # Validate elements against template capacity
            template_manager = get_template_manager()
            validation_errors = template_manager.validate_element_placement(template, elements)
            
            if validation_errors:
                print(f"WARN: Layout validation warnings for scene '{scene.get('id', 'unknown')}':")
                for error in validation_errors:
                    print(f"   - {error}")
            
            # Validate for overlaps
            layout_report = validate_layout_safety(elements)
            if layout_report['status'] == 'collisions_detected':
                print(f"WARN: Potential collisions detected in scene '{scene.get('id', 'unknown')}':")
                for collision in layout_report['detailed_collisions'][:3]:  # Show first 3
                    print(f"   - {collision['elements']}: {collision['resolution']}")
    
    def _generate_imports(self) -> str:
        """Generate import statements"""
        imports = [
            "from manim import *",
            "import numpy as np",
            "import math"
        ]
        
        if self.config.include_debug_helpers:
            imports.append("import warnings")
        
        return '\n'.join(imports)
    
    def _generate_helper_utilities(self, global_config: Dict[str, Any]) -> str:
        """Generate inline helper utilities for layout safety"""
        safe_margin = global_config.get('safe_margin_pct', self.config.safe_margin_pct)
        default_font_size = global_config.get('default_font_size', self.config.default_font_size)
        max_width_pct = global_config.get('max_width_pct', 0.92)
        
        template_name = global_config.get('grid', {}).get('template', 'single')
        
        # Get template-specific helpers
        template_helpers = get_template_helpers(template_name)
        
        utilities = f'''# Layout Safety Utilities
# Generated for safe margins: {safe_margin*100:.0f}%, max width: {max_width_pct*100:.0f}%

# Global configuration
SAFE_MARGIN = {safe_margin}
DEFAULT_FONT_SIZE = {default_font_size}
MAX_WIDTH_PCT = {max_width_pct}
BUFFER_DISTANCE = {self.config.buffer_distance}
MIN_FONT_SIZE = {self.config.min_font_size}

{template_helpers}

def ensure_text_legibility(text_obj, min_size=MIN_FONT_SIZE):
    """Ensure text is legible at 480p resolution"""
    if hasattr(text_obj, 'font_size') and text_obj.font_size < min_size:
        text_obj.font_size = min_size
    return text_obj

def safe_create_text(content, font_size=DEFAULT_FONT_SIZE, **kwargs):
    """Create text with automatic legibility enforcement"""
    actual_size = max(font_size, MIN_FONT_SIZE)
    return Text(content, font_size=actual_size, **kwargs)

def safe_create_mathtex(content, font_size=DEFAULT_FONT_SIZE, **kwargs):
    """Create MathTex with automatic legibility enforcement"""
    actual_size = max(font_size, MIN_FONT_SIZE)
    return MathTex(content, font_size=actual_size, **kwargs)

def auto_arrange_group(elements, direction=DOWN, buff=BUFFER_DISTANCE):
    """Arrange elements with safe spacing"""
    if len(elements) <= 1:
        return VGroup(*elements) if elements else VGroup()
    
    group = VGroup(*elements)
    group.arrange(direction, buff=max(buff, BUFFER_DISTANCE))
    
    # Scale to fit if too large
    safe_frame = get_safe_frame()
    max_width = safe_frame['right'] - safe_frame['left']
    max_height = safe_frame['top'] - safe_frame['bottom']
    
    if group.width > max_width:
        group.scale_to_fit_width(max_width * MAX_WIDTH_PCT)
    if group.height > max_height:
        group.scale_to_fit_height(max_height * MAX_WIDTH_PCT)
    
    return group

def fade_out_all_except(scene, keep_objects):
    """Fade out all objects except specified ones"""
    keep_set = set(keep_objects) if isinstance(keep_objects, (list, tuple)) else {{keep_objects}}
    to_fade = [obj for obj in scene.mobjects if obj not in keep_set]
    
    if to_fade:
        scene.play(*[FadeOut(obj) for obj in to_fade])

def clear_and_wait(scene, wait_time=0.5):
    """Clear scene and add wait time for clean transitions"""
    if scene.mobjects:
        scene.play(*[FadeOut(obj) for obj in scene.mobjects])
    scene.wait(wait_time)'''
        
        return utilities
    
    def _generate_scene_class(self, topic: str, scenes: List[Dict[str, Any]], 
                            global_config: Dict[str, Any]) -> str:
        """Generate the main Video scene class"""
        class_name = "Video"  # Fixed class name as required by Builder LLM
        
        # Generate scene methods for each scene
        scene_methods = []
        for i, scene in enumerate(scenes):
            method_name = f"scene_{scene.get('id', f'scene_{i}').replace('-', '_')}"
            method_code = self._generate_scene_method(scene, method_name)
            scene_methods.append(method_code)
        
        # Generate construct method that calls all scene methods
        construct_method = self._generate_construct_method(scenes)
        
        # Combine class definition
        scene_class = f'''class {class_name}(Scene):
    """Generated educational video scene"""
    
    def construct(self):
        """Main scene construction with deterministic layout"""
        # Set background color for 3Blue1Brown style
        self.camera.background_color = "#0c0c0c"
        
        # Fixed seed for determinism
        np.random.seed(42)
        
{construct_method}
    
{chr(10).join(scene_methods)}'''
        
        return scene_class
    
    def _generate_construct_method(self, scenes: List[Dict[str, Any]]) -> str:
        """Generate the main construct method"""
        lines = []
        total_time = 0.0
        
        for scene in scenes:
            scene_id = scene.get('id', 'unknown')
            time_budget = scene.get('time_budget_s', 10)
            method_name = f"scene_{scene_id.replace('-', '_')}"
            
            lines.extend([
                f"        # Scene: {scene.get('goal', scene_id)}",
                f"        self.{method_name}()",
                f"        self.wait(0.5)  # Transition pause",
                ""
            ])
            
            total_time += time_budget + 0.5
        
        lines.insert(0, f"        # Total estimated duration: {total_time:.1f}s")
        lines.insert(1, "")
        
        return '\n'.join(lines)
    
    def _generate_scene_method(self, scene: Dict[str, Any], method_name: str) -> str:
        """Generate individual scene method"""
        scene_id = scene.get('id', 'unknown')
        goal = scene.get('goal', 'Scene goal')
        time_budget = scene.get('time_budget_s', 10)
        layout = scene.get('layout', {})
        template = layout.get('template', 'single')
        elements = layout.get('elements', [])
        
        # Generate positioning for all elements
        positioned_elements = self.layout_manager.generate_safe_positioning(elements, template)
        
        # Generate element creation code
        element_creation_lines = []
        element_animation_lines = []
        element_cleanup_lines = []
        
        # Track elements by timing
        timeline_events = []
        
        for element in elements:
            element_key = element['key']
            element_type = element['type']
            
            # Get positioning information
            position_info = positioned_elements.get(element_key, {})
            
            # Generate creation code
            creation_code = self._generate_element_creation(element, position_info)
            element_creation_lines.append(creation_code)
            
            # Generate animation code
            enter_time = element.get('enter', {}).get('at', 0.0)
            exit_time = element.get('exit', {}).get('at', float('inf'))
            
            timeline_events.append((enter_time, 'enter', element_key, element))
            if exit_time != float('inf'):
                timeline_events.append((exit_time, 'exit', element_key, element))
        
        # Sort timeline events
        timeline_events.sort(key=lambda x: x[0])
        
        # Generate timeline-based animation code
        timeline_code = self._generate_timeline_animations(timeline_events, positioned_elements)
        
        # Combine method
        method_code = f'''    def {method_name}(self):
        """
        {goal}
        Duration: {time_budget}s, Template: {template}
        Elements: {len(elements)}
        """
        
        # Element creation
{chr(10).join(f"        {line}" for line in element_creation_lines)}
        
        # Timeline-based animations
{timeline_code}
        
        # Final cleanup
        clear_and_wait(self, 0.5)'''
        
        return method_code
    
    def _generate_element_creation(self, element: Dict[str, Any], 
                                 position_info: Dict[str, Any]) -> str:
        """Generate code to create a single element"""
        element_key = element['key']
        element_type = element['type']
        
        # Get content
        content = element.get('content', element.get('tex', ''))
        
        # Get style
        style = element.get('style', {})
        font_size = style.get('font_size', self.config.default_font_size)
        color = style.get('color', 'WHITE')
        
        # Generate creation based on type
        if element_type == 'Text':
            creation_line = f'{element_key} = safe_create_text("{content}", font_size={font_size}, color={color})'
        
        elif element_type == 'MathTex':
            # Escape LaTeX content for Python strings
            escaped_content = content.replace('\\', '\\\\').replace('"', '\\"')
            creation_line = f'{element_key} = safe_create_mathtex(r"{escaped_content}", font_size={font_size}, color={color})'
        
        elif element_type == 'AxesPlot':
            # Generate axes and plot
            fn_str = element.get('fn', 'lambda x: x**2')
            creation_line = f'''{element_key}_axes = Axes(x_range=[-3, 3], y_range=[-1, 5])
        {element_key}_plot = {element_key}_axes.plot({fn_str}, color={color})
        {element_key} = VGroup({element_key}_axes, {element_key}_plot)'''
        
        elif element_type == 'Table':
            # Simple table creation
            creation_line = f'{element_key} = Rectangle(width=4, height=2, color={color})  # Simplified table'
        
        elif element_type == 'Image':
            # Replace with placeholder (no external assets allowed)
            creation_line = f'{element_key} = Circle(radius=1, color={color})  # Image placeholder'
        
        else:
            # Default to text
            creation_line = f'{element_key} = safe_create_text("{content}", color={color})'
        
        # Add positioning
        position_code = position_info.get('safe_positioning', f'{element_key}.move_to(ORIGIN)')
        
        # Apply modifications if needed
        modifications = position_info.get('modifications', {})
        if modifications.get('shrunk', False):
            scale_factor = modifications.get('scale_factor', 0.95)
            creation_line += f'\n        {element_key} = scale_to_fit_pct({element_key}, max_width_pct={scale_factor})'
        
        return f'{creation_line}\n        {position_code}'
    
    def _generate_timeline_animations(self, timeline_events: List[Tuple], 
                                    positioned_elements: Dict[str, Dict[str, Any]]) -> str:
        """Generate timeline-based animation sequence"""
        if not timeline_events:
            return "        pass  # No animations"
        
        lines = []
        current_time = 0.0
        active_elements = set()
        
        for time, action, element_key, element in timeline_events:
            # Add wait if needed
            if time > current_time:
                wait_time = time - current_time
                if wait_time > 0.1:  # Only add significant waits
                    lines.append(f"        self.wait({wait_time:.1f})")
            
            if action == 'enter':
                # Get animation type
                enter_anim = element.get('enter', {})
                anim_type = enter_anim.get('anim', 'FadeIn')
                
                # Generate enter animation
                if anim_type == 'Write':
                    anim_code = f"Write({element_key})"
                elif anim_type == 'Create':
                    anim_code = f"Create({element_key})"
                elif anim_type == 'GrowFromCenter':
                    anim_code = f"GrowFromCenter({element_key})"
                else:
                    anim_code = f"FadeIn({element_key})"
                
                # Check for overlaps with active elements
                position_info = positioned_elements.get(element_key, {})
                modifications = position_info.get('modifications', {})
                
                if modifications.get('requires_fade_previous', False):
                    conflicting_elements = modifications.get('conflicting_elements', [])
                    if conflicting_elements and active_elements.intersection(conflicting_elements):
                        # Fade out conflicting elements first
                        to_fade = active_elements.intersection(conflicting_elements)
                        fade_animations = [f"FadeOut({elem})" for elem in to_fade]
                        lines.append(f"        self.play({', '.join(fade_animations)})")
                        active_elements -= to_fade
                
                lines.append(f"        self.play({anim_code})")
                active_elements.add(element_key)
                
            elif action == 'exit':
                if element_key in active_elements:
                    # Get animation type
                    exit_anim = element.get('exit', {})
                    anim_type = exit_anim.get('anim', 'FadeOut')
                    
                    if anim_type == 'ShrinkToCenter':
                        anim_code = f"ShrinkToCenter({element_key})"
                    else:
                        anim_code = f"FadeOut({element_key})"
                    
                    lines.append(f"        self.play({anim_code})")
                    active_elements.discard(element_key)
            
            current_time = time
        
        # Final cleanup of remaining elements
        if active_elements:
            remaining = list(active_elements)[:3]  # Limit to avoid too long lines
            fade_animations = [f"FadeOut({elem})" for elem in remaining]
            lines.append(f"        # Cleanup remaining elements")
            lines.append(f"        self.play({', '.join(fade_animations)})")
        
        return '\n'.join(lines) if lines else "        pass  # No timeline animations"


def create_manim_generator(config: Optional[CodeGenerationConfig] = None) -> ManimCodeGenerator:
    """Factory function for creating Manim code generator"""
    return ManimCodeGenerator(config)


def generate_code_from_yaml(yaml_spec: Dict[str, Any], 
                          config: Optional[CodeGenerationConfig] = None) -> str:
    """High-level function to generate code from YAML specification"""
    generator = create_manim_generator(config)
    return generator.generate_code(yaml_spec)