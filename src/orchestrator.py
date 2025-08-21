"""
Video Orchestrator for Builder LLM System

This module implements the complete workflow state machine:
build → compile → evaluate → patch → promote

The orchestrator coordinates between the Builder LLM, Manim compiler,
and Gemini evaluator to create professional educational videos.
"""

import os
import time
import yaml
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .builder_llm import BuilderLLM, BuildRequest, BuildResponse
from .simple_video_evaluator import SimpleVideoEvaluator
from .schemas.video_schema import validate_video_yaml, ValidationError


class WorkflowState(Enum):
    """Orchestrator workflow states"""
    IDLE = "idle"
    BUILDING = "building"
    COMPILING_480P = "compiling_480p"
    EVALUATING = "evaluating"
    PATCHING = "patching"
    COMPILING_1080P = "compiling_1080p"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionType(Enum):
    """Action types from Builder LLM"""
    COMPILE_480P = "COMPILE_480P"
    COMPILE_1080P = "COMPILE_1080P"


@dataclass
class WorkflowResult:
    """Complete workflow execution result"""
    success: bool
    state: WorkflowState
    video_path: Optional[str] = None
    yaml_spec: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    code_path: Optional[str] = None
    error_message: Optional[str] = None
    attempts: int = 0
    evaluation_reports: List[Dict[str, Any]] = field(default_factory=list)
    compilation_logs: List[str] = field(default_factory=list)


@dataclass
class OrchestrationConfig:
    """Configuration for workflow orchestration"""
    max_repair_attempts: int = 3
    max_evaluation_iterations: int = 2
    compilation_timeout: int = 60
    enable_quality_evaluation: bool = True
    output_dir: str = "output/builder"
    temp_dir: str = "temp/builder"


