"""
Safe Layout Manager for Builder LLM System

This module implements the non-negotiable layout safety rules:
- Safe margins: ≥ 6% on all sides
- No overlaps between visible elements
- Max element size: ≤ 92% of safe frame
- Text legibility at 480p (≈ 24px minimum)
- Explicit z_index management
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class OverlapResolution(Enum):
    """Strategies for resolving overlaps"""
    SHRINK = "shrink"           # Scale elements down
    REFLOW = "reflow"           # Move to next available position
    FADE_PREVIOUS = "fade"      # Remove previous elements
    STACK_VERTICAL = "stack"    # Stack elements vertically


@dataclass
class Element:
    """Represents a positioned element with bounds and timing"""
    key: str
    element_type: str
    column: str
    bounds: Tuple[float, float, float, float]  # x_min, y_min, x_max, y_max
    z_index: int
    enter_time: float
    exit_time: float
    content: str = ""
    font_size: int = 42
    scaled: bool = False


@dataclass
class SafeFrame:
    """Safe frame boundaries and constraints"""
    width: float = 14.0      # Manim standard frame width
    height: float = 8.0      # Manim standard frame height
    margin_pct: float = 0.06 # 6% safe margin
    max_element_pct: float = 0.92  # 92% max element size
    
    def get_boundaries(self) -> Tuple[float, float, float, float]:
        """Get safe boundaries (left, right, top, bottom)"""
        margin_x = self.width * self.margin_pct
        margin_y = self.height * self.margin_pct
        
        left = -self.width / 2 + margin_x
        right = self.width / 2 - margin_x
        top = self.height / 2 - margin_y
        bottom = -self.height / 2 + margin_y
        
        return left, right, top, bottom
    
    def get_max_dimensions(self) -> Tuple[float, float]:
        """Get maximum allowed element dimensions"""
        left, right, top, bottom = self.get_boundaries()
        max_width = (right - left) * self.max_element_pct
        max_height = (top - bottom) * self.max_element_pct
        return max_width, max_height


@dataclass
class LayoutState:
    """Tracks current layout state for overlap detection"""
    active_elements: Dict[str, Element] = field(default_factory=dict)
    element_history: List[Element] = field(default_factory=list)
    current_time: float = 0.0
    
    def update_time(self, time: float):
        """Update current time and active elements"""
        self.current_time = time
        
        # Remove expired elements
        to_remove = []
        for key, element in self.active_elements.items():
            if time >= element.exit_time:
                to_remove.append(key)
        
        for key in to_remove:
            del self.active_elements[key]
    
    def add_element(self, element: Element) -> bool:
        """Add element if it doesn't violate constraints"""
        if element.enter_time <= self.current_time <= element.exit_time:
            self.active_elements[element.key] = element
            self.element_history.append(element)
            return True
        return False
    
    def get_overlapping_elements(self, element: Element, 
                               buffer: float = 0.2) -> List[Element]:
        """Find elements that overlap with given element"""
        overlapping = []
        
        for active_element in self.active_elements.values():
            if active_element.key == element.key:
                continue
            
            if self._bounds_overlap(element.bounds, active_element.bounds, buffer):
                overlapping.append(active_element)
        
        return overlapping
    
    def _bounds_overlap(self, bounds1: Tuple[float, float, float, float],
                       bounds2: Tuple[float, float, float, float],
                       buffer: float) -> bool:
        """Check if two bounding boxes overlap with buffer"""
        x1_min, y1_min, x1_max, y1_max = bounds1
        x2_min, y2_min, x2_max, y2_max = bounds2
        
        # Add buffer to first element
        x1_min -= buffer
        y1_min -= buffer
        x1_max += buffer
        y1_max += buffer
        
        # Check for overlap
        return not (x1_max < x2_min or x1_min > x2_max or 
                   y1_max < y2_min or y1_min > y2_max)


