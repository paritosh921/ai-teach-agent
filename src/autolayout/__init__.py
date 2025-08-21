"""
Autolayout Module for Manim Content Safety

This module provides comprehensive layout safety utilities to ensure:
- All content stays within frame boundaries
- No overlapping elements
- Proper scaling and positioning
- Professional layout management
"""

from .frame_bounds import (
    get_safe_bounds,
    in_frame,
    fit_to_frame,
    enforce_safe_margins,
    FRAME_W,
    FRAME_H
)

from .auto_positioning import (
    arrange_and_fit,
    resolve_overlaps,
    paginate_content,
    safe_position
)

from .element_scaling import (
    auto_scale_element,
    set_max_width_shrink,
    ensure_legible_text,
    scale_to_fit_pct
)

from .layout_validators import (
    validate_layout_pre_render,
    check_element_bounds,
    detect_overlaps_batch,
    generate_layout_report
)

from .runtime_guards import (
    generate_runtime_safety_code,
    generate_scene_wrapper_code,
    get_embedded_safety_code,
    create_safe_code_template,
    inject_safety_into_existing_code
)

__all__ = [
    # Frame bounds
    'get_safe_bounds', 'in_frame', 'fit_to_frame', 'enforce_safe_margins',
    'FRAME_W', 'FRAME_H',
    
    # Auto positioning
    'arrange_and_fit', 'resolve_overlaps', 'paginate_content', 'safe_position',
    
    # Element scaling
    'auto_scale_element', 'set_max_width_shrink', 'ensure_legible_text', 'scale_to_fit_pct',
    
    # Layout validation
    'validate_layout_pre_render', 'check_element_bounds', 'detect_overlaps_batch', 
    'generate_layout_report',
    
    # Runtime guards
    'generate_runtime_safety_code', 'generate_scene_wrapper_code', 'get_embedded_safety_code',
    'create_safe_code_template', 'inject_safety_into_existing_code'
]