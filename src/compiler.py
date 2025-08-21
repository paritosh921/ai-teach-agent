"""
Manim Compiler for Builder LLM System

This module handles Manim compilation with support for:
- 480p → 1080p progression
- Traceback capture and formatting  
- Unified diff patching system
- Scene detection and validation
"""

import os
import re
import subprocess
import tempfile
import difflib
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompilationResult:
    """Result of a Manim compilation attempt"""
    success: bool
    stdout: str
    stderr: str
    video_path: Optional[str] = None
    scene_name: Optional[str] = None
    resolution: Optional[str] = None
    duration: float = 0.0
    error_type: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class PatchResult:
    """Result of applying a code patch"""
    success: bool
    patched_code: str
    error_message: Optional[str] = None
    changes_applied: int = 0


class ManimCompiler:
    """
    Handles Manim compilation with comprehensive error handling
    
    Features:
    - Progressive resolution compilation (480p → 1080p)
    - Detailed error analysis and reporting
    - Scene detection and validation
    - Output file management
    - Timeout handling for long compilations
    """
    
    def __init__(self, timeout: int = 60, output_dir: str = "output/builder",
                 temp_dir: str = "temp/builder"):
        """
        Initialize compiler with configuration
        
        Args:
            timeout: Maximum compilation time in seconds
            output_dir: Directory for final outputs
            temp_dir: Directory for temporary files
        """
        self.timeout = timeout
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Quality settings for different resolutions
        self.quality_settings = {
            "480p": {
                "quality": "low_quality",  # -ql
                "resolution": "480p",
                "fps": 15
            },
            "1080p": {
                "quality": "production_quality",  # -qp
                "resolution": "1080p", 
                "fps": 30
            },
            "preview": {
                "quality": "low_quality",
                "resolution": "480p",
                "fps": 15,
                "preview": True
            }
        }
    
    def compile_scene(self, code_filepath: str, resolution: str = "480p") -> Tuple[bool, str, str, Optional[str]]:
        """
        Compile a Manim scene file
        
        Args:
            code_filepath: Path to the Python scene file
            resolution: Target resolution ("480p", "1080p", "preview")
            
        Returns:
            Tuple of (success, stdout, stderr, video_path)
        """
        print(f"VIDEO: Compiling scene at {resolution}...")
        
        try:
            # Validate scene file
            scene_name = self._extract_scene_name(code_filepath)
            if not scene_name:
                return False, "", "No valid Scene class found in code", None
            
            print(f"NOTE: Detected scene class: {scene_name}")
            
            # Prepare compilation command
            cmd = self._build_manim_command(code_filepath, scene_name, resolution)
            print(f"⚙️ Command: {' '.join(cmd)}")
            
            # Execute compilation
            result = self._execute_compilation(cmd, code_filepath)
            
            if result.success:
                # Find generated video file
                video_path = self._find_output_video(code_filepath, scene_name, resolution)
                if video_path:
                    print(f"SUCCESS: Video generated: {video_path}")
                    return True, result.stdout, result.stderr, video_path
                else:
                    print("WARNING: Compilation succeeded but no video file found")
                    return False, result.stdout, "Video file not found after compilation", None
            else:
                print(f"ERROR: Compilation failed: {result.stderr[:200]}...")
                return False, result.stdout, result.stderr, None
                
        except Exception as e:
            error_msg = f"Compilation exception: {e}"
            print(f"BOOM: {error_msg}")
            return False, "", error_msg, None
    
    def apply_patch(self, original_code: str, patch_content: str) -> PatchResult:
        """
        Apply a unified diff patch to code
        
        Args:
            original_code: Original source code
            patch_content: Unified diff patch content
            
        Returns:
            PatchResult with patched code or error info
        """
        try:
            # Parse patch content - simplified implementation
            # In a full implementation, you'd use proper patch parsing
            lines = patch_content.split('\n')
            
            # For now, assume the patch contains complete replacement code
            # This is a simplification - real patches would be applied line by line
            if "```python" in patch_content:
                # Extract Python code from patch
                start_idx = None
                end_idx = None
                
                for i, line in enumerate(lines):
                    if "```python" in line:
                        start_idx = i + 1
                    elif line.strip() == "```" and start_idx is not None:
                        end_idx = i
                        break
                
                if start_idx is not None and end_idx is not None:
                    patched_code = '\n'.join(lines[start_idx:end_idx])
                    return PatchResult(
                        success=True,
                        patched_code=patched_code,
                        changes_applied=1
                    )
            
            # Fallback: try to apply as direct replacement
            # This assumes the LLM provides complete corrected code
            clean_patch = self._clean_patch_content(patch_content)
            if clean_patch and "from manim import" in clean_patch:
                return PatchResult(
                    success=True,
                    patched_code=clean_patch,
                    changes_applied=1
                )
            
            return PatchResult(
                success=False,
                patched_code=original_code,
                error_message="Could not parse patch format"
            )
            
        except Exception as e:
            return PatchResult(
                success=False,
                patched_code=original_code,
                error_message=f"Patch application failed: {e}"
            )
    
    def analyze_error(self, stderr: str) -> Dict[str, Any]:
        """
        Analyze compilation error and extract key information
        
        Args:
            stderr: Error output from Manim compilation
            
        Returns:
            Dictionary with error analysis
        """
        analysis = {
            'error_type': 'unknown',
            'line_number': None,
            'error_message': stderr,
            'suggestions': [],
            'severity': 'medium'
        }
        
        # Common error patterns
        error_patterns = {
            'syntax_error': r'SyntaxError.*line (\d+)',
            'import_error': r'ImportError|ModuleNotFoundError',
            'name_error': r'NameError.*\'(.+?)\' is not defined',
            'attribute_error': r'AttributeError.*\'(.+?)\' object has no attribute \'(.+?)\'',
            'type_error': r'TypeError.*(.+)',
            'manim_error': r'ManimError|Scene.*error',
            'unexpected_keyword': r'unexpected keyword argument \'(.+?)\'',
            'file_not_found': r'FileNotFoundError|No such file'
        }
        
        # Extract line number
        line_match = re.search(r'line (\d+)', stderr, re.IGNORECASE)
        if line_match:
            analysis['line_number'] = int(line_match.group(1))
        
        # Identify error type
        for error_type, pattern in error_patterns.items():
            if re.search(pattern, stderr, re.IGNORECASE):
                analysis['error_type'] = error_type
                break
        
        # Generate suggestions based on error type
        analysis['suggestions'] = self._generate_error_suggestions(analysis['error_type'], stderr)
        
        # Determine severity
        if analysis['error_type'] in ['syntax_error', 'import_error', 'file_not_found']:
            analysis['severity'] = 'high'
        elif analysis['error_type'] in ['manim_error', 'unexpected_keyword']:
            analysis['severity'] = 'medium'
        else:
            analysis['severity'] = 'low'
        
        return analysis
    
    def _extract_scene_name(self, code_filepath: str) -> Optional[str]:
        """Extract Scene class name from Python file"""
        try:
            with open(code_filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for class definitions that inherit from Scene or SafeScene
            scene_pattern = r'class\s+(\w+)\s*\(\s*(?:Scene|SafeScene)\s*\):'
            matches = re.findall(scene_pattern, content)
            
            if matches:
                # Skip SafeScene itself and return the first actual scene class
                for match in matches:
                    if match != 'SafeScene':
                        return match
                # If only SafeScene found, return it
                return matches[0]
            
            # Fallback: look for any class with "Scene" in the name
            fallback_pattern = r'class\s+(\w*Scene\w*)\s*\([^)]*\):'
            matches = re.findall(fallback_pattern, content)
            
            if matches:
                # Skip SafeScene itself and return the first actual scene class
                for match in matches:
                    if match != 'SafeScene':
                        return match
                # If only SafeScene found, return it
                return matches[0]
            
            return None
            
        except Exception as e:
            print(f"Error extracting scene name: {e}")
            return None
    
    def _build_manim_command(self, code_filepath: str, scene_name: str, resolution: str) -> List[str]:
        """Build Manim command line arguments"""
        settings = self.quality_settings.get(resolution, self.quality_settings["480p"])
        
        cmd = ["python", "-m", "manim"]
        
        # Quality flag
        if settings["quality"] == "low_quality":
            cmd.append("-ql")
        elif settings["quality"] == "production_quality":
            cmd.append("-qp")
        else:
            cmd.append("-qm")  # medium quality
        
        # Preview mode
        if settings.get("preview", False):
            cmd.append("-p")
        
        # Disable caching for consistency
        cmd.append("--disable_caching")
        
        # Output directory
        cmd.extend(["--media_dir", str(self.output_dir / "media")])
        
        # Input file and scene
        cmd.append(str(Path(code_filepath).absolute()))
        cmd.append(scene_name)
        
        return cmd
    
    def _execute_compilation(self, cmd: List[str], code_filepath: str) -> CompilationResult:
        """Execute Manim compilation command"""
        try:
            # Set working directory to the file's parent directory
            working_dir = Path(code_filepath).parent
            
            # Set environment variables for UTF-8 encoding
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONLEGACYWINDOWSFSENCODING'] = '0'
            
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
                encoding='utf-8',
                errors='replace'
            )
            

            
            # Check if compilation succeeded despite warnings
            success = result.returncode == 0
            
            # Handle pydub ffmpeg warnings - these are often just warnings, not fatal errors
            if not success and "pydub" in result.stderr and "ffmpeg" in result.stderr:
                # Check if there are actual error messages beyond the pydub warning
                error_lines = [line for line in result.stderr.split('\n') 
                             if line.strip() and not line.startswith('RuntimeWarning') 
                             and 'pydub' not in line.lower() and 'warn' not in line.lower()]
                
                if not error_lines:
                    # Only pydub warnings, treat as success
                    success = True
                    print("NOTE: Ignoring pydub ffmpeg warnings - treating as success")
            
            # Additional check: if return code is 0, it definitely succeeded
            if result.returncode == 0:
                success = True
            
            return CompilationResult(
                success=success,
                stdout=result.stdout,
                stderr=result.stderr
            )
            
        except subprocess.TimeoutExpired:
            return CompilationResult(
                success=False,
                stdout="",
                stderr=f"Compilation timed out after {self.timeout} seconds"
            )
        except Exception as e:
            return CompilationResult(
                success=False,
                stdout="",
                stderr=f"Compilation failed: {e}"
            )
    
    def _find_output_video(self, code_filepath: str, scene_name: str, resolution: str) -> Optional[str]:
        """Find the generated video file"""
        # Manim output structure: media/videos/{scene_name}/{quality}/{scene_name}.mp4
        settings = self.quality_settings.get(resolution, self.quality_settings["480p"])
        
        # Common quality directory names
        quality_dirs = {
            "low_quality": "480p15",
            "production_quality": "1080p60", 
            "medium_quality": "720p30"
        }
        
        quality_dir = quality_dirs.get(settings["quality"], "480p15")
        
        # Possible video paths
        possible_paths = [
            self.output_dir / "media" / "videos" / scene_name / quality_dir / f"{scene_name}.mp4",
            self.output_dir / "media" / "videos" / quality_dir / f"{scene_name}.mp4",
            Path(code_filepath).parent / "media" / "videos" / scene_name / quality_dir / f"{scene_name}.mp4"
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path.absolute())
        
        # Search recursively in output directory
        try:
            for mp4_file in self.output_dir.rglob("*.mp4"):
                if scene_name in mp4_file.name:
                    return str(mp4_file.absolute())
        except Exception:
            pass
        
        return None
    
    def _clean_patch_content(self, patch_content: str) -> str:
        """Clean patch content to extract valid Python code"""
        lines = patch_content.split('\n')
        cleaned_lines = []
        
        in_code_block = False
        
        for line in lines:
            # Skip diff headers
            if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
                continue
            
            # Handle code blocks
            if line.strip().startswith('```python'):
                in_code_block = True
                continue
            elif line.strip() == '```':
                in_code_block = False
                continue
            
            # Keep code lines (remove diff prefixes if present)
            if in_code_block or not line.startswith(('+', '-', ' ')):
                cleaned_line = line
                if line.startswith('+'):
                    cleaned_line = line[1:]
                elif line.startswith(' '):
                    cleaned_line = line[1:]
                
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _generate_error_suggestions(self, error_type: str, stderr: str) -> List[str]:
        """Generate suggestions based on error type"""
        suggestions = []
        
        if error_type == 'syntax_error':
            suggestions.extend([
                "Check for missing parentheses, brackets, or quotes",
                "Verify proper indentation",
                "Look for missing colons after function/class definitions"
            ])
        
        elif error_type == 'import_error':
            suggestions.extend([
                "Ensure 'from manim import *' is at the top of the file",
                "Check that all required packages are installed",
                "Verify Manim version compatibility"
            ])
        
        elif error_type == 'name_error':
            name_match = re.search(r'\'(.+?)\' is not defined', stderr)
            if name_match:
                undefined_name = name_match.group(1)
                suggestions.append(f"Define variable '{undefined_name}' before using it")
            suggestions.extend([
                "Check variable and function names for typos",
                "Ensure proper import statements"
            ])
        
        elif error_type == 'unexpected_keyword':
            param_match = re.search(r'unexpected keyword argument \'(.+?)\'', stderr)
            if param_match:
                param_name = param_match.group(1)
                suggestions.append(f"Remove or replace parameter '{param_name}'")
            suggestions.extend([
                "Check Manim API documentation for correct parameter names",
                "Use parameter fixes database for common issues"
            ])
        
        elif error_type == 'attribute_error':
            suggestions.extend([
                "Check for deprecated Manim methods (e.g., ShowCreation → Create)",
                "Verify object types and available methods",
                "Ensure objects are properly initialized"
            ])
        
        elif error_type == 'manim_error':
            suggestions.extend([
                "Check scene structure and animation sequences",
                "Verify proper self.play() usage",
                "Ensure all mobjects are properly created"
            ])
        
        else:
            suggestions.append("Review the error message for specific guidance")
        
        return suggestions
    
    def get_compilation_stats(self) -> Dict[str, Any]:
        """Get compilation statistics and performance metrics"""
        return {
            'timeout': self.timeout,
            'output_dir': str(self.output_dir),
            'temp_dir': str(self.temp_dir),
            'supported_resolutions': list(self.quality_settings.keys()),
            'quality_settings': self.quality_settings
        }


def create_compiler(timeout: int = 60, output_dir: str = "output/builder") -> ManimCompiler:
    """Factory function for creating Manim compiler"""
    return ManimCompiler(timeout=timeout, output_dir=output_dir)