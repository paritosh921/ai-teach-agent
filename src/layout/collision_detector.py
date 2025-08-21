"""
Collision Detection for Layout Safety

This module provides collision detection and overlap prevention utilities
for the Builder LLM system. It ensures that no visual elements occupy
the same screen space simultaneously.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CollisionType(Enum):
    """Types of collisions that can occur"""
    EXACT_OVERLAP = "exact_overlap"
    PARTIAL_OVERLAP = "partial_overlap"
    BUFFER_VIOLATION = "buffer_violation"
    Z_INDEX_CONFLICT = "z_index_conflict"


@dataclass
class BoundingBox:
    """Represents a 2D bounding box"""
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    
    @property
    def width(self) -> float:
        return self.x_max - self.x_min
    
    @property
    def height(self) -> float:
        return self.y_max - self.y_min
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @property
    def center(self) -> Tuple[float, float]:
        return ((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)
    
    def expand(self, buffer: float) -> 'BoundingBox':
        """Expand bounding box by buffer amount"""
        return BoundingBox(
            self.x_min - buffer,
            self.y_min - buffer,
            self.x_max + buffer,
            self.y_max + buffer
        )
    
    def intersects(self, other: 'BoundingBox') -> bool:
        """Check if this box intersects with another"""
        return not (
            self.x_max < other.x_min or
            self.x_min > other.x_max or
            self.y_max < other.y_min or
            self.y_min > other.y_max
        )
    
    def intersection(self, other: 'BoundingBox') -> Optional['BoundingBox']:
        """Get intersection of two bounding boxes"""
        if not self.intersects(other):
            return None
        
        return BoundingBox(
            max(self.x_min, other.x_min),
            max(self.y_min, other.y_min),
            min(self.x_max, other.x_max),
            min(self.y_max, other.y_max)
        )
    
    def union(self, other: 'BoundingBox') -> 'BoundingBox':
        """Get union of two bounding boxes"""
        return BoundingBox(
            min(self.x_min, other.x_min),
            min(self.y_min, other.y_min),
            max(self.x_max, other.x_max),
            max(self.y_max, other.y_max)
        )


@dataclass
class CollisionInfo:
    """Information about a detected collision"""
    element1_key: str
    element2_key: str
    collision_type: CollisionType
    overlap_area: float
    severity: float  # 0.0 to 1.0, higher = more severe
    suggested_resolution: str
    intersection_box: Optional[BoundingBox] = None


@dataclass
class ElementState:
    """Represents the state of an element at a specific time"""
    key: str
    element_type: str
    bounding_box: BoundingBox
    z_index: int
    visible: bool
    enter_time: float
    exit_time: float
    content: str = ""
    
    def is_active_at(self, time: float) -> bool:
        """Check if element is active at given time"""
        return self.visible and self.enter_time <= time < self.exit_time


class CollisionDetector:
    """
    Detects and analyzes collisions between visual elements
    
    Implements comprehensive collision detection including:
    - Exact overlap detection
    - Partial overlap with severity scoring
    - Buffer zone violations
    - Z-index conflict detection
    """
    
    def __init__(self, buffer_distance: float = 0.2, frame_width: float = 14.0,
                 frame_height: float = 8.0):
        """
        Initialize collision detector
        
        Args:
            buffer_distance: Minimum distance between elements
            frame_width: Total frame width
            frame_height: Total frame height
        """
        self.buffer_distance = buffer_distance
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.collision_history: List[CollisionInfo] = []
    
    def detect_collisions(self, elements: List[ElementState], 
                         time: float) -> List[CollisionInfo]:
        """
        Detect all collisions at a specific time point
        
        Args:
            elements: List of element states
            time: Time point to check
            
        Returns:
            List of detected collisions
        """
        active_elements = [e for e in elements if e.is_active_at(time)]
        collisions = []
        
        # Check all pairs of active elements
        for i in range(len(active_elements)):
            for j in range(i + 1, len(active_elements)):
                element1 = active_elements[i]
                element2 = active_elements[j]
                
                collision = self._check_element_pair(element1, element2)
                if collision:
                    collisions.append(collision)
        
        # Store in history
        self.collision_history.extend(collisions)
        
        return collisions
    
    def detect_collisions_over_time(self, elements: List[ElementState],
                                   time_points: List[float]) -> Dict[float, List[CollisionInfo]]:
        """
        Detect collisions across multiple time points
        
        Args:
            elements: List of element states
            time_points: List of time points to check
            
        Returns:
            Dictionary mapping time points to collision lists
        """
        collision_timeline = {}
        
        for time in time_points:
            collisions = self.detect_collisions(elements, time)
            if collisions:
                collision_timeline[time] = collisions
        
        return collision_timeline
    
    def get_collision_report(self) -> Dict[str, Any]:
        """Generate comprehensive collision report"""
        if not self.collision_history:
            return {
                'status': 'no_collisions',
                'total_collisions': 0,
                'collision_types': {},
                'severity_distribution': {},
                'recommendations': []
            }
        
        # Analyze collision types
        collision_types = {}
        severity_sum = 0.0
        
        for collision in self.collision_history:
            collision_type = collision.collision_type.value
            collision_types[collision_type] = collision_types.get(collision_type, 0) + 1
            severity_sum += collision.severity
        
        # Severity distribution
        severity_levels = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for collision in self.collision_history:
            if collision.severity < 0.25:
                severity_levels['low'] += 1
            elif collision.severity < 0.5:
                severity_levels['medium'] += 1
            elif collision.severity < 0.75:
                severity_levels['high'] += 1
            else:
                severity_levels['critical'] += 1
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        return {
            'status': 'collisions_detected',
            'total_collisions': len(self.collision_history),
            'collision_types': collision_types,
            'severity_distribution': severity_levels,
            'average_severity': severity_sum / len(self.collision_history),
            'recommendations': recommendations,
            'detailed_collisions': [
                {
                    'elements': [c.element1_key, c.element2_key],
                    'type': c.collision_type.value,
                    'severity': c.severity,
                    'resolution': c.suggested_resolution
                }
                for c in self.collision_history
            ]
        }
    
    def _check_element_pair(self, element1: ElementState, 
                          element2: ElementState) -> Optional[CollisionInfo]:
        """Check for collision between two elements"""
        box1 = element1.bounding_box
        box2 = element2.bounding_box
        
        # Check for any intersection
        if not box1.intersects(box2):
            # Check buffer zone violation
            buffered_box1 = box1.expand(self.buffer_distance)
            if buffered_box1.intersects(box2):
                return CollisionInfo(
                    element1_key=element1.key,
                    element2_key=element2.key,
                    collision_type=CollisionType.BUFFER_VIOLATION,
                    overlap_area=0.0,
                    severity=0.3,
                    suggested_resolution=f"Increase spacing between {element1.key} and {element2.key}"
                )
            return None
        
        # Calculate intersection details
        intersection = box1.intersection(box2)
        overlap_area = intersection.area if intersection else 0.0
        
        # Determine collision type and severity
        box1_area = box1.area
        box2_area = box2.area
        
        # Calculate overlap percentage relative to smaller element
        smaller_area = min(box1_area, box2_area)
        overlap_percentage = overlap_area / smaller_area if smaller_area > 0 else 1.0
        
        if overlap_percentage > 0.9:
            collision_type = CollisionType.EXACT_OVERLAP
            severity = 1.0
        else:
            collision_type = CollisionType.PARTIAL_OVERLAP
            severity = overlap_percentage
        
        # Check for z-index conflicts
        if element1.z_index == element2.z_index and overlap_percentage > 0.1:
            collision_type = CollisionType.Z_INDEX_CONFLICT
            severity = max(severity, 0.7)
        
        # Generate resolution suggestion
        resolution = self._suggest_resolution(element1, element2, collision_type, 
                                            overlap_percentage)
        
        return CollisionInfo(
            element1_key=element1.key,
            element2_key=element2.key,
            collision_type=collision_type,
            overlap_area=overlap_area,
            severity=severity,
            suggested_resolution=resolution,
            intersection_box=intersection
        )
    
    def _suggest_resolution(self, element1: ElementState, element2: ElementState,
                          collision_type: CollisionType, overlap_percentage: float) -> str:
        """Suggest resolution strategy for collision"""
        if collision_type == CollisionType.EXACT_OVERLAP:
            # For exact overlaps, suggest timing changes or z-index separation
            if abs(element1.enter_time - element2.enter_time) < 0.5:
                return f"Stagger entrance times: delay {element2.key} by 1-2 seconds"
            else:
                return f"Use different z-index or fade {element1.key} before showing {element2.key}"
        
        elif collision_type == CollisionType.Z_INDEX_CONFLICT:
            return f"Set different z-index values: {element1.key} and {element2.key}"
        
        elif collision_type == CollisionType.BUFFER_VIOLATION:
            return f"Increase spacing: move elements at least {self.buffer_distance:.1f} units apart"
        
        elif collision_type == CollisionType.PARTIAL_OVERLAP:
            if overlap_percentage > 0.5:
                return f"Major overlap: scale elements down by {100 - int(overlap_percentage * 80)}%"
            else:
                return f"Minor overlap: shift {element2.key} by {self.buffer_distance:.1f} units"
        
        return "Review element positioning and timing"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate overall recommendations based on collision history"""
        if not self.collision_history:
            return []
        
        recommendations = []
        
        # Count collision types
        type_counts = {}
        for collision in self.collision_history:
            collision_type = collision.collision_type.value
            type_counts[collision_type] = type_counts.get(collision_type, 0) + 1
        
        # Generate type-specific recommendations
        if type_counts.get('exact_overlap', 0) > 0:
            recommendations.append(
                "Multiple exact overlaps detected. Review element timing and use "
                "FadeOut animations before introducing new elements in the same region."
            )
        
        if type_counts.get('buffer_violation', 0) > 2:
            recommendations.append(
                f"Frequent buffer violations. Consider increasing minimum spacing "
                f"to {self.buffer_distance * 1.5:.1f} units."
            )
        
        if type_counts.get('z_index_conflict', 0) > 0:
            recommendations.append(
                "Z-index conflicts detected. Assign explicit z-index values with "
                "background=1, main=2, foreground=3, overlay=4."
            )
        
        # Severity-based recommendations
        high_severity_count = sum(1 for c in self.collision_history if c.severity > 0.7)
        if high_severity_count > 0:
            recommendations.append(
                f"{high_severity_count} high-severity collisions found. These require "
                "immediate attention to ensure professional video quality."
            )
        
        return recommendations


