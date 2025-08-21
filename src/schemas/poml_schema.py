"""
POML Schema Validation

This module provides validation for POML (Prompt Orchestration Markup Language) files
used in educational content generation.
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue in POML"""
    severity: ValidationSeverity
    message: str
    line_number: Optional[int] = None
    element_path: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class POMLValidationResult:
    """Result of POML validation"""
    is_valid: bool
    issues: List[ValidationIssue]
    parsed_content: Optional[Dict[str, Any]] = None


class POMLSchema:
    """Defines the expected structure and validation rules for POML"""
    
    def __init__(self):
        self.required_elements = {
            'poml': {
                'required': True,
                'children': ['role', 'task', 'output-format'],
                'optional_children': [
                    'content', 'educational-context', 'scene-requirements',
                    'mathematical-content', 'visual-guidelines'
                ]
            },
            'role': {
                'required': True,
                'text_required': True,
                'min_length': 20,
                'max_length': 500
            },
            'task': {
                'required': True,
                'text_required': True,
                'min_length': 50,
                'max_length': 1000
            },
            'output-format': {
                'required': True,
                'text_required': True,
                'min_length': 30
            }
        }
        
        self.element_patterns = {
            'subject': r'^(math|physics|chemistry|biology|computer_science|general)$',
            'audience': r'^(elementary|middle_school|high_school|undergraduate|graduate|general)$',
            'duration': r'^\d+\s*(seconds?|mins?|minutes?)$',
            'theme': r'^(3blue1brown|bright|dark|custom)$'
        }
        
        self.educational_elements = {
            'Text', 'MathTex', 'AxesPlot', 'Table', 'Image', 'Diagram', 'Vector'
        }


