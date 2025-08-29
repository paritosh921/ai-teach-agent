"""
Builder LLM - Master System for Deterministic Manim Video Generation

This module implements the MANIM-AUTOPILOT system that creates clean, overlap-free
educational animations following a strict OUTLINE → YAML → CODE → ACTION workflow.
"""

import os
import re
import yaml
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from openai import OpenAI

# Import POML validation
try:
    from .schemas.poml_schema import POMLValidator, POMLValidationResult
    POML_AVAILABLE = True
except ImportError:
    try:
        from schemas.poml_schema import POMLValidator, POMLValidationResult
        POML_AVAILABLE = True
    except ImportError:
        POML_AVAILABLE = False
        print("Warning: POML validation not available")

# Import layout validation utilities
try:
    from .autolayout import (
        validate_layout_pre_render,
        generate_layout_report,
        inject_safety_into_existing_code,
        get_embedded_safety_code
    )
    AUTOLAYOUT_AVAILABLE = True
except ImportError:
    try:
        # Try absolute import as fallback
        from autolayout import (
            validate_layout_pre_render,
            generate_layout_report,
            inject_safety_into_existing_code,
            get_embedded_safety_code
        )
        AUTOLAYOUT_AVAILABLE = True
    except ImportError:
        # Fallback if autolayout not available
        AUTOLAYOUT_AVAILABLE = False
        print("Warning: Autolayout utilities not available - layout validation disabled")


@dataclass
class BuildRequest:
    """Structure for a video build request"""
    topic: str
    audience: str = "general"
    voice: str = "professional"
    pace_wpm: int = 150
    theme: str = "3blue1brown"
    poml_content: Optional[str] = None  # Optional POML input
    source_content: Optional[str] = None  # Original book content


@dataclass
class BuildResponse:
    """Structure for Builder LLM response"""
    outline: str
    yaml_spec: Dict[str, Any]
    code: str
    action: str
    layout_validation: Optional[Dict[str, Any]] = None  # Layout validation results
    
    
class BuilderLLM:
    """
    MANIM-AUTOPILOT: Deterministic code-writing assistant for educational animations
    
    Implements the complete workflow:
    1) Topic expansion to structured outline
    2) YAML video specification generation
    3) Manim CE Python code generation with layout guardrails
    4) Compilation and error repair workflow
    """
    
    # Master System Prompt - the core deterministic instructions
    SYSTEM_PROMPT = """You are MANIM-AUTOPILOT, a deterministic code-writing assistant that turns a chapter topic into a clean, overlap-free Manim video.

## Goals
1) Expand a topic into an index of sections/subsections with learning objectives.
2) Emit a strict YAML video spec (scenes, timings, narration, layout, assets, checks).
3) Generate Manim CE Python code from the YAML using layout guardrails (no overlaps, no out-of-frame).
4) Ask the orchestrator to compile 480p first. If compile errors are returned, patch the code and request re-compile until success (bounded).
5) After a 480p success, wait for a layout report from an external visual evaluator (Gemini). If issues exist, patch code and re-request compile+evaluate. When "perfect", request 1080p compile.

## Non-negotiable layout rules
- Safe margins: ≥ 6% on all sides. Never place anchors outside safe frame.
- No overlaps: before/after each entrance/exit, ensure visible mobjects do not intersect. If they do: shrink ≤ 95% iteratively, reflow to next row/column, or fade/move prior items.
- Max usable width/height per element: ≤ 92% of safe frame.
- Text legibility at 480p: min text height ≈ 24 px equivalent (scale accordingly).
- Explicit z_index; fade out or move things away before reusing a region.
- Prefer fixed camera; if pan/zoom, recompute safe frame.
- Determinism: do not introduce randomness; if needed, set a fixed seed.

## Critical Manim API constraints
- Text objects: ONLY use font_size parameter, NEVER use weight, style, size, or align
- MathTex objects: ONLY use font_size parameter, NEVER use weight, style, or size  
- safe_position() function: NEVER call this function - use standard Manim positioning like .to_edge(), .next_to(), .shift()
- Position objects directly: text.to_edge(UP), text.shift(DOWN * 2), etc.

## Output blocks (always in this order)
1) OUTLINE  — hierarchical bullet list.
2) YAML     — video spec matching the SCHEMA below.
3) CODE     — complete `scene.py` Manim CE code, ready to run.
4) ACTION   — one line: `ACTION: COMPILE_480P` (or later `COMPILE_1080P`).
   - On error logs or visual feedback, emit only a PATCH block then a new ACTION.

## YAML SCHEMA (author strictly to this)
topic: str  # MUST match the educational topic from POML content, not generic topics
audience: str
style: { voice: str, pace_wpm: int, theme: str }
global:
  safe_margin_pct: number  # default 0.06
  default_font_size: int   # default 42
  max_width_pct: number    # default 0.92
  grid: [template:str, { ... }]  # eg "single","two_column","three_column"
scenes: 
  - id: str
    goal: str
    time_budget_s: int
    narration: str
    layout:
      template: str
      elements:
        - key: str
          type: Text|MathTex|AxesPlot|Table|Image
          # content fields (text|tex|path|fn etc.)
          column: left|right|center  # Use lowercase values only
          style: { font_size?: int, weight?: str }
          wrap?: { max_chars?: int }
          scale_fit?: { max_width_pct?: number, max_height_pct?: number }
          z_index?: int
          enter: { anim: str, at: number }  # Valid anim: Write, FadeIn, FadeOut, Create, GrowFromCenter, ShrinkToCenter, Transform
          exit?:  { anim: str, at: number }  # Valid anim: Write, FadeIn, FadeOut, Create, GrowFromCenter, ShrinkToCenter, Transform
    checks:
      require_no_overlap: bool
      require_in_frame:  bool

## Code expectations
- Provide a single file `scene.py` with imports and a `class Video(Scene):`.
- ALWAYS start with: `from manim import *` to import all necessary constants (CENTER, LEFT, RIGHT, UP, DOWN, etc.)
- Include helper utilities inline (safe_frame, scale_to_fit_pct, overlap checks, place_in_grid, wrap_text).
- Perform collision checks at each enter/exit boundary; auto-shrink/reflow if violated.
- Use VGroup(...).arrange() with nonzero `buff` (≥ 0.2).
- Explicit z_index. Ensure exits occur before new entrances in same region.
- Use proper Manim constants: `ORIGIN` (not `CENTER`), `LEFT`, `RIGHT`, `UP`, `DOWN` for positioning and alignment.
- Use correct Manim methods: `.to_edge(UP/DOWN/LEFT/RIGHT)`, `.next_to()`, `.move_to()`, `.shift()` for positioning.
- Do NOT use `.align_on_border()` - this method doesn't exist in Manim.
- In YAML, use lowercase column values: `left`, `right`, `center` (not `LEFT`, `RIGHT`, `CENTER`).
- Do NOT use `CENTER` constant in code - use `ORIGIN` instead for center positioning.
- Use valid animation types: Write, FadeIn, FadeOut, Create, GrowFromCenter, ShrinkToCenter, Transform.

## Error/feedback handling
- If the orchestrator sends you a `TRACEBACK` block, reply with:
  PATCH — a unified diff against `scene.py` (only the diff)
  ACTION: COMPILE_480P
- If the orchestrator sends you a `VISUAL_REPORT` (from Gemini), reply with:
  PATCH — minimal code changes to fix reported issues
  ACTION: COMPILE_480P
- When evaluation status is "perfect", respond with:
  ACTION: COMPILE_1080P

Follow formats exactly. Never add commentary outside the defined blocks."""

    # User prompt template for starting builds
    USER_PROMPT_TEMPLATE = """Build a video for the topic: "{topic}"
Audience: "{audience}"
Style: {{ voice: "{voice}", pace_wpm: {pace_wpm}, theme: "{theme}" }}

{source_content_section}

Constraints: Use the schema and rules in your system prompt. Begin with OUTLINE → YAML → CODE → ACTION."""

    POML_PROMPT_TEMPLATE = """Build a video using the provided POML (Prompt Orchestration Markup Language) specification:

{poml_content}

Additional context from source material:
{source_content}

Style preferences: {{ voice: "{voice}", pace_wpm: {pace_wpm}, theme: "{theme}" }}

Instructions:
1. Parse the POML content to understand the educational role, task, and requirements
2. Extract scene requirements, visual guidelines, and mathematical content from the POML
3. Use the learning objectives and content structure provided in the POML
4. Follow the output format specified in the POML while adhering to your system prompt constraints

CRITICAL: Ensure your YAML includes ALL required fields:
- Top level: topic, audience, style (voice/pace_wpm/theme), global, scenes
- Each scene: id, goal, time_budget_s, narration, layout, checks
- Each element: key, type, column, and appropriate content field:
  * Text/MathTex elements: text/content/tex field
  * AxesPlot elements: fn field (function to plot)
  * Image elements: path field

IMPORTANT: The topic field in your YAML MUST match the educational topic from the POML content. Do not use generic topics like "Understanding Limits" - use the specific topic from the POML task and content sections.

Begin with OUTLINE → YAML → CODE → ACTION, incorporating all POML specifications."""

    # Repair mode prompt template (shortened for token efficiency)
    REPAIR_PROMPT_TEMPLATE = """REPAIR: Fix compilation errors in scene.py. Return ONLY:
PATCH
<unified diff>
ACTION: COMPILE_480P

SCENE.PY:
{scene_py}

ERROR:
{traceback}"""

    # Visual feedback repair prompt template (shortened for token efficiency)
    VISUAL_FIX_PROMPT_TEMPLATE = """VISUAL-FIX: Patch scene.py to fix visual issues. Return ONLY:
PATCH
<unified diff>
ACTION: COMPILE_480P

SCENE.PY:
{scene_py}

VISUAL_REPORT:
{gemini_yaml}"""

    # Promotion to 1080p prompt
    PROMOTION_PROMPT = """The visual report is PERFECT. Output only:
ACTION: COMPILE_1080P"""

    def __init__(self, api_key: str, model: str = None):
        """Initialize the Builder LLM with OpenAI client"""
        self.client = OpenAI(api_key=api_key)
        # Model selection with fallback support
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        # Model capability tracking
        self.supports_temperature = self._check_temperature_support(self.model)
        self.fallback_models = ['gpt-4o', 'gpt-4-turbo', 'gpt-4o-mini', 'gpt-3.5-turbo']
        
    def _check_temperature_support(self, model: str) -> bool:
        """Check if model supports temperature parameter"""
        # GPT-5 models don't support custom temperature
        gpt5_models = ['gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'o3-mini', 'o1', 'o1-mini']
        return not any(gpt5_model in model.lower() for gpt5_model in gpt5_models)
        
    def build_video(self, request: BuildRequest) -> BuildResponse:
        """
        Main entry point: Generate initial OUTLINE → YAML → CODE → ACTION
        
        Args:
            request: BuildRequest with topic, audience, style preferences, and optional POML
            
        Returns:
            BuildResponse with outline, yaml_spec, code, and action
        """
        # Choose prompt template based on whether POML content is provided
        if request.poml_content and POML_AVAILABLE:
            # Validate POML if available
            validator = POMLValidator()
            validation_result = validator.validate_poml_content(request.poml_content)
            
            if not validation_result.is_valid:
                print(f"Warning: POML validation failed with {len(validation_result.issues)} issues")
                for issue in validation_result.issues:
                    if issue.severity.value == 'error':
                        print(f"  ERROR: {issue.message}")
            
            # Use POML template
            user_prompt = self.POML_PROMPT_TEMPLATE.format(
                poml_content=request.poml_content,
                source_content=request.source_content or "No additional source content provided",
                voice=request.voice,
                pace_wpm=request.pace_wpm,
                theme=request.theme
            )
        else:
            # Use standard template
            # Format source content section
            if request.source_content and request.source_content.strip():
                source_content_section = f"""EDUCATIONAL CONTENT TO COVER:
{request.source_content}

INSTRUCTIONS: Create a comprehensive educational animation that covers ALL the concepts, examples, formulas, and explanations provided in the educational content above. Structure the video to build understanding progressively through the material."""
            else:
                source_content_section = "Create a comprehensive educational animation that introduces and explains the topic clearly."
            
            user_prompt = self.USER_PROMPT_TEMPLATE.format(
                topic=request.topic,
                audience=request.audience,
                voice=request.voice,
                pace_wpm=request.pace_wpm,
                theme=request.theme,
                source_content_section=source_content_section
            )
        
        response = self._call_llm(user_prompt)
        build_response = self._parse_build_response(response)
        
        # Perform layout validation on the YAML specification
        if AUTOLAYOUT_AVAILABLE and build_response.yaml_spec:
            layout_validation = self._validate_yaml_layout(build_response.yaml_spec)
            build_response.layout_validation = layout_validation
            
            # If critical layout issues are found, attempt immediate fix
            # Temporarily disabled due to YAML parsing issues
            # if layout_validation.get('status') == 'failed':
            #     print("Critical layout issues detected - attempting automatic fixes...")
            #     fixed_response = self._auto_fix_layout_issues(build_response, layout_validation)
            #     if fixed_response:
            #         build_response = fixed_response
        
        return build_response
    
    def repair_code(self, scene_py: str, traceback: str) -> Tuple[str, str]:
        """
        Repair mode: Fix compilation errors and return PATCH + ACTION
        
        Args:
            scene_py: Current scene.py content
            traceback: Compilation error traceback
            
        Returns:
            Tuple of (patch, action)
        """
        # Truncate long content to prevent context length issues
        scene_py = self._truncate_content(scene_py, max_chars=3000)
        traceback = self._truncate_content(traceback, max_chars=1000)
        
        prompt = self.REPAIR_PROMPT_TEMPLATE.format(
            scene_py=scene_py,
            traceback=traceback
        )
        
        # Use fewer tokens for repair calls to avoid context length issues
        response = self._call_llm(prompt, max_tokens=2000)
        return self._parse_repair_response(response)
    
    def fix_visual_issues(self, scene_py: str, gemini_yaml: str) -> Tuple[str, str]:
        """
        Visual-fix mode: Address issues from Gemini evaluation
        
        Args:
            scene_py: Current scene.py content
            gemini_yaml: YAML report from Gemini visual evaluator
            
        Returns:
            Tuple of (patch, action)
        """
        # Truncate long content to prevent context length issues
        scene_py = self._truncate_content(scene_py, max_chars=3000)
        gemini_yaml = self._truncate_content(gemini_yaml, max_chars=1000)
        
        prompt = self.VISUAL_FIX_PROMPT_TEMPLATE.format(
            scene_py=scene_py,
            gemini_yaml=gemini_yaml
        )
        
        # Use fewer tokens for visual fix calls to avoid context length issues
        response = self._call_llm(prompt, max_tokens=2000)
        return self._parse_repair_response(response)
    
    def promote_to_1080p(self) -> str:
        """
        Promotion mode: Request 1080p compilation after perfect evaluation
        
        Returns:
            Action string
        """
        response = self._call_llm(self.PROMOTION_PROMPT)
        # Extract ACTION line
        for line in response.strip().split('\n'):
            if line.strip().startswith('ACTION:'):
                return line.strip()
        return "ACTION: COMPILE_1080P"
    
    def _call_llm(self, user_prompt: str, max_tokens: int = 4000) -> str:
        """Make API call to OpenAI with system and user prompts"""
        return self._call_llm_with_fallback(user_prompt, max_tokens, [self.model] + self.fallback_models)
    
    def _call_llm_with_fallback(self, user_prompt: str, max_tokens: int, models: List[str]) -> str:
        """Try API call with model fallbacks for compatibility"""
        last_error = None
        
        for model in models:
            try:
                # Build parameters based on model capabilities
                params = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_completion_tokens": max_tokens
                }
                
                # Add temperature only for models that support it
                if self._check_temperature_support(model):
                    params["temperature"] = 0.1
                
                response = self.client.chat.completions.create(**params)
                
                # Update current model if different from original
                if model != self.model:
                    print(f"INFO: Using fallback model {model} due to compatibility issues with {self.model}")
                    self.model = model
                    self.supports_temperature = self._check_temperature_support(model)
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Check for parameter-related errors
                if any(param in error_msg for param in ['temperature', 'unsupported', 'parameter']):
                    print(f"INFO: Model {model} has parameter compatibility issues, trying next model...")
                    continue
                else:
                    # Non-parameter errors - might be worth retrying with other models
                    print(f"WARNING: API call failed with {model}: {e}")
                    continue
        
        # All models failed
        raise Exception(f"Builder LLM API call failed with all models. Last error: {last_error}")
    
    def _truncate_content(self, content: str, max_chars: int = 5000) -> str:
        """Truncate content to prevent context length issues"""
        if len(content) <= max_chars:
            return content
        
        # Truncate and add indicator
        truncated = content[:max_chars]
        
        # Ensure we don't break in the middle of a critical code structure
        # Try to truncate at a line boundary to avoid breaking mid-line
        last_newline = truncated.rfind('\n')
        if last_newline > max_chars * 0.8:  # Only if we're not losing too much
            truncated = truncated[:last_newline]
        
        # Check for incomplete class or function definitions
        lines = truncated.split('\n')
        while lines:
            last_line = lines[-1].strip()
            if (last_line.startswith('class ') or last_line.startswith('def ') or 
                last_line.endswith('if ') or last_line.endswith('if current')):
                # Remove incomplete line to prevent syntax errors
                lines = lines[:-1]
                continue
            break
        
        truncated = '\n'.join(lines)
        truncated += f"\n\n... [TRUNCATED - Original length: {len(content)} chars]"
        return truncated
    
    def _parse_build_response(self, response: str) -> BuildResponse:
        """
        Parse the Builder LLM response into structured components
        
        Expected format:
        OUTLINE
        <outline content>
        
        YAML
        <yaml content>
        
        CODE
        <python code>
        
        ACTION: <action>
        """
        sections = {}
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # Detect section headers (support both plain and markdown formats)
            if line_stripped in ['OUTLINE', 'YAML', 'CODE'] or \
               line_stripped in ['## OUTLINE', '## YAML', '## CODE'] or \
               line_stripped in ['# OUTLINE', '# YAML', '# CODE']:
                # Extract section name (remove markdown headers)
                section_name = line_stripped.replace('#', '').strip()
                current_section = section_name
                sections[current_section] = []
            elif line_stripped.startswith('ACTION:') or line_stripped.startswith('## ACTION'):
                sections['ACTION'] = line_stripped
            elif current_section and line_stripped:
                sections[current_section].append(line)
        
        # Extract components
        outline = '\n'.join(sections.get('OUTLINE', []))
        yaml_content = '\n'.join(sections.get('YAML', []))
        code = '\n'.join(sections.get('CODE', []))
        
        # Clean code blocks (remove ```yaml, ```python markers)
        if yaml_content.startswith('```yaml'):
            yaml_lines = yaml_content.split('\n')
            yaml_lines = [line for line in yaml_lines if not line.strip().startswith('```')]
            yaml_content = '\n'.join(yaml_lines)
        
        if code.startswith('```python'):
            code_lines = code.split('\n')
            code_lines = [line for line in code_lines if not line.strip().startswith('```')]
            code = '\n'.join(code_lines)
        action = sections.get('ACTION', 'ACTION: COMPILE_480P')
        
        # Inject runtime safety guards into generated code
        if AUTOLAYOUT_AVAILABLE and code:
            try:
                code = inject_safety_into_existing_code(code)
                print("SUCCESS: Injected runtime safety guards into generated code")
            except Exception as e:
                print(f"WARNING:  Failed to inject safety guards: {e}")
                # Continue with original code if injection fails
        
        # Enhanced YAML parsing with multiple strategies
        yaml_spec = None
        if yaml_content:
            yaml_spec = self._parse_yaml_with_fallbacks(yaml_content)
        else:
            print("WARNING: No YAML content found, creating minimal structure")
            yaml_spec = self._create_minimal_yaml_structure()
        
        return BuildResponse(
            outline=outline or "# Basic Outline\n1. Introduction\n2. Main Content\n3. Conclusion",
            yaml_spec=yaml_spec,
            code=code.strip() if code.strip() else self._create_fallback_code(),
            action=action
        )
    
    def _parse_repair_response(self, response: str) -> Tuple[str, str]:
        """
        Parse repair response to extract PATCH and ACTION
        
        Expected format:
        PATCH
        <unified diff content>
        
        ACTION: <action>
        """
        lines = response.split('\n')
        patch_lines = []
        action = "ACTION: COMPILE_480P"
        
        in_patch = False
        for line in lines:
            if line.strip() == 'PATCH':
                in_patch = True
                continue
            elif line.strip().startswith('ACTION:'):
                action = line.strip()
                break
            elif in_patch:
                patch_lines.append(line)
        
        patch = '\n'.join(patch_lines)
        return patch, action
    
    def _validate_yaml_layout(self, yaml_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate YAML specification for layout safety issues
        
        Args:
            yaml_spec: The YAML specification to validate
            
        Returns:
            Dictionary with validation results
        """
        if not AUTOLAYOUT_AVAILABLE:
            return {'status': 'skipped', 'reason': 'autolayout_unavailable'}
        
        validation_issues = []
        recommendations = []
        
        # Extract global layout settings
        global_settings = yaml_spec.get('global', {})
        safe_margin = global_settings.get('safe_margin_pct', 0.06)
        max_width_pct = global_settings.get('max_width_pct', 0.92)
        
        # Validate scenes
        scenes = yaml_spec.get('scenes', [])
        total_critical_issues = 0
        
        for scene in scenes:
            scene_id = scene.get('id', 'unknown')
            elements = scene.get('layout', {}).get('elements', [])
            
            # Check element count per scene
            if len(elements) > 4:
                validation_issues.append({
                    'severity': 'high',
                    'scene': scene_id,
                    'issue': f'Scene has {len(elements)} elements - may cause overcrowding',
                    'suggestion': 'Consider splitting into multiple scenes or using pagination'
                })
            
            # Check for potential overlaps based on positioning
            element_regions = {}
            for element in elements:
                column = element.get('column', 'center')
                if column in element_regions:
                    element_regions[column].append(element.get('key', 'unknown'))
                else:
                    element_regions[column] = [element.get('key', 'unknown')]
            
            # Flag regions with multiple simultaneous elements
            for region, element_keys in element_regions.items():
                if len(element_keys) > 1:
                    # Check timing to see if they appear simultaneously
                    simultaneous_elements = []
                    for element in elements:
                        if element.get('column') == region:
                            enter_time = element.get('enter', {}).get('at', 0)
                            exit_time = element.get('exit', {}).get('at', float('inf'))
                            simultaneous_elements.append((element.get('key'), enter_time, exit_time))
                    
                    # Simple overlap check - if any elements have overlapping time ranges
                    for i in range(len(simultaneous_elements)):
                        for j in range(i + 1, len(simultaneous_elements)):
                            key1, enter1, exit1 = simultaneous_elements[i]
                            key2, enter2, exit2 = simultaneous_elements[j]
                            
                            # Check for time overlap
                            if not (exit1 <= enter2 or exit2 <= enter1):
                                validation_issues.append({
                                    'severity': 'critical',
                                    'scene': scene_id,
                                    'issue': f'Elements {key1} and {key2} overlap in region {region}',
                                    'suggestion': f'Stagger timing or use different regions'
                                })
                                total_critical_issues += 1
            
            # Check for font size issues
            for element in elements:
                style = element.get('style', {})
                font_size = style.get('font_size', global_settings.get('default_font_size', 42))
                
                if font_size < 24:
                    validation_issues.append({
                        'severity': 'high',
                        'scene': scene_id,
                        'element': element.get('key'),
                        'issue': f'Font size {font_size} may be illegible at 480p',
                        'suggestion': 'Increase font size to at least 24 or reduce text content'
                    })
        
        # Generate overall recommendations
        if total_critical_issues > 0:
            recommendations.append(f"{total_critical_issues} critical overlap issues must be resolved")
        
        if len(validation_issues) > 5:
            recommendations.append("Consider simplifying layouts or splitting content into more scenes")
        
        # Determine overall status
        critical_count = sum(1 for issue in validation_issues if issue['severity'] == 'critical')
        high_count = sum(1 for issue in validation_issues if issue['severity'] == 'high')
        
        if critical_count > 0:
            status = 'failed'
        elif high_count > 2:
            status = 'warnings'  
        else:
            status = 'passed'
        
        return {
            'status': status,
            'issues': validation_issues,
            'recommendations': recommendations,
            'total_issues': len(validation_issues),
            'critical_issues': critical_count,
            'high_issues': high_count
        }
    
    def _auto_fix_layout_issues(self, build_response: BuildResponse, 
                               validation_results: Dict[str, Any]) -> Optional[BuildResponse]:
        """
        Attempt to automatically fix critical layout issues
        
        Args:
            build_response: Original build response with issues
            validation_results: Layout validation results
            
        Returns:
            Fixed BuildResponse or None if fixes couldn't be applied
        """
        if not validation_results.get('issues'):
            return None
        
        # Extract critical issues that can be auto-fixed
        critical_issues = [
            issue for issue in validation_results['issues'] 
            if issue['severity'] == 'critical'
        ]
        
        if not critical_issues:
            return None
        
        # Create a layout fix prompt
        fix_prompt = self._generate_layout_fix_prompt(
            build_response.yaml_spec, 
            critical_issues
        )
        
        try:
            # Request fixes from LLM
            response = self._call_llm(fix_prompt)
            fixed_response = self._parse_build_response(response)
            
            # Validate the fixed version
            if AUTOLAYOUT_AVAILABLE:
                new_validation = self._validate_yaml_layout(fixed_response.yaml_spec)
                fixed_response.layout_validation = new_validation
                
                # Only return if we actually improved the layout
                if new_validation.get('critical_issues', 0) < validation_results.get('critical_issues', 0):
                    print(f"Layout auto-fix successful: reduced critical issues from {validation_results.get('critical_issues')} to {new_validation.get('critical_issues')}")
                    return fixed_response
            
            return None
            
        except Exception as e:
            print(f"Layout auto-fix failed: {e}")
            return None
    
    def _generate_layout_fix_prompt(self, yaml_spec: Dict[str, Any], 
                                   critical_issues: List[Dict[str, Any]]) -> str:
        """
        Generate a prompt to fix layout issues
        
        Args:
            yaml_spec: Original YAML specification
            critical_issues: List of critical layout issues
            
        Returns:
            Prompt string for layout fixes
        """
        yaml_str = yaml.dump(yaml_spec, indent=2, default_flow_style=False)
        
        issues_summary = []
        for issue in critical_issues:
            scene = issue.get('scene', 'unknown')
            description = issue.get('issue', 'layout issue')
            suggestion = issue.get('suggestion', 'fix layout')
            issues_summary.append(f"- Scene '{scene}': {description} → {suggestion}")
        
        issues_text = '\n'.join(issues_summary)
        
        return f"""You are MANIM-AUTOPILOT in LAYOUT-FIX mode. Fix the critical layout issues in the YAML specification below.

CRITICAL ISSUES TO FIX:
{issues_text}

RULES FOR FIXES:
1. Resolve overlaps by staggering element timing (add delays between enter/exit)
2. Move overlapping elements to different columns/regions
3. Reduce font sizes if elements are too large (minimum 24)
4. Split scenes with >4 elements into multiple scenes
5. Maintain all scene IDs and element keys
6. Keep the same topic structure and educational flow

Return ONLY the corrected YAML specification in the same format:

YAML
---BEGIN YAML---
{yaml_str}
---END YAML---

CODE
<regenerated scene.py code>

ACTION: COMPILE_480P"""

    def get_layout_validation_summary(self, build_response: BuildResponse) -> str:
        """
        Generate a human-readable summary of layout validation results
        
        Args:
            build_response: Build response with layout validation
            
        Returns:
            Formatted validation summary
        """
        if not build_response.layout_validation:
            return "Layout validation: Not performed"
        
        validation = build_response.layout_validation
        status = validation.get('status', 'unknown')
        total_issues = validation.get('total_issues', 0)
        critical_issues = validation.get('critical_issues', 0)
        
        if status == 'passed':
            return "SUCCESS: Layout validation: PASSED - No significant issues detected"
        elif status == 'warnings':
            return f"WARNING:  Layout validation: WARNINGS - {total_issues} issues found (non-critical)"
        else:
            return f"ERROR: Layout validation: FAILED - {total_issues} issues ({critical_issues} critical)"
    
    def _parse_yaml_with_fallbacks(self, yaml_content: str) -> Dict[str, Any]:
        """Parse YAML with multiple fallback strategies"""
        yaml_content = yaml_content.strip()
        
        # Clean YAML content of various markers
        if yaml_content:
            yaml_content = self._clean_yaml_content(yaml_content)
        
        # Try multiple parsing approaches
        for attempt_name, yaml_to_try in [
            ("Original content", yaml_content),
            ("Cleaned content", self._aggressive_yaml_cleanup(yaml_content)),
            ("Reconstructed content", self._reconstruct_yaml_from_fragments(yaml_content))
        ]:
            try:
                if yaml_to_try:
                    yaml_spec = yaml.safe_load(yaml_to_try)
                    if yaml_spec and isinstance(yaml_spec, dict):
                        print(f"SUCCESS: YAML parsed using {attempt_name}")
                        return yaml_spec
            except yaml.YAMLError as e:
                print(f"WARNING: YAML parsing failed for {attempt_name}: {e}")
                continue
        
        print("WARNING: All YAML parsing attempts failed, creating minimal structure")
        return self._create_minimal_yaml_structure()
    
    def _clean_yaml_content(self, yaml_content: str) -> str:
        """Clean YAML content of common issues"""
        # Remove code block markers
        if yaml_content.startswith('```yaml'):
            yaml_lines = yaml_content.split('\n')
            yaml_lines = [line for line in yaml_lines if not line.strip().startswith('```')]
            yaml_content = '\n'.join(yaml_lines)
        
        # Remove custom YAML markers
        if yaml_content.startswith('---BEGIN YAML---'):
            yaml_content = yaml_content[16:]  # Remove ---BEGIN YAML---
        elif yaml_content.startswith('---YAML---'):
            yaml_content = yaml_content[10:]  # Remove ---YAML---
        
        # Remove ending markers
        if yaml_content.endswith('---END YAML---'):
            yaml_content = yaml_content[:-14]  # Remove ---END YAML---
        elif yaml_content.endswith('---'):
            yaml_content = yaml_content[:-3]   # Remove ---
        elif yaml_content.endswith('```'):
            yaml_content = yaml_content[:-3]   # Remove ```
        
        # Fix common typos
        yaml_content = yaml_content.replace('template: singl', 'template: single')
        yaml_content = yaml_content.replace('template: "singl"', 'template: "single"')
        yaml_content = yaml_content.replace("template: 'singl'", "template: 'single'")
        
        return yaml_content.strip()
    
    def _aggressive_yaml_cleanup(self, yaml_content: str) -> str:
        """Aggressive cleanup for malformed YAML"""
        import re
        
        lines = yaml_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # Fix common issues
            line = re.sub(r'^\s*-\s*([^:])', r'- \1', line)  # Fix list items
            line = re.sub(r':([^\s])', r': \1', line)  # Add space after colons
            
            # Quote problematic values
            if re.match(r'^\s*narration:\s*[^"\n]', line):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    line = f"{parts[0]}: \"{parts[1].strip()}\""
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _reconstruct_yaml_from_fragments(self, yaml_content: str) -> str:
        """Attempt to reconstruct valid YAML from fragments"""
        import re
        
        # Extract key-value pairs
        topic_match = re.search(r'topic:?\s*([^\n]+)', yaml_content, re.IGNORECASE)
        audience_match = re.search(r'audience:?\s*([^\n]+)', yaml_content, re.IGNORECASE)
        
        reconstructed = []
        
        if topic_match:
            reconstructed.append(f'topic: "{topic_match.group(1).strip()}"')
        else:
            reconstructed.append('topic: "Untitled Topic"')
        
        if audience_match:
            reconstructed.append(f'audience: "{audience_match.group(1).strip()}"')
        else:
            reconstructed.append('audience: "undergraduate"')
        
        # Add basic structure
        reconstructed.extend([
            'style:',
            '  voice: "professional"',
            '  pace_wpm: 150',
            '  theme: "3blue1brown"',
            'global:',
            '  safe_margin_pct: 0.06',
            '  default_font_size: 42',
            '  max_width_pct: 0.92',
            '  grid:',
            '    template: "single"',
            '    config: {}',
            'scenes:',
            '  - id: "main_scene"',
            '    goal: "Present the content"',
            '    time_budget_s: 30',
            '    narration: "Let\'s explore this topic"',
            '    layout:',
            '      template: "single"',
            '      elements:',
            '        - key: "title"',
            '          type: "Text"',
            '          column: "center"',
            '          text: "Main Title"',
            '    checks: ["text_readable", "no_overlap"]'
        ])
        
        return '\n'.join(reconstructed)
    
    def _create_minimal_yaml_structure(self) -> Dict[str, Any]:
        """Create minimal valid YAML structure as last resort"""
        return {
            'topic': 'Emergency Fallback Topic',
            'audience': 'undergraduate',
            'style': {
                'voice': 'professional',
                'pace_wpm': 150,
                'theme': '3blue1brown'
            },
            'global': {
                'safe_margin_pct': 0.06,
                'default_font_size': 42,
                'max_width_pct': 0.92,
                'grid': {
                    'template': 'single',
                    'config': {}
                }
            },
            'scenes': [{
                'id': 'fallback_scene',
                'goal': 'Present basic content due to parsing failure',
                'time_budget_s': 20,
                'narration': 'This is a fallback scene created due to parsing issues.',
                'layout': {
                    'template': 'single',
                    'elements': [{
                        'key': 'emergency_text',
                        'type': 'Text',
                        'column': 'center',
                        'text': 'Content parsing failed - using emergency fallback'
                    }]
                },
                'checks': ['text_readable', 'no_overlap']
            }]
        }
    
    def _create_fallback_code(self) -> str:
        """Create basic fallback code when parsing fails"""
        return '''from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Fallback scene due to parsing failure
        title = Text("Parsing Error - Fallback Content", font_size=36)
        title.to_edge(UP)
        
        message = Text(
            "The original content could not be parsed.\\n"
            "This is a fallback scene.",
            font_size=24
        )
        message.next_to(title, DOWN, buff=1)
        
        self.play(Write(title))
        self.play(FadeIn(message))
        self.wait(2)
'''
    
    def _parse_response_standard(self, response: str) -> Dict[str, List[str]]:
        """Standard section-based parsing"""
        sections = {}
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # Detect section headers (support both plain and markdown formats)
            if line_stripped in ['OUTLINE', 'YAML', 'CODE'] or \
               line_stripped in ['## OUTLINE', '## YAML', '## CODE'] or \
               line_stripped in ['# OUTLINE', '# YAML', '# CODE']:
                # Extract section name (remove markdown headers)
                section_name = line_stripped.replace('#', '').strip()
                current_section = section_name
                sections[current_section] = []
            elif line_stripped.startswith('ACTION:') or line_stripped.startswith('## ACTION'):
                sections['ACTION'] = line_stripped
            elif current_section and line_stripped:
                sections[current_section].append(line)
        
        return sections
    
    def _parse_response_regex(self, response: str) -> Dict[str, List[str]]:
        """Regex-based parsing for malformed responses"""
        import re
        sections = {}
        
        # Try to extract YAML block using various patterns
        yaml_patterns = [
            r'YAML\s*\n(.*?)(?=\n(?:CODE|ACTION|$))',
            r'```yaml\n(.*?)\n```',
            r'topic:\s*.*?(?=\n\n|$)',
            r'\btopic:.*?\nscenes:.*?(?=\n\n|CODE|ACTION|$)'
        ]
        
        yaml_content = []
        for pattern in yaml_patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                yaml_content = match.group(1).strip().split('\n') if match.groups() else match.group(0).strip().split('\n')
                break
        
        if yaml_content:
            sections['YAML'] = yaml_content
        
        # Extract CODE similarly
        code_patterns = [
            r'CODE\s*\n(.*?)(?=\n(?:ACTION|$))',
            r'```python\n(.*?)\n```',
            r'class\s+\w*Scene.*?(?=\n\n|ACTION|$)'
        ]
        
        for pattern in code_patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                sections['CODE'] = match.group(1).strip().split('\n') if match.groups() else match.group(0).strip().split('\n')
                break
        
        # Extract ACTION
        action_match = re.search(r'ACTION:\s*(.*)', response, re.IGNORECASE)
        if action_match:
            sections['ACTION'] = f"ACTION: {action_match.group(1).strip()}"
        
        # Basic outline if nothing else found
        if 'OUTLINE' not in sections:
            sections['OUTLINE'] = ["1. Introduction", "2. Main content", "3. Conclusion"]
        
        return sections
    
    def _parse_response_emergency(self, response: str) -> Dict[str, List[str]]:
        """Emergency parsing for completely malformed responses"""
        sections = {}
        
        # Look for any YAML-like content
        if 'topic:' in response.lower() or 'scenes:' in response.lower():
            # Extract everything that looks like YAML
            lines = response.split('\n')
            yaml_lines = []
            in_yaml_block = False
            
            for line in lines:
                if any(key in line.lower() for key in ['topic:', 'audience:', 'style:', 'global:', 'scenes:']):
                    in_yaml_block = True
                if in_yaml_block and (line.strip().startswith('-') or ':' in line or line.strip() == ''):
                    yaml_lines.append(line)
                elif in_yaml_block and line.strip() and not (':' in line or line.strip().startswith('-')):
                    break
            
            if yaml_lines:
                sections['YAML'] = yaml_lines
        
        # Look for any Python code
        if 'class' in response and 'Scene' in response:
            lines = response.split('\n')
            code_lines = []
            in_code = False
            
            for line in lines:
                if 'class' in line and 'Scene' in line:
                    in_code = True
                if in_code:
                    code_lines.append(line)
            
            if code_lines:
                sections['CODE'] = code_lines
        
        return sections
    
    def _create_emergency_sections(self, response: str) -> Dict[str, List[str]]:
        """Create basic sections when all parsing fails"""
        return {
            'OUTLINE': ["# Emergency Outline", "1. Basic structure created due to parsing failure"],
            'YAML': [],  # Will trigger minimal YAML creation
            'CODE': [],  # Will trigger fallback code creation
            'ACTION': 'ACTION: COMPILE_480P'
        }
    
    def _validate_parsed_sections(self, sections: Dict[str, List[str]]) -> bool:
        """Validate that parsed sections contain reasonable content"""
        # Check if we have at least some content
        has_yaml = sections.get('YAML') and len(sections['YAML']) > 0
        has_code = sections.get('CODE') and len(sections['CODE']) > 0
        
        # At minimum, we need either YAML with key indicators or reasonable CODE
        if has_yaml:
            yaml_text = '\n'.join(sections['YAML']).lower()
            if any(key in yaml_text for key in ['topic:', 'scenes:', 'audience:']):
                return True
        
        if has_code:
            code_text = '\n'.join(sections['CODE'])
            if 'class' in code_text and 'Scene' in code_text:
                return True
        
        return False


def create_builder_llm(api_key: str) -> BuilderLLM:
    """Factory function to create a Builder LLM instance"""
    return BuilderLLM(api_key)