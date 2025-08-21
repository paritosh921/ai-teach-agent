from manim import *

# Injected Safety Utilities

# ========================================
# RUNTIME SAFETY GUARDS FOR MANIM
# Auto-generated safety utilities
# ========================================

import numpy as np
from typing import List, Any, Tuple, Optional

# Frame constants
FRAME_W = 14.0
FRAME_H = 8.0
SAFE_MARGIN = 0.35

def get_safe_boundaries() -> Tuple[float, float, float, float]:
    """Get safe area boundaries (left, right, top, bottom)"""
    left = -FRAME_W / 2 + SAFE_MARGIN
    right = FRAME_W / 2 - SAFE_MARGIN
    top = FRAME_H / 2 - SAFE_MARGIN
    bottom = -FRAME_H / 2 + SAFE_MARGIN
    return left, right, top, bottom

def safe_position(mobject: Any, position: Any) -> Any:
    """
    Safely position a mobject within frame boundaries
    
    Args:
        mobject: Manim mobject to position
        position: Target position (vector or coordinates)
        
    Returns:
        The positioned mobject
    """
    if not hasattr(mobject, 'move_to'):
        return mobject
    
    # Convert position to numpy array if needed
    if isinstance(position, (list, tuple)):
        pos = np.array([position[0], position[1], 0])
    else:
        pos = position
    
    # Get safe boundaries
    left, right, top, bottom = get_safe_boundaries()
    
    # Calculate element bounds at target position
    if hasattr(mobject, 'width') and hasattr(mobject, 'height'):
        half_width = mobject.width / 2
        half_height = mobject.height / 2
        
        # Adjust position if element would go out of bounds
        x, y = pos[0], pos[1]
        
        # Check and adjust X coordinate
        if x - half_width < left:
            x = left + half_width
        elif x + half_width > right:
            x = right - half_width
        
        # Check and adjust Y coordinate  
        if y - half_height < bottom:
            y = bottom + half_height
        elif y + half_height > top:
            y = top - half_height
        
        # Apply safe position
        pos = np.array([x, y, pos[2] if len(pos) > 2 else 0])
    
    mobject.move_to(safe_position(pos))
    return mobject

def scale_to_fit_safe(mobject: Any, max_width_pct: float = 0.92, max_height_pct: float = 0.92) -> Any:
    """
    Scale mobject to fit within safe area
    
    Args:
        mobject: Manim mobject to scale
        max_width_pct: Maximum width as percentage of safe area
        max_height_pct: Maximum height as percentage of safe area
        
    Returns:
        The scaled mobject
    """
    if not hasattr(mobject, 'scale') or not hasattr(mobject, 'width') or not hasattr(mobject, 'height'):
        return mobject
    
    left, right, top, bottom = get_safe_boundaries()
    safe_width = right - left
    safe_height = top - bottom
    
    max_allowed_width = safe_width * max_width_pct
    max_allowed_height = safe_height * max_height_pct
    
    # Calculate scale factors
    width_scale = max_allowed_width / mobject.width if mobject.width > max_allowed_width else 1.0
    height_scale = max_allowed_height / mobject.height if mobject.height > max_allowed_height else 1.0
    
    # Use more restrictive scale factor
    scale_factor = min(width_scale, height_scale, 1.0)  # Never enlarge
    
    if scale_factor < 1.0:
        mobject.scale(scale_factor)
    
    return mobject