class POMLValidator:
    """Validates POML files against schema and educational requirements"""
    
    def __init__(self):
        self.schema = POMLSchema()
    
    def validate_poml_content(self, poml_content: str) -> POMLValidationResult:
        """Validate POML content string"""
        issues = []
        parsed_content = None
        
        try:
            # Parse XML
            root = self._parse_xml_safely(poml_content)
            if root is None:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message="Invalid XML structure. POML must be valid XML.",
                    suggestion="Check for unclosed tags or invalid characters"
                ))
                return POMLValidationResult(is_valid=False, issues=issues)
            
            # Validate structure
            structure_issues = self._validate_structure(root)
            issues.extend(structure_issues)
            
            # Validate content
            content_issues = self._validate_content(root)
            issues.extend(content_issues)
            
            # Validate educational requirements
            edu_issues = self._validate_educational_content(root)
            issues.extend(edu_issues)
            
            # Parse content for use
            parsed_content = self._parse_poml_to_dict(root)
            
        except ET.ParseError as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"XML parsing error: {str(e)}",
                suggestion="Validate XML syntax and structure"
            ))
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Unexpected validation error: {str(e)}"
            ))
        
        # Determine if valid (no errors, warnings are ok)
        has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        
        return POMLValidationResult(
            is_valid=not has_errors,
            issues=issues,
            parsed_content=parsed_content
        )
    
    def _parse_xml_safely(self, content: str) -> Optional[ET.Element]:
        """Safely parse XML content"""
        try:
            # Clean up common issues
            content = content.strip()
            if not content.startswith('<?xml'):
                content = '<?xml version="1.0" encoding="utf-8"?>\n' + content
            
            root = ET.fromstring(content)
            return root
        except ET.ParseError:
            return None
    
    def _validate_structure(self, root: ET.Element) -> List[ValidationIssue]:
        """Validate the structural requirements of POML"""
        issues = []
        
        # Check root element
        if root.tag != 'poml':
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Root element must be 'poml', found '{root.tag}'",
                element_path="/"
            ))
            return issues
        
        # Check required children
        required_missing = []
        for child_name in self.schema.required_elements['poml']['children']:
            if root.find(child_name) is None:
                required_missing.append(child_name)
        
        if required_missing:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Missing required elements: {', '.join(required_missing)}",
                element_path="/poml",
                suggestion=f"Add the following elements: {', '.join(f'<{e}>' for e in required_missing)}"
            ))
        
        # Validate individual elements
        for element_name, rules in self.schema.required_elements.items():
            if element_name == 'poml':
                continue
                
            element = root.find(element_name)
            if element is not None:
                element_issues = self._validate_element(element, element_name, rules)
                issues.extend(element_issues)
        
        return issues
    
    def _validate_element(self, element: ET.Element, name: str, rules: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate individual element against rules"""
        issues = []
        element_path = f"/poml/{name}"
        
        # Check text content requirements
        if rules.get('text_required', False):
            text_content = (element.text or '').strip()
            if not text_content:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Element '{name}' requires text content",
                    element_path=element_path
                ))
            else:
                # Check length requirements
                min_length = rules.get('min_length')
                max_length = rules.get('max_length')
                
                if min_length and len(text_content) < min_length:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Element '{name}' text is too short ({len(text_content)} chars, minimum {min_length})",
                        element_path=element_path,
                        suggestion=f"Provide more detailed content for better educational value"
                    ))
                
                if max_length and len(text_content) > max_length:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Element '{name}' text is too long ({len(text_content)} chars, maximum {max_length})",
                        element_path=element_path,
                        suggestion=f"Consider breaking into smaller sections or summarizing"
                    ))
        
        return issues
    
    def _validate_content(self, root: ET.Element) -> List[ValidationIssue]:
        """Validate specific content patterns"""
        issues = []
        
        # Validate educational context if present
        edu_context = root.find('educational-context')
        if edu_context is not None:
            issues.extend(self._validate_educational_context(edu_context))
        
        # Validate scene requirements
        scene_req = root.find('scene-requirements')
        if scene_req is not None:
            issues.extend(self._validate_scene_requirements(scene_req))
        
        # Validate mathematical content
        math_content = root.find('mathematical-content')
        if math_content is not None:
            issues.extend(self._validate_mathematical_content(math_content))
        
        return issues
    
    def _validate_educational_context(self, edu_context: ET.Element) -> List[ValidationIssue]:
        """Validate educational context section"""
        issues = []
        
        # Validate subject
        subject_elem = edu_context.find('subject')
        if subject_elem is not None:
            subject_text = (subject_elem.text or '').strip()
            pattern = self.schema.element_patterns.get('subject')
            if pattern and not re.match(pattern, subject_text):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Subject '{subject_text}' not in recommended list",
                    element_path="/poml/educational-context/subject",
                    suggestion="Use: math, physics, chemistry, biology, computer_science, or general"
                ))
        
        # Validate audience
        audience_elem = edu_context.find('audience')
        if audience_elem is not None:
            audience_text = (audience_elem.text or '').strip()
            pattern = self.schema.element_patterns.get('audience')
            if pattern and not re.match(pattern, audience_text):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Audience '{audience_text}' not in recommended list",
                    element_path="/poml/educational-context/audience",
                    suggestion="Use: elementary, middle_school, high_school, undergraduate, graduate, or general"
                ))
        
        # Validate duration
        duration_elem = edu_context.find('duration')
        if duration_elem is not None:
            duration_text = (duration_elem.text or '').strip()
            pattern = self.schema.element_patterns.get('duration')
            if pattern and not re.match(pattern, duration_text):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Duration format '{duration_text}' may not be recognized",
                    element_path="/poml/educational-context/duration",
                    suggestion="Use format like '45 seconds' or '2 minutes'"
                ))
        
        return issues
    
    def _validate_scene_requirements(self, scene_req: ET.Element) -> List[ValidationIssue]:
        """Validate scene requirements section"""
        issues = []
        
        # Check for elements section
        elements_section = scene_req.find('elements')
        if elements_section is not None:
            # Count elements to avoid overcrowding
            element_count = len(list(elements_section))
            if element_count > 8:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Scene has {element_count} elements, may be overcrowded",
                    element_path="/poml/scene-requirements/elements",
                    suggestion="Consider reducing to 5-8 key elements for clarity"
                ))
        
        return issues
    
    def _validate_mathematical_content(self, math_content: ET.Element) -> List[ValidationIssue]:
        """Validate mathematical content section"""
        issues = []
        
        # Check formulas
        formulas = math_content.find('formulas')
        if formulas is not None:
            formula_count = len(list(formulas))
            if formula_count > 5:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Too many formulas ({formula_count}), may overwhelm students",
                    element_path="/poml/mathematical-content/formulas",
                    suggestion="Focus on 2-3 key formulas per animation"
                ))
        
        return issues
    
    def _validate_educational_content(self, root: ET.Element) -> List[ValidationIssue]:
        """Validate educational effectiveness"""
        issues = []
        
        # Check if learning objectives are present
        edu_context = root.find('educational-context')
        if edu_context is not None:
            objectives = edu_context.find('learning-objectives')
            if objectives is None:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message="No learning objectives specified",
                    element_path="/poml/educational-context",
                    suggestion="Add <learning-objectives> to clarify educational goals"
                ))
        
        # Check task clarity
        task = root.find('task')
        if task is not None:
            task_text = (task.text or '').strip().lower()
            if 'step' not in task_text and 'demonstrate' not in task_text:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message="Task might benefit from more specific instructions",
                    element_path="/poml/task",
                    suggestion="Include specific steps or demonstrations for clearer educational flow"
                ))
        
        return issues
    
    def _parse_poml_to_dict(self, root: ET.Element) -> Dict[str, Any]:
        """Parse POML XML to dictionary for easy access"""
        def element_to_dict(element):
            result = {}
            
            # Add text content
            if element.text and element.text.strip():
                result['_text'] = element.text.strip()
            
            # Add attributes
            if element.attrib:
                result['_attributes'] = element.attrib
            
            # Add children
            for child in element:
                child_dict = element_to_dict(child)
                if child.tag in result:
                    # Handle multiple children with same tag
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = child_dict
            
            return result
        
        return element_to_dict(root)
    
    def get_validation_summary(self, result: POMLValidationResult) -> str:
        """Get a human-readable validation summary"""
        if result.is_valid:
            summary = "✓ POML validation passed"
            if result.issues:
                warning_count = sum(1 for i in result.issues if i.severity == ValidationSeverity.WARNING)
                info_count = sum(1 for i in result.issues if i.severity == ValidationSeverity.INFO)
                if warning_count > 0:
                    summary += f" ({warning_count} warnings"
                if info_count > 0:
                    summary += f", {info_count} info" if warning_count > 0 else f" ({info_count} info"
                if warning_count > 0 or info_count > 0:
                    summary += ")"
        else:
            error_count = sum(1 for i in result.issues if i.severity == ValidationSeverity.ERROR)
            summary = f"✗ POML validation failed ({error_count} errors)"
        
        return summary


def main():
    """Test POML validation"""
    # Sample POML content for testing
    sample_poml = """
    <poml version="1.0">
        <role>You are an expert mathematics educator.</role>
        <task>Create a Manim animation that teaches derivatives through visual representation.</task>
        <output-format>Generate clean Manim code with proper formatting.</output-format>
        <educational-context>
            <subject>math</subject>
            <audience>undergraduate</audience>
            <duration>45 seconds</duration>
        </educational-context>
    </poml>
    """
    
    validator = POMLValidator()
    result = validator.validate_poml_content(sample_poml)
    
    print(validator.get_validation_summary(result))
    
    if result.issues:
        print("\nValidation issues:")
        for issue in result.issues:
            print(f"  {issue.severity.value.upper()}: {issue.message}")
            if issue.suggestion:
                print(f"    Suggestion: {issue.suggestion}")


if __name__ == "__main__":
    main()