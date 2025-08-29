"""
Position Mapping System for Advanced Layout Management

This module implements a comprehensive position mapping system that tracks
all screen elements across time, prevents overlaps, and manages content
continuity between scenes.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class ElementState(Enum):
    """Element lifecycle states"""
    PLANNED = "planned"      # Element is planned but not yet visible
    ENTERING = "entering"    # Element is animating in
    ACTIVE = "active"        # Element is fully visible and active
    EXITING = "exiting"      # Element is animating out
    HIDDEN = "hidden"        # Element exists but is not visible
    REMOVED = "removed"      # Element has been removed from scene


class PositionRegion(Enum):
    """Screen regions for element positioning"""
    CENTER = "center"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    FULL_SCREEN = "full_screen"


@dataclass
class ElementBounds:
    """Represents element boundaries and positioning"""
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    z_index: int = 0
    
    @property
    def width(self) -> float:
        return self.x_max - self.x_min
    
    @property
    def height(self) -> float:
        return self.y_max - self.y_min
    
    @property
    def center(self) -> Tuple[float, float]:
        return ((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    def overlaps_with(self, other: 'ElementBounds', buffer: float = 0.1) -> bool:
        """Check if this element overlaps with another (with buffer)"""
        return not (self.x_max + buffer <= other.x_min or
                   self.x_min - buffer >= other.x_max or
                   self.y_max + buffer <= other.y_min or
                   self.y_min - buffer >= other.y_max)
    
    def intersection_area(self, other: 'ElementBounds') -> float:
        """Calculate intersection area with another element"""
        if not self.overlaps_with(other, buffer=0):
            return 0.0
        
        x_overlap = min(self.x_max, other.x_max) - max(self.x_min, other.x_min)
        y_overlap = min(self.y_max, other.y_max) - max(self.y_min, other.y_min)
        
        return max(0, x_overlap) * max(0, y_overlap)
    
    def scale(self, factor: float) -> 'ElementBounds':
        """Scale element bounds by factor around center"""
        cx, cy = self.center
        new_width = self.width * factor
        new_height = self.height * factor
        
        return ElementBounds(
            x_min=cx - new_width / 2,
            y_min=cy - new_height / 2,
            x_max=cx + new_width / 2,
            y_max=cy + new_height / 2,
            z_index=self.z_index
        )
    
    def move_to(self, new_center: Tuple[float, float]) -> 'ElementBounds':
        """Move element to new center position"""
        cx, cy = new_center
        half_width = self.width / 2
        half_height = self.height / 2
        
        return ElementBounds(
            x_min=cx - half_width,
            y_min=cy - half_height,
            x_max=cx + half_width,
            y_max=cy + half_height,
            z_index=self.z_index
        )


@dataclass
class PositionedElement:
    """Represents a positioned element with full lifecycle tracking"""
    key: str
    element_type: str  # Text, MathTex, AxesPlot, etc.
    bounds: ElementBounds
    state: ElementState = ElementState.PLANNED
    enter_time: float = 0.0
    exit_time: float = float('inf')
    region: PositionRegion = PositionRegion.CENTER
    content: str = ""
    font_size: int = 42
    priority: int = 1  # Higher priority elements get better positions
    dependencies: List[str] = field(default_factory=list)  # Elements this depends on
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_visible_at_time(self, time: float) -> bool:
        """Check if element is visible at given time"""
        return (self.enter_time <= time < self.exit_time and 
                self.state in [ElementState.ENTERING, ElementState.ACTIVE, ElementState.EXITING])
    
    def get_overlap_penalty(self, other: 'PositionedElement') -> float:
        """Calculate overlap penalty with another element"""
        if not self.bounds.overlaps_with(other.bounds):
            return 0.0
        
        # Calculate intersection area
        intersection = self.bounds.intersection_area(other.bounds)
        min_area = min(self.bounds.area, other.bounds.area)
        
        if min_area == 0:
            return 0.0
        
        # Penalty based on percentage of overlap
        overlap_percentage = intersection / min_area
        return overlap_percentage * 10  # Scale penalty


@dataclass
class SafeFrame:
    """Screen safe area configuration"""
    width: float = 14.0      # Manim standard width
    height: float = 8.0      # Manim standard height
    margin_pct: float = 0.06  # 6% safe margin
    
    @property
    def safe_bounds(self) -> ElementBounds:
        """Get safe area bounds"""
        margin_x = self.width * self.margin_pct
        margin_y = self.height * self.margin_pct
        
        return ElementBounds(
            x_min=-self.width/2 + margin_x,
            y_min=-self.height/2 + margin_y,
            x_max=self.width/2 - margin_x,
            y_max=self.height/2 - margin_y
        )
    
    def get_region_bounds(self, region: PositionRegion) -> ElementBounds:
        """Get bounds for a specific screen region"""
        safe = self.safe_bounds
        
        region_map = {
            PositionRegion.CENTER: ElementBounds(
                safe.x_min + safe.width * 0.2, safe.y_min + safe.height * 0.2,
                safe.x_max - safe.width * 0.2, safe.y_max - safe.height * 0.2
            ),
            PositionRegion.TOP: ElementBounds(
                safe.x_min, safe.y_min + safe.height * 0.6,
                safe.x_max, safe.y_max
            ),
            PositionRegion.BOTTOM: ElementBounds(
                safe.x_min, safe.y_min,
                safe.x_max, safe.y_max - safe.height * 0.6
            ),
            PositionRegion.LEFT: ElementBounds(
                safe.x_min, safe.y_min + safe.height * 0.2,
                safe.x_max - safe.width * 0.6, safe.y_max - safe.height * 0.2
            ),
            PositionRegion.RIGHT: ElementBounds(
                safe.x_min + safe.width * 0.6, safe.y_min + safe.height * 0.2,
                safe.x_max, safe.y_max - safe.height * 0.2
            ),
            PositionRegion.TOP_LEFT: ElementBounds(
                safe.x_min, safe.y_min + safe.height * 0.5,
                safe.x_max - safe.width * 0.5, safe.y_max
            ),
            PositionRegion.TOP_RIGHT: ElementBounds(
                safe.x_min + safe.width * 0.5, safe.y_min + safe.height * 0.5,
                safe.x_max, safe.y_max
            ),
            PositionRegion.BOTTOM_LEFT: ElementBounds(
                safe.x_min, safe.y_min,
                safe.x_max - safe.width * 0.5, safe.y_max - safe.height * 0.5
            ),
            PositionRegion.BOTTOM_RIGHT: ElementBounds(
                safe.x_min + safe.width * 0.5, safe.y_min,
                safe.x_max, safe.y_max - safe.height * 0.5
            ),
            PositionRegion.FULL_SCREEN: safe
        }
        
        return region_map.get(region, safe)


@dataclass
class PositionMap:
    """Complete position map for all elements across time"""
    elements: Dict[str, PositionedElement] = field(default_factory=dict)
    time_snapshots: Dict[float, List[str]] = field(default_factory=dict)  # Time -> active elements
    safe_frame: SafeFrame = field(default_factory=SafeFrame)
    current_time: float = 0.0
    collision_tolerance: float = 0.1
    
    def add_element(self, element: PositionedElement) -> bool:
        """Add element to position map with conflict resolution"""
        if element.key in self.elements:
            print(f"WARNING: Element {element.key} already exists, updating...")
        
        # Check for conflicts and resolve
        if self._has_conflicts(element):
            element = self._resolve_conflicts(element)
        
        self.elements[element.key] = element
        self._update_time_snapshots(element)
        
        print(f"ADDED: Element {element.key} at {element.bounds.center} (region: {element.region.value})")
        return True
    
    def _has_conflicts(self, element: PositionedElement) -> bool:
        """Check if element has conflicts with existing elements"""
        for existing_key, existing_element in self.elements.items():
            if existing_key == element.key:
                continue
            
            # Check time overlap
            if not self._time_ranges_overlap(element, existing_element):
                continue
            
            # Check spatial overlap
            if element.bounds.overlaps_with(existing_element.bounds, self.collision_tolerance):
                return True
        
        return False
    
    def _resolve_conflicts(self, element: PositionedElement) -> PositionedElement:
        """Resolve conflicts for an element"""
        print(f"CONFLICT: Resolving conflicts for element {element.key}")
        
        # Strategy 1: Try alternative positions in same region
        for attempt in range(3):
            alternative_pos = self._find_alternative_position(element)
            if alternative_pos:
                element.bounds = alternative_pos
                if not self._has_conflicts(element):
                    print(f"RESOLVED: Found alternative position for {element.key}")
                    return element
        
        # Strategy 2: Try different region
        alternative_regions = self._get_alternative_regions(element.region)
        for alt_region in alternative_regions:
            region_bounds = self.safe_frame.get_region_bounds(alt_region)
            element.bounds = self._fit_element_in_bounds(element.bounds, region_bounds)
            element.region = alt_region
            
            if not self._has_conflicts(element):
                print(f"RESOLVED: Moved {element.key} to region {alt_region.value}")
                return element
        
        # Strategy 3: Scale down element
        for scale_factor in [0.9, 0.8, 0.7, 0.6]:
            element.bounds = element.bounds.scale(scale_factor)
            if not self._has_conflicts(element):
                print(f"RESOLVED: Scaled {element.key} by factor {scale_factor}")
                return element
        
        # Strategy 4: Adjust timing (delay entrance)
        for delay in [0.5, 1.0, 1.5, 2.0]:
            element.enter_time += delay
            element.exit_time += delay
            
            if not self._has_conflicts(element):
                print(f"RESOLVED: Delayed {element.key} by {delay} seconds")
                return element
        
        print(f"WARNING: Could not fully resolve conflicts for {element.key}")
        return element
    
    def _find_alternative_position(self, element: PositionedElement) -> Optional[ElementBounds]:
        """Find alternative position within same region"""
        region_bounds = self.safe_frame.get_region_bounds(element.region)
        
        # Try grid positions within region
        grid_positions = self._generate_grid_positions(region_bounds, 3, 3)
        
        for pos in grid_positions:
            # Position element at this grid point
            test_bounds = element.bounds.move_to(pos)
            
            # Check if it fits within region
            if self._bounds_within_bounds(test_bounds, region_bounds):
                # Check conflicts with this position
                element_copy = PositionedElement(
                    key=element.key + "_test",
                    element_type=element.element_type,
                    bounds=test_bounds,
                    enter_time=element.enter_time,
                    exit_time=element.exit_time
                )
                
                if not self._has_conflicts(element_copy):
                    return test_bounds
        
        return None
    
    def _generate_grid_positions(self, bounds: ElementBounds, rows: int, cols: int) -> List[Tuple[float, float]]:
        """Generate grid positions within bounds"""
        positions = []
        
        x_step = bounds.width / (cols + 1)
        y_step = bounds.height / (rows + 1)
        
        for i in range(1, rows + 1):
            for j in range(1, cols + 1):
                x = bounds.x_min + j * x_step
                y = bounds.y_min + i * y_step
                positions.append((x, y))
        
        return positions
    
    def _get_alternative_regions(self, current_region: PositionRegion) -> List[PositionRegion]:
        """Get alternative regions in priority order"""
        # Define region alternatives based on current region
        alternatives_map = {
            PositionRegion.CENTER: [PositionRegion.TOP, PositionRegion.BOTTOM, PositionRegion.LEFT, PositionRegion.RIGHT],
            PositionRegion.TOP: [PositionRegion.CENTER, PositionRegion.TOP_LEFT, PositionRegion.TOP_RIGHT],
            PositionRegion.BOTTOM: [PositionRegion.CENTER, PositionRegion.BOTTOM_LEFT, PositionRegion.BOTTOM_RIGHT],
            PositionRegion.LEFT: [PositionRegion.CENTER, PositionRegion.TOP_LEFT, PositionRegion.BOTTOM_LEFT],
            PositionRegion.RIGHT: [PositionRegion.CENTER, PositionRegion.TOP_RIGHT, PositionRegion.BOTTOM_RIGHT],
        }
        
        return alternatives_map.get(current_region, [PositionRegion.CENTER])
    
    def _fit_element_in_bounds(self, element_bounds: ElementBounds, container_bounds: ElementBounds) -> ElementBounds:
        """Fit element bounds within container bounds"""
        # Scale if necessary
        scale_x = min(1.0, container_bounds.width / element_bounds.width * 0.9)
        scale_y = min(1.0, container_bounds.height / element_bounds.height * 0.9)
        scale_factor = min(scale_x, scale_y)
        
        if scale_factor < 1.0:
            element_bounds = element_bounds.scale(scale_factor)
        
        # Center within container
        container_center = container_bounds.center
        return element_bounds.move_to(container_center)
    
    def _bounds_within_bounds(self, inner: ElementBounds, outer: ElementBounds) -> bool:
        """Check if inner bounds fit completely within outer bounds"""
        return (inner.x_min >= outer.x_min and inner.x_max <= outer.x_max and
                inner.y_min >= outer.y_min and inner.y_max <= outer.y_max)
    
    def _time_ranges_overlap(self, elem1: PositionedElement, elem2: PositionedElement) -> bool:
        """Check if two elements have overlapping time ranges"""
        return not (elem1.exit_time <= elem2.enter_time or elem2.exit_time <= elem1.enter_time)
    
    def _update_time_snapshots(self, element: PositionedElement):
        """Update time snapshots with element"""
        # Add to snapshots at key times
        key_times = [element.enter_time, element.exit_time]
        
        for time in key_times:
            if time not in self.time_snapshots:
                self.time_snapshots[time] = []
            
            if element.key not in self.time_snapshots[time]:
                self.time_snapshots[time].append(element.key)
    
    def get_active_elements_at_time(self, time: float) -> List[PositionedElement]:
        """Get all elements active at given time"""
        active = []
        
        for element in self.elements.values():
            if element.is_visible_at_time(time):
                active.append(element)
        
        return active
    
    def detect_collisions_at_time(self, time: float) -> List[Tuple[str, str, float]]:
        """Detect collisions between elements at given time"""
        collisions = []
        active_elements = self.get_active_elements_at_time(time)
        
        for i in range(len(active_elements)):
            for j in range(i + 1, len(active_elements)):
                elem1, elem2 = active_elements[i], active_elements[j]
                
                if elem1.bounds.overlaps_with(elem2.bounds, self.collision_tolerance):
                    overlap_area = elem1.bounds.intersection_area(elem2.bounds)
                    collisions.append((elem1.key, elem2.key, overlap_area))
        
        return collisions
    
    def optimize_layout(self) -> Dict[str, Any]:
        """Optimize entire layout to minimize overlaps"""
        print("OPTIMIZING: Starting layout optimization...")
        
        total_penalty = 0
        iterations = 0
        max_iterations = 10
        
        while iterations < max_iterations:
            penalties = []
            
            # Calculate penalties for all element pairs
            for elem1_key, elem1 in self.elements.items():
                for elem2_key, elem2 in self.elements.items():
                    if elem1_key >= elem2_key:  # Avoid double counting
                        continue
                    
                    if self._time_ranges_overlap(elem1, elem2):
                        penalty = elem1.get_overlap_penalty(elem2)
                        if penalty > 0:
                            penalties.append((elem1_key, elem2_key, penalty))
            
            if not penalties:
                break
            
            # Sort by penalty (highest first)
            penalties.sort(key=lambda x: x[2], reverse=True)
            
            # Fix the worst collision
            elem1_key, elem2_key, penalty = penalties[0]
            elem1, elem2 = self.elements[elem1_key], self.elements[elem2_key]
            
            # Move lower priority element
            if elem1.priority < elem2.priority:
                self._relocate_element(elem1_key)
            else:
                self._relocate_element(elem2_key)
            
            total_penalty += penalty
            iterations += 1
        
        optimization_result = {
            'iterations': iterations,
            'total_penalty_resolved': total_penalty,
            'remaining_collisions': len(self.detect_all_collisions()),
            'optimization_complete': iterations < max_iterations
        }
        
        print(f"OPTIMIZATION: Completed in {iterations} iterations, penalty resolved: {total_penalty:.2f}")
        return optimization_result
    
    def _relocate_element(self, element_key: str):
        """Relocate an element to resolve conflicts"""
        element = self.elements[element_key]
        
        # Try alternative position
        alternative_pos = self._find_alternative_position(element)
        if alternative_pos:
            element.bounds = alternative_pos
            return
        
        # Try different region
        alternative_regions = self._get_alternative_regions(element.region)
        for alt_region in alternative_regions:
            region_bounds = self.safe_frame.get_region_bounds(alt_region)
            element.bounds = self._fit_element_in_bounds(element.bounds, region_bounds)
            element.region = alt_region
            
            if not self._has_conflicts(element):
                return
        
        # Scale down
        element.bounds = element.bounds.scale(0.8)
    
    def detect_all_collisions(self) -> List[Dict[str, Any]]:
        """Detect all collisions across all times"""
        all_collisions = []
        
        # Sample key time points
        all_times = set()
        for element in self.elements.values():
            all_times.add(element.enter_time)
            all_times.add(element.exit_time)
            all_times.add((element.enter_time + element.exit_time) / 2)  # Midpoint
        
        for time in sorted(all_times):
            collisions = self.detect_collisions_at_time(time)
            for elem1_key, elem2_key, overlap_area in collisions:
                all_collisions.append({
                    'time': time,
                    'element1': elem1_key,
                    'element2': elem2_key,
                    'overlap_area': overlap_area,
                    'severity': 'critical' if overlap_area > 1.0 else 'moderate'
                })
        
        return all_collisions
    
    def generate_layout_report(self) -> Dict[str, Any]:
        """Generate comprehensive layout analysis report"""
        total_elements = len(self.elements)
        all_collisions = self.detect_all_collisions()
        critical_collisions = [c for c in all_collisions if c['severity'] == 'critical']
        
        # Region usage analysis
        region_usage = {}
        for element in self.elements.values():
            region = element.region.value
            region_usage[region] = region_usage.get(region, 0) + 1
        
        # Time analysis
        time_points = sorted(set(
            time for element in self.elements.values()
            for time in [element.enter_time, element.exit_time]
        ))
        
        max_concurrent_elements = 0
        for time in time_points:
            concurrent = len(self.get_active_elements_at_time(time))
            max_concurrent_elements = max(max_concurrent_elements, concurrent)
        
        return {
            'total_elements': total_elements,
            'total_collisions': len(all_collisions),
            'critical_collisions': len(critical_collisions),
            'max_concurrent_elements': max_concurrent_elements,
            'region_usage': region_usage,
            'collision_details': all_collisions,
            'layout_efficiency': max(0, 1.0 - (len(critical_collisions) * 0.2)),
            'recommendations': self._generate_layout_recommendations(all_collisions, region_usage)
        }
    
    def _generate_layout_recommendations(self, collisions: List[Dict[str, Any]], 
                                       region_usage: Dict[str, int]) -> List[str]:
        """Generate layout improvement recommendations"""
        recommendations = []
        
        if len(collisions) > 0:
            recommendations.append(f"Resolve {len(collisions)} element collisions")
        
        # Check for overcrowded regions
        max_usage = max(region_usage.values()) if region_usage else 0
        if max_usage > 3:
            overcrowded_regions = [region for region, count in region_usage.items() if count > 3]
            recommendations.append(f"Redistribute elements from overcrowded regions: {', '.join(overcrowded_regions)}")
        
        # Check for unused regions
        all_regions = {region.value for region in PositionRegion}
        unused_regions = all_regions - set(region_usage.keys())
        if unused_regions and len(region_usage) > 0:
            recommendations.append(f"Consider utilizing unused regions: {', '.join(unused_regions)}")
        
        return recommendations
    
    def save_to_file(self, filepath: str):
        """Save position map to JSON file"""
        data = {
            'elements': {
                key: {
                    'key': elem.key,
                    'element_type': elem.element_type,
                    'bounds': {
                        'x_min': elem.bounds.x_min,
                        'y_min': elem.bounds.y_min,
                        'x_max': elem.bounds.x_max,
                        'y_max': elem.bounds.y_max,
                        'z_index': elem.bounds.z_index
                    },
                    'state': elem.state.value,
                    'enter_time': elem.enter_time,
                    'exit_time': elem.exit_time,
                    'region': elem.region.value,
                    'content': elem.content,
                    'font_size': elem.font_size,
                    'priority': elem.priority
                }
                for key, elem in self.elements.items()
            },
            'safe_frame': {
                'width': self.safe_frame.width,
                'height': self.safe_frame.height,
                'margin_pct': self.safe_frame.margin_pct
            },
            'current_time': self.current_time,
            'collision_tolerance': self.collision_tolerance
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'PositionMap':
        """Load position map from JSON file"""
        if not Path(filepath).exists():
            return cls()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        position_map = cls()
        position_map.current_time = data.get('current_time', 0.0)
        position_map.collision_tolerance = data.get('collision_tolerance', 0.1)
        
        # Load safe frame
        if 'safe_frame' in data:
            sf_data = data['safe_frame']
            position_map.safe_frame = SafeFrame(
                width=sf_data.get('width', 14.0),
                height=sf_data.get('height', 8.0),
                margin_pct=sf_data.get('margin_pct', 0.06)
            )
        
        # Load elements
        for key, elem_data in data.get('elements', {}).items():
            bounds_data = elem_data['bounds']
            bounds = ElementBounds(
                x_min=bounds_data['x_min'],
                y_min=bounds_data['y_min'],
                x_max=bounds_data['x_max'],
                y_max=bounds_data['y_max'],
                z_index=bounds_data.get('z_index', 0)
            )
            
            element = PositionedElement(
                key=elem_data['key'],
                element_type=elem_data['element_type'],
                bounds=bounds,
                state=ElementState(elem_data.get('state', 'planned')),
                enter_time=elem_data.get('enter_time', 0.0),
                exit_time=elem_data.get('exit_time', float('inf')),
                region=PositionRegion(elem_data.get('region', 'center')),
                content=elem_data.get('content', ''),
                font_size=elem_data.get('font_size', 42),
                priority=elem_data.get('priority', 1)
            )
            
            position_map.elements[key] = element
        
        return position_map


class PositionMapper:
    """Main interface for position mapping operations"""
    
    def __init__(self, safe_frame: Optional[SafeFrame] = None):
        self.position_map = PositionMap(safe_frame=safe_frame or SafeFrame())
        
    def create_element_from_yaml(self, yaml_element: Dict[str, Any], 
                                scene_id: str, enter_time: float = 0.0) -> PositionedElement:
        """Create positioned element from YAML specification"""
        key = yaml_element.get('key', f"element_{len(self.position_map.elements)}")
        element_type = yaml_element.get('type', 'Text')
        column = yaml_element.get('column', 'center')
        
        # Map column to region
        region_map = {
            'center': PositionRegion.CENTER,
            'left': PositionRegion.LEFT,
            'right': PositionRegion.RIGHT,
            'top': PositionRegion.TOP,
            'bottom': PositionRegion.BOTTOM
        }
        region = region_map.get(column, PositionRegion.CENTER)
        
        # Get region bounds and create element bounds
        region_bounds = self.position_map.safe_frame.get_region_bounds(region)
        
        # Estimate element size based on type and content
        element_bounds = self._estimate_element_bounds(yaml_element, region_bounds)
        
        # Extract timing
        enter_anim = yaml_element.get('enter', {})
        exit_anim = yaml_element.get('exit')
        
        element_enter_time = enter_time + enter_anim.get('at', 0.0)
        element_exit_time = float('inf')
        
        if exit_anim:
            element_exit_time = enter_time + exit_anim.get('at', 10.0)
        
        return PositionedElement(
            key=f"{scene_id}_{key}",
            element_type=element_type,
            bounds=element_bounds,
            region=region,
            enter_time=element_enter_time,
            exit_time=element_exit_time,
            content=yaml_element.get('text', yaml_element.get('content', '')),
            font_size=yaml_element.get('style', {}).get('font_size', 42),
            priority=self._calculate_element_priority(yaml_element)
        )
    
    def _estimate_element_bounds(self, yaml_element: Dict[str, Any], 
                                region_bounds: ElementBounds) -> ElementBounds:
        """Estimate element bounds based on content and type"""
        element_type = yaml_element.get('type', 'Text')
        content = yaml_element.get('text', yaml_element.get('content', ''))
        font_size = yaml_element.get('style', {}).get('font_size', 42)
        
        # Basic size estimation
        if element_type in ['Text', 'MathTex']:
            # Estimate text dimensions
            char_width = font_size * 0.6  # Rough character width
            char_height = font_size * 1.2  # Rough character height
            
            # Estimate lines
            max_width = region_bounds.width * 0.8
            chars_per_line = max(1, int(max_width / char_width))
            lines = max(1, len(content) / chars_per_line)
            
            width = min(len(content) * char_width, max_width)
            height = lines * char_height
            
        elif element_type == 'AxesPlot':
            # Plots are typically larger
            width = region_bounds.width * 0.7
            height = region_bounds.height * 0.6
            
        else:
            # Default sizing
            width = region_bounds.width * 0.5
            height = region_bounds.height * 0.3
        
        # Center in region
        center = region_bounds.center
        
        return ElementBounds(
            x_min=center[0] - width/2,
            y_min=center[1] - height/2,
            x_max=center[0] + width/2,
            y_max=center[1] + height/2
        )
    
    def _calculate_element_priority(self, yaml_element: Dict[str, Any]) -> int:
        """Calculate element priority for conflict resolution"""
        element_type = yaml_element.get('type', 'Text')
        
        # Priority based on element type
        type_priorities = {
            'Text': 3,      # High priority for text
            'MathTex': 4,   # Higher priority for math
            'AxesPlot': 2,  # Medium priority for plots
            'Image': 1      # Lower priority for images
        }
        
        return type_priorities.get(element_type, 2)
    
    def process_yaml_scenes(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process all scenes from YAML specification"""
        processing_results = {
            'scenes_processed': 0,
            'elements_added': 0,
            'conflicts_resolved': 0,
            'warnings': []
        }
        
        current_time = 0.0
        
        for scene in scenes:
            scene_id = scene.get('id', f'scene_{processing_results["scenes_processed"]}')
            scene_duration = scene.get('time_budget_s', 10.0)
            
            # Process elements in this scene
            layout = scene.get('layout', {})
            elements = layout.get('elements', [])
            
            for yaml_element in elements:
                try:
                    positioned_element = self.create_element_from_yaml(
                        yaml_element, scene_id, current_time
                    )
                    
                    # Adjust exit time to scene boundary
                    if positioned_element.exit_time == float('inf'):
                        positioned_element.exit_time = current_time + scene_duration
                    
                    # Add to position map
                    self.position_map.add_element(positioned_element)
                    processing_results['elements_added'] += 1
                    
                except Exception as e:
                    warning = f"Failed to process element in scene {scene_id}: {e}"
                    processing_results['warnings'].append(warning)
                    print(f"WARNING: {warning}")
            
            current_time += scene_duration
            processing_results['scenes_processed'] += 1
        
        # Optimize layout
        optimization_results = self.position_map.optimize_layout()
        processing_results['conflicts_resolved'] = optimization_results['total_penalty_resolved']
        
        return processing_results
    
    def generate_manim_positioning_code(self) -> str:
        """Generate Manim positioning code for all elements"""
        code_lines = [
            "# Generated positioning code",
            "from manim import *",
            "import numpy as np",
            "",
            "# Safe positioning utilities",
            "def safe_position(pos):",
            "    '''Ensure position is within safe frame'''",
            "    safe_x = np.clip(pos[0], -6.2, 6.2)",
            "    safe_y = np.clip(pos[1], -3.7, 3.7)",
            "    return np.array([safe_x, safe_y, pos[2] if len(pos) > 2 else 0])",
            "",
            "# Element positioning map",
            "ELEMENT_POSITIONS = {"
        ]
        
        for element in self.position_map.elements.values():
            center = element.bounds.center
            code_lines.append(
                f"    '{element.key}': {{'pos': [{center[0]:.2f}, {center[1]:.2f}, 0], "
                f"'enter': {element.enter_time}, 'exit': {element.exit_time}}},"
            )
        
        code_lines.extend([
            "}",
            "",
            "def get_element_position(key):",
            "    '''Get safe position for element'''",
            "    if key in ELEMENT_POSITIONS:",
            "        return safe_position(ELEMENT_POSITIONS[key]['pos'])",
            "    return ORIGIN",
            ""
        ])
        
        return '\n'.join(code_lines)
    
    def get_layout_report(self) -> Dict[str, Any]:
        """Get comprehensive layout analysis report"""
        return self.position_map.generate_layout_report()