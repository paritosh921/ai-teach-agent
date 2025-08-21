"""
Frame Bounds Utilities

This module provides utilities for detecting and enforcing frame boundaries
to ensure all content stays visible within the Manim video frame.
"""

import numpy as np
from typing import Tuple, List, Union, Any

# Manim standard frame dimensions
FRAME_W = 14.0
FRAME_H = 8.0

# Default safe margins (6% as per Builder LLM requirements)
DEFAULT_MARGIN = 0.35  # units from edges


def get_safe_bounds(margin: float = DEFAULT_MARGIN) -> Tuple[float, float, float, float]:
    """
    Get safe area boundaries with specified margin
    
    Args:
        margin: Distance in Manim units from frame edges
        
    Returns:
        Tuple of (left, right, top, bottom) boundaries
    """
    left = -FRAME_W / 2 + margin
    right = FRAME_W / 2 - margin
    top = FRAME_H / 2 - margin
    bottom = -FRAME_H / 2 + margin
    
    return left, right, top, bottom


def get_element_bounds(element: Any) -> Tuple[float, float, float, float]:
    """
    Get bounding box of a Manim element
    
    Args:
        element: Manim mobject
        
    Returns:
        Tuple of (x_min, y_min, x_max, y_max)
    """
    if hasattr(element, 'get_bounding_box_point'):
        # Use Manim's bounding box method
        min_point = element.get_bounding_box_point(np.array([-1, -1, 0]))
        max_point = element.get_bounding_box_point(np.array([1, 1, 0]))
        return min_point[0], min_point[1], max_point[0], max_point[1]
    elif hasattr(element, 'get_center') and hasattr(element, 'width') and hasattr(element, 'height'):
        # Fallback using center and dimensions
        center = element.get_center()[:2]  # x, y only
        half_width = element.width / 2
        half_height = element.height / 2
        return (
            center[0] - half_width,
            center[1] - half_height,
            center[0] + half_width,
            center[1] + half_height
        )
    else:
        # Default bounds if no information available
        return -1.0, -0.5, 1.0, 0.5


def in_frame(element: Any, margin: float = DEFAULT_MARGIN) -> bool:
    """
    Check if element is completely within safe frame boundaries
    
    Args:
        element: Manim mobject to check
        margin: Safe margin from edges
        
    Returns:
        True if element is within bounds, False otherwise
    """
    left, right, top, bottom = get_safe_bounds(margin)
    x_min, y_min, x_max, y_max = get_element_bounds(element)
    
    return (
        x_min >= left and
        x_max <= right and
        y_min >= bottom and
        y_max <= top
    )


def fit_to_frame(element: Any, margin: float = DEFAULT_MARGIN) -> Any:
    """
    Scale element to fit within safe frame boundaries
    
    Args:
        element: Manim mobject to fit
        margin: Safe margin from edges
        
    Returns:
        The element (modified in place)
    """
    if not hasattr(element, 'scale') or not hasattr(element, 'width') or not hasattr(element, 'height'):
        return element
    
    left, right, top, bottom = get_safe_bounds(margin)
    max_width = right - left
    max_height = top - bottom
    
    # Calculate required scale factor
    width_scale = max_width / max(element.width, 1e-6) if element.width > max_width else 1.0
    height_scale = max_height / max(element.height, 1e-6) if element.height > max_height else 1.0
    
    # Use the more restrictive scale factor, but only shrink (never enlarge)
    scale_factor = min(width_scale, height_scale, 1.0)
    
    if scale_factor < 1.0:
        element.scale(scale_factor)
    
    return element


def enforce_safe_margins(element: Any, margin: float = DEFAULT_MARGIN) -> Any:
    """
    Move element to safe area if it's outside frame bounds
    
    Args:
        element: Manim mobject to reposition
        margin: Safe margin from edges
        
    Returns:
        The element (modified in place)
    """
    if not hasattr(element, 'move_to') or not hasattr(element, 'get_center'):
        return element
    
    # First, ensure element fits within frame
    fit_to_frame(element, margin)
    
    # Get current bounds after fitting
    left, right, top, bottom = get_safe_bounds(margin)
    x_min, y_min, x_max, y_max = get_element_bounds(element)
    
    # Calculate required adjustments
    dx = 0
    dy = 0
    
    if x_min < left:
        dx = left - x_min
    elif x_max > right:
        dx = right - x_max
    
    if y_min < bottom:
        dy = bottom - y_min
    elif y_max > top:
        dy = top - y_max
    
    # Apply adjustments
    if dx != 0 or dy != 0:
        current_center = element.get_center()
        new_center = current_center + np.array([dx, dy, 0])
        element.move_to(new_center)
    
    return element


def calculate_safe_position(desired_position: Tuple[float, float],
                          element_width: float,
                          element_height: float,
                          margin: float = DEFAULT_MARGIN) -> Tuple[float, float]:
    """
    Calculate adjusted position to ensure element stays within safe bounds
    
    Args:
        desired_position: Desired (x, y) center position
        element_width: Width of the element
        element_height: Height of the element
        margin: Safe margin from edges
        
    Returns:
        Adjusted (x, y) position that keeps element in bounds
    """
    left, right, top, bottom = get_safe_bounds(margin)
    x, y = desired_position
    
    # Calculate element bounds at desired position
    half_width = element_width / 2
    half_height = element_height / 2
    
    elem_left = x - half_width
    elem_right = x + half_width
    elem_bottom = y - half_height
    elem_top = y + half_height
    
    # Adjust position if out of bounds
    if elem_left < left:
        x = left + half_width
    elif elem_right > right:
        x = right - half_width
    
    if elem_bottom < bottom:
        y = bottom + half_height
    elif elem_top > top:
        y = top - half_height
    
    return x, y


def get_frame_utilization(elements: List[Any], margin: float = DEFAULT_MARGIN) -> dict:
    """
    Calculate how much of the frame is being utilized by elements
    
    Args:
        elements: List of Manim mobjects
        margin: Safe margin from edges
        
    Returns:
        Dictionary with utilization statistics
    """
    if not elements:
        return {
            'total_area_used': 0.0,
            'frame_coverage': 0.0,
            'safe_area_coverage': 0.0,
            'elements_in_bounds': 0,
            'elements_out_of_bounds': 0
        }
    
    left, right, top, bottom = get_safe_bounds(margin)
    safe_area = (right - left) * (top - bottom)
    total_frame_area = FRAME_W * FRAME_H
    
    total_used_area = 0.0
    in_bounds_count = 0
    out_of_bounds_count = 0
    
    for element in elements:
        x_min, y_min, x_max, y_max = get_element_bounds(element)
        element_area = (x_max - x_min) * (y_max - y_min)
        total_used_area += element_area
        
        if in_frame(element, margin):
            in_bounds_count += 1
        else:
            out_of_bounds_count += 1
    
    return {
        'total_area_used': total_used_area,
        'frame_coverage': total_used_area / total_frame_area,
        'safe_area_coverage': total_used_area / safe_area,
        'elements_in_bounds': in_bounds_count,
        'elements_out_of_bounds': out_of_bounds_count
    }


def suggest_margin_adjustment(elements: List[Any], current_margin: float = DEFAULT_MARGIN) -> float:
    """
    Suggest optimal margin based on current element layout
    
    Args:
        elements: List of Manim mobjects
        current_margin: Current margin setting
        
    Returns:
        Suggested margin value
    """
    if not elements:
        return current_margin
    
    # Find the minimum distance from any element to frame edge
    min_distance = float('inf')
    
    for element in elements:
        x_min, y_min, x_max, y_max = get_element_bounds(element)
        
        # Distances to frame edges
        dist_left = x_min - (-FRAME_W / 2)
        dist_right = (FRAME_W / 2) - x_max
        dist_bottom = y_min - (-FRAME_H / 2)
        dist_top = (FRAME_H / 2) - y_max
        
        min_distance = min(min_distance, dist_left, dist_right, dist_bottom, dist_top)
    
    # Suggest margin that's 80% of minimum distance to provide buffer
    suggested_margin = max(0.1, min_distance * 0.8)
    
    # Cap at reasonable maximum
    return min(suggested_margin, 1.0)