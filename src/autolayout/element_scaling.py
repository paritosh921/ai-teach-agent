"""
Element Scaling Utilities

This module provides automatic scaling utilities to ensure elements
fit properly within the frame and maintain legibility.
"""

import numpy as np
from typing import Any, Tuple, Optional, Union
from .frame_bounds import (
    get_safe_bounds,
    get_element_bounds,
    FRAME_W,
    FRAME_H,
    DEFAULT_MARGIN
)


def auto_scale_element(element: Any, 
                      max_width_pct: float = 0.92,
                      max_height_pct: float = 0.92,
                      margin: float = DEFAULT_MARGIN,
                      min_scale: float = 0.1) -> Tuple[Any, float]:
    """
    Automatically scale element to fit within safe bounds
    
    Args:
        element: Manim mobject to scale
        max_width_pct: Maximum width as percentage of safe area
        max_height_pct: Maximum height as percentage of safe area
        margin: Safe margin from edges
        min_scale: Minimum allowed scale factor
        
    Returns:
        Tuple of (scaled_element, scale_factor_applied)
    """
    if not hasattr(element, 'scale') or not hasattr(element, 'width') or not hasattr(element, 'height'):
        return element, 1.0
    
    left, right, top, bottom = get_safe_bounds(margin)
    safe_width = right - left
    safe_height = top - bottom
    
    # Calculate maximum allowed dimensions
    max_allowed_width = safe_width * max_width_pct
    max_allowed_height = safe_height * max_height_pct
    
    # Calculate required scale factors
    current_width = element.width
    current_height = element.height
    
    width_scale = max_allowed_width / current_width if current_width > max_allowed_width else 1.0
    height_scale = max_allowed_height / current_height if current_height > max_allowed_height else 1.0
    
    # Use the more restrictive scale factor
    scale_factor = min(width_scale, height_scale, 1.0)  # Never enlarge
    scale_factor = max(scale_factor, min_scale)  # Respect minimum scale
    
    if scale_factor < 1.0:
        element.scale(scale_factor)
    
    return element, scale_factor


def set_max_width_shrink(element: Any, max_width: float) -> Any:
    """
    Shrink element width if it exceeds maximum, maintaining aspect ratio
    
    Args:
        element: Manim mobject to potentially shrink
        max_width: Maximum allowed width
        
    Returns:
        The element (modified in place if needed)
    """
    if not hasattr(element, 'width') or not hasattr(element, 'scale'):
        return element
    
    if element.width > max_width:
        scale_factor = max_width / element.width
        element.scale(scale_factor)
    
    return element


def set_max_height_shrink(element: Any, max_height: float) -> Any:
    """
    Shrink element height if it exceeds maximum, maintaining aspect ratio
    
    Args:
        element: Manim mobject to potentially shrink
        max_height: Maximum allowed height
        
    Returns:
        The element (modified in place if needed)
    """
    if not hasattr(element, 'height') or not hasattr(element, 'scale'):
        return element
    
    if element.height > max_height:
        scale_factor = max_height / element.height
        element.scale(scale_factor)
    
    return element


def ensure_legible_text(element: Any, 
                       min_font_size: int = 24,
                       target_resolution: str = '480p') -> Tuple[Any, bool]:
    """
    Ensure text element maintains minimum legible font size
    
    Args:
        element: Text-like Manim mobject
        min_font_size: Minimum font size in points
        target_resolution: Target video resolution
        
    Returns:
        Tuple of (element, was_adjusted)
    """
    was_adjusted = False
    
    # Check if element has font_size attribute
    if hasattr(element, 'font_size'):
        current_font_size = element.font_size
        
        if current_font_size < min_font_size:
            # Need to increase font size or suggest content reduction
            scale_factor = min_font_size / current_font_size
            
            if hasattr(element, 'scale'):
                element.scale(scale_factor)
                was_adjusted = True
    
    # Alternative approach for elements with set_font_size method
    elif hasattr(element, 'set_font_size'):
        try:
            current_size = getattr(element, 'font_size', 36)  # Default assumption
            if current_size < min_font_size:
                element.set_font_size(min_font_size)
                was_adjusted = True
        except:
            # If setting font size fails, scale the element
            if hasattr(element, 'scale'):
                scale_factor = min_font_size / 36  # Assume default of 36
                element.scale(scale_factor)
                was_adjusted = True
    
    return element, was_adjusted


def scale_to_fit_pct(element: Any, 
                    width_pct: Optional[float] = None,
                    height_pct: Optional[float] = None,
                    margin: float = DEFAULT_MARGIN) -> Any:
    """
    Scale element to specific percentage of safe area
    
    Args:
        element: Manim mobject to scale
        width_pct: Target width as percentage (0.0 to 1.0)
        height_pct: Target height as percentage (0.0 to 1.0)
        margin: Safe margin from edges
        
    Returns:
        Scaled element
    """
    if not hasattr(element, 'scale') or not hasattr(element, 'width') or not hasattr(element, 'height'):
        return element
    
    left, right, top, bottom = get_safe_bounds(margin)
    safe_width = right - left
    safe_height = top - bottom
    
    current_width = element.width
    current_height = element.height
    
    scale_factors = []
    
    if width_pct is not None:
        target_width = safe_width * width_pct
        width_scale = target_width / current_width
        scale_factors.append(width_scale)
    
    if height_pct is not None:
        target_height = safe_height * height_pct
        height_scale = target_height / current_height
        scale_factors.append(height_scale)
    
    if scale_factors:
        # Use the more restrictive scale factor to maintain aspect ratio
        final_scale = min(scale_factors)
        element.scale(final_scale)
    
    return element


