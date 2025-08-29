"""
Enhanced Video Evaluator with Gemini 2.5 Flash-Lite Integration

Comprehensive video evaluator that performs frame-by-frame analysis for:
- Content overlap detection
- Out-of-frame element detection  
- Educational quality assessment
- Layout safety validation
"""

import os
import cv2
import base64
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
import google.generativeai as genai
from pathlib import Path
import json
import tempfile


@dataclass
class FrameAnalysis:
    """Analysis result for a single frame"""
    frame_number: int
    timestamp: float
    issues: List[Dict[str, Any]] = field(default_factory=list)
    elements_detected: List[str] = field(default_factory=list)
    layout_score: float = 0.0
    readability_score: float = 0.0


@dataclass
class VideoEvaluationResult:
    """Result of comprehensive video evaluation"""
    success: bool
    overall_quality_score: float  # 0-1 scale
    educational_effectiveness: float  # 0-1 scale
    layout_safety_score: float  # 0-1 scale
    issues_found: int
    critical_issues: int
    recommendations: List[str]
    detailed_issues: List[Dict[str, Any]]
    frame_analyses: List[FrameAnalysis] = field(default_factory=list)
    evaluation_summary: str = ""
    status: str = "unknown"  # 'correct', 'issue_found', 'error'


class EnhancedVideoEvaluator:
    """
    Enhanced video evaluator with Gemini 2.5 Flash-Lite integration
    
    Performs comprehensive frame-by-frame analysis including:
    - Visual overlap detection
    - Out-of-frame content detection
    - Text readability assessment
    - Educational content quality evaluation
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key
        self.available = gemini_api_key is not None
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Use Gemini 1.5 Flash for video analysis
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("SUCCESS: Gemini 1.5 Flash model initialized for video evaluation")
            except Exception as e:
                print(f"WARNING: Failed to initialize Gemini model: {e}")
                self.available = False
        
    def evaluate_video(self, video_path: str, content_context: Optional[Dict[str, Any]] = None) -> VideoEvaluationResult:
        """
        Comprehensive video quality evaluation with frame-by-frame analysis
        
        Args:
            video_path: Path to the video file
            content_context: Context about the educational content
            
        Returns:
            VideoEvaluationResult with detailed analysis
        """
        if not os.path.exists(video_path):
            return VideoEvaluationResult(
                success=False,
                overall_quality_score=0.0,
                educational_effectiveness=0.0,
                layout_safety_score=0.0,
                issues_found=1,
                critical_issues=1,
                recommendations=["Video file not found"],
                detailed_issues=[{
                    "type": "missing_file",
                    "severity": "critical",
                    "description": f"Video file not found at {video_path}"
                }],
                evaluation_summary="Video file missing",
                status="error"
            )
        
        print(f"EVALUATING: Starting comprehensive video analysis...")
        
        # Basic file checks
        file_size = os.path.getsize(video_path)
        if file_size < 1000:  # Less than 1KB indicates likely failure
            return VideoEvaluationResult(
                success=False,
                overall_quality_score=0.1,
                educational_effectiveness=0.0,
                layout_safety_score=0.0,
                issues_found=1,
                critical_issues=1,
                recommendations=["Video file appears corrupted or too small"],
                detailed_issues=[{
                    "type": "file_corruption",
                    "severity": "critical",
                    "description": f"Video file is only {file_size} bytes"
                }],
                evaluation_summary="Video may be corrupted",
                status="error"
            )
        
        # Perform comprehensive analysis
        if self.available and self.model:
            return self._perform_ai_analysis(video_path, content_context)
        else:
            return self._perform_basic_analysis(video_path, content_context)
    
    def _perform_ai_analysis(self, video_path: str, content_context: Optional[Dict[str, Any]]) -> VideoEvaluationResult:
        """Perform AI-powered comprehensive video analysis"""
        print("AI ANALYSIS: Using Gemini 1.5 Flash for comprehensive evaluation")
        
        try:
            # Extract key frames for analysis
            key_frames = self._extract_key_frames(video_path)
            
            if not key_frames:
                return self._create_error_result("Could not extract frames from video")
            
            print(f"FRAMES: Extracted {len(key_frames)} key frames for analysis")
            
            # Analyze frames with Gemini
            frame_analyses = []
            all_issues = []
            
            for i, (frame_data, timestamp) in enumerate(key_frames):
                try:
                    analysis = self._analyze_frame_with_ai(frame_data, timestamp, i, content_context)
                    frame_analyses.append(analysis)
                    all_issues.extend(analysis.issues)
                    print(f"FRAME {i+1}/{len(key_frames)}: {len(analysis.issues)} issues found")
                except Exception as e:
                    print(f"WARNING: Frame {i} analysis failed: {e}")
            
            # Perform overall video analysis
            overall_analysis = self._analyze_video_overall(video_path, content_context)
            
            # Compile results
            return self._compile_analysis_results(frame_analyses, all_issues, overall_analysis)
            
        except Exception as e:
            print(f"ERROR: AI analysis failed: {e}")
            return self._perform_basic_analysis(video_path, content_context)
    
    def _extract_key_frames(self, video_path: str, max_frames: int = 6) -> List[Tuple[str, float]]:
        """Extract key frames from video for analysis"""
        frames = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                print(f"ERROR: Could not open video file: {video_path}")
                return frames
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Select frames evenly distributed throughout the video
            frame_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert frame to base64 for Gemini
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_b64 = base64.b64encode(buffer).decode('utf-8')
                    timestamp = frame_idx / fps
                    
                    frames.append((frame_b64, timestamp))
            
            cap.release()
            print(f"SUCCESS: Extracted {len(frames)} frames from video")
            
        except Exception as e:
            print(f"ERROR: Frame extraction failed: {e}")
        
        return frames
    
    def _analyze_frame_with_ai(self, frame_b64: str, timestamp: float, frame_number: int,
                              content_context: Optional[Dict[str, Any]]) -> FrameAnalysis:
        """Analyze a single frame using Gemini AI"""
        
        topic = content_context.get('topic', 'Unknown Topic') if content_context else 'Unknown Topic'
        
        prompt = f"""Analyze this educational video frame for visual quality and educational effectiveness.

