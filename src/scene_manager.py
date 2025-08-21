"""
Professional Scene Management System for Educational Videos

This module provides proper scene-based architecture for generating 
3Blue1Brown quality educational animations.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class SceneSection:
    """Represents one section of an educational video."""
    section_id: str
    title: str
    duration: float  # seconds
    start_time: float
    content_type: str  # 'hook', 'foundation', 'concept', 'example', 'application', 'summary'
    elements: List[Dict[str, Any]]
    visual_focus: str  # 'center', 'left', 'right', 'full'
    transition_type: str = "fade"  # 'fade', 'slide', 'morph'
    clear_previous: bool = True

class SceneManager:
    """Manages the creation and organization of educational video scenes."""
    
    def __init__(self):
        self.sections: List[SceneSection] = []
        self.total_duration = 0.0
        
    def create_10_minute_structure(self, topic: str, complexity: str = "intermediate") -> List[SceneSection]:
        """Create a 3Blue1Brown style 10-minute educational video structure."""
        
        sections = []
        
        # Hook Section (0:00-1:00) - Engage with a compelling question
        sections.append(SceneSection(
            section_id="hook",
            title=f"Why {topic} Matters",
            duration=60.0,
            start_time=0.0,
            content_type="hook",
            elements=self._generate_hook_elements(topic),
            visual_focus="center",
            transition_type="fade",
            clear_previous=True
        ))
        
        # Foundation Section (1:00-3:00) - Build prerequisites
        sections.append(SceneSection(
            section_id="foundation", 
            title="Essential Background",
            duration=120.0,
            start_time=60.0,
            content_type="foundation",
            elements=self._generate_foundation_elements(topic),
            visual_focus="center",
            transition_type="fade",
            clear_previous=True
        ))
        
        # Core Concept Section 1 (3:00-4:30)
        sections.append(SceneSection(
            section_id="concept_1",
            title=f"Understanding {topic} - Part 1", 
            duration=90.0,
            start_time=180.0,
            content_type="concept",
            elements=self._generate_concept_elements(topic, part=1),
            visual_focus="center",
            transition_type="fade",
            clear_previous=True
        ))
        
        # Core Concept Section 2 (4:30-6:00)
        sections.append(SceneSection(
            section_id="concept_2",
            title=f"Understanding {topic} - Part 2",
            duration=90.0, 
            start_time=270.0,
            content_type="concept",
            elements=self._generate_concept_elements(topic, part=2),
            visual_focus="center",
            transition_type="fade",
            clear_previous=True
        ))
        
        # Worked Examples (6:00-8:30)
        sections.append(SceneSection(
            section_id="examples",
            title="Solving Problems Step-by-Step",
            duration=150.0,
            start_time=360.0, 
            content_type="example",
            elements=self._generate_example_elements(topic),
            visual_focus="left",  # Leave room for work
            transition_type="fade",
            clear_previous=True
        ))
        
        # Applications (8:30-9:30) 
        sections.append(SceneSection(
            section_id="applications",
            title="Real-World Applications",
            duration=60.0,
            start_time=510.0,
            content_type="application", 
            elements=self._generate_application_elements(topic),
            visual_focus="center",
            transition_type="fade",
            clear_previous=True
        ))
        
        # Summary (9:30-10:00)
        sections.append(SceneSection(
            section_id="summary",
            title="Key Takeaways",
            duration=30.0,
            start_time=570.0,
            content_type="summary",
            elements=self._generate_summary_elements(topic),
            visual_focus="center",
            transition_type="fade", 
            clear_previous=True
        ))
        
        self.sections = sections
        self.total_duration = 600.0  # 10 minutes
        return sections
    
    def _generate_hook_elements(self, topic: str) -> List[Dict[str, Any]]:
        """Generate engaging hook elements based on topic."""
        elements = []
        
        if "derivative" in topic.lower():
            elements = [
                {
                    "type": "text",
                    "content": "What if I told you calculus can predict the future?",
                    "position": "center",
                    "style": {"font_size": 48, "color": "#FFD166"},
                    "animation": {"type": "write", "duration": 3, "delay": 0}
                },
                {
                    "type": "graph",
                    "content": "position vs time curve with tangent line",
                    "position": "center",
                    "style": {"color": "#58C4DD"},
                    "animation": {"type": "create", "duration": 4, "delay": 3}
                }
            ]
        elif "integral" in topic.lower():
            elements = [
                {
                    "type": "text", 
                    "content": "How do you find the area of any shape?",
                    "position": "center",
                    "style": {"font_size": 48, "color": "#FFD166"},
                    "animation": {"type": "write", "duration": 3, "delay": 0}
                }
            ]
        elif "differential" in topic.lower():
            elements = [
                {
                    "type": "text",
                    "content": "The equations that describe our universe",
                    "position": "center", 
                    "style": {"font_size": 48, "color": "#FFD166"},
                    "animation": {"type": "write", "duration": 3, "delay": 0}
                }
            ]
        else:
            # Generic hook
            elements = [
                {
                    "type": "text",
                    "content": f"Let's explore {topic} from the ground up",
                    "position": "center",
                    "style": {"font_size": 48, "color": "#FFD166"}, 
                    "animation": {"type": "write", "duration": 3, "delay": 0}
                }
            ]
            
        return elements
    
    def _generate_foundation_elements(self, topic: str) -> List[Dict[str, Any]]:
        """Generate foundation/prerequisite elements."""
        return [
            {
                "type": "text",
                "content": "First, let's review what you need to know",
                "position": "top",
                "style": {"font_size": 36, "color": "#ECECF1"},
                "animation": {"type": "write", "duration": 2, "delay": 0}
            }
        ]
    
    def _generate_concept_elements(self, topic: str, part: int) -> List[Dict[str, Any]]:
        """Generate core concept elements."""
        return [
            {
                "type": "text", 
                "content": f"Core Concept {part}",
                "position": "top",
                "style": {"font_size": 42, "color": "#58C4DD"},
                "animation": {"type": "write", "duration": 2, "delay": 0}
            }
        ]
    
    def _generate_example_elements(self, topic: str) -> List[Dict[str, Any]]:
        """Generate worked example elements."""
        return [
            {
                "type": "text",
                "content": "Let's solve a real problem",
                "position": "top",
                "style": {"font_size": 36, "color": "#FF6B6B"},
                "animation": {"type": "write", "duration": 2, "delay": 0}
            }
        ]
    
    def _generate_application_elements(self, topic: str) -> List[Dict[str, Any]]:
        """Generate real-world application elements.""" 
        return [
            {
                "type": "text",
                "content": "Where you'll use this in real life",
                "position": "center", 
                "style": {"font_size": 36, "color": "#FFD166"},
                "animation": {"type": "write", "duration": 2, "delay": 0}
            }
        ]
    
    def _generate_summary_elements(self, topic: str) -> List[Dict[str, Any]]:
        """Generate summary elements."""
        return [
            {
                "type": "text",
                "content": "Key takeaways you should remember",
                "position": "center",
                "style": {"font_size": 36, "color": "#58C4DD"},
                "animation": {"type": "write", "duration": 2, "delay": 0}
            }
        ]
    
    def generate_manim_code(self, sections: List[SceneSection]) -> str:
        """Generate properly structured Manim code from sections."""
        
        code_parts = [
            "from manim import *",
            "",
            "class EducationalScene(Scene):",
            "    def construct(self):",
            "        # 3Blue1Brown style background",
            "        self.camera.background_color = \"#0c0c0c\"",
            "",
            "        # Define safe positioning constants",
            "        SAFE_TOP = UP * 2.5",
            "        SAFE_CENTER = ORIGIN", 
            "        SAFE_BOTTOM = DOWN * 2.5",
            "        SAFE_LEFT = LEFT * 4.5",
            "        SAFE_RIGHT = RIGHT * 4.5",
            "",
            "        # 3Blue1Brown colors",
            "        PRIMARY = \"#58C4DD\"  # Blue",
            "        SECONDARY = \"#FFD166\"  # Yellow", 
            "        ACCENT = \"#FF6B6B\"  # Red",
            "        TEXT_COLOR = \"#ECECF1\"  # Off-white",
            ""
        ]
        
        for i, section in enumerate(sections):
            code_parts.extend(self._generate_section_code(section, i))
            
        return "\n".join(code_parts)
    
    def _generate_section_code(self, section: SceneSection, section_num: int) -> List[str]:
        """Generate Manim code for one section."""
        
        code_lines = [
            f"        # Section {section_num + 1}: {section.title}",
            f"        # Duration: {section.duration}s | Type: {section.content_type}",
        ]
        
        # Clear previous content if needed
        if section.clear_previous and section_num > 0:
            code_lines.extend([
                "        # Clear previous section",
                "        if len(self.mobjects) > 0:",
                "            self.play(FadeOut(*self.mobjects), run_time=1)",
                "            self.wait(0.5)",
            ])
        
        # Generate elements for this section
        for element in section.elements:
            element_code = self._generate_element_code(element, section.visual_focus)
            code_lines.extend(element_code)
            
        # Section pause
        code_lines.extend([
            f"        self.wait({min(3.0, section.duration / 4)})",
            ""
        ])
        
        return code_lines
    
    def _generate_element_code(self, element: Dict[str, Any], focus: str) -> List[str]:
        """Generate Manim code for one element."""
        
        element_type = element.get("type", "text")
        content = element.get("content", "")
        position = element.get("position", "center")
        style = element.get("style", {})
        animation = element.get("animation", {})
        
        # Safe text wrapping
        if element_type == "text" and len(content) > 60:
            content = self._wrap_text(content, max_chars=50)
        
        var_name = f"element_{hash(content) % 1000}"
        code_lines = []
        
        # Create the object
        if element_type == "text":
            font_size = style.get("font_size", 36)
            color = style.get("color", "WHITE")
            code_lines.append(f'        {var_name} = Text("{content}", font_size={font_size}, color="{color}")')
            
        elif element_type == "formula":
            font_size = style.get("font_size", 42)
            color = style.get("color", "WHITE")
            code_lines.append(f'        {var_name} = MathTex(r"{content}", font_size={font_size}, color="{color}")')
            
        elif element_type == "graph":
            # Enhanced graph generation based on content
            if "position vs time" in content.lower():
                code_lines.extend([
                    f"        axes = Axes(x_range=[0, 5], y_range=[0, 25], x_length=6, y_length=4)",
                    f"        axes.add_coordinate_labels()",
                    f"        position_func = axes.plot(lambda t: 0.5*t**2 + 2*t + 1, color=PRIMARY)",
                    f"        # Add tangent line at t=2",
                    f"        tangent_point = axes.coords_to_point(2, 0.5*4 + 2*2 + 1)",
                    f"        tangent_slope = 2 + 2*2  # derivative at t=2",
                    f"        tangent_line = axes.plot(lambda t: tangent_slope*(t-2) + 9, x_range=[1, 3], color=ACCENT)",
                    f"        graph_label = axes.get_graph_label(position_func, 'x(t)', x_val=4)",
                    f"        {var_name} = VGroup(axes, position_func, tangent_line, graph_label)"
                ])
            elif "area under curve" in content.lower():
                code_lines.extend([
                    f"        axes = Axes(x_range=[0, 3], y_range=[0, 9], x_length=6, y_length=4)",
                    f"        func = axes.plot(lambda x: x**2, color=PRIMARY)",
                    f"        area = axes.get_area(func, x_range=[0, 2], color=SECONDARY, opacity=0.3)",
                    f"        graph_label = axes.get_graph_label(func, 'f(x) = x^2', x_val=2.5)",
                    f"        {var_name} = VGroup(axes, func, area, graph_label)"
                ])
            else:
                # Default mathematical function
                code_lines.extend([
                    f"        axes = Axes(x_range=[-3, 3], y_range=[-2, 8], x_length=6, y_length=4)",
                    f"        {var_name} = axes.plot(lambda x: x**2, color=PRIMARY)",
                    f"        graph_group = VGroup(axes, {var_name})"
                ])
                var_name = "graph_group"
        
        # Position the object safely
        position_code = self._get_position_code(position, focus)
        if position_code:
            code_lines.append(f"        {var_name}.{position_code}")
        
        # Animate the object
        anim_type = animation.get("type", "write")
        duration = animation.get("duration", 2)
        delay = animation.get("delay", 0)
        
        if delay > 0:
            code_lines.append(f"        self.wait({delay})")
            
        if anim_type == "write":
            code_lines.append(f"        self.play(Write({var_name}), run_time={duration})")
        elif anim_type == "create":
            code_lines.append(f"        self.play(Create({var_name}), run_time={duration})")
        elif anim_type == "fade_in":
            code_lines.append(f"        self.play(FadeIn({var_name}), run_time={duration})")
        
        return code_lines
    
    def _wrap_text(self, text: str, max_chars: int = 50) -> str:
        """Wrap long text to prevent off-screen issues."""
        if len(text) <= max_chars:
            return text
            
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    # Word is too long, truncate it
                    lines.append(word[:max_chars-3] + "...")
                    current_line = []
                    current_length = 0
        
        if current_line:
            lines.append(" ".join(current_line))
            
        return "\\n".join(lines[:3])  # Maximum 3 lines
    
    def _get_position_code(self, position: str, focus: str) -> str:
        """Get safe positioning code."""
        position_map = {
            "top": "move_to(SAFE_TOP)",
            "center": "move_to(SAFE_CENTER)", 
            "bottom": "move_to(SAFE_BOTTOM)",
            "left": "move_to(SAFE_LEFT)",
            "right": "move_to(SAFE_RIGHT)"
        }
        
        return position_map.get(position, "move_to(SAFE_CENTER)")