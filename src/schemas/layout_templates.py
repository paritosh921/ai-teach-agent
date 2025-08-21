"""
Layout Templates for Builder LLM System

This module defines the grid layout templates that govern how elements are
positioned on screen. Templates ensure consistent, professional layouts
while maintaining the non-negotiable layout safety rules.
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TemplateType(Enum):
    """Available layout template types"""
    SINGLE = "single"
    TWO_COLUMN = "two_column"
    THREE_COLUMN = "three_column"


@dataclass
class Region:
    """Screen region with safe positioning constraints"""
    x_start: float  # Normalized coordinates (0.0 to 1.0)
    x_end: float
    y_start: float
    y_end: float
    max_elements: int = 1  # Maximum concurrent elements
    z_index_base: int = 1  # Base z-index for elements in this region


@dataclass
class LayoutTemplate:
    """Complete layout template specification"""
    name: str
    description: str
    regions: Dict[str, Region]
    safe_margin_pct: float = 0.06
    element_spacing: float = 0.2  # Minimum spacing between elements
    
    def get_region(self, column: str) -> Optional[Region]:
        """Get region by column name"""
        return self.regions.get(column)
    
    def get_safe_bounds(self) -> Tuple[float, float, float, float]:
        """Get safe area bounds (x_min, x_max, y_min, y_max)"""
        margin = self.safe_margin_pct
        return (margin, 1.0 - margin, margin, 1.0 - margin)


class LayoutTemplateManager:
    """Manager for all layout templates"""
    
    def __init__(self):
        """Initialize with built-in templates"""
        self.templates = self._create_builtin_templates()
    
    def get_template(self, template_name: str) -> Optional[LayoutTemplate]:
        """Get template by name"""
        return self.templates.get(template_name)
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template names"""
        return list(self.templates.keys())
    
    def validate_element_placement(self, template_name: str, 
                                 elements: List[Dict[str, Any]]) -> List[str]:
        """
        Validate that elements can be placed in the template without violations
        
        Args:
            template_name: Name of the template to validate against
            elements: List of element specifications
            
        Returns:
            List of validation errors (empty if valid)
        """
        template = self.get_template(template_name)
        if not template:
            return [f"Unknown template: {template_name}"]
        
        errors = []
        
        # Group elements by column and check capacity
        column_usage = {}
        for element in elements:
            column = element.get('column', 'center')
            if column not in column_usage:
                column_usage[column] = []
            column_usage[column].append(element)
        
        # Check each column
        for column, column_elements in column_usage.items():
            region = template.get_region(column)
            if not region:
                errors.append(f"Column '{column}' not supported in template '{template_name}'")
                continue
            
            # Check element count with timing
            concurrent_elements = self._get_max_concurrent_elements(column_elements)
            if concurrent_elements > region.max_elements:
                errors.append(
                    f"Column '{column}' exceeds capacity: {concurrent_elements} elements "
                    f"concurrent (max: {region.max_elements})"
                )
        
        return errors
    
    def enforce_capacity_limits(self, template_name: str, 
                               elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Automatically enforce capacity limits by redistributing or splitting elements
        
        Args:
            template_name: Template to enforce limits for
            elements: Elements to redistribute
            
        Returns:
            List of elements with adjusted positioning or timing
        """
        template = self.get_template(template_name)
        if not template:
            return elements
        
        # Create a copy of elements to modify
        modified_elements = [dict(element) for element in elements]
        
        # Group elements by column
        column_groups = {}
        for element in modified_elements:
            column = element.get('column', 'center')
            if column not in column_groups:
                column_groups[column] = []
            column_groups[column].append(element)
        
        # Check each column for violations
        for column, column_elements in column_groups.items():
            region = template.get_region(column)
            if not region:
                continue
                
            # Calculate max concurrent elements
            max_concurrent = self._get_max_concurrent_elements(column_elements)
            
            if max_concurrent > region.max_elements:
                # Apply overflow handling
                fixed_elements = self._handle_column_overflow(
                    column_elements, region, template
                )
                
                # Replace elements in the main list
                for i, element in enumerate(modified_elements):
                    element_key = element.get('key', f'element_{i}')
                    for fixed_element in fixed_elements:
                        if fixed_element.get('key') == element_key:
                            modified_elements[i] = fixed_element
                            break
        
        return modified_elements
    
    def _handle_column_overflow(self, elements: List[Dict[str, Any]], 
                               region: Region, template: LayoutTemplate) -> List[Dict[str, Any]]:
        """
        Handle overflow in a column by applying various strategies
        
        Args:
            elements: Elements in the overflowing column
            region: The region specification
            template: The template being used
            
        Returns:
            List of fixed elements
        """
        # Strategy 1: Try time-based staggering
        staggered = self._apply_time_staggering(elements, region.max_elements)
        if self._get_max_concurrent_elements(staggered) <= region.max_elements:
            return staggered
        
        # Strategy 2: Redistribute to available columns
        redistributed = self._redistribute_to_available_columns(elements, template)
        if redistributed:
            return redistributed
        
        # Strategy 3: Split elements with scene boundaries
        split_elements = self._split_elements_across_scenes(elements, region.max_elements)
        return split_elements
    
    def _apply_time_staggering(self, elements: List[Dict[str, Any]], 
                              max_concurrent: int) -> List[Dict[str, Any]]:
        """Apply time-based staggering to reduce concurrent elements"""
        if len(elements) <= max_concurrent:
            return elements
        
        staggered = [dict(element) for element in elements]
        
        # Sort by original enter time
        staggered.sort(key=lambda x: x.get('enter', {}).get('at', 0))
        
        # Apply staggering with 2-second delays
        stagger_delay = 2.0
        for i in range(max_concurrent, len(staggered)):
            previous_element = staggered[i - max_concurrent]
            previous_exit = previous_element.get('exit', {}).get('at', float('inf'))
            
            if previous_exit == float('inf'):
                # Set exit time for previous element to make room
                previous_element.setdefault('exit', {})['at'] = \
                    previous_element.get('enter', {}).get('at', 0) + 4.0
                previous_exit = previous_element['exit']['at']
            
            # Stagger current element after previous exits
            staggered[i].setdefault('enter', {})['at'] = previous_exit + 0.5
        
        return staggered
    
    def _redistribute_to_available_columns(self, elements: List[Dict[str, Any]], 
                                         template: LayoutTemplate) -> Optional[List[Dict[str, Any]]]:
        """Try to redistribute elements to available columns"""
        redistributed = [dict(element) for element in elements]
        
        # Find columns with available capacity
        available_columns = []
        for column, region in template.regions.items():
            if region.max_elements > 0:  # Has capacity
                available_columns.append((column, region.max_elements))
        
        if len(available_columns) <= 1:
            return None  # Can't redistribute
        
        # Simple round-robin redistribution
        current_column_idx = 0
        for i, element in enumerate(redistributed):
            if i > 0:  # Keep first element in original position
                column_name = available_columns[current_column_idx % len(available_columns)][0]
                element['column'] = column_name
                current_column_idx += 1
        
        return redistributed
    
    def _split_elements_across_scenes(self, elements: List[Dict[str, Any]], 
                                    max_per_scene: int) -> List[Dict[str, Any]]:
        """Split elements across multiple scene boundaries"""
        if len(elements) <= max_per_scene:
            return elements
        
        split_elements = []
        scene_duration = 6.0  # Default scene duration
        
        for i, element in enumerate(elements):
            new_element = dict(element)
            
            # Calculate which scene this element belongs to
            scene_number = i // max_per_scene
            position_in_scene = i % max_per_scene
            
            # Adjust timing based on scene
            base_enter_time = scene_number * scene_duration
            original_enter = element.get('enter', {}).get('at', 0)
            
            new_element.setdefault('enter', {})['at'] = base_enter_time + (position_in_scene * 1.5)
            
            # Add scene boundary markers
            new_element['scene_boundary'] = scene_number
            if position_in_scene == 0 and scene_number > 0:
                new_element['requires_scene_clear'] = True
            
            split_elements.append(new_element)
        
        return split_elements
    
    def suggest_better_template(self, elements: List[Dict[str, Any]], 
                               current_template: str = 'single') -> str:
        """
        Suggest a better template based on element distribution
        
        Args:
            elements: List of elements to analyze
            current_template: Current template name
            
        Returns:
            Suggested template name
        """
        # Count elements by intended column/position
        column_counts = {}
        for element in elements:
            column = element.get('column', 'center')
            column_counts[column] = column_counts.get(column, 0) + 1
        
        unique_columns = len([col for col, count in column_counts.items() if count > 0])
        max_elements_per_column = max(column_counts.values()) if column_counts else 0
        
        # Suggest based on column distribution
        if unique_columns <= 1 and max_elements_per_column <= 3:
            return 'single'
        elif unique_columns == 2 or ('left' in column_counts and 'right' in column_counts):
            return 'two_column'
        elif unique_columns >= 3:
            return 'three_column'
        else:
            # If current template might work with modifications
            current_template_obj = self.get_template(current_template)
            if current_template_obj:
                total_capacity = sum(region.max_elements for region in current_template_obj.regions.values())
                if len(elements) <= total_capacity:
                    return current_template
        
        # Default escalation: single -> two_column -> three_column
        if current_template == 'single':
            return 'two_column'
        elif current_template == 'two_column':
            return 'three_column'
        else:
            return 'three_column'  # Already at max complexity
    
    def get_overflow_report(self, template_name: str, 
                           elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate detailed overflow analysis report
        
        Args:
            template_name: Template to analyze against
            elements: Elements to analyze
            
        Returns:
            Dictionary with overflow analysis
        """
        template = self.get_template(template_name)
        if not template:
            return {'error': f'Template {template_name} not found'}
        
        # Analyze each column
        column_analysis = {}
        total_overflows = 0
        
        column_groups = {}
        for element in elements:
            column = element.get('column', 'center')
            if column not in column_groups:
                column_groups[column] = []
            column_groups[column].append(element)
        
        for column, column_elements in column_groups.items():
            region = template.get_region(column)
            if not region:
                column_analysis[column] = {
                    'status': 'invalid_column',
                    'issue': f'Column {column} not supported in template'
                }
                continue
            
            max_concurrent = self._get_max_concurrent_elements(column_elements)
            overflow_amount = max(0, max_concurrent - region.max_elements)
            
            column_analysis[column] = {
                'status': 'overflow' if overflow_amount > 0 else 'ok',
                'max_concurrent': max_concurrent,
                'capacity': region.max_elements,
                'overflow_amount': overflow_amount,
                'elements': [elem.get('key', 'unknown') for elem in column_elements]
            }
            
            total_overflows += overflow_amount
        
        # Generate recommendations
        recommendations = []
        if total_overflows > 0:
            recommendations.append(f"Total overflow: {total_overflows} elements exceed capacity")
            recommendations.append("Consider time staggering, column redistribution, or template change")
            
            better_template = self.suggest_better_template(elements, template_name)
            if better_template != template_name:
                recommendations.append(f"Suggested template: {better_template}")
        
        return {
            'template': template_name,
            'total_elements': len(elements),
            'total_overflows': total_overflows,
            'column_analysis': column_analysis,
            'recommendations': recommendations
        }
    
    def _get_max_concurrent_elements(self, elements: List[Dict[str, Any]]) -> int:
        """Calculate maximum concurrent elements based on enter/exit timing"""
        # Create timeline events
        events = []
        for element in elements:
            enter_time = element.get('enter', {}).get('at', 0)
            exit_time = element.get('exit', {}).get('at', float('inf'))
            events.append(('enter', enter_time, element['key']))
            if exit_time != float('inf'):
                events.append(('exit', exit_time, element['key']))
        
        # Sort by time
        events.sort(key=lambda x: x[1])
        
        # Count concurrent elements
        active_elements = set()
        max_concurrent = 0
        
        for event_type, time, element_key in events:
            if event_type == 'enter':
                active_elements.add(element_key)
            else:
                active_elements.discard(element_key)
            max_concurrent = max(max_concurrent, len(active_elements))
        
        return max_concurrent
    
    def _create_builtin_templates(self) -> Dict[str, LayoutTemplate]:
        """Create the built-in layout templates"""
        templates = {}
        
        # Single column template - full width, centered
        templates['single'] = LayoutTemplate(
            name='single',
            description='Single column layout with full-width content',
            regions={
                'center': Region(
                    x_start=0.06,
                    x_end=0.94,
                    y_start=0.06,
                    y_end=0.94,
                    max_elements=1,
                    z_index_base=1
                ),
                # Alternative names for center
                'left': Region(
                    x_start=0.06,
                    x_end=0.94,
                    y_start=0.06,
                    y_end=0.94,
                    max_elements=1,
                    z_index_base=1
                ),
                'right': Region(
                    x_start=0.06,
                    x_end=0.94,
                    y_start=0.06,
                    y_end=0.94,
                    max_elements=1,
                    z_index_base=1
                )
            }
        )
        
        # Two column template - left and right halves
        templates['two_column'] = LayoutTemplate(
            name='two_column',
            description='Two column layout with left and right sections',
            regions={
                'left': Region(
                    x_start=0.06,
                    x_end=0.48,  # Leave 2% gap in middle (48% + 2% + 48% = 98%)
                    y_start=0.06,
                    y_end=0.94,
                    max_elements=1,
                    z_index_base=1
                ),
                'right': Region(
                    x_start=0.52,
                    x_end=0.94,
                    y_start=0.06,
                    y_end=0.94,
                    max_elements=1,
                    z_index_base=1
                ),
                'center': Region(
                    x_start=0.25,  # Centered region for titles, etc.
                    x_end=0.75,
                    y_start=0.06,
                    y_end=0.94,
                    max_elements=1,
                    z_index_base=2  # Higher z-index for overlays
                )
            }
        )
        
        # Three column template - left, center, right thirds
        templates['three_column'] = LayoutTemplate(
            name='three_column',
            description='Three column layout with equal thirds',
            regions={
                'left': Region(
                    x_start=0.06,
                    x_end=0.32,  # ~31% width with 1% gaps
                    y_start=0.06,
                    y_end=0.94,
                    max_elements=1,
                    z_index_base=1
                ),
                'center': Region(
                    x_start=0.34,
                    x_end=0.66,  # ~31% width
                    y_start=0.06,
                    y_end=0.94,
                    max_elements=1,
                    z_index_base=1
                ),
                'right': Region(
                    x_start=0.68,
                    x_end=0.94,  # ~31% width
                    y_start=0.06,
                    y_end=0.94,
                    max_elements=1,
                    z_index_base=1
                )
            }
        )
        
        return templates
    
    def generate_manim_positions(self, template_name: str, 
                               frame_width: float = 14.0, 
                               frame_height: float = 8.0) -> Dict[str, str]:
        """
        Generate Manim position constants for a template
        
        Args:
            template_name: Name of the template
            frame_width: Manim frame width (default 14.0)
            frame_height: Manim frame height (default 8.0)
            
        Returns:
            Dictionary mapping column names to Manim position expressions
        """
        template = self.get_template(template_name)
        if not template:
            return {}
        
        positions = {}
        
        for column, region in template.regions.items():
            # Calculate center of region
            x_center = (region.x_start + region.x_end) / 2.0
            y_center = (region.y_start + region.y_end) / 2.0
            
            # Convert to Manim coordinates (center is origin)
            manim_x = (x_center - 0.5) * frame_width
            manim_y = (0.5 - y_center) * frame_height  # Y is flipped in Manim
            
            # Generate position expression
            if abs(manim_x) < 0.1 and abs(manim_y) < 0.1:
                positions[column] = "ORIGIN"
            elif abs(manim_x) < 0.1:
                if manim_y > 0:
                    positions[column] = f"UP * {manim_y:.2f}"
                else:
                    positions[column] = f"DOWN * {abs(manim_y):.2f}"
            elif abs(manim_y) < 0.1:
                if manim_x > 0:
                    positions[column] = f"RIGHT * {manim_x:.2f}"
                else:
                    positions[column] = f"LEFT * {abs(manim_x):.2f}"
            else:
                x_part = f"RIGHT * {manim_x:.2f}" if manim_x > 0 else f"LEFT * {abs(manim_x):.2f}"
                y_part = f"UP * {manim_y:.2f}" if manim_y > 0 else f"DOWN * {abs(manim_y):.2f}"
                positions[column] = f"{x_part} + {y_part}"
        
        return positions
    
    def get_template_code_helpers(self, template_name: str) -> str:
        """
        Generate helper code for a specific template
        
        Returns Python code string with helper functions and constants
        """
        template = self.get_template(template_name)
        if not template:
            return ""
        
        positions = self.generate_manim_positions(template_name)
        
        code = f"""
# Layout template: {template.name}
# {template.description}

# Safe margins
SAFE_MARGIN = {template.safe_margin_pct}
ELEMENT_SPACING = {template.element_spacing}

# Region positions
"""
        
        for column, position_expr in positions.items():
            var_name = f"{column.upper()}_POS"
            code += f"{var_name} = {position_expr}\n"
        
        code += """
def get_safe_frame():
    \"\"\"Get safe frame boundaries\"\"\"
    fw = config.frame_width
    fh = config.frame_height
    margin_x = fw * SAFE_MARGIN
    margin_y = fh * SAFE_MARGIN
    return {
        'left': -fw/2 + margin_x,
        'right': fw/2 - margin_x,
        'top': fh/2 - margin_y,
        'bottom': -fh/2 + margin_y
    }

def scale_to_fit_pct(mobject, max_width_pct=0.92, max_height_pct=0.92):
    \"\"\"Scale mobject to fit within percentage of safe frame\"\"\"
    safe_frame = get_safe_frame()
    max_width = (safe_frame['right'] - safe_frame['left']) * max_width_pct
    max_height = (safe_frame['top'] - safe_frame['bottom']) * max_height_pct
    
    # Get current dimensions
    width = mobject.width
    height = mobject.height
    
    # Calculate scale factors
    width_scale = max_width / width if width > max_width else 1.0
    height_scale = max_height / height if height > max_height else 1.0
    
    # Use the more restrictive scale
    scale_factor = min(width_scale, height_scale)
    
    if scale_factor < 1.0:
        mobject.scale(scale_factor)
    
    return mobject

def check_overlap(mobject1, mobject2, buffer=ELEMENT_SPACING):
    \"\"\"Check if two mobjects overlap with buffer\"\"\"
    # Get bounding boxes
    box1 = mobject1.get_bounding_box_point(UL), mobject1.get_bounding_box_point(DR)
    box2 = mobject2.get_bounding_box_point(UL), mobject2.get_bounding_box_point(DR)
    
    # Add buffer
    box1_expanded = (
        box1[0] + np.array([-buffer, buffer, 0]),  # UL with buffer
        box1[1] + np.array([buffer, -buffer, 0])   # DR with buffer
    )
    
    # Check for intersection
    return not (
        box1_expanded[1][0] < box2[0][0] or  # box1 right < box2 left
        box1_expanded[0][0] > box2[1][0] or  # box1 left > box2 right
        box1_expanded[0][1] < box2[1][1] or  # box1 top < box2 bottom
        box1_expanded[1][1] > box2[0][1]     # box1 bottom > box2 top
    )

def place_in_grid(mobject, column, template="{template_name}"):
    \"\"\"Place mobject in the specified column of the grid template\"\"\"
    positions = {positions}
    
    if column in positions:
        # Use eval to convert position expression to actual position
        pos_expr = positions[column]
        if pos_expr == "ORIGIN":
            position = ORIGIN
        else:
            # This is a simplified evaluation - in practice you'd want more robust parsing
            position = eval(pos_expr.replace("UP", "np.array([0, 1, 0])").replace("DOWN", "np.array([0, -1, 0])").replace("LEFT", "np.array([-1, 0, 0])").replace("RIGHT", "np.array([1, 0, 0])"))
        
        mobject.move_to(position)
    
    return mobject
"""
        
        return code


# Global template manager instance
template_manager = LayoutTemplateManager()


def get_template_manager() -> LayoutTemplateManager:
    """Get the global template manager instance"""
    return template_manager


def validate_template_elements(template_name: str, elements: List[Dict[str, Any]]) -> List[str]:
    """Validate elements against a template"""
    return template_manager.validate_element_placement(template_name, elements)


def get_template_positions(template_name: str) -> Dict[str, str]:
    """Get Manim position expressions for a template"""
    return template_manager.generate_manim_positions(template_name)


def get_template_helpers(template_name: str) -> str:
    """Get helper code for a template"""
    return template_manager.get_template_code_helpers(template_name)