def adaptive_font_sizing(text_content: str,
                        available_width: float,
                        available_height: float,
                        min_font_size: int = 24,
                        max_font_size: int = 72) -> int:
    """
    Calculate optimal font size for given content and space
    
    Args:
        text_content: The text content to size
        available_width: Available width in Manim units
        available_height: Available height in Manim units
        min_font_size: Minimum allowed font size
        max_font_size: Maximum allowed font size
        
    Returns:
        Recommended font size
    """
    # Rough estimates for text sizing
    chars_per_line = len(text_content)
    estimated_lines = max(1, chars_per_line // 40)  # Assume ~40 chars per line
    
    # Estimate font size based on available space
    # These are rough heuristics based on typical Manim text rendering
    width_based_font = available_width / (chars_per_line * 0.6) * 72
    height_based_font = available_height / (estimated_lines * 1.2) * 72
    
    # Use the more restrictive constraint
    optimal_font = min(width_based_font, height_based_font)
    
    # Clamp to min/max bounds
    return max(min_font_size, min(int(optimal_font), max_font_size))


def calculate_content_density(elements: list, 
                            margin: float = DEFAULT_MARGIN) -> dict:
    """
    Calculate how densely packed the content is
    
    Args:
        elements: List of Manim mobjects
        margin: Safe margin from edges
        
    Returns:
        Dictionary with density metrics
    """
    if not elements:
        return {
            'density_score': 0.0,
            'recommendation': 'add_content',
            'available_space': 1.0,
            'overcrowded': False
        }
    
    left, right, top, bottom = get_safe_bounds(margin)
    safe_area = (right - left) * (top - bottom)
    
    # Calculate total area used by elements
    total_used_area = 0.0
    for element in elements:
        if hasattr(element, 'width') and hasattr(element, 'height'):
            total_used_area += element.width * element.height
    
    density = total_used_area / safe_area
    
    if density > 0.8:
        recommendation = 'reduce_content_or_paginate'
        overcrowded = True
    elif density > 0.6:
        recommendation = 'consider_scaling_down'
        overcrowded = False
    elif density < 0.3:
        recommendation = 'can_add_more_content'
        overcrowded = False
    else:
        recommendation = 'optimal_density'
        overcrowded = False
    
    return {
        'density_score': density,
        'recommendation': recommendation,
        'available_space': max(0.0, 1.0 - density),
        'overcrowded': overcrowded,
        'safe_area': safe_area,
        'used_area': total_used_area
    }


def suggest_scaling_strategy(element: Any, 
                           available_space: dict,
                           content_type: str = 'text') -> dict:
    """
    Suggest optimal scaling strategy for element
    
    Args:
        element: Manim mobject to analyze
        available_space: Available space metrics
        content_type: Type of content ('text', 'math', 'diagram', 'image')
        
    Returns:
        Dictionary with scaling recommendations
    """
    if not hasattr(element, 'width') or not hasattr(element, 'height'):
        return {'strategy': 'no_scaling_needed', 'scale_factor': 1.0}
    
    current_width = element.width
    current_height = element.height
    available_width = available_space.get('width', FRAME_W * 0.8)
    available_height = available_space.get('height', FRAME_H * 0.8)
    
    # Calculate if scaling is needed
    width_ratio = current_width / available_width
    height_ratio = current_height / available_height
    max_ratio = max(width_ratio, height_ratio)
    
    if max_ratio <= 1.0:
        return {'strategy': 'no_scaling_needed', 'scale_factor': 1.0}
    
    # Determine strategy based on content type
    if content_type == 'text':
        if max_ratio > 1.5:
            return {
                'strategy': 'split_content',
                'scale_factor': 0.8,
                'reason': 'Text would become illegible if scaled down too much'
            }
        else:
            return {
                'strategy': 'scale_down',
                'scale_factor': 1.0 / max_ratio * 0.9,  # 10% buffer
                'reason': 'Moderate scaling maintains readability'
            }
    
    elif content_type in ['math', 'formula']:
        return {
            'strategy': 'scale_down',
            'scale_factor': 1.0 / max_ratio * 0.95,  # 5% buffer for formulas
            'reason': 'Math notation can handle moderate scaling'
        }
    
    elif content_type in ['diagram', 'chart']:
        return {
            'strategy': 'scale_down',
            'scale_factor': 1.0 / max_ratio * 0.85,  # More aggressive for diagrams
            'reason': 'Diagrams can be scaled more aggressively'
        }
    
    else:  # Default for unknown content types
        return {
            'strategy': 'scale_down',
            'scale_factor': 1.0 / max_ratio * 0.9,
            'reason': 'Conservative scaling for unknown content type'
        }