def create_element_from_spec(element_spec: Dict[str, Any], 
                           estimated_bounds: Tuple[float, float, float, float]) -> ElementState:
    """Create ElementState from element specification"""
    key = element_spec['key']
    element_type = element_spec['type']
    
    # Create bounding box
    x_min, y_min, x_max, y_max = estimated_bounds
    bounding_box = BoundingBox(x_min, y_min, x_max, y_max)
    
    # Get timing information
    enter_time = element_spec.get('enter', {}).get('at', 0.0)
    exit_time = element_spec.get('exit', {}).get('at', float('inf'))
    
    # Get z-index
    z_index = element_spec.get('z_index', 1)
    
    # Get content
    content = element_spec.get('content', element_spec.get('tex', ''))
    
    return ElementState(
        key=key,
        element_type=element_type,
        bounding_box=bounding_box,
        z_index=z_index,
        visible=True,
        enter_time=enter_time,
        exit_time=exit_time,
        content=content
    )


def validate_layout_safety(elements: List[Dict[str, Any]], 
                         time_points: Optional[List[float]] = None) -> Dict[str, Any]:
    """
    High-level function to validate layout safety for a set of elements
    
    Args:
        elements: List of element specifications
        time_points: Optional list of time points to check (auto-generated if None)
        
    Returns:
        Validation report with collision information and recommendations
    """
    # Create collision detector
    detector = CollisionDetector()
    
    # Convert specifications to element states
    element_states = []
    for element_spec in elements:
        # Estimate bounds (simplified for validation)
        bounds = (-1.0, -0.5, 1.0, 0.5)  # Default bounds
        element_state = create_element_from_spec(element_spec, bounds)
        element_states.append(element_state)
    
    # Generate time points if not provided
    if time_points is None:
        all_times = set()
        for element in element_states:
            all_times.add(element.enter_time)
            if element.exit_time != float('inf'):
                all_times.add(element.exit_time)
        time_points = sorted(all_times)
        
        # Add intermediate points
        extended_points = []
        for i, time in enumerate(time_points):
            extended_points.append(time)
            if i < len(time_points) - 1:
                mid_time = (time + time_points[i + 1]) / 2
                extended_points.append(mid_time)
        time_points = extended_points
    
    # Detect collisions across timeline
    collision_timeline = detector.detect_collisions_over_time(element_states, time_points)
    
    # Generate report
    report = detector.get_collision_report()
    report['collision_timeline'] = collision_timeline
    report['checked_time_points'] = time_points
    
    return report