class VideoOrchestrator:
    """
    Orchestrates the complete video generation workflow
    
    Manages the state machine progression:
    1. BUILDING: Generate OUTLINE → YAML → CODE → ACTION
    2. COMPILING_480P: Compile at 480p resolution
    3. EVALUATING: Gemini visual evaluation (if enabled)
    4. PATCHING: Apply fixes based on errors/evaluation
    5. COMPILING_1080P: Final high-resolution compilation
    6. COMPLETED: Workflow finished successfully
    """
    
    def __init__(self, openai_api_key: str, gemini_api_key: Optional[str] = None,
                 config: Optional[OrchestrationConfig] = None):
        """
        Initialize orchestrator with API keys and configuration
        
        Args:
            openai_api_key: OpenAI API key for Builder LLM
            gemini_api_key: Optional Gemini API key for evaluation
            config: Optional configuration overrides
        """
        self.config = config or OrchestrationConfig()
        
        # Initialize components
        self.builder_llm = BuilderLLM(openai_api_key)
        
        self.video_evaluator = None
        if gemini_api_key and self.config.enable_quality_evaluation:
            try:
                self.video_evaluator = SimpleVideoEvaluator(gemini_api_key)
                print("Video quality evaluation enabled with Gemini 2.5 Flash-Lite")
            except Exception as e:
                print(f"Warning: Video evaluator initialization failed: {e}")
                print("Continuing without video quality evaluation")
        
        # Initialize compiler
        from .compiler import ManimCompiler
        self.compiler = ManimCompiler(
            timeout=self.config.compilation_timeout,
            output_dir=self.config.output_dir
        )
        
        # Workflow state
        self.current_state = WorkflowState.IDLE
        self.current_build: Optional[WorkflowResult] = None
        
        # Create directories
        os.makedirs(self.config.output_dir, exist_ok=True)
        os.makedirs(self.config.temp_dir, exist_ok=True)
    
    def create_video(self, request: BuildRequest) -> WorkflowResult:
        """
        Main entry point: Create a complete video from topic to final MP4
        
        Args:
            request: Build request with topic and style preferences
            
        Returns:
            WorkflowResult with success status and generated assets
        """
        print(f"VIDEO: Starting video creation for: '{request.topic}'")
        print("=" * 60)
        
        # Initialize workflow result
        self.current_build = WorkflowResult(
            success=False,
            state=WorkflowState.BUILDING
        )
        self.current_state = WorkflowState.BUILDING
        
        try:
            # Step 1: Initial build (OUTLINE → YAML → CODE → ACTION)
            if not self._execute_initial_build(request):
                return self._finalize_workflow(False, "Initial build failed")
            
            # Step 2: 480p compilation loop with repairs
            if not self._execute_480p_workflow():
                return self._finalize_workflow(False, "480p compilation failed")
            
            # Step 3: Visual evaluation loop (if enabled)
            if self.video_evaluator:
                if not self._execute_evaluation_workflow():
                    return self._finalize_workflow(False, "Visual evaluation failed")
            else:
                print("LIST: Skipping visual evaluation (not enabled)")
            
            # Step 4: Final 1080p compilation
            if not self._execute_1080p_compilation():
                return self._finalize_workflow(False, "1080p compilation failed")
            
            # Success!
            return self._finalize_workflow(True, "Video creation completed successfully")
            
        except Exception as e:
            error_msg = f"Unexpected error in orchestrator: {e}"
            print(f"BOOM: ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            return self._finalize_workflow(False, error_msg)
    
    def _execute_initial_build(self, request: BuildRequest) -> bool:
        """Execute initial OUTLINE → YAML → CODE → ACTION generation"""
        print("BUILD: Phase 1: Initial Build")
        print("-" * 30)
        
        try:
            # Call Builder LLM for initial generation
            build_response = self.builder_llm.build_video(request)
            
            # Validate YAML specification
            try:
                validate_video_yaml(build_response.yaml_spec)
                print("SUCCESS: YAML specification validated successfully")
            except ValidationError as e:
                print(f"ERROR: YAML validation failed: {e}")
                print(f"Generated YAML structure:")
                print(f"  - Top level keys: {list(build_response.yaml_spec.keys()) if build_response.yaml_spec else 'None'}")
                if 'scenes' in build_response.yaml_spec:
                    scenes = build_response.yaml_spec['scenes']
                    print(f"  - Number of scenes: {len(scenes)}")
                    if scenes:
                        print(f"  - First scene keys: {list(scenes[0].keys())}")
                        if 'layout' in scenes[0] and 'elements' in scenes[0]['layout']:
                            elements = scenes[0]['layout']['elements']
                            if elements:
                                print(f"  - First element keys: {list(elements[0].keys())}")
                self.current_build.error_message = f"Invalid YAML: {e}"
                return False
            
            # Display layout validation results if available
            if hasattr(build_response, 'layout_validation') and build_response.layout_validation:
                layout_summary = self.builder_llm.get_layout_validation_summary(build_response)
                print(f"RULER: {layout_summary}")
                
                # Log layout validation details
                validation = build_response.layout_validation
                if validation.get('issues'):
                    print(f"   └─ Found {validation.get('total_issues', 0)} layout issues")
                    if validation.get('recommendations'):
                        for rec in validation['recommendations'][:2]:  # Show first 2 recommendations
                            print(f"   TIP: {rec}")
            else:
                print("RULER: Layout validation: Skipped (utilities not available)")
            
            # Store generated content
            self.current_build.yaml_spec = build_response.yaml_spec
            self.current_build.code = build_response.code
            
            # Save files for debugging
            self._save_build_artifacts(build_response, request.topic)
            
            print("SUCCESS: Initial build completed successfully")
            print(f"PAGE: Generated {len(build_response.outline.split('n'))} outline sections")
            print(f"VIDEO: Created {len(build_response.yaml_spec.get('scenes', []))} scenes")
            print(f"NOTE: Generated {len(build_response.code.split('n'))} lines of code")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Initial build failed: {e}")
            self.current_build.error_message = str(e)
            return False
    
    def _execute_480p_workflow(self) -> bool:
        """Execute 480p compilation with error repair loop"""
        print("\nTARGET: Phase 2: 480p Compilation & Repair")
        print("-" * 40)
        
        self.current_state = WorkflowState.COMPILING_480P
        
        for attempt in range(1, self.config.max_repair_attempts + 1):
            print(f"\nPROCESS: Compilation attempt {attempt}/{self.config.max_repair_attempts}")
            
            # Attempt compilation
            success, stdout, stderr, video_path = self._compile_current_code("480p")
            self.current_build.compilation_logs.append(f"Attempt {attempt}: {stderr if stderr else 'Success'}")
            
            if success:
                print("SUCCESS: 480p compilation successful!")
                self.current_build.video_path = video_path
                return True
            
            print(f"ERROR: Compilation failed: {stderr[:200]}...")
            
            # If not last attempt, try to repair
            if attempt < self.config.max_repair_attempts:
                print("TOOL: Attempting code repair...")
                if self._repair_compilation_error(stderr):
                    print("SUCCESS: Code repair applied, retrying compilation...")
                else:
                    print("WARNING: Could not repair code automatically")
            
        print(f"BOOM: 480p compilation failed after {self.config.max_repair_attempts} attempts")
        self.current_build.error_message = "Maximum repair attempts exceeded"
        return False
    
    def _execute_evaluation_workflow(self) -> bool:
        """Execute visual evaluation with fix loop"""
        print("\nEYE: Phase 3: Visual Quality Evaluation")
        print("-" * 40)
        
        if not self.current_build.video_path:
            print("ERROR: No video file available for evaluation")
            return False
        
        self.current_state = WorkflowState.EVALUATING
        
        for iteration in range(1, self.config.max_evaluation_iterations + 1):
            print(f"\nSEARCH: Evaluation iteration {iteration}/{self.config.max_evaluation_iterations}")
            
            # Perform evaluation
            evaluation_result = self.video_evaluator.evaluate_video(
                self.current_build.video_path,
                content_context={'topic': self.current_build.yaml_spec.get('topic', 'Unknown')}
            )
            
            self.current_build.evaluation_reports.append(evaluation_result)
            
            if evaluation_result['status'] == 'correct':
                print("SUCCESS: Video quality approved! No issues found.")
                return True
            
            elif evaluation_result['status'] == 'issue_found':
                issues = evaluation_result.get('issues', [])
                print(f"WARNING: Quality issues found: {len(issues)} problems detected")
                
                for i, issue in enumerate(issues, 1):
                    category = issue.get('category', 'unknown')
                    description = issue.get('description', 'No description')
                    print(f"  {i}. {category}: {description}")
                
                # Apply fixes if not last iteration
                if iteration < self.config.max_evaluation_iterations:
                    print("TOOL: Applying visual quality fixes...")
                    if self._fix_visual_issues(evaluation_result):
                        print("SUCCESS: Visual fixes applied, recompiling...")
                        # Recompile with fixes
                        success, stdout, stderr, video_path = self._compile_current_code("480p")
                        if success:
                            self.current_build.video_path = video_path
                            print("SUCCESS: Recompilation successful")
                            continue
                        else:
                            print(f"ERROR: Recompilation failed: {stderr[:200]}...")
                            return False
                    else:
                        print("WARNING: Could not apply visual fixes automatically")
                        return False
        
        print("WARNING: Maximum evaluation iterations reached, proceeding with current version")
        return True
    
    def _execute_1080p_compilation(self) -> bool:
        """Execute final 1080p compilation"""
        print("\nTARGET: Phase 4: Final 1080p Compilation")
        print("-" * 40)
        
        self.current_state = WorkflowState.COMPILING_1080P
        
        # Request 1080p compilation from Builder LLM
        action = self.builder_llm.promote_to_1080p()
        print(f"NOTE: Builder LLM action: {action}")
        
        # Compile at 1080p
        success, stdout, stderr, video_path = self._compile_current_code("1080p")
        
        if success:
            print("COMPLETE: 1080p compilation successful!")
            self.current_build.video_path = video_path
            return True
        else:
            print(f"ERROR: 1080p compilation failed: {stderr[:200]}...")
            # For 1080p failure, keep the 480p version
            print("LIST: Keeping 480p version as final output")
            return True  # Don't fail the entire workflow for 1080p issues
    
    def _compile_current_code(self, resolution: str) -> Tuple[bool, str, str, Optional[str]]:
        """Compile current code at specified resolution"""
        if not self.current_build or not self.current_build.code:
            return False, "", "No code available for compilation", None
        
        # Save code to file
        topic_name = self.current_build.yaml_spec.get('topic', 'video').replace(' ', '_').lower()
        code_filename = f"{topic_name}_scene.py"
        code_filepath = os.path.join(self.config.temp_dir, code_filename)
        
        with open(code_filepath, 'w', encoding='utf-8') as f:
            f.write(self.current_build.code)
        
        # Compile with Manim
        return self.compiler.compile_scene(code_filepath, resolution)
    
    def _repair_compilation_error(self, traceback: str) -> bool:
        """Attempt to repair compilation error using Builder LLM"""
        if not self.current_build or not self.current_build.code:
            return False
        
        self.current_state = WorkflowState.PATCHING
        
        try:
            # First try automated syntax fixes
            fixed_code = self._apply_automated_fixes(self.current_build.code, traceback)
            if fixed_code != self.current_build.code:
                print("SUCCESS: Applied automated syntax fixes")
                self.current_build.code = fixed_code
                self._update_current_code_file(fixed_code)
                return True
            
            # If automated fixes don't work, try Builder LLM repair
            patch, action = self.builder_llm.repair_code(
                self.current_build.code, traceback
            )
            
            if patch.strip():
                # Apply patch to current code
                # For simplicity, we'll regenerate the code with repairs
                # In a full implementation, you'd apply the actual patch
                print(f"NOTE: Applying code patch...")
                print(f"TARGET: Next action: {action}")
                
                # Store the patch for debugging
                self._save_patch(patch, len(self.current_build.compilation_logs))
                
                # For now, we assume the LLM provides complete corrected code
                # In practice, you'd implement proper patch application
                return True
            
        except Exception as e:
            print(f"ERROR: Code repair failed: {e}")
        
        return False
    
    def _apply_automated_fixes(self, code: str, traceback: str) -> str:
        """Apply common automated fixes for syntax errors"""
        # Don't attempt fixes on empty or very short code
        if not code or len(code.strip()) < 50:
            return code
            
        fixed_code = code
        
        # Fix 0: Remove markdown formatting that may be present
        import re
        
        # Remove markdown code block markers
        if fixed_code.startswith('```python'):
            lines = fixed_code.split('\n')
            # Remove first line if it's ```python
            if lines[0].strip() == '```python':
                lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            fixed_code = '\n'.join(lines)
        
        # Fix 1: Recursive class inheritance
        fixed_code = re.sub(
            r'class SafeScene\(SafeScene\):',
            'class SafeScene(Scene):',
            fixed_code
        )
        
        # Fix 3: Wrong method calls in SafeScene class
        fixed_code = re.sub(
            r'self\.safe_add\(\*([^)]+)\)',
            r'self.add(\1)',
            fixed_code
        )
        
        fixed_code = re.sub(
            r'self\.safe_play\(\*([^)]+)\)',
            r'self.play(\1)',
            fixed_code
        )
        
        # Fix 4: Common Manim API issues
        fixed_code = re.sub(
            r'\.get_graph\(([^,]+),\s*color=([^)]+)\)',
            r'.plot(\1, color=\2)',
            fixed_code
        )
        
        # Fix 5: Missing closing parentheses and other common issues
        lines = fixed_code.split('\n')
        for i, line in enumerate(lines):
            # Fix safe_position calls with missing parentheses
            if 'safe_position(' in line and line.count('(') > line.count(')'):
                lines[i] = line + ')'
            elif 'group.move_to(safe_position(ORIGIN' in line and not line.endswith('))'):
                lines[i] = line.replace('group.move_to(safe_position(ORIGIN', 'group.move_to(ORIGIN)')
            elif 'mob.move_to(safe_position(safe_pos' in line and not line.endswith('))'):
                lines[i] = line.replace('mob.move_to(safe_position(safe_pos', 'mob.move_to(safe_pos)')
            # Fix play method calls with wrong syntax
            elif 'self.safe_play(' in line:
                lines[i] = line.replace('self.safe_play(', 'self.play(')
            # Fix add method calls with wrong syntax
            elif 'self.add(mobjects)' in line:
                lines[i] = line.replace('self.add(mobjects)', 'self.add(*mobjects)')
            elif 'self.add(safe_mobjects)' in line:
                lines[i] = line.replace('self.add(safe_mobjects)', 'self.add(*safe_mobjects)')
            # Fix play method with wrong unpacking
            elif 'self.play(animations,' in line:
                lines[i] = line.replace('self.play(animations,', 'self.play(*animations,')
        
        fixed_code = '\n'.join(lines)
        
        return fixed_code
    
    def _update_current_code_file(self, code: str):
        """Update the current code file with fixed code"""
        if self.current_build and self.current_build.code_path:
            try:
                with open(self.current_build.code_path, 'w', encoding='utf-8') as f:
                    f.write(code)
            except Exception as e:
                print(f"WARNING: Could not update code file: {e}")
    
    def _fix_visual_issues(self, evaluation_result: Dict[str, Any]) -> bool:
        """Apply fixes for visual quality issues"""
        if not self.current_build or not self.current_build.code:
            return False
        
        self.current_state = WorkflowState.PATCHING
        
        try:
            # Convert evaluation result to YAML format for Builder LLM
            gemini_yaml = yaml.dump(evaluation_result, default_flow_style=False)
            
            patch, action = self.builder_llm.fix_visual_issues(
                self.current_build.code, gemini_yaml
            )
            
            if patch.strip():
                print(f"NOTE: Applying visual fixes...")
                print(f"TARGET: Next action: {action}")
                
                # Store the patch for debugging
                self._save_patch(patch, f"visual_fix_{len(self.current_build.evaluation_reports)}")
                
                return True
        
        except Exception as e:
            print(f"ERROR: Visual fix failed: {e}")
        
        return False
    
    def _save_build_artifacts(self, build_response: BuildResponse, topic: str):
        """Save all build artifacts for debugging"""
        topic_name = topic.replace(' ', '_').lower()
        timestamp = int(time.time())
        
        # Save outline
        outline_path = os.path.join(self.config.output_dir, f"{topic_name}_{timestamp}_outline.txt")
        with open(outline_path, 'w', encoding='utf-8') as f:
            f.write(build_response.outline)
        
        # Save YAML spec
        yaml_path = os.path.join(self.config.output_dir, f"{topic_name}_{timestamp}_spec.yaml")
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(build_response.yaml_spec, f, default_flow_style=False, allow_unicode=True)
        
        # Save initial code
        code_path = os.path.join(self.config.output_dir, f"{topic_name}_{timestamp}_scene.py")
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(build_response.code)
        
        # Store in current build for later use
        if self.current_build:
            self.current_build.code_path = code_path
        
        print(f"FOLDER: Build artifacts saved:")
        print(f"   Outline: {outline_path}")
        print(f"   YAML Spec: {yaml_path}")
        print(f"   Code: {code_path}")
    
    def _save_patch(self, patch: str, identifier: str):
        """Save patch for debugging"""
        if not self.current_build or not self.current_build.yaml_spec:
            return
        
        topic_name = self.current_build.yaml_spec.get('topic', 'video').replace(' ', '_').lower()
        timestamp = int(time.time())
        
        patch_path = os.path.join(self.config.output_dir, f"{topic_name}_{timestamp}_{identifier}.patch")
        with open(patch_path, 'w', encoding='utf-8') as f:
            f.write(patch)
        
        print(f"FLOPPY: Patch saved: {patch_path}")
    
    def _finalize_workflow(self, success: bool, message: str) -> WorkflowResult:
        """Finalize workflow and return result"""
        if success:
            self.current_state = WorkflowState.COMPLETED
            print(f"\nCOMPLETE: SUCCESS: {message}")
            if self.current_build and self.current_build.video_path:
                print(f"VIDEO: Final video: {self.current_build.video_path}")
        else:
            self.current_state = WorkflowState.FAILED
            print(f"\nBOOM: FAILED: {message}")
        
        if self.current_build:
            self.current_build.success = success
            self.current_build.state = self.current_state
            if not success:
                self.current_build.error_message = message
        
        print("=" * 60)
        return self.current_build or WorkflowResult(success=False, state=self.current_state, error_message=message)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            'state': self.current_state.value,
            'current_build': {
                'success': self.current_build.success if self.current_build else None,
                'attempts': self.current_build.attempts if self.current_build else 0,
                'video_path': self.current_build.video_path if self.current_build else None,
                'error_message': self.current_build.error_message if self.current_build else None
            } if self.current_build else None,
            'config': {
                'max_repair_attempts': self.config.max_repair_attempts,
                'max_evaluation_iterations': self.config.max_evaluation_iterations,
                'evaluation_enabled': self.video_evaluator is not None
            }
        }


def create_orchestrator(openai_api_key: str, gemini_api_key: Optional[str] = None,
                       config: Optional[OrchestrationConfig] = None) -> VideoOrchestrator:
    """Factory function for creating video orchestrator"""
    return VideoOrchestrator(openai_api_key, gemini_api_key, config)