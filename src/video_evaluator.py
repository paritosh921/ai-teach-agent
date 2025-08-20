import os
import yaml
from typing import Dict, Any, Optional, List, Tuple
from google import genai

class VideoEvaluator:
    """
    Gemini 2.5 Flash-Lite video evaluator for checking:
    - Visual content correctness
    - Element overlapping detection  
    - Out-of-frame content detection
    """
    
    def __init__(self, gemini_api_key: str):
        """Initialize Gemini evaluator with API key."""
        # Set API key as environment variable for the client
        os.environ['GEMINI_API_KEY'] = gemini_api_key
        
        # Initialize Gemini client
        self.client = genai.Client()
        
        # Model configuration
        self.model_name = "gemini-2.5-flash-lite"
        
        # Load evaluation schema
        self.evaluation_schema = self._load_evaluation_schema()
        
    def _load_evaluation_schema(self) -> Dict[str, Any]:
        """Load video evaluation criteria and response schema."""
        try:
            schema_path = os.path.join(os.path.dirname(__file__), 'config', 'video_evaluation_schema.yaml')
            with open(schema_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print("WARNING: Video evaluation schema not found, using basic criteria")
            return {
                "evaluation_criteria": {
                    "visual_correctness": ["Text clearly readable", "Formulas render correctly"],
                    "overlap_detection": ["No overlapping elements", "Minimum 0.6 unit gaps"],
                    "frame_boundaries": ["Content within safe margins", "No cut-off elements"]
                }
            }
    
    def evaluate_video(self, video_path: str, content_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate video quality using Gemini 2.5 Flash-Lite.
        
        Args:
            video_path: Path to the generated video file
            content_context: Optional context about expected content
            
        Returns:
            Dict with 'status' and optionally 'issues' for feedback
        """
        print(f"Evaluating video quality: {video_path}")
        
        # Check if video file exists
        if not os.path.exists(video_path):
            return {
                "status": "issue_found",
                "issues": [{
                    "issue_id": "file_not_found",
                    "category": "technical",
                    "severity": "critical", 
                    "description": f"Video file not found: {video_path}",
                    "timestamp": 0,
                    "suggested_fix": {
                        "action": "regenerate",
                        "specific_changes": "Ensure Manim compilation completes successfully"
                    }
                }]
            }
        
        # Check video file size to determine upload method
        try:
            file_size = os.path.getsize(video_path)
            print(f"Video file size: {file_size / (1024*1024):.1f} MB")
            
            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(content_context)
            
            if file_size < 20 * 1024 * 1024:  # Less than 20MB - use inline data
                print("Using inline video data for analysis...")
                evaluation_result = self._analyze_video_inline(video_path, prompt)
            else:  # Larger files - use Files API
                print("Uploading video to Gemini for analysis...")
                evaluation_result = self._analyze_video_upload(video_path, prompt)
            
            print(f"Evaluation complete: {evaluation_result['status']}")
            if evaluation_result['status'] == 'issue_found':
                print(f"Found {len(evaluation_result.get('issues', []))} issues")
            
            return evaluation_result
            
        except Exception as e:
            print(f"ERROR: Error during video evaluation: {e}")
            return {
                "status": "issue_found",
                "issues": [{
                    "issue_id": "evaluation_error",
                    "category": "technical",
                    "severity": "critical",
                    "description": f"Video evaluation failed: {str(e)}",
                    "timestamp": 0,
                    "suggested_fix": {
                        "action": "retry",
                        "specific_changes": "Check API connection and video format"
                    }
                }]
            }
    
    def _analyze_video_inline(self, video_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze video using inline data method (< 20MB)."""
        try:
            print("Analyzing video with Gemini (inline method)...")
            # For smaller files, we'll use the upload method as it's more reliable
            return self._analyze_video_upload(video_path, prompt)
            
        except Exception as e:
            raise Exception(f"Inline video analysis failed: {e}")
    
    def _analyze_video_upload(self, video_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze video using Files API upload method."""
        try:
            # Upload video file
            print("Uploading video file...")
            uploaded_file = self.client.files.upload(file=video_path)
            print(f"Video uploaded: {uploaded_file.name}")
            
            try:
                # Wait for file to be processed and become ACTIVE
                print("Waiting for video to be processed...")
                import time
                max_wait_time = 60  # 60 seconds max wait
                wait_time = 0
                poll_interval = 2  # Check every 2 seconds
                
                while wait_time < max_wait_time:
                    # Get file status
                    file_info = self.client.files.get(name=uploaded_file.name)
                    if hasattr(file_info, 'state') and hasattr(file_info.state, 'name'):
                        state_name = file_info.state.name
                        if state_name == 'ACTIVE':
                            print("Video processing complete!")
                            break
                        elif state_name == 'FAILED':
                            raise Exception(f"Video processing failed: {state_name}")
                        print(f"Video processing... state: {state_name} (waited {wait_time}s)")
                    else:
                        print(f"Video processing... (waited {wait_time}s)")
                    
                    time.sleep(poll_interval)
                    wait_time += poll_interval
                
                if wait_time >= max_wait_time:
                    raise Exception("Video processing timeout - file not ready within 60 seconds")
                
                # Generate content with uploaded file
                print("Analyzing video with Gemini...")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[uploaded_file, prompt]
                )
                
                result = self._parse_evaluation_response(response.text)
                
                # Clean up uploaded file
                self.client.files.delete(name=uploaded_file.name)
                print("Cleaned up uploaded file")
                
                return result
                
            except Exception as e:
                # Ensure cleanup even if analysis fails
                try:
                    self.client.files.delete(name=uploaded_file.name)
                except:
                    pass
                raise e
                
        except Exception as e:
            raise Exception(f"Upload video analysis failed: {e}")
    
    def _create_evaluation_prompt(self, content_context: Dict[str, Any] = None) -> str:
        """Create detailed evaluation prompt for Gemini."""
        criteria = self.evaluation_schema.get('evaluation_criteria', {})
        
        prompt = f"""
        Analyze this educational animation video for quality issues. You are evaluating a Manim-generated educational video that should follow professional 3Blue1Brown standards.

        EVALUATION CRITERIA:

        1. VISUAL CORRECTNESS:
        {self._format_criteria_list(criteria.get('visual_correctness', []))}

        2. OVERLAP DETECTION:
        {self._format_criteria_list(criteria.get('overlap_detection', []))}

        3. FRAME BOUNDARIES:
        {self._format_criteria_list(criteria.get('frame_boundaries', []))}

        4. TIMING ISSUES:
        {self._format_criteria_list(criteria.get('timing_issues', []))}

        RESPONSE FORMAT:
        You must respond with ONLY one of these two options:

        Option 1 - If video is perfect:
        ```yaml
        status: "correct"
        ```

        Option 2 - If issues found:
        ```yaml
        status: "issue_found"
        issues:
          - issue_id: "unique_id"
            category: "overlap|out_of_frame|visual_correctness|timing"
            severity: "critical|major|minor"
            description: "Clear description of the problem"
            timestamp: 5.2  # seconds where issue occurs
            affected_elements:
              - element_type: "text|shape|formula|graph"
                element_description: "specific element description"
                position_issue: "exact positioning problem"
            suggested_fix:
              action: "reposition|resize|remove|modify_timing"
              specific_changes: "detailed fix instructions"
        ```

        IMPORTANT REQUIREMENTS:
        - Check EVERY second of the video carefully
        - Look for ANY overlapping text, shapes, or formulas
        - Verify ALL content stays within video frame boundaries
        - Ensure text is readable and formulas render correctly
        - Report specific timestamps where issues occur
        - Provide actionable fix suggestions

        Expected content context: {content_context.get('topic', 'Educational animation') if content_context else 'Educational animation'}

        Return ONLY the YAML response - no additional text or explanations.
        """
        
        return prompt.strip()
    
    def _format_criteria_list(self, criteria_list: List[str]) -> str:
        """Format criteria list for prompt."""
        if not criteria_list:
            return "- Standard quality requirements"
        return '\n'.join(f"        - {criterion}" for criterion in criteria_list)
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured evaluation result."""
        try:
            # Extract YAML content from response
            yaml_content = response_text.strip()
            
            # Clean up response if it has markdown formatting
            if "```yaml" in yaml_content:
                import re
                yaml_match = re.search(r'```yaml\n(.*?)```', yaml_content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
            elif "```" in yaml_content:
                import re
                yaml_match = re.search(r'```\n(.*?)```', yaml_content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
            
            # Parse YAML response
            evaluation_result = yaml.safe_load(yaml_content)
            
            # Validate response format
            if not isinstance(evaluation_result, dict):
                raise ValueError("Response is not a valid dictionary")
            
            if 'status' not in evaluation_result:
                raise ValueError("Response missing required 'status' field")
            
            status = evaluation_result['status']
            if status not in ['correct', 'issue_found']:
                raise ValueError(f"Invalid status: {status}")
            
            # Validate issues if status is issue_found
            if status == 'issue_found':
                if 'issues' not in evaluation_result:
                    raise ValueError("Response with issue_found status missing 'issues' field")
                
                issues = evaluation_result['issues']
                if not isinstance(issues, list) or len(issues) == 0:
                    raise ValueError("Issues must be a non-empty list")
            
            return evaluation_result
            
        except Exception as e:
            print(f"WARNING: Error parsing evaluation response: {e}")
            print(f"Raw response: {response_text[:200]}...")
            
            # Return safe fallback indicating parsing error
            return {
                "status": "issue_found",
                "issues": [{
                    "issue_id": "parse_error",
                    "category": "technical",
                    "severity": "critical",
                    "description": f"Failed to parse evaluation response: {str(e)}",
                    "timestamp": 0,
                    "suggested_fix": {
                        "action": "retry",
                        "specific_changes": "Check Gemini response format"
                    }
                }]
            }
    
    def save_evaluation_feedback(self, evaluation_result: Dict[str, Any], output_path: str) -> None:
        """Save evaluation feedback to YAML file for debugging."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(evaluation_result, f, default_flow_style=False, allow_unicode=True)
            print(f"Evaluation feedback saved: {output_path}")
        except Exception as e:
            print(f"WARNING: Could not save evaluation feedback: {e}")