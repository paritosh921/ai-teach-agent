"""
Auto Positioning Utilities

This module provides intelligent positioning utilities that automatically
arrange elements to prevent overlaps and ensure professional layouts.
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Union
from .frame_bounds import (
    get_safe_bounds, 
    fit_to_frame, 
    get_element_bounds, 
    in_frame,
    DEFAULT_MARGIN
)


def get_overlap_amount(element1: Any, element2: Any, buffer: float = 0.2) -> float:
    """
    Calculate the amount of overlap between two elements
    
    Args:
        element1, element2: Manim mobjects
        buffer: Additional buffer space
        
    Returns:
        Overlap area (0.0 if no overlap)
    """
    x1_min, y1_min, x1_max, y1_max = get_element_bounds(element1)
    x2_min, y2_min, x2_max, y2_max = get_element_bounds(element2)
    
    # Add buffer to first element
    x1_min -= buffer
    y1_min -= buffer
    x1_max += buffer
    y1_max += buffer
    
    # Calculate intersection
    x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
    y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
    
    return x_overlap * y_overlap


def elements_overlap(element1: Any, element2: Any, buffer: float = 0.2) -> bool:
    """
    Check if two elements overlap with buffer zone
    
    Args:
        element1, element2: Manim mobjects to check
        buffer: Buffer distance between elements
        
    Returns:
        True if elements overlap (including buffer zone)
    """
    return get_overlap_amount(element1, element2, buffer) > 0


def arrange_and_fit(elements: List[Any], 
                   direction: Any = None,  # Manim direction constant
                   buff: float = 0.5,
                   margin: float = DEFAULT_MARGIN,
                   max_per_row: int = 3) -> Any:
    """
    Arrange elements in a group and fit to frame
    
    Args:
        elements: List of Manim mobjects
        direction: Manim direction (DOWN, RIGHT, etc.)
        buff: Buffer between elements
        margin: Safe margin from edges
        max_per_row: Maximum elements per row before wrapping
        
    Returns:
        VGroup containing arranged elements
    """
    if not elements:
        return None
    
    # Import here to avoid circular imports
    try:
        from manim import VGroup, DOWN, RIGHT
        if direction is None:
            direction = DOWN
    except ImportError:
        # Fallback if manim not available
        return elements[0] if elements else None
    
    # First, ensure all elements fit individually
    for element in elements:
        fit_to_frame(element, margin)
    
    # Create arrangement
    if len(elements) <= max_per_row:
        # Simple linear arrangement
        group = VGroup(*elements).arrange(direction, buff=buff, center=True)
    else:
        # Grid arrangement for many elements
        rows = (len(elements) + max_per_row - 1) // max_per_row
        cols = min(len(elements), max_per_row)
        group = VGroup(*elements).arrange_in_grid(rows=rows, cols=cols, buff=buff)
    
    # Move to center and fit to frame
    group.move_to([0, 0, 0])  # ORIGIN equivalent
    fit_to_frame(group, margin)
    
    return group


def resolve_overlaps(elements: List[Any],
                    direction: Any = None,
                    buff: float = 0.5,
                    margin: float = DEFAULT_MARGIN,
                    max_attempts: int = 3) -> Any:
    """
    Resolve overlapping elements through repositioning and scaling
    
    Args:
        elements: List of potentially overlapping elements
        direction: Preferred arrangement direction
        buff: Buffer between elements
        margin: Safe margin from edges
        max_attempts: Maximum resolution attempts
        
    Returns:
        VGroup with resolved layout
    """
    if not elements:
        return None
    
    try:
        from manim import VGroup, DOWN
        if direction is None:
            direction = DOWN
    except ImportError:
        return elements[0] if elements else None
    
    # Attempt 1: Basic arrangement
    group = arrange_and_fit(elements, direction, buff, margin)
    
    # Check for overlaps
    overlaps_detected = False
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            if elements_overlap(elements[i], elements[j], buff * 0.5):
                overlaps_detected = True
                break
        if overlaps_detected:
            break
    
    if not overlaps_detected:
        return group
    
    # Attempt 2: Increase spacing
    if max_attempts > 1:
        group = arrange_and_fit(elements, direction, buff * 1.5, margin)
        
        # Check again
        overlaps_detected = False
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                if elements_overlap(elements[i], elements[j], buff * 0.5):
                    overlaps_detected = True
                    break
            if overlaps_detected:
                break
        
        if not overlaps_detected:
            return group
    
    # Attempt 3: Grid layout with scaling
    if max_attempts > 2:
        cols = 2 if len(elements) > 2 else 1
        rows = (len(elements) + cols - 1) // cols
        
        group = VGroup(*elements).arrange_in_grid(
            rows=rows, cols=cols, buff=buff
        ).move_to([0, 0, 0])
        
        fit_to_frame(group, margin)
    
    return group


def paginate_content(elements: List[Any], max_per_page: int = 3) -> List[List[Any]]:
    """
    Split elements into pages to avoid overcrowding
    
    Args:
        elements: List of elements to paginate
        max_per_page: Maximum elements per page
        
    Returns:
        List of element lists (pages)
    """
    if not elements:
        return []
    
    pages = []
    current_page = []
    
    for element in elements:
        current_page.append(element)
        
        if len(current_page) >= max_per_page:
            pages.append(current_page)
            current_page = []
    
    # Add remaining elements
    if current_page:
        pages.append(current_page)
    
    return pages


def safe_position(element: Any, 
                 position: Union[Tuple[float, float], Any],
                 margin: float = DEFAULT_MARGIN) -> Any:
    """
    Position element safely within frame bounds
    
    Args:
        element: Manim mobject to position
        position: Target position (tuple or Manim vector)
        margin: Safe margin from edges
        
    Returns:
        The positioned element
    """
    if not hasattr(element, 'move_to'):
        return element
    
    # Convert position to tuple if needed
    if hasattr(position, '__len__') and len(position) >= 2:
        if len(position) == 2:
            pos = (position[0], position[1])
        else:
            pos = (position[0], position[1])
    else:
        pos = (0.0, 0.0)  # Default to center
    
    # Ensure element fits first
    fit_to_frame(element, margin)
    
    # Calculate safe position
    from .frame_bounds import calculate_safe_position
    element_width = getattr(element, 'width', 2.0)
    element_height = getattr(element, 'height', 1.0)
    
    safe_pos = calculate_safe_position(pos, element_width, element_height, margin)
    
    # Move element to safe position
    if len(safe_pos) == 2:
        element.move_to([safe_pos[0], safe_pos[1], 0])
    else:
        element.move_to(safe_pos)
    
    return element


def distribute_elements(elements: List[Any],
                       region: str = 'center',
                       margin: float = DEFAULT_MARGIN) -> List[Any]:
    """
    Distribute elements within a screen region
    
    Args:
        elements: List of elements to distribute
        region: Target region ('top', 'center', 'bottom', 'left', 'right')
        margin: Safe margin from edges
        
    Returns:
        List of positioned elements
    """
    if not elements:
        return elements
    
    # Define region centers
    region_centers = {
        'center': (0.0, 0.0),
        'top': (0.0, 2.5),
        'bottom': (0.0, -2.5),
        'left': (-4.0, 0.0),
        'right': (4.0, 0.0),
        'top_left': (-3.5, 2.0),
        'top_right': (3.5, 2.0),
        'bottom_left': (-3.5, -2.0),
        'bottom_right': (3.5, -2.0)
    }
    
    center_pos = region_centers.get(region, (0.0, 0.0))
    
    if len(elements) == 1:
        # Single element - place at region center
        safe_position(elements[0], center_pos, margin)
    elif len(elements) == 2:
        # Two elements - place side by side or top/bottom
        if region in ['top', 'bottom', 'center']:
            # Horizontal arrangement
            safe_position(elements[0], (center_pos[0] - 1.5, center_pos[1]), margin)
            safe_position(elements[1], (center_pos[0] + 1.5, center_pos[1]), margin)
        else:
            # Vertical arrangement
            safe_position(elements[0], (center_pos[0], center_pos[1] + 1.0), margin)
            safe_position(elements[1], (center_pos[0], center_pos[1] - 1.0), margin)
    else:
        # Multiple elements - use grid
        cols = min(2, len(elements))
        rows = (len(elements) + cols - 1) // cols
        
        start_x = center_pos[0] - (cols - 1) * 1.5 / 2
        start_y = center_pos[1] + (rows - 1) * 1.0 / 2
        
        for i, element in enumerate(elements):
            row = i // cols
            col = i % cols
            
            x = start_x + col * 1.5
            y = start_y - row * 1.0
            
            safe_position(element, (x, y), margin)
    
    return elements


def suggest_better_layout(elements: List[Any], 
                         current_layout_issues: List[str]) -> Dict[str, Any]:
    """
    Suggest improved layout based on detected issues
    
    Args:
        elements: List of elements with layout issues
        current_layout_issues: List of issue descriptions
        
    Returns:
        Dictionary with layout suggestions
    """
    suggestions = {
        'recommended_action': 'maintain_current',
        'specific_changes': [],
        'alternative_layouts': [],
        'estimated_improvement': 0
    }
    
    if not elements or not current_layout_issues:
        return suggestions
    
    # Analyze issues
    has_overlaps = any('overlap' in issue.lower() for issue in current_layout_issues)
    has_out_of_bounds = any('bounds' in issue.lower() or 'frame' in issue.lower() 
                           for issue in current_layout_issues)
    
    if has_overlaps:
        if len(elements) > 3:
            suggestions['recommended_action'] = 'paginate'
            suggestions['specific_changes'].append('Split content into multiple slides')
            suggestions['alternative_layouts'].append('grid_layout')
            suggestions['estimated_improvement'] = 80
        else:
            suggestions['recommended_action'] = 'increase_spacing'
            suggestions['specific_changes'].append('Increase buffer distance to 1.0 units')
            suggestions['alternative_layouts'].append('vertical_stack')
            suggestions['estimated_improvement'] = 60
    
    if has_out_of_bounds:
        suggestions['specific_changes'].append('Scale elements down by 10-20%')
        suggestions['alternative_layouts'].append('centered_layout')
        if suggestions['recommended_action'] == 'maintain_current':
            suggestions['recommended_action'] = 'scale_and_reposition'
            suggestions['estimated_improvement'] = 70
    
    return suggestions