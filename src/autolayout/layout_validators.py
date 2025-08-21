"""
Layout Validation Utilities

This module provides comprehensive validation to catch layout issues
before rendering, enabling pre-emptive fixes and quality assurance.
"""

import json
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from .frame_bounds import (
    get_safe_bounds,
    get_element_bounds, 
    in_frame,
    get_frame_utilization,
    DEFAULT_MARGIN
)
from .auto_positioning import elements_overlap


@dataclass
class ValidationIssue:
    """Represents a layout validation issue"""
    severity: str  # 'critical', 'high', 'medium', 'low'
    issue_type: str  # 'out_of_bounds', 'overlap', 'too_small', 'too_dense'
    element_keys: List[str]
    description: str
    suggested_fix: str
    confidence: float  # 0.0 to 1.0


@dataclass
class LayoutReport:
    """Comprehensive layout validation report"""
    status: str  # 'passed', 'warnings', 'failed'
    issues: List[ValidationIssue]
    frame_utilization: Dict[str, float]
    element_count: int
    validation_timestamp: str
    recommendations: List[str]


def validate_element_bounds(element: Any, 
                          element_key: str,
                          margin: float = DEFAULT_MARGIN) -> List[ValidationIssue]:
    """
    Validate that element stays within frame bounds
    
    Args:
        element: Manim mobject to validate
        element_key: Identifier for the element
        margin: Safe margin from edges
        
    Returns:
        List of validation issues found
    """
    issues = []
    
    if not in_frame(element, margin):
        x_min, y_min, x_max, y_max = get_element_bounds(element)
        left, right, top, bottom = get_safe_bounds(margin)
        
        out_of_bounds_directions = []
        if x_min < left:
            out_of_bounds_directions.append('left')
        if x_max > right:
            out_of_bounds_directions.append('right')
        if y_min < bottom:
            out_of_bounds_directions.append('bottom')
        if y_max > top:
            out_of_bounds_directions.append('top')
        
        severity = 'critical' if len(out_of_bounds_directions) > 1 else 'high'
        
        issues.append(ValidationIssue(
            severity=severity,
            issue_type='out_of_bounds',
            element_keys=[element_key],
            description=f"Element '{element_key}' extends beyond frame boundaries ({', '.join(out_of_bounds_directions)})",
            suggested_fix=f"Scale element down or reposition within safe area. Consider fit_to_frame() utility.",
            confidence=0.95
        ))
    
    return issues


def validate_element_size(element: Any,
                         element_key: str,
                         min_font_size: int = 24,
                         content_type: str = 'text') -> List[ValidationIssue]:
    """
    Validate element size for legibility and appropriateness
    
    Args:
        element: Manim mobject to validate
        element_key: Identifier for the element
        min_font_size: Minimum legible font size
        content_type: Type of content for context
        
    Returns:
        List of validation issues found
    """
    issues = []
    
    # Check for text legibility
    if hasattr(element, 'font_size'):
        current_font_size = element.font_size
        if current_font_size < min_font_size:
            issues.append(ValidationIssue(
                severity='high',
                issue_type='too_small',
                element_keys=[element_key],
                description=f"Text element '{element_key}' font size ({current_font_size}) below legibility threshold ({min_font_size})",
                suggested_fix=f"Increase font size to at least {min_font_size} or reduce text content",
                confidence=0.9
            ))
    
    # Check for overly large elements
    if hasattr(element, 'width') and hasattr(element, 'height'):
        left, right, top, bottom = get_safe_bounds()
        safe_width = right - left
        safe_height = top - bottom
        
        if element.width > safe_width * 0.95:
            issues.append(ValidationIssue(
                severity='medium',
                issue_type='too_large',
                element_keys=[element_key],
                description=f"Element '{element_key}' width ({element.width:.2f}) approaches frame limit",
                suggested_fix="Consider scaling down or splitting content",
                confidence=0.8
            ))
        
        if element.height > safe_height * 0.95:
            issues.append(ValidationIssue(
                severity='medium', 
                issue_type='too_large',
                element_keys=[element_key],
                description=f"Element '{element_key}' height ({element.height:.2f}) approaches frame limit",
                suggested_fix="Consider scaling down or splitting content",
                confidence=0.8
            ))
    
    return issues