def safe_arrange(mobjects: List[Any], direction: Any, buff: float = 0.5, center: bool = True) -> Any:
    """
    Safely arrange mobjects with automatic scaling and positioning
    
    Args:
        mobjects: List of mobjects to arrange
        direction: Manim direction constant (UP, DOWN, LEFT, RIGHT)
        buff: Buffer between mobjects
        center: Whether to center the group
        
    Returns:
        VGroup of arranged mobjects
    """
    if not mobjects:
        return None
        
    from manim import VGroup
    
    # First ensure all mobjects fit individually
    for mob in mobjects:
        scale_to_fit_safe(mob, 0.85, 0.85)  # Leave room for spacing
    
    # Create group and arrange
    group = VGroup(*mobjects)
    group.arrange(direction, buff=buff)
    
    if center:
        group.move_to(safe_position(ORIGIN))
    
    # Scale group down if it exceeds boundaries
    scale_to_fit_safe(group, 0.95, 0.95)
    
    # Ensure final position is safe
    if center:
        safe_position(group, ORIGIN)
    
    return group

def check_overlap(mob1: Any, mob2: Any, buffer: float = 0.1) -> bool:
    """
    Check if two mobjects overlap
    
    Args:
        mob1, mob2: Mobjects to check
        buffer: Minimum buffer distance
        
    Returns:
        True if mobjects overlap (including buffer zone)
    """
    if not all(hasattr(mob, attr) for mob in [mob1, mob2] for attr in ['get_center', 'width', 'height']):
        return False
    
    center1 = mob1.get_center()[:2]
    center2 = mob2.get_center()[:2]
    
    half_w1, half_h1 = mob1.width / 2, mob1.height / 2
    half_w2, half_h2 = mob2.width / 2, mob2.height / 2
    
    # Calculate bounding boxes with buffer
    x1_min, x1_max = center1[0] - half_w1 - buffer, center1[0] + half_w1 + buffer
    y1_min, y1_max = center1[1] - half_h1 - buffer, center1[1] + half_h1 + buffer
    
    x2_min, x2_max = center2[0] - half_w2, center2[0] + half_w2
    y2_min, y2_max = center2[1] - half_h2, center2[1] + half_h2
    
    # Check for overlap
    return not (x1_max < x2_min or x1_min > x2_max or y1_max < y2_min or y1_min > y2_max)

def resolve_overlap(mobjects: List[Any], min_spacing: float = 0.3) -> List[Any]:
    """
    Automatically resolve overlaps between mobjects
    
    Args:
        mobjects: List of mobjects to check and fix
        min_spacing: Minimum spacing between mobjects
        
    Returns:
        List of repositioned mobjects
    """
    if len(mobjects) < 2:
        return mobjects
    
    # Check for overlaps and resolve
    for i in range(len(mobjects)):
        for j in range(i + 1, len(mobjects)):
            if check_overlap(mobjects[i], mobjects[j], min_spacing):
                # Move second mobject to avoid overlap
                mob1_center = mobjects[i].get_center()
                mob2_center = mobjects[j].get_center()
                
                # Calculate direction to move mob2
                dx = mob2_center[0] - mob1_center[0]
                dy = mob2_center[1] - mob1_center[1]
                
                # If objects are at same position, move in default direction
                if abs(dx) < 0.1 and abs(dy) < 0.1:
                    dx, dy = 1.0, 0.0
                
                # Normalize direction
                length = np.sqrt(dx*dx + dy*dy)
                if length > 0:
                    dx, dy = dx/length, dy/length
                
                # Calculate minimum distance needed
                required_distance = (mobjects[i].width + mobjects[j].width) / 2 + min_spacing
                
                # Move mob2 to safe distance
                new_pos = np.array([
                    mob1_center[0] + dx * required_distance,
                    mob1_center[1] + dy * required_distance,
                    mob2_center[2]
                ])
                
                safe_position(mobjects[j], new_pos)
    
    return mobjects

def ensure_text_legible(text_mob: Any, min_font_size: int = 24) -> Any:
    """
    Ensure text mobject has legible font size
    
    Args:
        text_mob: Text mobject to check
        min_font_size: Minimum legible font size
        
    Returns:
        The text mobject (potentially scaled)
    """
    if hasattr(text_mob, 'font_size'):
        if text_mob.font_size < min_font_size:
            scale_factor = min_font_size / text_mob.font_size
            if hasattr(text_mob, 'scale'):
                text_mob.scale(scale_factor)
    
    return text_mob

