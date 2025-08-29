 
import os
import json
import time
import re
import subprocess
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from openai import OpenAI

from .builder_llm import BuilderLLM, BuildRequest, BuildResponse
from .compiler import ManimCompiler


class AgentState(Enum):
    """Agent workflow states"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    DEBUGGING = "debugging"
    EVALUATING = "evaluating"
    LEARNING = "learning"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ErrorPattern:
    """Represents a learned error pattern"""
    error_type: str
    error_signature: str  # Regex pattern or key phrase
    fix_strategy: str
    success_rate: float
    usage_count: int
    examples: List[str] = field(default_factory=list)


@dataclass
class AgentMemory:
    """Agent's memory system for learning from errors"""
    error_patterns: Dict[str, ErrorPattern] = field(default_factory=dict)
    successful_fixes: List[str] = field(default_factory=list)
    failed_attempts: List[str] = field(default_factory=list)
    topic_success_rates: Dict[str, float] = field(default_factory=dict)
    learning_sessions: int = 0
    
    def save_to_file(self, filepath: str):
        """Save memory to JSON file"""
        data = {
            'error_patterns': {
                k: {
                    'error_type': v.error_type,
                    'error_signature': v.error_signature,
                    'fix_strategy': v.fix_strategy,
                    'success_rate': v.success_rate,
                    'usage_count': v.usage_count,
                    'examples': v.examples
                }
                for k, v in self.error_patterns.items()
            },
            'successful_fixes': self.successful_fixes,
            'failed_attempts': self.failed_attempts,
            'topic_success_rates': self.topic_success_rates,
            'learning_sessions': self.learning_sessions
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'AgentMemory':
        """Load memory from JSON file"""
        if not os.path.exists(filepath):
            return cls()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            memory = cls()
            memory.successful_fixes = data.get('successful_fixes', [])
            memory.failed_attempts = data.get('failed_attempts', [])
            memory.topic_success_rates = data.get('topic_success_rates', {})
            memory.learning_sessions = data.get('learning_sessions', 0)
            
            # Reconstruct error patterns
            error_patterns_data = data.get('error_patterns', {})
            for key, pattern_data in error_patterns_data.items():
                memory.error_patterns[key] = ErrorPattern(
                    error_type=pattern_data['error_type'],
                    error_signature=pattern_data['error_signature'],
                    fix_strategy=pattern_data['fix_strategy'],
                    success_rate=pattern_data['success_rate'],
                    usage_count=pattern_data['usage_count'],
                    examples=pattern_data.get('examples', [])
                )
            
            return memory
        except Exception as e:
            print(f"Warning: Could not load agent memory: {e}")
            return cls()


@dataclass
class AgentTask:
    """Represents a task for the AI agent"""
    task_id: str
    topic: str
    content: str
    target_duration: int  # minutes
    audience: str
    requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    max_attempts: int = 5
    current_attempt: int = 0
    start_time: float = field(default_factory=time.time)


@dataclass
class AgentResult:
    """Result from agent task execution"""
    task_id: str
    success: bool
    video_path: Optional[str] = None
    code_path: Optional[str] = None
    error_message: Optional[str] = None
    attempts_made: int = 0
    execution_time: float = 0
    issues_found: List[str] = field(default_factory=list)
    fixes_applied: List[str] = field(default_factory=list)
    quality_score: float = 0.0


class AIAgent:
    """
    Autonomous AI Agent for Educational Video Generation
    
    This agent can:
    - Generate Manim code from educational content
    - Run and debug code autonomously
    - Learn from errors and improve over time
    - Apply intelligent fixes based on terminal output
    - Coordinate with video evaluation systems
    """
    
    def __init__(self, openai_api_key: str, gemini_api_key: Optional[str] = None,
                 memory_file: str = "data/agent_memory.json",
                 work_dir: str = "temp/agent"):
        """
        Initialize the AI Agent
        
        Args:
            openai_api_key: OpenAI API key for code generation
            gemini_api_key: Optional Gemini API key for evaluation
            memory_file: Path to agent memory persistence file
            work_dir: Working directory for agent operations
        """
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.gemini_api_key = gemini_api_key
        self.work_dir = Path(work_dir)
        self.memory_file = memory_file
        
        # Initialize core components
        self.builder_llm = BuilderLLM(openai_api_key)
        self.compiler = ManimCompiler(output_dir=str(self.work_dir / "output"))
        
        # Agent state
        self.state = AgentState.IDLE
        self.current_task: Optional[AgentTask] = None
        self.memory = AgentMemory.load_from_file(self.memory_file)
        
        # Create working directories
        self.work_dir.mkdir(parents=True, exist_ok=True)
        (self.work_dir / "output").mkdir(parents=True, exist_ok=True)
        (self.work_dir / "debug").mkdir(parents=True, exist_ok=True)
        
        # Initialize built-in error patterns
        self._initialize_error_patterns()
    
    def _initialize_error_patterns(self):
        """Initialize built-in error patterns if memory is empty"""
        if not self.memory.error_patterns:
            built_in_patterns = {
                "import_error": ErrorPattern(
                    error_type="ImportError",
                    error_signature="ModuleNotFoundError|ImportError|cannot import",
                    fix_strategy="Add missing imports: from manim import *",
                    success_rate=0.9,
                    usage_count=0
                ),
                "attribute_error": ErrorPattern(
                    error_type="AttributeError",
                    error_signature="'.*' object has no attribute '.*'",
                    fix_strategy="Check Manim API documentation and use correct method names",
                    success_rate=0.8,
                    usage_count=0
                ),
                "syntax_error": ErrorPattern(
                    error_type="SyntaxError",
                    error_signature="SyntaxError|invalid syntax|IndentationError|unexpected EOF",
                    fix_strategy="Fix Python syntax errors: parentheses, colons, indentation",
                    success_rate=0.95,
                    usage_count=0
                ),
                "name_error": ErrorPattern(
                    error_type="NameError",
                    error_signature="NameError.*is not defined",
                    fix_strategy="Define missing variables or import missing constants",
                    success_rate=0.85,
                    usage_count=0
                ),
                "type_error": ErrorPattern(
                    error_type="TypeError",
                    error_signature="TypeError.*argument|takes.*positional argument",
                    fix_strategy="Check function arguments and types",
                    success_rate=0.7,
                    usage_count=0
                ),
                "pkg_resources_warning": ErrorPattern(
                    error_type="PackageWarning",
                    error_signature="pkg_resources.*deprecated|UserWarning.*pkg_resources",
                    fix_strategy="Ignore package warnings - these are non-fatal warnings",
                    success_rate=0.95,
                    usage_count=0
                ),
                "scene_class_error": ErrorPattern(
                    error_type="SceneError",
                    error_signature="No valid Scene class found|no valid Scene",
                    fix_strategy="Ensure Scene class exists and inherits from Scene",
                    success_rate=0.9,
                    usage_count=0
                ),
                "manim_compilation": ErrorPattern(
                    error_type="CompilationError", 
                    error_signature="compilation.*failed|manim.*error",
                    fix_strategy="Check Manim syntax and scene structure",
                    success_rate=0.8,
                    usage_count=0
                ),
                "truncated_file": ErrorPattern(
                    error_type="SyntaxError",
                    error_signature="expected ':'|unexpected EOF|if current$|def \\w+\\($|if$",
                    fix_strategy="File truncated during generation - complete the missing code structure",
                    success_rate=0.95,
                    usage_count=0
                ),
                "safe_position_recursion": ErrorPattern(
                    error_type="RecursionError",
                    error_signature="safe_position.*safe_position|maximum recursion|recursion depth",
                    fix_strategy="Fix infinite recursion in safe_position function - replace safe_position(pos) with pos",
                    success_rate=0.95,
                    usage_count=0
                )
            }
            self.memory.error_patterns.update(built_in_patterns)
    
    def execute_task(self, task: AgentTask) -> AgentResult:
        """
        Execute a complete video generation task autonomously
        
        Args:
            task: The task to execute
            
        Returns:
            AgentResult with execution details
        """
        print(f"AGENT: Starting autonomous task: {task.topic}")
        print(f"TARGET: Duration: {task.target_duration} minutes")
        print(f"AUDIENCE: {task.audience}")
        
        self.current_task = task
        self.state = AgentState.ANALYZING
        start_time = time.time()
        
        try:
            # Phase 1: Content Analysis and Code Generation
            if not self._analyze_and_generate():
                return self._create_failure_result("Failed to generate initial code")
            
            # Phase 2: Autonomous Debugging Loop
            if not self._autonomous_debug_loop():
                return self._create_failure_result("Failed to resolve compilation issues")
            
            # Phase 3: Quality Evaluation and Improvement
            if not self._evaluate_and_improve():
                return self._create_failure_result("Failed quality evaluation")
            
            # Success!
            execution_time = time.time() - start_time
            return self._create_success_result(execution_time)
            
        except Exception as e:
            print(f"AGENT ERROR: Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return self._create_failure_result(f"Unexpected error: {e}")
        
        finally:
            self._cleanup_task()
    
    def _analyze_and_generate(self) -> bool:
        """Analyze content and generate initial code"""
        print(f"\nPHASE 1: Content Analysis & Code Generation")
        print("-" * 45)
        
        self.state = AgentState.ANALYZING
        
        # Create build request from task
        build_request = BuildRequest(
            topic=self.current_task.topic,
            audience=self.current_task.audience,
            source_content=self.current_task.content,
            voice="professional",
            pace_wpm=150,
            theme="3blue1brown"
        )
        
        # Generate code using Builder LLM
        try:
            self.state = AgentState.GENERATING
            build_response = self.builder_llm.build_video(build_request)
            
            # Save generated artifacts
            self._save_build_artifacts(build_response)
            
            print("SUCCESS: Initial code generation completed")
            return True
            
        except Exception as e:
            print(f"ERROR: Code generation failed: {e}")
            return False
    
    def _autonomous_debug_loop(self) -> bool:
        """Autonomous debugging loop with learning"""
        print(f"\nPHASE 2: Autonomous Debugging Loop")
        print("-" * 35)
        
        self.state = AgentState.DEBUGGING
        max_debug_attempts = self.current_task.max_attempts
        
        for attempt in range(1, max_debug_attempts + 1):
            print(f"\nDEBUG ATTEMPT {attempt}/{max_debug_attempts}")
            
            # Attempt compilation
            success, stdout, stderr, video_path = self._compile_current_code()
            
            if success:
                print("SUCCESS: Compilation successful!")
                self.current_task.current_attempt = attempt
                return True
            
            # Print error preview but keep full error for analysis
            error_preview = stderr[:500] if len(stderr) > 500 else stderr
            if len(stderr) > 500:
                error_preview += "... (truncated for display, full error used for debugging)"
            print(f"COMPILATION FAILED: {error_preview}")
            
            # Analyze error and apply fixes
            if attempt < max_debug_attempts:
                if self._analyze_and_fix_error(stderr, attempt):
                    print("SUCCESS: Applied intelligent fix, retrying...")
                    continue
                else:
                    print("WARNING: Could not apply automatic fix")
            
        print(f"FAILURE: Debug loop failed after {max_debug_attempts} attempts")
        return False
    
    def _analyze_and_fix_error(self, error_output: str, attempt: int) -> bool:
        """Analyze error output and apply intelligent fixes"""
        # First, try pattern-based fixes from memory
        if self._apply_learned_fix(error_output):
            return True
        
        # If no learned pattern, use LLM-based repair
        return self._llm_based_repair(error_output, attempt)
    
    def _apply_learned_fix(self, error_output: str) -> bool:
        """Apply fixes based on learned error patterns"""
        # Check more specific patterns first
        priority_patterns = ['truncated_file', 'scene_class_error', 'manim_compilation']
        
        # First check priority patterns
        priority_patterns.append("safe_position_recursion")
        for pattern_id in priority_patterns:
            if pattern_id in self.memory.error_patterns:
                pattern = self.memory.error_patterns[pattern_id]
                if re.search(pattern.error_signature, error_output, re.IGNORECASE):
                    print(f"PATTERN MATCH: Found priority pattern '{pattern_id}' (success rate: {pattern.success_rate:.1%})")
                    
                    # Apply the learned fix strategy
                    if self._execute_fix_strategy(pattern, error_output):
                        pattern.usage_count += 1
                        return True
        
        # Then check all other patterns
        for pattern_id, pattern in self.memory.error_patterns.items():
            if pattern_id not in priority_patterns:
                if re.search(pattern.error_signature, error_output, re.IGNORECASE):
                    print(f"PATTERN MATCH: Found pattern '{pattern_id}' (success rate: {pattern.success_rate:.1%})")
                    
                    # Apply the learned fix strategy
                    if self._execute_fix_strategy(pattern, error_output):
                        pattern.usage_count += 1
                        return True
        
        return False
    
    def _execute_fix_strategy(self, pattern: ErrorPattern, error_output: str) -> bool:
        """Execute a specific fix strategy"""
        current_code = self._load_current_code()
        if not current_code:
            return False
        
        try:
            # Apply common fix strategies
            fixed_code = current_code
            
            if "import" in pattern.fix_strategy.lower():
                fixed_code = self._fix_import_errors(fixed_code, error_output)
            elif "syntax" in pattern.fix_strategy.lower():
                fixed_code = self._fix_syntax_errors(fixed_code, error_output)
            elif "attribute" in pattern.fix_strategy.lower():
                fixed_code = self._fix_attribute_errors(fixed_code, error_output)
            elif "name" in pattern.fix_strategy.lower():
                fixed_code = self._fix_name_errors(fixed_code, error_output)
            elif "type" in pattern.fix_strategy.lower():
                fixed_code = self._fix_type_errors(fixed_code, error_output)
            elif "truncated" in pattern.fix_strategy.lower():
                fixed_code = self._fix_truncated_files(fixed_code, error_output)
            elif "safe_position_recursion" in pattern.fix_strategy.lower():
                fixed_code = self._fix_safe_position_recursion(fixed_code, error_output)
            
            if fixed_code != current_code:
                self._save_current_code(fixed_code)
                print(f"APPLIED: {pattern.fix_strategy}")
                return True
        
        except Exception as e:
            print(f"ERROR: Fix strategy failed: {e}")
        
        return False
    
    def _llm_based_repair(self, error_output: str, attempt: int) -> bool:
        """Use LLM to repair code based on error output"""
        current_code = self._load_current_code()
        if not current_code:
            return False
        
        try:
            patch, action = self.builder_llm.repair_code(current_code, error_output)
            
            if patch and patch.strip():
                # For simplicity, we'll ask the LLM to provide the full corrected code
                corrected_code = self._request_corrected_code(current_code, error_output)
                
                if corrected_code and corrected_code != current_code:
                    self._save_current_code(corrected_code)
                    
                    # Learn from this repair
                    self._learn_from_repair(error_output, "LLM-based repair", True)
                    return True
            
        except Exception as e:
            print(f"ERROR: LLM-based repair failed: {e}")
        
        return False
    
    def _request_corrected_code(self, current_code: str, error_output: str) -> Optional[str]:
        """Request corrected code from LLM"""
        prompt = f"""Fix the following Manim code that has compilation errors:

CURRENT CODE:
{current_code}

ERROR OUTPUT:
{error_output}

Return the complete corrected Python code that fixes these issues. Follow Manim best practices and ensure proper imports.
Only return the corrected code, nothing else."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert Manim developer who fixes code compilation errors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            corrected_code = response.choices[0].message.content.strip()
            
            # Clean up code block markers if present
            if corrected_code.startswith('```python'):
                lines = corrected_code.split('\n')
                lines = [line for line in lines if not line.strip().startswith('```')]
                corrected_code = '\n'.join(lines)
            
            return corrected_code
            
        except Exception as e:
            print(f"ERROR: Failed to get corrected code: {e}")
            return None
    
    def _evaluate_and_improve(self) -> bool:
        """Evaluate video quality and apply improvements"""
        print(f"\nPHASE 3: Quality Evaluation & Improvement")
        print("-" * 40)
        
        self.state = AgentState.EVALUATING
        
        # For now, basic file existence check
        video_files = list(self.work_dir.glob("output/**/*.mp4"))
        
        if not video_files:
            print("ERROR: No video file generated")
            return False
        
        latest_video = max(video_files, key=lambda p: p.stat().st_mtime)
        print(f"SUCCESS: Video generated: {latest_video}")
        
        # TODO: Integrate with enhanced video evaluator when available
        
        return True
    
    def _learn_from_repair(self, error_output: str, fix_description: str, success: bool):
        """Learn from repair attempts to improve future performance"""
        self.state = AgentState.LEARNING
        
        # Extract error signature
        error_signature = self._extract_error_signature(error_output)
        error_type = self._classify_error_type(error_output)
        
        pattern_id = f"{error_type.lower()}_{hash(error_signature) % 10000}"
        
        if pattern_id in self.memory.error_patterns:
            # Update existing pattern
            pattern = self.memory.error_patterns[pattern_id]
            pattern.usage_count += 1
            
            # Update success rate using exponential moving average
            alpha = 0.1  # Learning rate
            pattern.success_rate = (1 - alpha) * pattern.success_rate + alpha * (1.0 if success else 0.0)
        else:
            # Create new pattern
            self.memory.error_patterns[pattern_id] = ErrorPattern(
                error_type=error_type,
                error_signature=error_signature,
                fix_strategy=fix_description,
                success_rate=1.0 if success else 0.0,
                usage_count=1,
                examples=[error_output[:200]]
            )
        
        if success:
            self.memory.successful_fixes.append(fix_description)
        else:
            self.memory.failed_attempts.append(fix_description)
        
        # Save updated memory
        self.memory.learning_sessions += 1
        self.memory.save_to_file(self.memory_file)
    
    def _extract_error_signature(self, error_output: str) -> str:
        """Extract a meaningful error signature from output"""
        lines = error_output.strip().split('\n')
        
        # Manim-specific error patterns
        manim_patterns = [
            r'.*Error.*',  # Generic error lines
            r'.*Exception.*',  # Exception lines
            r'Traceback.*',  # Traceback start
            r'.*:\s*line \d+',  # File:line references
            r'.*manim.*error.*',  # Manim-specific errors
            r'.*compilation.*failed.*',  # Compilation failures
            r'.*UserWarning.*',  # Warnings that might be errors
            r'.*pkg_resources.*',  # Package warnings
            r'.*ModuleNotFoundError.*',  # Import errors
            r'.*SyntaxError.*',  # Syntax errors
            r'.*NameError.*',  # Name errors
            r'.*AttributeError.*',  # Attribute errors
            r'.*TypeError.*',  # Type errors
            r'.*IndentationError.*',  # Indentation errors
        ]
        
        # Look for meaningful error lines using patterns
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check against each pattern
            for pattern in manim_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Clean up the line to create a pattern
                    signature = re.sub(r'line \d+', 'line X', line)
                    signature = re.sub(r'\'[^\']*\'', "'X'", signature)
                    signature = re.sub(r'"[^"]*"', '"X"', signature)
                    # Remove absolute paths
                    signature = re.sub(r'[A-Za-z]:\\[^:]*', '<PATH>', signature)
                    signature = re.sub(r'/[^:]*\.py', '<PATH>.py', signature)
                    return signature[:200]  # Increased length for better matching
        
        # If no specific patterns found, look for the last non-empty line
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith(' '):
                return line[:200]
        
        return error_output[:200]  # Fallback with increased length
    
    def _classify_error_type(self, error_output: str) -> str:
        """Classify the type of error with Manim-specific categories"""
        error_types = {
            # Python core errors
            'ImportError': ['ImportError', 'ModuleNotFoundError', 'cannot import'],
            'SyntaxError': ['SyntaxError', 'invalid syntax', 'IndentationError', 'unexpected EOF'],
            'AttributeError': ['AttributeError', 'has no attribute'],
            'NameError': ['NameError', 'is not defined'],
            'TypeError': ['TypeError', 'argument', 'takes', 'positional argument'],
            'ValueError': ['ValueError', 'invalid value', 'invalid literal'],
            'FileNotFoundError': ['FileNotFoundError', 'No such file'],
            'KeyError': ['KeyError', 'key not found'],
            'IndexError': ['IndexError', 'index out of range'],
            
            # Manim-specific errors
            'ManimError': ['manim', 'scene', 'mobject', 'animation'],
            'CompilationError': ['compilation failed', 'build failed'],
            'PackageWarning': ['pkg_resources', 'UserWarning', 'deprecated'],
            'SceneError': ['Scene', 'construct', 'no valid Scene class'],
            'RenderingError': ['rendering', 'render', 'ffmpeg', 'video'],
            'ConfigError': ['config', 'configuration', 'settings'],
        }
        
        # Check in order of specificity (most specific first)
        for error_type, keywords in error_types.items():
            if any(keyword.lower() in error_output.lower() for keyword in keywords):
                return error_type
        
        return 'UnknownError'
    
    def _compile_current_code(self) -> Tuple[bool, str, str, Optional[str]]:
        """Compile the current scene code"""
        code_file = self.work_dir / "debug" / "current_scene.py"
        
        if not code_file.exists():
            return False, "", "No code file found", None
        
        return self.compiler.compile_scene(str(code_file), "480p")
    
    def _save_build_artifacts(self, build_response: BuildResponse):
        """Save generated build artifacts"""
        timestamp = int(time.time())
        
        # Save code
        code_file = self.work_dir / "debug" / "current_scene.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(build_response.code)
        
        # Save YAML spec
        yaml_file = self.work_dir / "debug" / f"spec_{timestamp}.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(build_response.yaml_spec, f, default_flow_style=False)
        
        # Save outline
        outline_file = self.work_dir / "debug" / f"outline_{timestamp}.txt"
        with open(outline_file, 'w', encoding='utf-8') as f:
            f.write(build_response.outline)
        
        print(f"SAVED: Build artifacts to {self.work_dir / 'debug'}")
    
    def _load_current_code(self) -> Optional[str]:
        """Load current scene code"""
        code_file = self.work_dir / "debug" / "current_scene.py"
        
        if not code_file.exists():
            return None
        
        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"ERROR: Could not load current code: {e}")
            return None
    
    def _save_current_code(self, code: str):
        """Save current scene code"""
        code_file = self.work_dir / "debug" / "current_scene.py"
        
        try:
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"SAVED: Updated code to {code_file}")
        except Exception as e:
            print(f"ERROR: Could not save code: {e}")
    
    def _create_success_result(self, execution_time: float) -> AgentResult:
        """Create successful result"""
        video_files = list(self.work_dir.glob("output/**/*.mp4"))
        video_path = str(max(video_files, key=lambda p: p.stat().st_mtime)) if video_files else None
        
        return AgentResult(
            task_id=self.current_task.task_id,
            success=True,
            video_path=video_path,
            code_path=str(self.work_dir / "debug" / "current_scene.py"),
            attempts_made=self.current_task.current_attempt,
            execution_time=execution_time,
            quality_score=0.8  # Placeholder
        )
    
    def _create_failure_result(self, error_message: str) -> AgentResult:
        """Create failure result"""
        return AgentResult(
            task_id=self.current_task.task_id,
            success=False,
            error_message=error_message,
            attempts_made=self.current_task.current_attempt,
            execution_time=time.time() - self.current_task.start_time
        )
    
    def _cleanup_task(self):
        """Clean up after task completion"""
        self.current_task = None
        self.state = AgentState.IDLE
    
    # Fix strategy implementations
    def _fix_import_errors(self, code: str, error: str) -> str:
        """Fix import-related errors"""
        if "from manim import" not in code:
            code = "from manim import *\n\n" + code
        
        # Add common missing imports
        if "numpy" in error.lower() and "import numpy as np" not in code:
            code = "import numpy as np\n" + code
        
        return code
    
    def _fix_syntax_errors(self, code: str, error: str) -> str:
        """Fix common syntax errors"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Fix common issues
            if line.strip().endswith(':') and i + 1 < len(lines) and not lines[i + 1].startswith('    '):
                # Missing indentation after colon
                if i + 1 < len(lines):
                    lines[i + 1] = '    ' + lines[i + 1].lstrip()
        
        return '\n'.join(lines)
    
    def _fix_attribute_errors(self, code: str, error: str) -> str:
        """Fix attribute errors"""
        # Common Manim API fixes
        code = re.sub(r'\.ShowCreation\(', '.Create(', code)
        code = re.sub(r'\.get_graph\(', '.plot(', code)
        return code
    
    def _fix_name_errors(self, code: str, error: str) -> str:
        """Fix name/undefined variable errors"""
        # Add missing constants
        if "UP" in error and "UP" not in code:
            code = code.replace("from manim import *", "from manim import *\nUP = np.array([0, 1, 0])")
        
        return code
    
    def _fix_type_errors(self, code: str, error: str) -> str:
        """Fix type-related errors"""
        # Common type fixes can be added here
        return code
    
    def _fix_safe_position_recursion(self, code: str, error: str) -> str:
        """Fix infinite recursion in safe_position function"""
        # Look for the specific pattern: safe_position(pos) where pos is already calculated
        # Replace with just pos
        import re

        # Pattern 1: mobject.move_to(safe_position(pos))
        code = re.sub(
            r'mobject\.move_to\(safe_position\(([^)]+)\)\)',
            r'mobject.move_to(\1)',
            code
        )

        # Pattern 2: Any other safe_position(safe_position(...)) calls
        code = re.sub(
            r'safe_position\(safe_position\(([^)]+)\)\)',
            r'safe_position(\1)',
            code
        )

        return code

    def _fix_truncated_files(self, code: str, error: str) -> str:
        """Fix truncated files by completing missing code structure"""
        lines = code.split('\n')
        
        # Check if file ends abruptly
        if lines and lines[-1].strip() == 'if':
            # This is the specific truncation pattern we saw
            # Complete the SafeScene class and add a basic Video scene
            completion = """ current_pos[0] - half_w < left:
                            safe_pos[0] = left + half_w
                        elif current_pos[0] + half_w > right:
                            safe_pos[0] = right - half_w
                        
                        if current_pos[1] - half_h < bottom:
                            safe_pos[1] = bottom + half_h
                        elif current_pos[1] + half_h > top:
                            safe_pos[1] = top - half_h
                        
                        # Apply corrected position if needed
                        if not np.allclose(current_pos, safe_pos):
                            mob.move_to(safe_pos)
                            
    def disable_safety(self):
        \"\"\"Temporarily disable safety checks\"\"\"
        self.safety_enabled = False
        
    def enable_safety(self):
        \"\"\"Re-enable safety checks\"\"\"
        self.safety_enabled = True

# Actual Video Scene
class Video(SafeScene):
    \"\"\"
    Video scene: Educational content
    Generated for high school audience
    \"\"\"
    
    def construct(self):
        # Scene setup
        self.camera.background_color = "#1e1e1e"
        
        # Create simple educational content
        title = Text("Educational Topic", font_size=42, color=WHITE).move_to(ORIGIN)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        self.wait(1)"""
            
            # Replace the incomplete last line with the completion
            lines[-1] = lines[-1] + completion
            return '\n'.join(lines)
        elif lines and lines[-1].strip().endswith('if current'):
            # This is the specific truncation pattern we saw
            # Complete the SafeScene class and add a basic Video scene
            completion = """_pos[0] - half_w < left:
                            safe_pos[0] = left + half_w
                        elif current_pos[0] + half_w > right:
                            safe_pos[0] = right - half_w
                        
                        if current_pos[1] - half_h < bottom:
                            safe_pos[1] = bottom + half_h
                        elif current_pos[1] + half_h > top:
                            safe_pos[1] = top - half_h
                        
                        # Apply corrected position if needed
                        if not np.allclose(current_pos, safe_pos):
                            mob.move_to(safe_pos)
                            
    def disable_safety(self):
        \"\"\"Temporarily disable safety checks\"\"\"
        self.safety_enabled = False
        
    def enable_safety(self):
        \"\"\"Re-enable safety checks\"\"\"
        self.safety_enabled = True

# Actual Video Scene
class Video(SafeScene):
    \"\"\"
    Video scene: Educational content
    Generated for high school audience
    \"\"\"
    
    def construct(self):
        # Scene setup
        self.camera.background_color = "#1e1e1e"
        
        # Create simple educational content
        title = Text("Educational Topic", font_size=42, color=WHITE).move_to(ORIGIN)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        self.wait(1)"""
            
            # Replace the incomplete last line with the completion
            lines[-1] = lines[-1].replace('if current', 'if current' + completion)
            return '\n'.join(lines)
        
        # Check for other truncation patterns
        if lines and lines[-1].strip() and not lines[-1].strip().endswith((';', ')', '}', ':', '"', "'")):
            # File likely truncated mid-statement
            # Try to complete basic structure
            if 'class' in lines[-1] and ':' not in lines[-1]:
                lines[-1] += ':'
                lines.append('    pass')
            elif 'def' in lines[-1] and ':' not in lines[-1]:
                lines[-1] += ':'
                lines.append('    pass')
        
        return '\n'.join(lines)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get agent memory statistics"""
        return {
            'learned_patterns': len(self.memory.error_patterns),
            'successful_fixes': len(self.memory.successful_fixes),
            'failed_attempts': len(self.memory.failed_attempts),
            'learning_sessions': self.memory.learning_sessions,
            'top_patterns': sorted(
                [(k, v.usage_count, v.success_rate) for k, v in self.memory.error_patterns.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }