"""
Helper Utilities for Generated Manim Code

This module contains reusable utility functions that get embedded inline
in generated Manim code to ensure layout safety and proper functioning.
"""

from typing import Dict, Any, List, Tuple, Optional


def generate_safe_frame_utilities() -> str:
    """Generate safe frame utility functions"""
    return '''def get_safe_frame():
    """Get safe frame boundaries accounting for margins"""
    fw = config.frame_width
    fh = config.frame_height
    margin_x = fw * SAFE_MARGIN
    margin_y = fh * SAFE_MARGIN
    return {
        'left': -fw/2 + margin_x,
        'right': fw/2 - margin_x,
        'top': fh/2 - margin_y,
        'bottom': -fh/2 + margin_y,
        'width': fw - 2*margin_x,
        'height': fh - 2*margin_y
    }

def check_bounds(mobject, safe_frame=None):
    """Check if mobject is within safe bounds"""
    if safe_frame is None:
        safe_frame = get_safe_frame()
    
    bbox = mobject.get_bounding_box_point
    
    # Get bounding points
    try:
        left_bound = bbox(LEFT)[0]
        right_bound = bbox(RIGHT)[0]
        top_bound = bbox(UP)[1]
        bottom_bound = bbox(DOWN)[1]
        
        return (
            left_bound >= safe_frame['left'] and
            right_bound <= safe_frame['right'] and
            bottom_bound >= safe_frame['bottom'] and
            top_bound <= safe_frame['top']
        )
    except:
        # Fallback for objects without proper bounding box
        return True

def enforce_safe_bounds(mobject, safe_frame=None):
    """Ensure mobject stays within safe bounds by scaling if necessary"""
    if safe_frame is None:
        safe_frame = get_safe_frame()
    
    try:
        current_width = mobject.width
        current_height = mobject.height
        
        max_width = safe_frame['width'] * MAX_WIDTH_PCT
        max_height = safe_frame['height'] * MAX_WIDTH_PCT
        
        # Calculate required scaling
        width_scale = max_width / current_width if current_width > max_width else 1.0
        height_scale = max_height / current_height if current_height > max_height else 1.0
        
        # Use the more restrictive scaling factor
        scale_factor = min(width_scale, height_scale, 1.0)
        
        if scale_factor < 1.0:
            mobject.scale(scale_factor)
            
    except Exception as e:
        # Graceful degradation
        warnings.warn(f"Could not enforce bounds for object: {e}")
    
    return mobject'''


def generate_collision_detection_utilities() -> str:
    """Generate collision detection utility functions"""
    return '''def get_bounding_box(mobject):
    """Get normalized bounding box for collision detection"""
    try:
        # Use Manim's bounding box methods
        left = mobject.get_bounding_box_point(LEFT)[0]
        right = mobject.get_bounding_box_point(RIGHT)[0] 
        bottom = mobject.get_bounding_box_point(DOWN)[1]
        top = mobject.get_bounding_box_point(UP)[1]
        
        return {
            'left': left,
            'right': right,
            'top': top,
            'bottom': bottom,
            'width': right - left,
            'height': top - bottom,
            'center_x': (left + right) / 2,
            'center_y': (top + bottom) / 2
        }
    except:
        # Fallback for problematic objects
        return {
            'left': -0.5, 'right': 0.5, 'top': 0.5, 'bottom': -0.5,
            'width': 1.0, 'height': 1.0, 'center_x': 0.0, 'center_y': 0.0
        }

def check_overlap(obj1, obj2, buffer=BUFFER_DISTANCE):
    """Check if two objects overlap with buffer consideration"""
    try:
        box1 = get_bounding_box(obj1)
        box2 = get_bounding_box(obj2)
        
        # Expand first box by buffer
        box1_expanded = {
            'left': box1['left'] - buffer,
            'right': box1['right'] + buffer,
            'top': box1['top'] + buffer,
            'bottom': box1['bottom'] - buffer
        }
        
        # Check for intersection
        overlap = not (
            box1_expanded['right'] < box2['left'] or
            box1_expanded['left'] > box2['right'] or
            box1_expanded['top'] < box2['bottom'] or
            box1_expanded['bottom'] > box2['top']
        )
        
        return overlap
    except:
        # Conservative approach: assume overlap if detection fails
        return True

def resolve_overlap(primary_obj, conflicting_objs, strategy="shrink"):
    """Resolve overlap using specified strategy"""
    if strategy == "shrink":
        # Scale down the primary object
        scale_factor = 0.9
        primary_obj.scale(scale_factor)
        
    elif strategy == "shift":
        # Try shifting primary object
        shift_distance = BUFFER_DISTANCE * 2
        # Simple strategy: shift down
        primary_obj.shift(DOWN * shift_distance)
        
    elif strategy == "reposition":
        # Move to a safe position (fallback to center-right)
        safe_frame = get_safe_frame()
        safe_x = safe_frame['right'] - safe_frame['width'] * 0.25
        safe_y = 0  # Center vertically
        primary_obj.move_to(np.array([safe_x, safe_y, 0]))
    
    return primary_obj'''


def generate_text_utilities() -> str:
    """Generate text handling utilities"""
    return '''def create_safe_text(content, max_width=None, **kwargs):
    """Create text that respects safe area constraints"""
    # Set minimum font size
    font_size = kwargs.get('font_size', DEFAULT_FONT_SIZE)
    font_size = max(font_size, MIN_FONT_SIZE)
    kwargs['font_size'] = font_size
    
    # Create text object
    text_obj = Text(str(content), **kwargs)
    
    # Apply width constraint if specified
    if max_width:
        if text_obj.width > max_width:
            scale_factor = max_width / text_obj.width
            text_obj.scale(scale_factor)
            # Ensure font size doesn't go below minimum
            if font_size * scale_factor < MIN_FONT_SIZE:
                text_obj.scale(MIN_FONT_SIZE / (font_size * scale_factor))
    
    return ensure_text_legibility(text_obj)

def create_wrapped_text(content, max_chars_per_line=40, **kwargs):
    """Create text with automatic line wrapping"""
    lines = []
    words = str(content).split()
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= max_chars_per_line:
            current_line += (" " + word) if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Create text objects for each line
    text_objects = []
    for line in lines[:3]:  # Limit to 3 lines max
        line_obj = create_safe_text(line, **kwargs)
        text_objects.append(line_obj)
    
    if not text_objects:
        return create_safe_text(content, **kwargs)
    
    # Arrange vertically
    wrapped_text = VGroup(*text_objects)
    wrapped_text.arrange(DOWN, buff=0.1)
    
    return wrapped_text

def create_safe_mathtex(content, **kwargs):
    """Create MathTex that respects safe area constraints"""
    font_size = kwargs.get('font_size', DEFAULT_FONT_SIZE)
    font_size = max(font_size, MIN_FONT_SIZE)
    kwargs['font_size'] = font_size
    
    # Clean up LaTeX content
    clean_content = str(content).strip()
    if not clean_content:
        clean_content = "x"  # Fallback
    
    try:
        tex_obj = MathTex(clean_content, **kwargs)
        return ensure_text_legibility(tex_obj)
    except:
        # Fallback to text if LaTeX fails
        return create_safe_text(clean_content, **kwargs)'''


def generate_animation_utilities() -> str:
    """Generate animation utility functions"""
    return '''def safe_play(*animations, run_time=2, rate_func=smooth):
    """Play animations with safe defaults"""
    # Filter out None animations
    valid_animations = [anim for anim in animations if anim is not None]
    
    if not valid_animations:
        return
    
    # Apply safe defaults
    for anim in valid_animations:
        if hasattr(anim, 'run_time') and not hasattr(anim, '_run_time_set'):
            anim.run_time = run_time
            anim._run_time_set = True
        if hasattr(anim, 'rate_func') and not hasattr(anim, '_rate_func_set'):
            anim.rate_func = rate_func
            anim._rate_func_set = True
    
    return valid_animations

def create_enter_animation(obj, anim_type="FadeIn", **kwargs):
    """Create entrance animation with safety checks"""
    if anim_type == "Write":
        return Write(obj, **kwargs)
    elif anim_type == "Create":
        return Create(obj, **kwargs)
    elif anim_type == "GrowFromCenter":
        return GrowFromCenter(obj, **kwargs)
    elif anim_type == "DrawBorderThenFill":
        return DrawBorderThenFill(obj, **kwargs)
    else:
        return FadeIn(obj, **kwargs)

def create_exit_animation(obj, anim_type="FadeOut", **kwargs):
    """Create exit animation with safety checks"""
    if anim_type == "ShrinkToCenter":
        return ShrinkToCenter(obj, **kwargs)
    elif anim_type == "Uncreate":
        return Uncreate(obj, **kwargs)
    else:
        return FadeOut(obj, **kwargs)

def safe_wait(scene, duration=1.0):
    """Safe wait with minimum duration"""
    min_wait = 0.1
    actual_duration = max(duration, min_wait)
    scene.wait(actual_duration)'''


def generate_positioning_utilities() -> str:
    """Generate positioning utility functions"""
    return '''def get_safe_position(position_name, offset=None):
    """Get safe position coordinates by name"""
    positions = {
        'center': ORIGIN,
        'top': UP * 2.5,
        'bottom': DOWN * 2.5,
        'left': LEFT * 4,
        'right': RIGHT * 4,
        'top_left': UP * 2.5 + LEFT * 4,
        'top_right': UP * 2.5 + RIGHT * 4,
        'bottom_left': DOWN * 2.5 + LEFT * 4,
        'bottom_right': DOWN * 2.5 + RIGHT * 4,
    }
    
    base_pos = positions.get(position_name, ORIGIN)
    
    if offset:
        if isinstance(offset, (list, tuple)) and len(offset) >= 2:
            base_pos += RIGHT * offset[0] + UP * offset[1]
        elif hasattr(offset, '__len__') and len(offset) == 3:
            base_pos += np.array(offset)
    
    return base_pos

def place_in_safe_position(obj, position_name, offset=None):
    """Place object in safe position and ensure it stays in bounds"""
    target_pos = get_safe_position(position_name, offset)
    obj.move_to(target_pos)
    
    # Ensure it stays within safe bounds
    enforce_safe_bounds(obj)
    
    return obj

def distribute_objects_safely(objects, container_width=None, container_height=None):
    """Distribute objects safely within container bounds"""
    if not objects:
        return VGroup()
    
    safe_frame = get_safe_frame()
    max_width = container_width or (safe_frame['width'] * MAX_WIDTH_PCT)
    max_height = container_height or (safe_frame['height'] * MAX_WIDTH_PCT)
    
    group = VGroup(*objects)
    
    # Try horizontal arrangement first
    group.arrange(RIGHT, buff=BUFFER_DISTANCE)
    
    if group.width <= max_width:
        # Horizontal arrangement fits
        pass
    else:
        # Try vertical arrangement
        group.arrange(DOWN, buff=BUFFER_DISTANCE)
        
        if group.height > max_height:
            # Scale down to fit
            scale_factor = min(max_width / group.width, max_height / group.height)
            group.scale(scale_factor)
    
    return group'''


def generate_debug_utilities() -> str:
    """Generate debugging utility functions"""
    return '''def show_safe_frame_debug(scene):
    """Show safe frame boundaries for debugging (only if debug enabled)"""
    if not hasattr(scene, '_debug_mode') or not scene._debug_mode:
        return
    
    safe_frame = get_safe_frame()
    
    # Create debug rectangles
    outer_rect = Rectangle(
        width=config.frame_width,
        height=config.frame_height,
        color=RED,
        stroke_width=1
    )
    
    inner_rect = Rectangle(
        width=safe_frame['width'],
        height=safe_frame['height'],
        color=GREEN,
        stroke_width=1
    )
    
    debug_group = VGroup(outer_rect, inner_rect)
    debug_group.set_fill(opacity=0)  # Transparent fill
    
    scene.add(debug_group)
    
    return debug_group

def log_element_info(obj, name="object"):
    """Log element information for debugging"""
    try:
        bbox = get_bounding_box(obj)
        print(f"DEBUG: {name} - Width: {bbox['width']:.2f}, Height: {bbox['height']:.2f}")
        print(f"       Position: ({bbox['center_x']:.2f}, {bbox['center_y']:.2f})")
        print(f"       Bounds: L{bbox['left']:.2f} R{bbox['right']:.2f} T{bbox['top']:.2f} B{bbox['bottom']:.2f}")
    except Exception as e:
        print(f"DEBUG: Could not analyze {name}: {e}")

def validate_scene_safety(scene):
    """Validate that all objects in scene follow safety rules"""
    issues = []
    safe_frame = get_safe_frame()
    
    for i, obj1 in enumerate(scene.mobjects):
        # Check bounds
        if not check_bounds(obj1, safe_frame):
            issues.append(f"Object {i} exceeds safe bounds")
        
        # Check overlaps with other objects  
        for j, obj2 in enumerate(scene.mobjects[i+1:], i+1):
            if check_overlap(obj1, obj2):
                issues.append(f"Objects {i} and {j} overlap")
    
    if issues:
        print("SAFETY VALIDATION ISSUES:")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"  - {issue}")
    else:
        print("OK: Scene passes safety validation")
    
    return len(issues) == 0'''


def get_all_utilities() -> str:
    """Get all utility functions as a single code block"""
    utilities = [
        generate_safe_frame_utilities(),
        generate_collision_detection_utilities(), 
        generate_text_utilities(),
        generate_animation_utilities(),
        generate_positioning_utilities(),
        generate_debug_utilities()
    ]
    
    return '\n\n'.join(utilities)