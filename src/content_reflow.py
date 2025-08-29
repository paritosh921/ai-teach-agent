"""
Intelligent Content Reflow System

This module manages content continuity between scenes, handles element
persistence, and provides intelligent reflow when space constraints occur.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from copy import deepcopy

from .position_mapper import PositionedElement, ElementBounds, PositionRegion, SafeFrame


class ReflowStrategy(Enum):
    """Strategies for handling content reflow"""
    SCALE_DOWN = "scale_down"           # Reduce element sizes
    REDISTRIBUTE = "redistribute"       # Move elements to different regions
    PAGINATE = "paginate"              # Split content across multiple scenes
    STACK_VERTICAL = "stack_vertical"   # Stack elements vertically
    PRIORITIZE = "prioritize"          # Keep high-priority elements, fade others


class ContinuityType(Enum):
    """Types of element continuity"""
    PERSISTENT = "persistent"          # Element stays across multiple scenes
    TRANSFORMING = "transforming"      # Element changes but maintains identity
    REFERENTIAL = "referential"       # Element is referenced but may disappear
    CONTEXTUAL = "contextual"          # Element provides context for other elements


@dataclass
class ElementContinuity:
    """Tracks element continuity across scenes"""
    element_key: str
    continuity_type: ContinuityType
    source_scene: str
    target_scenes: List[str] = field(default_factory=list)
    transformation_rules: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # Higher priority = more important to maintain
    dependencies: List[str] = field(default_factory=list)  # Elements this depends on
    
    def should_persist_in_scene(self, scene_id: str) -> bool:
        """Check if element should persist in given scene"""
        return scene_id in self.target_scenes


@dataclass
class ReflowOperation:
    """Represents a content reflow operation"""
    operation_id: str
    strategy: ReflowStrategy
    affected_elements: List[str]
    scene_id: str
    reason: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    fallback_strategy: Optional[ReflowStrategy] = None


@dataclass
class SceneTransition:
    """Manages transition between scenes"""
    from_scene: str
    to_scene: str
    persistent_elements: List[str] = field(default_factory=list)
    new_elements: List[str] = field(default_factory=list)
    removed_elements: List[str] = field(default_factory=list)
    transition_effects: Dict[str, str] = field(default_factory=dict)


class ContentReflowManager:
    """
    Manages intelligent content reflow and scene continuity
    
    This system handles:
    - Element persistence across scenes
    - Automatic content reflow when space is limited
    - Scene-to-scene transitions
    - Content prioritization and overflow management
    """
    
    def __init__(self, safe_frame: Optional[SafeFrame] = None):
        self.safe_frame = safe_frame or SafeFrame()
        self.element_continuities: Dict[str, ElementContinuity] = {}
        self.scene_transitions: Dict[str, SceneTransition] = {}
        self.reflow_history: List[ReflowOperation] = []
        self.global_elements: Dict[str, PositionedElement] = {}  # Elements that persist across scenes
        
    def register_element_continuity(self, continuity: ElementContinuity):
        """Register element continuity requirements"""
        self.element_continuities[continuity.element_key] = continuity
        print(f"CONTINUITY: Registered {continuity.continuity_type.value} continuity for {continuity.element_key}")
    
    def plan_scene_transition(self, from_scene: str, to_scene: str, 
                            from_elements: List[PositionedElement],
                            to_elements: List[PositionedElement]) -> SceneTransition:
        """Plan transition between two scenes"""
        
        from_keys = {elem.key for elem in from_elements}
        to_keys = {elem.key for elem in to_elements}
        
        # Identify different element categories
        persistent = []
        new = []
        removed = []
        
        for elem_key in to_keys:
            if elem_key in from_keys:
                # Check if this should persist based on continuity rules
                continuity = self.element_continuities.get(elem_key)
                if continuity and continuity.should_persist_in_scene(to_scene):
                    persistent.append(elem_key)
                else:
                    new.append(elem_key)  # Re-entering element
            else:
                new.append(elem_key)
        
        for elem_key in from_keys:
            if elem_key not in to_keys:
                removed.append(elem_key)
        
        transition = SceneTransition(
            from_scene=from_scene,
            to_scene=to_scene,
            persistent_elements=persistent,
            new_elements=new,
            removed_elements=removed
        )
        
        # Plan transition effects
        transition.transition_effects = self._plan_transition_effects(transition)
        
        self.scene_transitions[f"{from_scene}_{to_scene}"] = transition
        
        print(f"TRANSITION: Planned {from_scene} → {to_scene}")
        print(f"  Persistent: {len(persistent)}, New: {len(new)}, Removed: {len(removed)}")
        
        return transition
    
    def _plan_transition_effects(self, transition: SceneTransition) -> Dict[str, str]:
        """Plan transition effects for elements"""
        effects = {}
        
        # Persistent elements: maintain position or smoothly transition
        for elem_key in transition.persistent_elements:
            continuity = self.element_continuities.get(elem_key)
            if continuity and continuity.continuity_type == ContinuityType.TRANSFORMING:
                effects[elem_key] = "transform"
            else:
                effects[elem_key] = "maintain"
        
        # New elements: fade in or animate in
        for elem_key in transition.new_elements:
            effects[elem_key] = "fade_in"
        
        # Removed elements: fade out
        for elem_key in transition.removed_elements:
            effects[elem_key] = "fade_out"
        
        return effects
    
    def check_overflow(self, scene_elements: List[PositionedElement]) -> Dict[str, Any]:
        """Check if scene has content overflow or spacing issues"""
        
        overflow_info = {
            'has_overflow': False,
            'overflow_elements': [],
            'crowded_regions': [],
            'collision_pairs': [],
            'total_collisions': 0,
            'severity': 'none'  # none, minor, moderate, severe
        }
        
        # Check for out-of-bounds elements
        safe_bounds = self.safe_frame.safe_bounds
        
        for element in scene_elements:
            if not self._element_within_bounds(element.bounds, safe_bounds):
                overflow_info['overflow_elements'].append(element.key)
        
        # Check for collisions
        collision_pairs = []
        for i in range(len(scene_elements)):
            for j in range(i + 1, len(scene_elements)):
                elem1, elem2 = scene_elements[i], scene_elements[j]
                
                if elem1.bounds.overlaps_with(elem2.bounds, buffer=0.1):
                    collision_pairs.append((elem1.key, elem2.key))
        
        overflow_info['collision_pairs'] = collision_pairs
        overflow_info['total_collisions'] = len(collision_pairs)
        
        # Check region crowding
        region_counts = {}
        for element in scene_elements:
            region = element.region.value
            region_counts[region] = region_counts.get(region, 0) + 1
        
        crowded_regions = [region for region, count in region_counts.items() if count > 3]
        overflow_info['crowded_regions'] = crowded_regions
        
        # Determine severity
        has_overflow = (len(overflow_info['overflow_elements']) > 0 or 
                       len(collision_pairs) > 0 or 
                       len(crowded_regions) > 0)
        
        overflow_info['has_overflow'] = has_overflow
        
        if not has_overflow:
            overflow_info['severity'] = 'none'
        elif len(collision_pairs) > 3 or len(overflow_info['overflow_elements']) > 2:
            overflow_info['severity'] = 'severe'
        elif len(collision_pairs) > 1 or len(crowded_regions) > 1:
            overflow_info['severity'] = 'moderate'
        else:
            overflow_info['severity'] = 'minor'
        
        return overflow_info
    
    def _element_within_bounds(self, element_bounds: ElementBounds, 
                              container_bounds: ElementBounds) -> bool:
        """Check if element is within container bounds"""
        return (element_bounds.x_min >= container_bounds.x_min and
                element_bounds.x_max <= container_bounds.x_max and
                element_bounds.y_min >= container_bounds.y_min and
                element_bounds.y_max <= container_bounds.y_max)
    
    def apply_reflow_strategy(self, scene_id: str, 
                            scene_elements: List[PositionedElement],
                            overflow_info: Dict[str, Any]) -> ReflowOperation:
        """Apply appropriate reflow strategy based on overflow analysis"""
        
        severity = overflow_info['severity']
        
        # Choose strategy based on severity and content type
        if severity == 'minor':
            strategy = ReflowStrategy.SCALE_DOWN
        elif severity == 'moderate':
            strategy = ReflowStrategy.REDISTRIBUTE
        else:  # severe
            strategy = ReflowStrategy.PAGINATE
        
        operation = ReflowOperation(
            operation_id=f"reflow_{scene_id}_{len(self.reflow_history)}",
            strategy=strategy,
            affected_elements=[elem.key for elem in scene_elements],
            scene_id=scene_id,
            reason=f"Overflow severity: {severity}",
            fallback_strategy=self._get_fallback_strategy(strategy)
        )
        
        # Execute the reflow strategy
        success = self._execute_reflow_strategy(operation, scene_elements, overflow_info)
        operation.success = success
        
        if not success and operation.fallback_strategy:
            print(f"REFLOW: Primary strategy failed, trying fallback: {operation.fallback_strategy.value}")
            operation.strategy = operation.fallback_strategy
            success = self._execute_reflow_strategy(operation, scene_elements, overflow_info)
            operation.success = success
        
        self.reflow_history.append(operation)
        return operation
    
    def _get_fallback_strategy(self, primary_strategy: ReflowStrategy) -> Optional[ReflowStrategy]:
        """Get fallback strategy for failed primary strategy"""
        fallback_map = {
            ReflowStrategy.SCALE_DOWN: ReflowStrategy.REDISTRIBUTE,
            ReflowStrategy.REDISTRIBUTE: ReflowStrategy.STACK_VERTICAL,
            ReflowStrategy.STACK_VERTICAL: ReflowStrategy.PRIORITIZE,
            ReflowStrategy.PRIORITIZE: ReflowStrategy.PAGINATE,
            ReflowStrategy.PAGINATE: None  # Last resort
        }
        return fallback_map.get(primary_strategy)
    
    def _execute_reflow_strategy(self, operation: ReflowOperation,
                               scene_elements: List[PositionedElement],
                               overflow_info: Dict[str, Any]) -> bool:
        """Execute specific reflow strategy"""
        
        strategy = operation.strategy
        
        try:
            if strategy == ReflowStrategy.SCALE_DOWN:
                return self._apply_scale_down(scene_elements, operation)
            elif strategy == ReflowStrategy.REDISTRIBUTE:
                return self._apply_redistribute(scene_elements, operation)
            elif strategy == ReflowStrategy.STACK_VERTICAL:
                return self._apply_stack_vertical(scene_elements, operation)
            elif strategy == ReflowStrategy.PRIORITIZE:
                return self._apply_prioritize(scene_elements, operation)
            elif strategy == ReflowStrategy.PAGINATE:
                return self._apply_paginate(scene_elements, operation)
            
        except Exception as e:
            print(f"REFLOW ERROR: Strategy {strategy.value} failed: {e}")
            return False
        
        return False
    
    def _apply_scale_down(self, elements: List[PositionedElement], 
                         operation: ReflowOperation) -> bool:
        """Scale down elements to fit within space"""
        scale_factor = 0.85  # 15% reduction
        
        scaled_count = 0
        for element in elements:
            # Don't scale critical elements too much
            continuity = self.element_continuities.get(element.key)
            if continuity and continuity.priority > 3:
                continue  # Skip high-priority elements
            
            # Scale bounds
            element.bounds = element.bounds.scale(scale_factor)
            
            # Scale font if it's a text element
            if element.element_type in ['Text', 'MathTex']:
                element.font_size = max(24, int(element.font_size * scale_factor))
            
            scaled_count += 1
        
        operation.parameters['scale_factor'] = scale_factor
        operation.parameters['elements_scaled'] = scaled_count
        
        print(f"REFLOW: Scaled down {scaled_count} elements by {scale_factor}")
        return scaled_count > 0
    
    def _apply_redistribute(self, elements: List[PositionedElement],
                          operation: ReflowOperation) -> bool:
        """Redistribute elements to less crowded regions"""
        
        # Count elements per region
        region_counts = {}
        for element in elements:
            region = element.region
            region_counts[region] = region_counts.get(region, 0) + 1
        
        # Find overcrowded regions
        overcrowded = [region for region, count in region_counts.items() if count > 2]
        
        if not overcrowded:
            return False
        
        redistributed_count = 0
        available_regions = [r for r in PositionRegion if region_counts.get(r, 0) < 2]
        
        for element in elements:
            if element.region in overcrowded and available_regions:
                # Move to less crowded region
                new_region = available_regions.pop(0)
                
                # Update element region and bounds
                region_bounds = self.safe_frame.get_region_bounds(new_region)
                element.bounds = self._fit_element_in_region(element.bounds, region_bounds)
                element.region = new_region
                
                redistributed_count += 1
                
                # Update region counts
                region_counts[element.region] = region_counts.get(new_region, 0) + 1
        
        operation.parameters['elements_redistributed'] = redistributed_count
        print(f"REFLOW: Redistributed {redistributed_count} elements to less crowded regions")
        return redistributed_count > 0
    
    def _apply_stack_vertical(self, elements: List[PositionedElement],
                            operation: ReflowOperation) -> bool:
        """Stack overlapping elements vertically"""
        
        # Group elements by region
        region_elements = {}
        for element in elements:
            region = element.region
            if region not in region_elements:
                region_elements[region] = []
            region_elements[region].append(element)
        
        stacked_count = 0
        
        for region, region_elems in region_elements.items():
            if len(region_elems) <= 1:
                continue
            
            # Sort by priority (higher priority at top)
            region_elems.sort(key=lambda e: self.element_continuities.get(e.key, type('', (), {'priority': 1})()).priority, reverse=True)
            
            # Stack vertically within region
            region_bounds = self.safe_frame.get_region_bounds(region)
            stack_height = region_bounds.height / len(region_elems)
            
            for i, element in enumerate(region_elems):
                # Calculate new position
                y_center = region_bounds.y_max - (i + 0.5) * stack_height
                element.bounds = element.bounds.move_to((region_bounds.center[0], y_center))
                
                # Scale if necessary
                if element.bounds.height > stack_height * 0.8:
                    scale_factor = (stack_height * 0.8) / element.bounds.height
                    element.bounds = element.bounds.scale(scale_factor)
                    
                    if element.element_type in ['Text', 'MathTex']:
                        element.font_size = max(20, int(element.font_size * scale_factor))
                
                stacked_count += 1
        
        operation.parameters['elements_stacked'] = stacked_count
        print(f"REFLOW: Stacked {stacked_count} elements vertically")
        return stacked_count > 0
    
    def _apply_prioritize(self, elements: List[PositionedElement],
                         operation: ReflowOperation) -> bool:
        """Keep high-priority elements, fade out low-priority ones"""
        
        # Sort elements by priority
        prioritized = []
        for element in elements:
            continuity = self.element_continuities.get(element.key)
            priority = continuity.priority if continuity else 1
            prioritized.append((element, priority))
        
        prioritized.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top elements that fit within space constraints
        safe_bounds = self.safe_frame.safe_bounds
        max_elements_per_region = 2
        region_counts = {}
        kept_elements = []
        removed_elements = []
        
        for element, priority in prioritized:
            region = element.region
            current_count = region_counts.get(region, 0)
            
            if current_count < max_elements_per_region:
                kept_elements.append(element)
                region_counts[region] = current_count + 1
            else:
                removed_elements.append(element)
        
        # Remove low-priority elements from the scene
        elements[:] = kept_elements
        
        operation.parameters['elements_kept'] = len(kept_elements)
        operation.parameters['elements_removed'] = len(removed_elements)
        
        print(f"REFLOW: Kept {len(kept_elements)} high-priority elements, removed {len(removed_elements)}")
        return len(removed_elements) > 0
    
    def _apply_paginate(self, elements: List[PositionedElement],
                       operation: ReflowOperation) -> bool:
        """Split content into multiple scenes (pagination)"""
        
        if len(elements) <= 3:
            return False  # Already minimal content
        
        # This is a more complex operation that would require scene splitting
        # For now, we'll simulate by marking elements for next scene
        
        # Sort by priority and keep top elements
        prioritized = []
        for element in elements:
            continuity = self.element_continuities.get(element.key)
            priority = continuity.priority if continuity else 1
            prioritized.append((element, priority))
        
        prioritized.sort(key=lambda x: x[1], reverse=True)
        
        # Keep roughly half the elements in current scene
        keep_count = max(2, len(elements) // 2)
        kept_elements = [elem for elem, _ in prioritized[:keep_count]]
        overflow_elements = [elem for elem, _ in prioritized[keep_count:]]
        
        # Update elements list
        elements[:] = kept_elements
        
        # Store overflow elements for next scene
        operation.parameters['elements_kept'] = len(kept_elements)
        operation.parameters['overflow_elements'] = [elem.key for elem in overflow_elements]
        
        print(f"REFLOW: Paginated - kept {len(kept_elements)}, moved {len(overflow_elements)} to next scene")
        return True
    
    def _fit_element_in_region(self, element_bounds: ElementBounds,
                              region_bounds: ElementBounds) -> ElementBounds:
        """Fit element bounds within region bounds"""
        
        # Scale if too large
        scale_x = min(1.0, region_bounds.width / element_bounds.width * 0.9)
        scale_y = min(1.0, region_bounds.height / element_bounds.height * 0.9)
        scale_factor = min(scale_x, scale_y)
        
        if scale_factor < 1.0:
            element_bounds = element_bounds.scale(scale_factor)
        
        # Center within region
        return element_bounds.move_to(region_bounds.center)
    
    def get_persistent_elements(self, scene_id: str) -> List[str]:
        """Get elements that should persist in given scene"""
        persistent = []
        
        for elem_key, continuity in self.element_continuities.items():
            if continuity.should_persist_in_scene(scene_id):
                persistent.append(elem_key)
        
        return persistent
    
    def generate_continuity_code(self) -> str:
        """Generate Manim code for handling element continuity"""
        
        code_lines = [
            "# Generated continuity management code",
            "from manim import *",
            "",
            "class ContinuityManager:",
            "    '''Manages element continuity across scenes'''",
            "    ",
            "    def __init__(self):",
            "        self.persistent_elements = {}",
            "        self.element_states = {}",
            "    ",
            "    def register_persistent(self, key, mobject, scene_id):",
            "        '''Register an element as persistent across scenes'''",
            "        if key not in self.persistent_elements:",
            "            self.persistent_elements[key] = {}",
            "        self.persistent_elements[key][scene_id] = mobject",
            "    ",
            "    def get_persistent(self, key, scene_id):",
            "        '''Get persistent element for scene'''",
            "        return self.persistent_elements.get(key, {}).get(scene_id)",
            "    ",
            "    def transition_element(self, key, from_scene, to_scene, transform_func=None):",
            "        '''Transition element between scenes'''",
            "        from_element = self.get_persistent(key, from_scene)",
            "        to_element = self.get_persistent(key, to_scene)",
            "        ",
            "        if from_element and to_element:",
            "            if transform_func:",
            "                return Transform(from_element, to_element)",
            "            else:",
            "                return from_element.animate.move_to(to_element.get_center())",
            "        return None",
            "",
            "# Global continuity manager instance",
            "continuity_manager = ContinuityManager()",
            ""
        ]
        
        # Add specific continuity rules
        for elem_key, continuity in self.element_continuities.items():
            if continuity.continuity_type == ContinuityType.PERSISTENT:
                code_lines.extend([
                    f"# Persistent element: {elem_key}",
                    f"# Appears in scenes: {', '.join(continuity.target_scenes)}",
                    ""
                ])
        
        return '\n'.join(code_lines)
    
    def generate_reflow_report(self) -> Dict[str, Any]:
        """Generate comprehensive reflow analysis report"""
        
        total_operations = len(self.reflow_history)
        successful_operations = sum(1 for op in self.reflow_history if op.success)
        
        # Strategy usage statistics
        strategy_stats = {}
        for operation in self.reflow_history:
            strategy = operation.strategy.value
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {'count': 0, 'success': 0}
            strategy_stats[strategy]['count'] += 1
            if operation.success:
                strategy_stats[strategy]['success'] += 1
        
        # Calculate success rates
        for strategy, stats in strategy_stats.items():
            if stats['count'] > 0:
                stats['success_rate'] = stats['success'] / stats['count']
        
        return {
            'total_reflow_operations': total_operations,
            'successful_operations': successful_operations,
            'success_rate': successful_operations / total_operations if total_operations > 0 else 0,
            'strategy_statistics': strategy_stats,
            'element_continuities': len(self.element_continuities),
            'scene_transitions': len(self.scene_transitions),
            'most_effective_strategy': max(strategy_stats.items(), 
                                         key=lambda x: x[1]['success_rate'])[0] if strategy_stats else 'none',
            'recommendations': self._generate_reflow_recommendations()
        }
    
    def _generate_reflow_recommendations(self) -> List[str]:
        """Generate recommendations for improving reflow performance"""
        recommendations = []
        
        if len(self.reflow_history) == 0:
            return ["No reflow operations performed yet"]
        
        # Analyze common failures
        failed_operations = [op for op in self.reflow_history if not op.success]
        
        if len(failed_operations) > len(self.reflow_history) * 0.3:
            recommendations.append("High failure rate - consider reducing content density")
        
        # Check if pagination is being used too frequently
        paginate_ops = [op for op in self.reflow_history if op.strategy == ReflowStrategy.PAGINATE]
        if len(paginate_ops) > 3:
            recommendations.append("Frequent pagination suggests need for better content planning")
        
        # Check for repeated issues with same elements
        problem_elements = {}
        for op in failed_operations:
            for elem in op.affected_elements:
                problem_elements[elem] = problem_elements.get(elem, 0) + 1
        
        if problem_elements:
            most_problematic = max(problem_elements.items(), key=lambda x: x[1])
            recommendations.append(f"Element '{most_problematic[0]}' frequently causes reflow issues")
        
        return recommendations if recommendations else ["Reflow system performing well"]