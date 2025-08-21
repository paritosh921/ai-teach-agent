"""
Simple Video Evaluator for Builder LLM System

Standalone video evaluator that doesn't depend on the removed legacy video_evaluator.
"""

import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class VideoEvaluationResult:
    """Result of video evaluation"""
    success: bool
    issues_found: int
    visual_quality_score: float  # 0-1 scale
    recommendations: List[str]
    detailed_issues: List[Dict[str, Any]]
    evaluation_summary: str


class SimpleVideoEvaluator:
    """Simple video evaluator without external dependencies"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key
        self.available = gemini_api_key is not None
        
    def evaluate_video(self, video_path: str, yaml_spec: Dict[str, Any]) -> VideoEvaluationResult:
        """
        Evaluate video quality (simplified version without Gemini)
        
        Args:
            video_path: Path to the video file
            yaml_spec: YAML specification used for generation
            
        Returns:
            VideoEvaluationResult with basic evaluation
        """
        if not os.path.exists(video_path):
            return VideoEvaluationResult(
                success=False,
                issues_found=1,
                visual_quality_score=0.0,
                recommendations=["Video file not found"],
                detailed_issues=[{
                    "type": "missing_file",
                    "description": f"Video file not found at {video_path}"
                }],
                evaluation_summary="Video file missing"
            )
        
        # Basic file existence check (placeholder for more sophisticated evaluation)
        file_size = os.path.getsize(video_path)
        
        if file_size < 1000:  # Less than 1KB indicates likely failure
            return VideoEvaluationResult(
                success=False,
                issues_found=1,
                visual_quality_score=0.2,
                recommendations=["Video file appears corrupted or too small"],
                detailed_issues=[{
                    "type": "file_size",
                    "description": f"Video file is only {file_size} bytes"
                }],
                evaluation_summary="Video may be corrupted"
            )
        
        # If we reach here, basic checks passed
        return VideoEvaluationResult(
            success=True,
            issues_found=0,
            visual_quality_score=0.8,  # Optimistic default
            recommendations=["Video appears to be generated successfully"],
            detailed_issues=[],
            evaluation_summary="Video generated successfully (basic evaluation)"
        )
    
    def is_available(self) -> bool:
        """Check if evaluator is available"""
        return self.available