def validate_overlaps(elements: Dict[str, Any], buffer: float = 0.2) -> List[ValidationIssue]:
    """
    Validate that no elements overlap inappropriately
    
    Args:
        elements: Dictionary mapping element keys to mobjects
        buffer: Minimum buffer distance between elements
        
    Returns:
        List of overlap validation issues
    """
    issues = []
    element_list = list(elements.items())
    
    for i in range(len(element_list)):
        key1, element1 = element_list[i]
        for j in range(i + 1, len(element_list)):
            key2, element2 = element_list[j]
            
            if elements_overlap(element1, element2, buffer):
                from .auto_positioning import get_overlap_amount
                overlap_area = get_overlap_amount(element1, element2, buffer)
                
                # Determine severity based on overlap amount
                element1_area = getattr(element1, 'width', 1) * getattr(element1, 'height', 1)
                element2_area = getattr(element2, 'width', 1) * getattr(element2, 'height', 1)
                smaller_area = min(element1_area, element2_area)
                
                overlap_percentage = overlap_area / smaller_area if smaller_area > 0 else 1.0
                
                if overlap_percentage > 0.8:
                    severity = 'critical'
                elif overlap_percentage > 0.5:
                    severity = 'high'
                elif overlap_percentage > 0.2:
                    severity = 'medium'
                else:
                    severity = 'low'
                
                issues.append(ValidationIssue(
                    severity=severity,
                    issue_type='overlap',
                    element_keys=[key1, key2],
                    description=f"Elements '{key1}' and '{key2}' overlap by {overlap_percentage*100:.1f}%",
                    suggested_fix=f"Increase spacing, use resolve_overlaps(), or stagger timing",
                    confidence=0.9
                ))
    
    return issues


def validate_content_density(elements: Dict[str, Any], 
                           margin: float = DEFAULT_MARGIN) -> List[ValidationIssue]:
    """
    Validate overall content density and distribution
    
    Args:
        elements: Dictionary mapping element keys to mobjects
        margin: Safe margin from edges
        
    Returns:
        List of density-related validation issues
    """
    issues = []
    
    if not elements:
        return issues
    
    from .element_scaling import calculate_content_density
    density_info = calculate_content_density(list(elements.values()), margin)
    
    if density_info['overcrowded']:
        issue_keys = list(elements.keys())
        issues.append(ValidationIssue(
            severity='high',
            issue_type='too_dense',
            element_keys=issue_keys,
            description=f"Content density ({density_info['density_score']:.2f}) exceeds recommended maximum (0.8)",
            suggested_fix="Consider pagination, scaling down elements, or removing less critical content",
            confidence=0.85
        ))
    
    elif density_info['density_score'] < 0.2 and len(elements) > 1:
        issues.append(ValidationIssue(
            severity='low',
            issue_type='underutilized',
            element_keys=list(elements.keys()),
            description=f"Content density ({density_info['density_score']:.2f}) is quite low - screen space underutilized",
            suggested_fix="Consider larger elements or additional content",
            confidence=0.7
        ))
    
    return issues


def validate_layout_pre_render(elements: Dict[str, Any],
                              margin: float = DEFAULT_MARGIN,
                              min_font_size: int = 24) -> LayoutReport:
    """
    Comprehensive pre-render layout validation
    
    Args:
        elements: Dictionary mapping element keys to mobjects
        margin: Safe margin from edges
        min_font_size: Minimum legible font size
        
    Returns:
        Complete validation report
    """
    all_issues = []
    
    # Validate individual element bounds and sizes
    for key, element in elements.items():
        all_issues.extend(validate_element_bounds(element, key, margin))
        all_issues.extend(validate_element_size(element, key, min_font_size))
    
    # Validate overlaps between elements
    all_issues.extend(validate_overlaps(elements))
    
    # Validate overall content density
    all_issues.extend(validate_content_density(elements, margin))
    
    # Calculate frame utilization
    utilization = get_frame_utilization(list(elements.values()), margin)
    
    # Determine overall status
    critical_count = sum(1 for issue in all_issues if issue.severity == 'critical')
    high_count = sum(1 for issue in all_issues if issue.severity == 'high')
    
    if critical_count > 0:
        status = 'failed'
    elif high_count > 0:
        status = 'warnings'
    else:
        status = 'passed'
    
    # Generate recommendations
    recommendations = generate_recommendations(all_issues, utilization)
    
    import datetime
    
    return LayoutReport(
        status=status,
        issues=all_issues,
        frame_utilization=utilization,
        element_count=len(elements),
        validation_timestamp=datetime.datetime.now().isoformat(),
        recommendations=recommendations
    )


def check_element_bounds(elements: List[Any], margin: float = DEFAULT_MARGIN) -> Dict[str, bool]:
    """
    Quick check of which elements are within bounds
    
    Args:
        elements: List of Manim mobjects
        margin: Safe margin from edges
        
    Returns:
        Dictionary mapping element indices to in-bounds status
    """
    results = {}
    
    for i, element in enumerate(elements):
        results[f'element_{i}'] = in_frame(element, margin)
    
    return results