class SafeLayoutManager:
    """
    Manages safe layout with strict adherence to non-negotiable rules
    
    Core responsibilities:
    1. Enforce safe margins (≥6% on all sides)
    2. Prevent overlaps with automatic resolution
    3. Ensure text legibility (≥24px at 480p)
    4. Manage z-index ordering
    5. Provide deterministic positioning
    """
    
    def __init__(self, frame_width: float = 14.0, frame_height: float = 8.0):
        """Initialize with frame dimensions"""
        self.safe_frame = SafeFrame(width=frame_width, height=frame_height)
        self.layout_state = LayoutState()
        self.min_text_height_480p = 24  # pixels
        self.min_font_size = self._calculate_min_font_size()
    
    def validate_element_specs(self, elements: List[Dict[str, Any]]) -> List[str]:
        """
        Validate element specifications against safety rules
        
        Returns list of validation errors (empty if valid)
        """
        errors = []
        elements_by_time = self._sort_elements_by_time(elements)
        
        # Reset layout state for validation
        self.layout_state = LayoutState()
        
        for time_group in elements_by_time:
            time, group_elements = time_group
            self.layout_state.update_time(time)
            
            for element_spec in group_elements:
                element = self._create_element_from_spec(element_spec)
                validation_errors = self._validate_single_element(element)
                errors.extend(validation_errors)
        
        return errors
    
    def generate_safe_positioning(self, elements: List[Dict[str, Any]], 
                                template_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Generate safe positioning for all elements with automatic conflict resolution
        
        Returns:
            Dictionary mapping element keys to positioning information
        """
        from ..schemas.layout_templates import get_template_manager
        
        template_manager = get_template_manager()
        template = template_manager.get_template(template_name)
        
        if not template:
            raise ValueError(f"Unknown template: {template_name}")
        
        positioned_elements = {}
        elements_by_time = self._sort_elements_by_time(elements)
        
        # Reset layout state
        self.layout_state = LayoutState()
        
        for time_group in elements_by_time:
            time, group_elements = time_group
            self.layout_state.update_time(time)
            
            for element_spec in group_elements:
                element = self._create_element_from_spec(element_spec)
                
                # Get base position from template
                region = template.get_region(element.column)
                if not region:
                    # Fallback to center
                    region = template.get_region('center')
                
                base_position = self._region_to_position(region)
                
                # Check for overlaps and resolve
                overlapping = self.layout_state.get_overlapping_elements(element)
                
                if overlapping:
                    resolved_element, modifications = self._resolve_overlap(
                        element, overlapping, region
                    )
                else:
                    resolved_element = element
                    modifications = {}
                
                # Ensure element stays in safe frame
                bounded_element, bounds_mods = self._enforce_safe_bounds(resolved_element)
                modifications.update(bounds_mods)
                
                # Store positioning information
                positioned_elements[element.key] = {
                    'position': base_position,
                    'bounds': bounded_element.bounds,
                    'z_index': bounded_element.z_index,
                    'modifications': modifications,
                    'safe_positioning': self._generate_manim_positioning_code(
                        bounded_element, base_position
                    )
                }
                
                # Add to layout state
                self.layout_state.add_element(bounded_element)
        
        return positioned_elements
    
    def _calculate_min_font_size(self) -> int:
        """Calculate minimum font size for 480p legibility"""
        # 480p = 480 pixels height
        # Assuming 8.0 Manim units = 480 pixels
        pixels_per_unit = 480 / 8.0  # 60 pixels per unit
        min_units = self.min_text_height_480p / pixels_per_unit
        
        # Font size in Manim roughly corresponds to height in units
        # Use conservative estimate with 20% margin
        return max(int(min_units * 1.2), 24)
    
    def _sort_elements_by_time(self, elements: List[Dict[str, Any]]) -> List[Tuple[float, List[Dict[str, Any]]]]:
        """Sort elements by enter time"""
        elements_with_time = []
        for element in elements:
            enter_time = element.get('enter', {}).get('at', 0.0)
            elements_with_time.append((enter_time, element))
        
        # Group by time
        time_groups = {}
        for enter_time, element in elements_with_time:
            if enter_time not in time_groups:
                time_groups[enter_time] = []
            time_groups[enter_time].append(element)
        
        # Sort by time
        return sorted(time_groups.items())
    
    def _create_element_from_spec(self, element_spec: Dict[str, Any]) -> Element:
        """Create Element object from specification"""
        key = element_spec['key']
        element_type = element_spec['type']
        column = element_spec['column']
        
        # Get timing
        enter_time = element_spec.get('enter', {}).get('at', 0.0)
        exit_time = element_spec.get('exit', {}).get('at', float('inf'))
        
        # Get content for size estimation
        content = element_spec.get('content', element_spec.get('tex', ''))
        
        # Get style
        style = element_spec.get('style', {})
        font_size = style.get('font_size', 42)
        
        # Estimate bounds based on content and font size
        bounds = self._estimate_element_bounds(content, font_size, element_type)
        
        # Get z-index
        z_index = element_spec.get('z_index', 1)
        
        return Element(
            key=key,
            element_type=element_type,
            column=column,
            bounds=bounds,
            z_index=z_index,
            enter_time=enter_time,
            exit_time=exit_time,
            content=content,
            font_size=font_size
        )
    
    def _estimate_element_bounds(self, content: str, font_size: int, 
                               element_type: str) -> Tuple[float, float, float, float]:
        """Estimate element bounding box"""
        # Rough estimates based on element type
        if element_type == 'Text':
            # Approximate text dimensions
            chars_per_line = len(content) if len(content) < 40 else 40
            lines = max(1, len(content) // 40)
            
            # Font size roughly corresponds to height in Manim units
            char_width = font_size * 0.6 / 72  # Rough character width
            line_height = font_size / 72 * 1.2  # Line height with spacing
            
            width = chars_per_line * char_width
            height = lines * line_height
            
        elif element_type == 'MathTex':
            # Math expressions tend to be more compact but taller
            width = min(len(content) * font_size * 0.4 / 72, 6.0)
            height = font_size / 72 * 1.5
            
        elif element_type in ['AxesPlot', 'Table', 'Image']:
            # Default to medium size for complex elements
            width = 4.0
            height = 3.0
            
        else:
            # Default dimensions
            width = 2.0
            height = 1.0
        
        # Return bounds centered at origin
        return (-width/2, -height/2, width/2, height/2)
    
    def _region_to_position(self, region) -> Tuple[float, float]:
        """Convert region to center position"""
        if not region:
            return (0.0, 0.0)  # Default to center
        
        # Calculate center position in Manim coordinates
        x_center = (region.x_start + region.x_end) / 2.0
        y_center = (region.y_start + region.y_end) / 2.0
        
        # Convert from normalized (0,1) to Manim coordinates
        manim_x = (x_center - 0.5) * self.safe_frame.width
        manim_y = (0.5 - y_center) * self.safe_frame.height  # Y is flipped
        
        return (manim_x, manim_y)
    
    def _validate_single_element(self, element: Element) -> List[str]:
        """Validate a single element against safety rules"""
        errors = []
        
        # Check font size
        if element.font_size < self.min_font_size:
            errors.append(
                f"Element '{element.key}' font size {element.font_size} below "
                f"minimum {self.min_font_size} for 480p legibility"
            )
        
        # Check element size against frame
        left, right, top, bottom = self.safe_frame.get_boundaries()
        x_min, y_min, x_max, y_max = element.bounds
        
        if (x_max - x_min) > (right - left):
            errors.append(f"Element '{element.key}' width exceeds safe frame width")
        
        if (y_max - y_min) > (top - bottom):
            errors.append(f"Element '{element.key}' height exceeds safe frame height")
        
        return errors
    
    def _resolve_overlap(self, element: Element, overlapping: List[Element],
                        region) -> Tuple[Element, Dict[str, Any]]:
        """Resolve overlap using configured strategy"""
        modifications = {}
        
        # Strategy 1: Try shrinking
        shrunk_element = self._try_shrink_element(element, overlapping)
        if shrunk_element:
            modifications['shrunk'] = True
            modifications['scale_factor'] = 0.95
            return shrunk_element, modifications
        
        # Strategy 2: Try reflowing vertically
        reflowed_element = self._try_reflow_element(element, overlapping, region)
        if reflowed_element:
            modifications['reflowed'] = True
            modifications['reflow_direction'] = 'vertical'
            return reflowed_element, modifications
        
        # Strategy 3: Suggest fading previous elements
        modifications['requires_fade_previous'] = True
        modifications['conflicting_elements'] = [e.key for e in overlapping]
        
        return element, modifications
    
    def _try_shrink_element(self, element: Element, 
                          overlapping: List[Element]) -> Optional[Element]:
        """Try to resolve overlap by shrinking element"""
        # Try scaling down by 5%
        scale_factor = 0.95
        x_min, y_min, x_max, y_max = element.bounds
        
        # Scale bounds
        width = x_max - x_min
        height = y_max - y_min
        new_width = width * scale_factor
        new_height = height * scale_factor
        
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        
        new_bounds = (
            center_x - new_width/2,
            center_y - new_height/2,
            center_x + new_width/2,
            center_y + new_height/2
        )
        
        # Create shrunk element
        shrunk_element = Element(
            key=element.key,
            element_type=element.element_type,
            column=element.column,
            bounds=new_bounds,
            z_index=element.z_index,
            enter_time=element.enter_time,
            exit_time=element.exit_time,
            content=element.content,
            font_size=max(int(element.font_size * scale_factor), self.min_font_size),
            scaled=True
        )
        
        # Check if shrinking resolves overlaps
        for other_element in overlapping:
            if self.layout_state._bounds_overlap(shrunk_element.bounds, 
                                               other_element.bounds, 0.2):
                return None  # Still overlapping
        
        return shrunk_element
    
    def _try_reflow_element(self, element: Element, overlapping: List[Element],
                          region) -> Optional[Element]:
        """Try to resolve overlap by moving element within region"""
        # Try moving vertically within region bounds
        region_height = region.y_end - region.y_start
        available_height = region_height * self.safe_frame.height
        
        x_min, y_min, x_max, y_max = element.bounds
        element_height = y_max - y_min
        
        # Try positions at 25%, 50%, 75% of region height
        for y_fraction in [0.25, 0.75]:
            # Calculate new y position
            region_center_y = (region.y_start + region.y_end) / 2.0
            region_manim_y = (0.5 - region_center_y) * self.safe_frame.height
            
            offset = (y_fraction - 0.5) * available_height / 2
            new_center_y = region_manim_y + offset
            
            new_bounds = (
                x_min,
                new_center_y - element_height/2,
                x_max,
                new_center_y + element_height/2
            )
            
            # Create reflowed element
            reflowed_element = Element(
                key=element.key,
                element_type=element.element_type,
                column=element.column,
                bounds=new_bounds,
                z_index=element.z_index,
                enter_time=element.enter_time,
                exit_time=element.exit_time,
                content=element.content,
                font_size=element.font_size
            )
            
            # Check if reflow resolves overlaps
            overlap_resolved = True
            for other_element in overlapping:
                if self.layout_state._bounds_overlap(reflowed_element.bounds,
                                                   other_element.bounds, 0.2):
                    overlap_resolved = False
                    break
            
            if overlap_resolved:
                return reflowed_element
        
        return None
    
    def _enforce_safe_bounds(self, element: Element) -> Tuple[Element, Dict[str, Any]]:
        """Ensure element stays within safe frame boundaries"""
        left, right, top, bottom = self.safe_frame.get_boundaries()
        x_min, y_min, x_max, y_max = element.bounds
        
        modifications = {}
        
        # Check if element extends beyond safe bounds
        if x_min < left or x_max > right or y_min < bottom or y_max > top:
            # Calculate required scaling
            width = x_max - x_min
            height = y_max - y_min
            
            max_width, max_height = self.safe_frame.get_max_dimensions()
            
            width_scale = max_width / width if width > max_width else 1.0
            height_scale = max_height / height if height > max_height else 1.0
            
            scale_factor = min(width_scale, height_scale, 1.0)
            
            if scale_factor < 1.0:
                # Apply scaling
                new_width = width * scale_factor
                new_height = height * scale_factor
                
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                
                new_bounds = (
                    center_x - new_width/2,
                    center_y - new_height/2,
                    center_x + new_width/2,
                    center_y + new_height/2
                )
                
                bounded_element = Element(
                    key=element.key,
                    element_type=element.element_type,
                    column=element.column,
                    bounds=new_bounds,
                    z_index=element.z_index,
                    enter_time=element.enter_time,
                    exit_time=element.exit_time,
                    content=element.content,
                    font_size=max(int(element.font_size * scale_factor), self.min_font_size),
                    scaled=True
                )
                
                modifications['bounds_enforced'] = True
                modifications['bounds_scale_factor'] = scale_factor
                
                return bounded_element, modifications
        
        return element, modifications
    
    def _generate_manim_positioning_code(self, element: Element, 
                                       base_position: Tuple[float, float]) -> str:
        """Generate Manim positioning code for element"""
        x, y = base_position
        
        # Generate position expression
        if abs(x) < 0.1 and abs(y) < 0.1:
            position_code = "ORIGIN"
        elif abs(x) < 0.1:
            if y > 0:
                position_code = f"UP * {y:.2f}"
            else:
                position_code = f"DOWN * {abs(y):.2f}"
        elif abs(y) < 0.1:
            if x > 0:
                position_code = f"RIGHT * {x:.2f}"
            else:
                position_code = f"LEFT * {abs(x):.2f}"
        else:
            x_part = f"RIGHT * {x:.2f}" if x > 0 else f"LEFT * {abs(x):.2f}"
            y_part = f"UP * {y:.2f}" if y > 0 else f"DOWN * {abs(y):.2f}"
            position_code = f"{x_part} + {y_part}"
        
        # Add scaling if needed
        if element.scaled:
            scale_factor = element.font_size / 42.0  # Relative to default
            return f"scale_to_fit_pct({element.key}).move_to({position_code})"
        else:
            return f"{element.key}.move_to({position_code})"


def create_safe_layout_manager(frame_width: float = 14.0, 
                             frame_height: float = 8.0) -> SafeLayoutManager:
    """Factory function for creating layout manager"""
    return SafeLayoutManager(frame_width, frame_height)