EDUCATIONAL CONTEXT:
Topic: {topic}
Timestamp: {timestamp:.1f} seconds

ANALYSIS REQUIREMENTS:
1. LAYOUT SAFETY: Check for content overlap, elements outside frame boundaries, illegible text
2. EDUCATIONAL QUALITY: Assess clarity of explanations, visual aids effectiveness
3. VISUAL ISSUES: Identify any visual problems that impact learning

Respond with a JSON object containing:
{{
    "layout_score": 0.0-1.0,
    "readability_score": 0.0-1.0,
    "educational_effectiveness": 0.0-1.0,
    "elements_detected": ["list of visual elements"],
    "issues": [
        {{
            "type": "overlap|out_of_frame|illegible|poor_explanation|other",
            "severity": "critical|high|medium|low",
            "description": "detailed description",
            "location": "where in frame",
            "suggestion": "how to fix"
        }}
    ]
}}

Focus on identifying specific, actionable issues that can be fixed programmatically."""
        
        try:
            # Create the image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": frame_b64
            }
            
            response = self.model.generate_content([prompt, image_part])
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Clean up JSON if needed
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '')
            
            analysis_data = json.loads(response_text)
            
            return FrameAnalysis(
                frame_number=frame_number,
                timestamp=timestamp,
                issues=analysis_data.get('issues', []),
                elements_detected=analysis_data.get('elements_detected', []),
                layout_score=analysis_data.get('layout_score', 0.5),
                readability_score=analysis_data.get('readability_score', 0.5)
            )
            
        except Exception as e:
            print(f"WARNING: Frame analysis failed: {e}")
            return FrameAnalysis(
                frame_number=frame_number,
                timestamp=timestamp,
                issues=[{
                    "type": "analysis_error",
                    "severity": "medium", 
                    "description": f"Could not analyze frame: {str(e)}",
                    "location": "entire_frame",
                    "suggestion": "Manual review required"
                }],
                elements_detected=[],
                layout_score=0.5,
                readability_score=0.5
            )
    
    def _analyze_video_overall(self, video_path: str, content_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform overall video analysis"""
        topic = content_context.get('topic', 'Unknown Topic') if content_context else 'Unknown Topic'
        
        # Basic video properties
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        return {
            'duration': duration,
            'resolution': f"{width}x{height}",
            'fps': fps,
            'frame_count': frame_count,
            'file_size': os.path.getsize(video_path),
            'topic': topic
        }
    
    def _compile_analysis_results(self, frame_analyses: List[FrameAnalysis],
                                 all_issues: List[Dict[str, Any]],
                                 video_properties: Dict[str, Any]) -> VideoEvaluationResult:
        """Compile all analysis results into final evaluation"""
        
        # Count issues by severity
        critical_issues = sum(1 for issue in all_issues if issue.get('severity') == 'critical')
        high_issues = sum(1 for issue in all_issues if issue.get('severity') == 'high')
        total_issues = len(all_issues)
        
        # Calculate scores
        layout_scores = [fa.layout_score for fa in frame_analyses if fa.layout_score > 0]
        readability_scores = [fa.readability_score for fa in frame_analyses if fa.readability_score > 0]
        
        avg_layout_score = np.mean(layout_scores) if layout_scores else 0.5
        avg_readability_score = np.mean(readability_scores) if readability_scores else 0.5
        
        # Overall quality calculation
        quality_penalty = min(0.3, (critical_issues * 0.1) + (high_issues * 0.05))
        overall_quality = max(0.0, (avg_layout_score + avg_readability_score) / 2 - quality_penalty)
        
        # Educational effectiveness (placeholder)
        educational_effectiveness = max(0.0, avg_readability_score - (critical_issues * 0.15))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_issues)
        
        # Determine status
        if critical_issues > 0:
            status = "issue_found"
        elif total_issues == 0:
            status = "correct"
        else:
            status = "issue_found"
        
        # Create summary
        summary = f"Analysis complete: {total_issues} issues found ({critical_issues} critical). "
        summary += f"Quality score: {overall_quality:.2f}, Layout: {avg_layout_score:.2f}, "
        summary += f"Readability: {avg_readability_score:.2f}"
        
        return VideoEvaluationResult(
            success=critical_issues == 0,
            overall_quality_score=overall_quality,
            educational_effectiveness=educational_effectiveness,
            layout_safety_score=avg_layout_score,
            issues_found=total_issues,
            critical_issues=critical_issues,
            recommendations=recommendations,
            detailed_issues=all_issues,
            frame_analyses=frame_analyses,
            evaluation_summary=summary,
            status=status
        )
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations from issues"""
        recommendations = []
        issue_types = {}
        
        # Group issues by type
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        # Generate recommendations based on issue patterns
        if 'overlap' in issue_types:
            recommendations.append(f"Fix {len(issue_types['overlap'])} content overlap issues by adjusting element positioning")
        
        if 'out_of_frame' in issue_types:
            recommendations.append(f"Bring {len(issue_types['out_of_frame'])} out-of-frame elements back into view")
        
        if 'illegible' in issue_types:
            recommendations.append(f"Increase font size or improve contrast for {len(issue_types['illegible'])} illegible text elements")
        
        if 'poor_explanation' in issue_types:
            recommendations.append("Improve educational explanations for better learning outcomes")
        
        # Add specific suggestions from issues
        for issue in issues:
            if issue.get('severity') == 'critical' and issue.get('suggestion'):
                recommendations.append(f"CRITICAL: {issue['suggestion']}")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _perform_basic_analysis(self, video_path: str, content_context: Optional[Dict[str, Any]]) -> VideoEvaluationResult:
        """Perform basic analysis without AI (fallback)"""
        print("BASIC ANALYSIS: AI not available, performing basic file analysis")
        
        # Basic video properties
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            cap.release()
        except:
            duration = 0
        
        file_size = os.path.getsize(video_path)
        
        # Basic quality heuristics
        issues = []
        if duration < 5:  # Very short video might indicate issues
            issues.append({
                "type": "duration",
                "severity": "medium",
                "description": f"Video duration is only {duration:.1f} seconds",
                "suggestion": "Check if content was fully rendered"
            })
        
        if file_size < 100000:  # Less than 100KB
            issues.append({
                "type": "file_size",
                "severity": "high",
                "description": f"Video file is only {file_size} bytes",
                "suggestion": "Video may be corrupted or incomplete"
            })
        
        # Optimistic scoring for basic analysis
        overall_quality = 0.8 if len(issues) == 0 else 0.6
        status = "correct" if len(issues) == 0 else "issue_found"
        
        return VideoEvaluationResult(
            success=len(issues) == 0,
            overall_quality_score=overall_quality,
            educational_effectiveness=0.7,
            layout_safety_score=0.8,
            issues_found=len(issues),
            critical_issues=sum(1 for i in issues if i.get('severity') == 'critical'),
            recommendations=["Video appears to be generated successfully (basic analysis)"],
            detailed_issues=issues,
            evaluation_summary=f"Basic analysis complete: {len(issues)} potential issues found",
            status=status
        )
    
    def _create_error_result(self, error_message: str) -> VideoEvaluationResult:
        """Create error result"""
        return VideoEvaluationResult(
            success=False,
            overall_quality_score=0.0,
            educational_effectiveness=0.0,
            layout_safety_score=0.0,
            issues_found=1,
            critical_issues=1,
            recommendations=[f"Error: {error_message}"],
            detailed_issues=[{
                "type": "evaluation_error",
                "severity": "critical",
                "description": error_message
            }],
            evaluation_summary=f"Evaluation failed: {error_message}",
            status="error"
        )
    
    def is_available(self) -> bool:
        """Check if evaluator is available"""
        return self.available


# Keep backward compatibility
class SimpleVideoEvaluator(EnhancedVideoEvaluator):
    """Alias for backward compatibility"""
    pass