def safe_next_to(mobject: Any, reference: Any, direction: Any, buff: float = 0.5) -> Any:
    """
    Safely position mobject next to reference with bounds checking
    
    Args:
        mobject: Mobject to position
        reference: Reference mobject
        direction: Direction to place mobject (UP, DOWN, LEFT, RIGHT)
        buff: Buffer distance
        
    Returns:
        The positioned mobject
    """
    if not hasattr(mobject, 'next_to'):
        return mobject
    
    # Use standard next_to first
    mobject.next_to(reference, direction, buff=buff)
    
    # Then ensure it stays in bounds
    safe_position(mobject, mobject.get_center())
    
    # Check for overlap and resolve if needed
    if check_overlap(mobject, reference, buff * 0.5):
        # If still overlapping, increase distance
        mobject.next_to(reference, direction, buff=buff * 2)
        safe_position(mobject, mobject.get_center())
    
    return mobject

def create_safe_scene_elements(elements_data: List[dict], scene_instance: Any) -> List[Any]:
    """
    Create scene elements with automatic safety checks
    
    Args:
        elements_data: List of element specifications
        scene_instance: The Scene instance for creating mobjects
        
    Returns:
        List of safely created and positioned mobjects
    """
    from manim import Text, MathTex, Rectangle, Circle, FunctionGraph, Axes
    
    created_mobjects = []
    
    for element in elements_data:
        element_type = element.get('type', 'text')
        content = element.get('content', 'Sample')
        
        # Create mobject based on type
        if element_type == 'text':
            mob = Text(content, font_size=element.get('font_size', 36))
        elif element_type == 'math':
            mob = MathTex(content, font_size=element.get('font_size', 36))
        elif element_type == 'rectangle':
            mob = Rectangle(width=2, height=1, color=WHITE)
        elif element_type == 'circle':
            mob = Circle(radius=1, color=WHITE)
        else:
            mob = Text(f"Unknown type: {element_type}", font_size=24)
        
        # Apply safety measures
        scale_to_fit_safe(mob)
        ensure_text_legible(mob)
        
        # Position safely
        position = element.get('position', [0, 0, 0])
        safe_position(mob, position)
        
        created_mobjects.append(mob)
    
    # Resolve any overlaps
    resolve_overlap(created_mobjects)
    
    return created_mobjects

# Helper constants for common safe positions
SAFE_TOP = np.array([0, FRAME_H/2 - SAFE_MARGIN - 1, 0])
SAFE_BOTTOM = np.array([0, -FRAME_H/2 + SAFE_MARGIN + 1, 0])
SAFE_LEFT = np.array([-FRAME_W/2 + SAFE_MARGIN + 2, 0, 0])
SAFE_RIGHT = np.array([FRAME_W/2 - SAFE_MARGIN - 2, 0, 0])
SAFE_CENTER = np.array([0, 0, 0])

# ========================================
# END RUNTIME SAFETY GUARDS
# ========================================