def detect_overlaps_batch(elements: List[Any], buffer: float = 0.2) -> List[Tuple[int, int, float]]:
    """
    Detect overlaps in a batch of elements
    
    Args:
        elements: List of Manim mobjects
        buffer: Buffer distance for overlap detection
        
    Returns:
        List of tuples (index1, index2, overlap_amount)
    """
    overlaps = []
    
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            if elements_overlap(elements[i], elements[j], buffer):
                from .auto_positioning import get_overlap_amount
                overlap_amount = get_overlap_amount(elements[i], elements[j], buffer)
                overlaps.append((i, j, overlap_amount))
    
    return overlaps


def generate_layout_report(elements: Dict[str, Any], 
                          output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate comprehensive layout analysis report
    
    Args:
        elements: Dictionary of elements to analyze
        output_path: Optional path to save JSON report
        
    Returns:
        Dictionary containing detailed report
    """
    validation_report = validate_layout_pre_render(elements)
    
    # Convert to serializable dictionary
    report_dict = {
        'validation_summary': {
            'status': validation_report.status,
            'total_issues': len(validation_report.issues),
            'critical_issues': sum(1 for i in validation_report.issues if i.severity == 'critical'),
            'high_issues': sum(1 for i in validation_report.issues if i.severity == 'high'),
            'medium_issues': sum(1 for i in validation_report.issues if i.severity == 'medium'),
            'low_issues': sum(1 for i in validation_report.issues if i.severity == 'low'),
        },
        'frame_utilization': validation_report.frame_utilization,
        'element_count': validation_report.element_count,
        'timestamp': validation_report.validation_timestamp,
        'recommendations': validation_report.recommendations,
        'detailed_issues': [asdict(issue) for issue in validation_report.issues]
    }
    
    # Save to file if requested
    if output_path:
        try:
            with open(output_path, 'w') as f:
                json.dump(report_dict, f, indent=2)
        except Exception as e:
            print(f"Failed to save report to {output_path}: {e}")
    
    return report_dict


def generate_recommendations(issues: List[ValidationIssue], 
                           utilization: Dict[str, float]) -> List[str]:
    """
    Generate actionable recommendations based on validation issues
    
    Args:
        issues: List of validation issues
        utilization: Frame utilization statistics
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Analyze issue patterns
    critical_issues = [i for i in issues if i.severity == 'critical']
    overlap_issues = [i for i in issues if i.issue_type == 'overlap']
    bounds_issues = [i for i in issues if i.issue_type == 'out_of_bounds']
    size_issues = [i for i in issues if i.issue_type in ['too_small', 'too_large']]
    
    # Critical issues first
    if critical_issues:
        recommendations.append(
            f"URGENT: {len(critical_issues)} critical issues must be fixed before rendering. "
            "These will cause visible problems in the final video."
        )
    
    # Overlaps
    if len(overlap_issues) > 2:
        recommendations.append(
            "Multiple overlapping elements detected. Consider using paginate_content() "
            "to split into multiple scenes or resolve_overlaps() for automatic repositioning."
        )
    elif overlap_issues:
        recommendations.append(
            "Some elements overlap. Use arrange_and_fit() with increased buffer distance "
            "or manually reposition elements."
        )
    
    # Out of bounds
    if bounds_issues:
        recommendations.append(
            "Elements extend beyond safe frame boundaries. Use fit_to_frame() utility "
            "or scale elements down to ensure visibility."
        )
    
    # Size issues
    if size_issues:
        text_issues = [i for i in size_issues if 'font' in i.description.lower()]
        if text_issues:
            recommendations.append(
                "Text elements may be illegible due to small font size. "
                "Use ensure_legible_text() or reduce content per screen."
            )
    
    # Utilization-based recommendations
    if utilization.get('elements_out_of_bounds', 0) > 0:
        recommendations.append(
            f"{utilization['elements_out_of_bounds']} elements are outside safe boundaries. "
            "Review element positioning and scaling."
        )
    
    if utilization.get('safe_area_coverage', 0) > 0.8:
        recommendations.append(
            "Screen appears crowded (>80% coverage). Consider splitting content "
            "across multiple scenes or reducing element sizes."
        )
    elif utilization.get('safe_area_coverage', 0) < 0.3:
        recommendations.append(
            "Screen space is underutilized (<30% coverage). You could add more content "
            "or make existing elements larger for better visibility."
        )
    
    if not recommendations:
        recommendations.append("Layout validation passed! No issues detected.")
    
    return recommendations