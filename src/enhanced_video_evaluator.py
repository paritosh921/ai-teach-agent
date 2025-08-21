"""
Enhanced Video Evaluator for Builder LLM System

This module extends the existing video evaluator with the new YAML format
required by the Builder LLM system. It provides strict visual evaluation
according to the non-negotiable layout rules.
"""

import os
import yaml
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import google.generativeai as genai

# Import the original evaluator as base
from .video_evaluator import VideoEvaluator as BaseVideoEvaluator


@dataclass
class IssueDetails:
    """Detailed issue information for Builder LLM format"""
    issue_id: str
    category: str  # "overlap", "out_of_frame", "visual_correctness", "timing"
    severity: str  # "critical", "major", "minor"
    description: str
    timestamp: float  # seconds into video
    affected_elements: List[Dict[str, str]]
    suggested_fix: Dict[str, str]


class EnhancedVideoEvaluator(BaseVideoEvaluator):
    """
    Enhanced video evaluator for Builder LLM system
    
    Provides strict evaluation according to Builder LLM requirements:
    - Frame-by-frame analysis for 6% safe margins
    - Overlap detection with buffer requirements
    - Text legibility at 480p (≥24px equivalent)
    - Sequencing validation
    - Content alignment checking
    """
    
    # Builder LLM specific evaluation prompt
    BUILDER_EVALUATION_PROMPT = """You are a strict visual/layout QA for Manim videos.

Task: Inspect the attached video frame-by-frame for:
1) In-frame: No element breaches a 6% safe margin on any edge.
2) No overlaps: Visible labels/equations/legends do not intersect at the same time.
3) Legibility: Text ≥ ~24 px equivalent at 480p; equations readable.
4) Sequencing: Items don't appear under existing ones; prior items fade/move before reuse.
5) Content alignment: On-screen visuals match narration timing roughly.

Return ONLY this YAML:

status: "perfect" | "needs_changes"
issues:
  - scene_id: str
    timecode_s: number
    type: "overlap" | "out_of_frame" | "illegible" | "sequencing" | "content_mismatch"
    actors: [str, ...]     # element keys if inferable
    suggestion: str        # concrete, minimal fix (scale %, shift %, fade timing, etc.)

If no problems, set status: "perfect" and issues: []."""
    
    def __init__(self, gemini_api_key: str):
        """Initialize enhanced evaluator"""
        super().__init__(gemini_api_key)
        
        # Builder LLM specific configuration
        self.safe_margin_pct = 0.06  # 6% safe margin requirement
        self.min_text_height_px = 24  # Minimum text height at 480p
        self.buffer_distance = 0.2   # Minimum spacing between elements
        
        # Issue tracking
        self.evaluation_history: List[Dict[str, Any]] = []
    
    def evaluate_video_builder_format(self, video_path: str, 
                                    content_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate video using Builder LLM format requirements
        
        Args:
            video_path: Path to the generated video file
            content_context: Optional context about expected content
            
        Returns:
            Dictionary with 'status' and optionally 'issues' for Builder LLM feedback
        """
        print(f"SEARCH: Evaluating video with Builder LLM format: {video_path}")
        
        # Check if video file exists
        if not os.path.exists(video_path):
            return self._create_error_response("file_not_found", f"Video file not found: {video_path}")
        
        try:
            # Create Builder LLM specific evaluation prompt
            prompt = self._create_builder_evaluation_prompt(content_context)
            
            # Get file size to determine upload method
            file_size = os.path.getsize(video_path)
            print(f"CHART: Video file size: {file_size / (1024*1024):.1f} MB")
            
            if file_size < 20 * 1024 * 1024:  # Less than 20MB
                print("📤 Using direct upload method for analysis...")
                evaluation_result = self._analyze_video_upload(video_path, prompt)
            else:
                print("📤 Using file upload method for large video...")
                evaluation_result = self._analyze_video_upload(video_path, prompt)
            
            # Parse and validate the response
            validated_result = self._validate_builder_response(evaluation_result)
            
            # Store in evaluation history
            self.evaluation_history.append({
                'timestamp': time.time(),
                'video_path': video_path,
                'context': content_context,
                'result': validated_result
            })
            
            print(f"OK: Evaluation complete: {validated_result['status']}")
            if validated_result['status'] == 'needs_changes':
                print(f"LIST: Found {len(validated_result.get('issues', []))} issues")
            
            return validated_result
            
        except Exception as e:
            print(f"NO: Evaluation failed: {e}")
            return self._create_error_response("evaluation_error", f"Evaluation failed: {str(e)}")
    
    def _create_builder_evaluation_prompt(self, content_context: Dict[str, Any] = None) -> str:
        """Create evaluation prompt specifically for Builder LLM requirements"""
        topic = content_context.get('topic', 'Educational animation') if content_context else 'Educational animation'
        
        prompt = f"""{self.BUILDER_EVALUATION_PROMPT}

Expected content context: {topic}

CRITICAL REQUIREMENTS:
- 6% safe margins: No content within 6% of any edge
- Zero overlaps: Elements must not intersect visually
- Text legibility: All text ≥ 24px equivalent at 480p
- Proper sequencing: No elements appearing over existing ones
- Buffer zones: Minimum 0.2 unit spacing between elements

Return ONLY the YAML response - no additional text or explanations."""
        
        return prompt.strip()
    
    def _validate_builder_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and format response for Builder LLM requirements
        
        Ensures the response matches the exact format expected by Builder LLM
        """
        if not isinstance(response, dict):
            return self._create_error_response("parse_error", "Invalid response format")
        
        status = response.get('status', 'needs_changes')
        if status not in ['perfect', 'needs_changes']:
            return self._create_error_response("invalid_status", f"Invalid status: {status}")
        
        validated_response = {
            'status': status
        }
        
        if status == 'needs_changes':
            issues = response.get('issues', [])
            if not isinstance(issues, list):
                return self._create_error_response("invalid_issues", "Issues must be a list")
            
            # Validate each issue
            validated_issues = []
            for i, issue in enumerate(issues):
                try:
                    validated_issue = self._validate_issue(issue, i)
                    validated_issues.append(validated_issue)
                except Exception as e:
                    print(f"WARN: Issue {i} validation failed: {e}")
                    # Continue with other issues
            
            validated_response['issues'] = validated_issues
        
        return validated_response
    
    def _validate_issue(self, issue: Dict[str, Any], issue_index: int) -> Dict[str, Any]:
        """Validate individual issue format"""
        required_fields = ['scene_id', 'timecode_s', 'type', 'actors', 'suggestion']
        
        # Check required fields
        for field in required_fields:
            if field not in issue:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate issue type
        valid_types = ['overlap', 'out_of_frame', 'illegible', 'sequencing', 'content_mismatch']
        if issue['type'] not in valid_types:
            raise ValueError(f"Invalid issue type: {issue['type']}")
        
        # Validate timecode
        try:
            timecode = float(issue['timecode_s'])
            if timecode < 0:
                raise ValueError("Timecode must be non-negative")
        except (ValueError, TypeError):
            raise ValueError("Invalid timecode format")
        
        # Validate actors
        if not isinstance(issue['actors'], list):
            issue['actors'] = [str(issue['actors'])] if issue['actors'] else []
        
        # Generate issue ID if not present
        if 'issue_id' not in issue:
            issue['issue_id'] = f"{issue['type']}_{issue_index:03d}"
        
        return {
            'scene_id': str(issue['scene_id']),
            'timecode_s': timecode,
            'type': issue['type'],
            'actors': [str(actor) for actor in issue['actors']],
            'suggestion': str(issue['suggestion']),
            'issue_id': issue['issue_id']
        }
    
    def _create_error_response(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """Create error response in Builder LLM format"""
        return {
            'status': 'needs_changes',
            'issues': [{
                'issue_id': f'error_{int(time.time())}',
                'scene_id': 'unknown',
                'timecode_s': 0.0,
                'type': 'out_of_frame' if error_type == 'file_not_found' else 'sequencing',
                'actors': [],
                'suggestion': f"Technical issue: {error_message}"
            }]
        }
    
    def generate_detailed_feedback(self, evaluation_result: Dict[str, Any]) -> str:
        """
        Generate detailed human-readable feedback from evaluation result
        
        Useful for debugging and manual review
        """
        if evaluation_result['status'] == 'perfect':
            return "OK: VIDEO QUALITY APPROVED: No issues found!"
        
        issues = evaluation_result.get('issues', [])
        if not issues:
            return "WARN: Status indicates changes needed but no specific issues found"
        
        feedback_lines = [
            f"🚨 QUALITY ISSUES FOUND: {len(issues)} problems detected",
            "=" * 50
        ]
        
        # Group issues by type
        issue_groups = {}
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in issue_groups:
                issue_groups[issue_type] = []
            issue_groups[issue_type].append(issue)
        
        # Generate feedback for each type
        for issue_type, type_issues in issue_groups.items():
            feedback_lines.append(f"\n📍 {issue_type.upper()} ISSUES ({len(type_issues)}):")
            
            for i, issue in enumerate(type_issues, 1):
                timecode = issue['timecode_s']
                actors = ', '.join(issue['actors']) if issue['actors'] else 'unknown elements'
                suggestion = issue['suggestion']
                
                feedback_lines.append(f"  {i}. At {timecode:.1f}s - {actors}")
                feedback_lines.append(f"     IDEA: {suggestion}")
        
        # Add summary recommendations
        feedback_lines.extend([
            "\n" + "=" * 50,
            "TOOL: RECOMMENDED ACTIONS:",
            "1. Apply suggested fixes in order of severity",
            "2. Focus on overlaps and out-of-frame issues first", 
            "3. Re-compile and evaluate after making changes",
            "4. Repeat until status is 'perfect'"
        ])
        
        return '\n'.join(feedback_lines)
    
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """Get statistics from evaluation history"""
        if not self.evaluation_history:
            return {'total_evaluations': 0}
        
        total_evaluations = len(self.evaluation_history)
        perfect_count = sum(1 for eval_result in self.evaluation_history 
                          if eval_result['result']['status'] == 'perfect')
        
        # Count issue types
        issue_type_counts = {}
        total_issues = 0
        
        for eval_result in self.evaluation_history:
            issues = eval_result['result'].get('issues', [])
            total_issues += len(issues)
            
            for issue in issues:
                issue_type = issue['type']
                issue_type_counts[issue_type] = issue_type_counts.get(issue_type, 0) + 1
        
        return {
            'total_evaluations': total_evaluations,
            'perfect_evaluations': perfect_count,
            'success_rate': perfect_count / total_evaluations if total_evaluations > 0 else 0,
            'total_issues_found': total_issues,
            'average_issues_per_video': total_issues / total_evaluations if total_evaluations > 0 else 0,
            'issue_type_distribution': issue_type_counts,
            'most_common_issue': max(issue_type_counts.keys(), key=issue_type_counts.get) if issue_type_counts else None
        }
    
    def save_evaluation_session(self, output_path: str) -> None:
        """Save complete evaluation session for analysis"""
        session_data = {
            'session_info': {
                'timestamp': time.time(),
                'evaluator_version': 'enhanced_builder_llm',
                'safe_margin_pct': self.safe_margin_pct,
                'min_text_height_px': self.min_text_height_px,
                'buffer_distance': self.buffer_distance
            },
            'evaluation_history': self.evaluation_history,
            'statistics': self.get_evaluation_statistics()
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(session_data, f, default_flow_style=False, allow_unicode=True)
            print(f"FOLDER: Evaluation session saved: {output_path}")
        except Exception as e:
            print(f"WARN: Could not save evaluation session: {e}")


def create_enhanced_evaluator(gemini_api_key: str) -> EnhancedVideoEvaluator:
    """Factory function for creating enhanced video evaluator"""
    return EnhancedVideoEvaluator(gemini_api_key)


# Backward compatibility - extend the existing VideoEvaluator
def enhance_existing_evaluator(evaluator: BaseVideoEvaluator, 
                             gemini_api_key: str) -> EnhancedVideoEvaluator:
    """Enhance existing evaluator instance with Builder LLM capabilities"""
    return EnhancedVideoEvaluator(gemini_api_key)