class SafeScene(Scene):
    """
    Scene wrapper with built-in layout safety features
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_mobjects_registry = []
        self.safety_enabled = True
        
    def safe_add(self, *mobjects: Any) -> None:
        """Add mobjects with safety checks"""
        if not self.safety_enabled:
            self.add(*mobjects)
            return
            
        safe_mobjects = []
        for mob in mobjects:
            # Apply safety transformations
            scale_to_fit_safe(mob)
            safe_position(mob, mob.get_center())
            safe_mobjects.append(mob)
        
        # Resolve overlaps with existing mobjects
        all_mobjects = self.active_mobjects_registry + safe_mobjects
        resolved_mobjects = resolve_overlap(all_mobjects)
        
        # Update registry
        self.active_mobjects_registry.extend(safe_mobjects)
        
        # Add to scene
        self.add(*safe_mobjects)
    
    def safe_play(self, *animations: Any, **kwargs) -> None:
        """Play animations with post-animation safety checks"""
        # Run the animations
        self.play(*animations, **kwargs)
        
        if self.safety_enabled:
            # Check all mobjects are still in bounds after animation
            for mob in self.mobjects:
                if hasattr(mob, 'get_center') and hasattr(mob, 'move_to'):
                    current_pos = mob.get_center()
                    safe_pos = current_pos.copy()
                    
                    left, right, top, bottom = get_safe_boundaries()
                    
                    # Adjust position if out of bounds
                    if hasattr(mob, 'width') and hasattr(mob, 'height'):
                        half_w, half_h = mob.width / 2, mob.height / 2
                        
                        if current_pos[0] - half_w < left:
                            safe_pos[0] = left + half_w
                        elif current_pos[0] + half_w > right:
                            safe_pos[0] = right - half_w
                            
                        if current_pos[1] - half_h < bottom:
                            safe_pos[1] = bottom + half_h
                        elif current_pos[1] + half_h > top:
                            safe_pos[1] = top - half_h
                        
                        if not np.allclose(current_pos, safe_pos, atol=0.1):
                            mob.move_to(safe_position(safe_pos))
    
    def clear_registry(self) -> None:
        """Clear the active mobjects registry"""
        self.active_mobjects_registry.clear()
    
    def disable_safety(self) -> None:
        """Temporarily disable safety checks"""
        self.safety_enabled = False
        
    def enable_safety(self) -> None:
        """Re-enable safety checks"""  
        self.safety_enabled = True



from functools import wraps

def safe_animation(func):
    """
    Decorator to add safety checks to animation methods
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Pre-animation safety checks
        for mob in args:
            if hasattr(mob, 'get_center'):
                scale_to_fit_safe(mob)
                safe_position(mob, mob.get_center())
        
        # Run the original function
        result = func(self, *args, **kwargs)
        
        # Post-animation validation
        if hasattr(self, 'mobjects'):
            resolve_overlap(list(self.mobjects))
        
        return result
    return wrapper

def bounds_check(func):
    """
    Decorator to ensure mobjects stay within frame bounds
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Check bounds for any mobject in result
        if hasattr(result, 'get_center'):
            safe_position(result, result.get_center())
        elif isinstance(result, (list, tuple)):
            for item in result:
                if hasattr(item, 'get_center'):
                    safe_position(item, item.get_center())
        
        return result
    return wrapper

def no_overlap(min_spacing: float = 0.3):
    """
    Decorator to prevent overlapping mobjects
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            
            if hasattr(self, 'mobjects') and len(self.mobjects) > 1:
                resolve_overlap(list(self.mobjects), min_spacing)
            
            return result
        return wrapper
    return decorator


# End Safety Utilities

class EducationalScene(SafeScene):
    def construct(self):
        # Scene 1: Introduction
        title = Text("Understanding Limits", font_size=48)
        self.play(FadeIn(title))
        self.wait(10)
        self.play(FadeOut(title))
        # Scene 2: Function Example
        function = MathTex("f(x) = x^2")
        self.play(FadeIn(function))
        self.wait(10)
        self.play(FadeOut(function))
        # Scene 3: Mathematical Development
        limit = MathTex("\\lim_{x\\to2} x^2 = 4")
        self.play(FadeIn(limit))
        self.wait(10)
        self.play(FadeOut(limit))
        # Scene 4: Visual Demonstration
        axes = Axes((-3, 3, 1), (-1, 9, 1))
        graph = axes.plot(lambda x: x**2, color=BLUE)
        self.play(FadeIn(axes), FadeIn(graph))
        self.wait(10)
        self.play(FadeOut(axes), FadeOut(graph))
        # Scene 5: Key Insights
        insight = Text("What value does f(x) get arbitrarily close to as x gets arbitrarily close to some number a?")
        self.play(FadeIn(insight))
        self.wait(5)
        self.play(FadeOut(insight))