import os
import re
import subprocess
import sys
import yaml
from typing import Optional, Tuple, Dict, Any, List
import openai
from openai import OpenAI

class FinalManimGenerator:
    def __init__(self, api_key: str):
        """Initialize the final Manim generator with advanced shot-by-shot approach."""
        self.client = OpenAI(api_key=api_key)
        self.output_dir = "output/animations"
        self.content_dir = "output/content"
        self.max_retries = 5
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.content_dir, exist_ok=True)
        
        # Load Manim API reference and parameter fixes
        self.manim_api = self._load_manim_api_reference()
        self.parameter_fixes = self._load_parameter_fixes()
        self.fix_attempts = []  # Track what has been tried
        
        # Extract layout safety configuration used across all topics
        self.layout_rules = self._extract_layout_rules()
        self.named_positions = self._extract_named_positions()
    
    def _load_manim_api_reference(self) -> Dict[str, Any]:
        """Load the Manim API reference for accurate code generation."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'manim_api.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print("WARNING: Manim API reference not found, using basic reference")
            return {
                "animations": {
                    "Create": {"note": "Use Create, not ShowCreation"},
                    "Write": {"for_objects": ["Text", "Tex"]},
                    "FadeIn": {"for_objects": ["any object"]},
                    "FadeOut": {"for_objects": ["any object"]}
                }
            }
    
    def _load_parameter_fixes(self) -> Dict[str, Any]:
        """Load parameter fix database for intelligent error correction."""
        try:
            fixes_path = os.path.join(os.path.dirname(__file__), 'config', 'manim_parameter_fixes.yaml')
            with open(fixes_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print("WARNING: Parameter fixes database not found")
            return {"parameter_fixes": {}, "error_patterns": {}}

    def _extract_layout_rules(self) -> Dict[str, Any]:
        """Extract layout rules from configuration to guide generation globally."""
        layout_rules: Dict[str, Any] = {}
        try:
            if isinstance(self.manim_api, dict):
                # Prefer top-level layout_rules if provided
                top_level = self.manim_api.get('layout_rules', {})
                if isinstance(top_level, dict):
                    layout_rules.update(top_level)
                # Also check nested under manim_api
                nested = self.manim_api.get('manim_api', {}).get('layout_rules', {})
                if isinstance(nested, dict):
                    for k, v in nested.items():
                        layout_rules.setdefault(k, v)

            # Supplement from content schema global_layout_rules if present
            schema_path = os.path.join(os.path.dirname(__file__), 'config', 'content_schema.yaml')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_yaml = yaml.safe_load(f)
                if isinstance(schema_yaml, dict):
                    global_rules = schema_yaml.get('global_layout_rules', {})
                    if isinstance(global_rules, dict):
                        safe_area = global_rules.get('safe_area', {})
                        if isinstance(safe_area, dict) and 'safe_area_margin' not in layout_rules:
                            layout_rules['safe_area_margin'] = {
                                'x': safe_area.get('margin_x', 0.7),
                                'y': safe_area.get('margin_y', 0.5),
                            }
                        spacing = global_rules.get('spacing', {})
                        if isinstance(spacing, dict) and 'min_gap_between_objects' not in layout_rules:
                            layout_rules['min_gap_between_objects'] = spacing.get('min_gap_between_elements', 0.6)
        except Exception:
            pass
        return layout_rules

    def _extract_named_positions(self) -> Dict[str, Any]:
        """Extract safe named positions from configuration for consistent placement."""
        try:
            if isinstance(self.manim_api, dict):
                # Prefer duplicated top-level positioning
                top = self.manim_api.get('positioning', {})
                if isinstance(top, dict) and top:
                    return top
                # Fallback to nested named positions
                nested = self.manim_api.get('manim_api', {}).get('positioning', {}).get('named_positions', {})
                if isinstance(nested, dict) and nested:
                    return nested
        except Exception:
            pass
        # Conservative defaults within frame
        return {
            'center': 'ORIGIN',
            'top': 'UP * 2.8',
            'bottom': 'DOWN * 2.8',
            'left': 'LEFT * 5.5',
            'right': 'RIGHT * 5.5',
            'top_left': 'UP * 2.2 + LEFT * 4.5',
            'top_right': 'UP * 2.2 + RIGHT * 4.5',
            'bottom_left': 'DOWN * 2.2 + LEFT * 4.5',
            'bottom_right': 'DOWN * 2.2 + RIGHT * 4.5',
        }
    
    def generate_detailed_content_yaml(self, topic: str) -> Optional[Dict[Any, Any]]:
        """Generate detailed shot-by-shot content structure."""
        print(f"Generating detailed shot-by-shot content for: '{topic}'")
        
        # Load advanced schema as template
        try:
            schema_path = os.path.join(os.path.dirname(__file__), 'config', 'content_schema.yaml')
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_example = f.read()[:2000]  # First 2000 chars as example
        except FileNotFoundError:
            schema_example = "# Basic schema structure"
        
        prompt = f"""
        Create a detailed shot-by-shot educational animation structure for: "{topic}"
        
        You are creating a professional educational video like 3Blue1Brown with:
        1. PRECISE TIMING for each visual element
        2. CLEAR POSITIONING to prevent overlaps  
        3. SHOT-BY-SHOT breakdown like a film storyboard
        4. OBJECT LIFECYCLE management (create → use → remove)
        
        Follow this advanced schema structure:
        {schema_example}
        
        CRITICAL REQUIREMENTS:
        
        1. Timeline with precise shots:
           - Each shot: start_time, end_time, scene_state
           - scene_state: "clean" (clear previous) or "build_on_previous"
           - NO overlapping visual elements; if multiple elements, place them in different screen regions
        
        2. Element specifications:
           - Exact position (center, top_left, bottom_right, etc.) using NAMED POSITIONS only
           - Layer (1=background, 2=main, 3=foreground)
           - Animation timing (entry_duration, stay_duration, exit_duration)
           - Use next_to(reference, DIRECTION, buff) with buff >= {self.layout_rules.get('min_gap_between_objects', 0.6)} when placing related objects
        
        3. Object lifecycle:
           - When each object is created
           - When it's transformed
           - When it's removed from scene
        
        4. Educational flow:
           - Introduce concept → Show visual → Explain → Clear → Next
           - Each concept gets its own clean shot
           - Build complexity step by step
        
        4.1 Curriculum progression (MANDATORY):
           - Sections and shots must progress from basics to advanced:
             a) Foundations/Definitions
             b) Core Concepts
             c) Visual Demonstrations (charts/graphs/diagrams)
             d) Applications/Examples
             e) Advanced Insights/Edge cases
             f) Summary/Key Takeaways
           - Include charts and diagrams using axes and function graphs where relevant.
           - Prefer simple shapes to depict diagrams; avoid external assets.

        5. LAYOUT SAFETY (MANDATORY):
           - Respect SAFE AREA margins: x ≥ {self.layout_rules.get('safe_area_margin', {}).get('x', 0.7)}, y ≥ {self.layout_rules.get('safe_area_margin', {}).get('y', 0.5)}
           - Per-region capacity: max 1 element visible per region at the same time
           - Min gap between elements: ≥ {self.layout_rules.get('min_gap_between_objects', 0.6)}
           - Wrap or scale text to fit its region; avoid long single-line strings
           - Prefer 'clean' shots; if build_on_previous, ensure no overlaps
        
        IMPORTANT: Include a technical_specs section that contains 'positioning' and 'layout_rules' matching the constraints above.
        
        Return ONLY the YAML structure.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.7
            )
            
            yaml_content = response.choices[0].message.content.strip()
            
            # Clean YAML content
            if "```yaml" in yaml_content:
                yaml_content = re.search(r'```yaml\n(.*?)```', yaml_content, re.DOTALL).group(1)
            elif "```" in yaml_content:
                yaml_content = re.search(r'```\n(.*?)```', yaml_content, re.DOTALL).group(1)
            
            # Parse and validate YAML
            try:
                content_structure = yaml.safe_load(yaml_content)
                if not isinstance(content_structure, dict):
                    return None
                # Post-process: enforce technical specs and layout constraints
                content_structure = self._ensure_technical_specs(content_structure)
                content_structure = self._enforce_layout_rules_on_shots(content_structure)
                return content_structure
            except yaml.YAMLError as e:
                print(f"ERROR: YAML parsing error: {e}")
                return None
                
        except Exception as e:
            print(f"ERROR: Error generating content: {e}")
            return None
    
    def generate_shot_based_manim_code(self, content: Dict[Any, Any]) -> str:
        """Generate Manim code with shot-by-shot structure and proper API usage."""
        print("Generating shot-based Manim code...")
        
        # Extract key info for focused prompt
        timeline = content.get('animation', {}).get('timeline', {})
        shots = timeline.get('shots', [])[:8]  # Include more shots to cover basics → advanced
        topic = content.get('animation', {}).get('metadata', {}).get('topic', 'Topic')
        
        # Create focused content summary
        content_summary = {
            'topic': topic,
            'shots': shots,
            'technical_specs': content.get('technical_specs', {}),
            'positioning': self.named_positions,
            'layout_rules': self.layout_rules,
        }
        
        prompt = f"""
        Generate clean, working Manim code using this shot-by-shot structure:

        Content: {yaml.dump(content_summary, default_flow_style=False)}
        
        MANIM API REQUIREMENTS (CRITICAL):
        
        1. Correct Animation Names:
           - Use Create (NOT ShowCreation)
           - Use Write for text
           - Use FadeIn/FadeOut for appearance
           - Use GrowFromCenter/ShrinkToCenter for scaling
           
        2. Proper Object Management:
           - Create objects in one shot
           - Use them in that shot
           - FadeOut or clear before next shot
           - NO overlapping elements
           
        3. Scene skeleton (must match exactly):
           from manim import *
           
           class EducationalScene(Scene):
               def construct(self):
                   pass
           
           - You MUST define exactly one class named EducationalScene that subclasses Scene.
           - Put all shot code inside construct(self). Do not create additional classes or functions.
           
         4. Positioning System:
            - Use only the provided named positions in Content.positioning
            - Respect safe area margins; do not place objects outside visible frame
           
         5. Timing Control:
           - Add run_time parameter: self.play(Write(text), run_time=2)
           - Add waits: self.wait(1)
           - Clear between sections: self.play(FadeOut(*self.mobjects))
           
        6. Dynamic Frame (REQUIRED):
           - At the top of construct(self), define dynamic safe frame values:
             fw = config.frame_width
             fh = config.frame_height
             margin_x = {self.layout_rules.get('safe_area_margin', {}).get('x', 0.7)}
             margin_y = {self.layout_rules.get('safe_area_margin', {}).get('y', 0.5)}
             safe_left = LEFT * (fw/2 - margin_x)
             safe_right = RIGHT * (fw/2 - margin_x)
             safe_top = UP * (fh/2 - margin_y)
             safe_bottom = DOWN * (fh/2 - margin_y)
             # Corners
             safe_top_left = safe_top + safe_left
             safe_top_right = safe_top + safe_right
             safe_bottom_left = safe_bottom + safe_left
             safe_bottom_right = safe_bottom + safe_right
           - Use these safe_* positions for move_to()/next_to()/to_edge() and ensure everything stays in-frame
           - For wide text/diagrams: use .scale_to_fit_width(fw - 2*margin_x) or .scale_to_fit_height(fh - 2*margin_y)

        7. Layout Safety (MANDATORY):
           - Per-region capacity: Max 1 element visible per region per shot
           - Use next_to(reference, DIRECTION, buff={self.layout_rules.get('min_gap_between_objects', 0.6)}) to space objects
           - For long text, reduce font_size or split into multiple lines so it fits within safe area
           - Avoid manual coordinates that push objects off-screen

        8. Visual Elements (ENCOURAGED):
           - Use Axes + functions for graphs; add dots/labels where meaningful
           - Build simple bar charts with Axes and Rectangle groups if needed
           - Use NumberPlane for geometric demonstrations

        9. Asset usage constraints (IMPORTANT):
           - Do NOT use ImageMobject or any external files (no images, no videos).
           - If the content includes an image, replace it with a simple placeholder such as a Circle or a Text label.
           - Do NOT call any .set_weight() or use weight/style parameters.
           
        Generate COMPLETE working code that follows this shot structure exactly.
        Each shot should be a distinct code block with clear scene state management.
        Return ONLY the Python code without any backticks.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,  # Reduced to stay under limits
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"ERROR: Error generating Manim code: {e}")
            return None

    def _ensure_technical_specs(self, content: Dict[Any, Any]) -> Dict[str, Any]:
        """Ensure technical_specs include safe positioning and layout for any topic."""
        technical_specs = content.setdefault('technical_specs', {})
        # Positioning
        if not isinstance(technical_specs.get('positioning'), dict) or not technical_specs['positioning']:
            technical_specs['positioning'] = dict(self.named_positions)
        # Layout rules
        if not isinstance(technical_specs.get('layout_rules'), dict) or not technical_specs['layout_rules']:
            technical_specs['layout_rules'] = dict(self.layout_rules)
        # Timing defaults
        timing = technical_specs.setdefault('timing', {})
        timing.setdefault('default_run_time', 2)
        timing.setdefault('default_wait', 1)
        timing.setdefault('transition_time', 0.5)
        # Scene management
        scene_mgmt = technical_specs.setdefault('scene_management', {})
        scene_mgmt.setdefault('clear_between_shots', True)
        scene_mgmt.setdefault('use_fadeout_all', 'self.play(FadeOut(*self.mobjects))')
        return content

    def _enforce_layout_rules_on_shots(self, content: Dict[Any, Any]) -> Dict[str, Any]:
        """Normalize and enforce per-shot layout constraints without changing topic content."""
        animation = content.get('animation', {})
        timeline = animation.get('timeline', {})
        shots = timeline.get('shots', [])
        if not isinstance(shots, list):
            return content

        # Preferred reassignment regions
        preferred_regions: List[str] = [
            'center', 'center_right', 'center_left',
            'top', 'bottom', 'top_right', 'top_left', 'bottom_right', 'bottom_left'
        ]

        # Capacity rules
        rules_capacity = self.layout_rules.get('per_region_capacity', {})
        default_capacity = 1

        for shot in shots:
            elements = shot.get('elements', [])
            if not isinstance(elements, list):
                continue
            region_usage: Dict[str, int] = {}

            for element in elements:
                # Default position to center if missing
                region = element.get('position') or 'center'
                if region in ('middle', 'centre'):
                    region = 'center'
                element['position'] = region

                # Enforce per-region capacity
                cap = int(rules_capacity.get(region, default_capacity)) if isinstance(rules_capacity, dict) else default_capacity
                used = region_usage.get(region, 0)
                if used < cap:
                    region_usage[region] = used + 1
                else:
                    # Reassign to an available region
                    reassigned = False
                    for candidate in preferred_regions:
                        c_cap = int(rules_capacity.get(candidate, default_capacity)) if isinstance(rules_capacity, dict) else default_capacity
                        c_used = region_usage.get(candidate, 0)
                        if c_used < c_cap:
                            element['position'] = candidate
                            region_usage[candidate] = c_used + 1
                            reassigned = True
                            break
                    if not reassigned:
                        # Last resort: hint to separate on render time
                        hint = element.setdefault('layout_hint', {})
                        hint['use_next_to'] = True
                        hint['buff'] = self.layout_rules.get('min_gap_between_objects', 0.6)

                # Basic text safety defaults
                if element.get('type') in ('text', 'formula'):
                    style = element.setdefault('style', {})
                    style.setdefault('font_size', 36)
        return content
    
    def _truncate_error_context(self, code: str, error_message: str) -> Tuple[str, str]:
        """Truncate code and error to fit within token limits."""
        # Extract error line number if possible
        line_match = re.search(r'line (\d+)', error_message)
        if line_match:
            error_line = int(line_match.group(1))
            code_lines = code.split('\n')
            
            # Get context around error line (±10 lines)
            start_line = max(0, error_line - 10)
            end_line = min(len(code_lines), error_line + 10)
            context_code = '\n'.join(code_lines[start_line:end_line])
        else:
            # Take last 1000 characters of code
            context_code = code[-1000:]
        
        # Truncate error message to last 500 characters
        truncated_error = error_message[-500:]
        
        return context_code, truncated_error
    
    def fix_manim_code_progressive(self, filepath: str, error_message: str, attempt_number: int) -> bool:
        """Progressive auto-fixing with different strategies per attempt."""
        print(f"Progressive fix attempt {attempt_number}/5")
        
        # Read current code
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            print(f"ERROR: Could not read file: {e}")
            return False
        
        # Apply different fix strategy based on attempt number
        if attempt_number == 1:
            success = self._fix_parameters(filepath, code, error_message)
        elif attempt_number == 2:
            success = self._fix_api_calls(filepath, code, error_message)
        elif attempt_number == 3:
            success = self._fix_simplify_objects(filepath, code, error_message)
        elif attempt_number == 4:
            success = self._fix_with_llm_targeted(filepath, code, error_message)
        else:  # attempt 5
            success = self._fix_fallback_template(filepath, error_message)
        
        if success:
            print(f"SUCCESS: Strategy {attempt_number} applied successfully")
        else:
            print(f"WARNING: Strategy {attempt_number} could not be applied")
        
        return success
    
    def _fix_parameters(self, filepath: str, code: str, error_message: str) -> bool:
        """Fix Strategy 1: Parameter corrections using database."""
        print("Strategy 1: Fixing parameter issues")
        
        # Check if this is a parameter error
        if "unexpected keyword argument" not in error_message:
            return False
        
        # Extract the problematic parameter
        param_match = re.search(r"unexpected keyword argument '(\w+)'", error_message)
        if not param_match:
            return False
            
        problematic_param = param_match.group(1)
        print(f"Fixing parameter: {problematic_param}")
        
        # Get parameter fixes
        fixes = self.parameter_fixes.get("parameter_fixes", {})

        # Apply fixes for the specific problematic parameter only, scoped to matching constructors
        fixed_code = code
        changes_made = False

        for obj_type, obj_fixes in fixes.items():
            invalid_params = obj_fixes.get("invalid_params", [])
            if problematic_param not in invalid_params:
                continue

            mappings = obj_fixes.get("correct_mappings", {})
            new_param = mappings.get(problematic_param, None)

            fixed_code, changed_here = self._replace_param_in_calls(
                fixed_code, obj_type, problematic_param, new_param
            )
            if changed_here:
                changes_made = True
                if new_param is None:
                    print(f"Removed parameter '{problematic_param}' in {obj_type}() calls")
                else:
                    print(f"Replaced {problematic_param} -> {new_param} in {obj_type}() calls")

        # As a conservative fallback, if nothing matched specific constructors, remove the parameter globally
        if not changes_made:
            pattern = rf'\b{problematic_param}\s*=\s*[^,\)]+,?\s*'
            if re.search(pattern, fixed_code):
                fixed_code = re.sub(pattern, '', fixed_code)
                changes_made = True
                print(f"Removed unknown parameter globally: {problematic_param}")
        
        # Clean up any duplicate commas or trailing commas that might result
        if changes_made:
            # Fix double commas
            fixed_code = re.sub(r',\s*,', ',', fixed_code)
            # Fix trailing commas before closing parentheses
            fixed_code = re.sub(r',\s*\)', ')', fixed_code)
            # Fix leading commas after opening parentheses
            fixed_code = re.sub(r'\(\s*,', '(', fixed_code)
        
        # Save fixed code if changes were made
        if changes_made:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                return True
            except Exception as e:
                print(f"ERROR: Could not save fixed code: {e}")
                return False
        
        return False

    def _replace_param_in_calls(
        self,
        code: str,
        constructor_name: str,
        old_param: str,
        new_param: Optional[str],
    ) -> Tuple[str, bool]:
        """Replace or remove a parameter inside calls to a given constructor only.
        Returns the updated code and whether any change was made.
        """
        updated_code_parts: List[str] = []
        position = 0
        changed = False

        while True:
            start = code.find(f"{constructor_name}(", position)
            if start == -1:
                break

            # Append text before the constructor call
            updated_code_parts.append(code[position:start])

            # Find matching closing parenthesis
            paren_start = code.find("(", start)
            if paren_start == -1:
                # Malformed; append rest and break
                updated_code_parts.append(code[start:])
                position = len(code)
                break

            depth = 1
            i = paren_start + 1
            while i < len(code) and depth > 0:
                ch = code[i]
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                i += 1

            if depth != 0:
                # No closing paren found; append rest and break
                updated_code_parts.append(code[start:])
                position = len(code)
                break

            call_end = i  # index just after ')'
            call_text = code[start:call_end]

            new_call_text = call_text
            if new_param is None:
                # Remove the parameter assignments robustly
                # Case 1: param=val,
                new_call_text = re.sub(
                    rf'\b{re.escape(old_param)}\s*=\s*[^,\)]+\s*,\s*',
                    '',
                    new_call_text,
                )
                # Case 2: , param=val
                new_call_text = re.sub(
                    rf',\s*\b{re.escape(old_param)}\s*=\s*[^,\)]+',
                    '',
                    new_call_text,
                )
                # Case 3: only or last param: param=val)
                new_call_text = re.sub(
                    rf'\b{re.escape(old_param)}\s*=\s*[^,\)]+\s*\)',
                    ')',
                    new_call_text,
                )
                # Cleanup redundant commas
                new_call_text = re.sub(r'\(\s*,\s*', '(', new_call_text)
                new_call_text = re.sub(r',\s*\)', ')', new_call_text)
            else:
                # Replace the parameter name only
                new_call_text = re.sub(
                    rf'\b{re.escape(old_param)}\s*=',
                    f'{new_param}=',
                    new_call_text,
                )

            if new_call_text != call_text:
                changed = True

            updated_code_parts.append(new_call_text)
            position = call_end

        # Append the remainder
        updated_code_parts.append(code[position:])
        new_code = ''.join(updated_code_parts)
        return new_code, changed
    
    def _fix_api_calls(self, filepath: str, code: str, error_message: str) -> bool:
        """Fix Strategy 2: Modern Manim API calls."""
        print(" Strategy 2: Modernizing API calls")
        
        api_fixes = [
            ("ShowCreation", "Create"),
            ("DrawBorderThenFill", "Create"),
            ("ShowIncreasingSubsets", "Create"),
        ]
        
        fixed_code = code
        changes_made = False
        
        for old_api, new_api in api_fixes:
            if old_api in fixed_code:
                fixed_code = fixed_code.replace(old_api, new_api)
                changes_made = True
                print(f" Replaced {old_api} -> {new_api}")
        
        # Save if changes made
        if changes_made:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                return True
            except Exception as e:
                print(f"ERROR: Could not save: {e}")
                return False
        
        return False
    
    def _fix_simplify_objects(self, filepath: str, code: str, error_message: str) -> bool:
        """Fix Strategy 3: Simplify problematic objects."""
        print(" Strategy 3: Simplifying objects")
        
        # Simplification rules
        simplifications = [
            # Remove style/weight methods that can cause issues
            (r'\.set_weight\([^)]+\)', ''),
            (r'\.set_style\([^)]+\)', ''),

            # Simplify to basic colors
            (r'color=YELLOW', 'color=BLUE'),
            (r'color=\w+', 'color=WHITE'),

            # Remove complex positioning
            (r'\.move_to\([^)]+\)', '.move_to(ORIGIN)'),
            (r'\.to_edge\([^)]+\)', ''),

            # Replace external images with a simple shape
            (r'ImageMobject\([^)]+\)', 'Circle(radius=2, color=BLUE)'),

            # Fix nested Text(Text("...")) → Text("...")
            (r'Text\(\s*Text\(([^)]*)\)\s*\)', r'Text(\1)'),
        ]
        
        fixed_code = code
        changes_made = False
        
        for pattern, replacement in simplifications:
            if re.search(pattern, fixed_code):
                if callable(replacement):
                    fixed_code = re.sub(pattern, replacement, fixed_code)
                else:
                    fixed_code = re.sub(pattern, replacement, fixed_code)
                changes_made = True
                print(f" Applied simplification: {pattern[:30]}...")
        
        if changes_made:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                return True
            except Exception as e:
                print(f"ERROR: Could not save: {e}")
                return False
        
        return False
    
    def _fix_with_llm_targeted(self, filepath: str, code: str, error_message: str) -> bool:
        """Fix Strategy 4: Targeted LLM fix with better context."""
        print(" Strategy 4: LLM targeted repair")
        
        # Extract error line and context
        lines = code.split('\n')
        error_line_match = re.search(r'line (\d+)', error_message)
        
        if error_line_match:
            error_line_num = int(error_line_match.group(1))
            start = max(0, error_line_num - 5)
            end = min(len(lines), error_line_num + 5)
            context_lines = lines[start:end]
            context_code = '\n'.join(context_lines)
        else:
            context_code = code[:1000]  # First 1000 chars
        
        prompt = f"""
        Fix this specific Manim error. Make minimal changes to fix the issue.
        
        Error: {error_message[:200]}
        
        Code context:
        {context_code}
        
        Rules:
        1. Only fix the specific error, don't rewrite everything
        2. Use only basic Manim objects: Text, Circle, Rectangle
        3. Use only these parameters: color, font_size (for Text), radius (for Circle)
        4. Use only Create, Write, FadeIn, FadeOut animations
        5. Return the entire corrected code section
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.1
            )
            
            fixed_section = response.choices[0].message.content.strip()
            
            # Clean the response
            if "```python" in fixed_section:
                fixed_section = re.search(r'```python\n(.*?)```', fixed_section, re.DOTALL).group(1)
            elif "```" in fixed_section:
                fixed_section = re.search(r'```\n(.*?)```', fixed_section, re.DOTALL).group(1)
            
            # Replace the context in the original code
            if error_line_match and len(context_lines) < 20:  # Only if context is small
                new_code = code.replace(context_code, fixed_section)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_code)
                return True
            
        except Exception as e:
            print(f"ERROR: LLM fix failed: {e}")
        
        return False
    
    def _fix_fallback_template(self, filepath: str, error_message: str) -> bool:
        """Fix Strategy 5: Use working template as last resort."""
        print(" Strategy 5: Fallback to working template")
        
        # Get topic from filepath
        topic = os.path.basename(filepath).replace('_final.py', '').replace('_', ' ').title()
        
        # Use simple working template
        fallback_code = f"""from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Title
        title = Text("{topic}", color=BLUE)
        self.play(Write(title))
        self.wait(2)
        
        # Clear title
        self.play(FadeOut(title))
        
        # Main concept
        concept = Text("Key Concepts", color=WHITE)
        self.play(FadeIn(concept))
        self.wait(2)
        
        # Simple shape
        shape = Circle(radius=2, color=YELLOW)
        shape.next_to(concept, DOWN)
        self.play(Create(shape))
        self.wait(2)
        
        # Conclusion
        conclusion = Text("Understanding {topic}", color=GREEN)
        conclusion.next_to(shape, DOWN)
        self.play(Write(conclusion))
        self.wait(3)
        
        # Final clear
        self.play(FadeOut(concept), FadeOut(shape), FadeOut(conclusion))
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fallback_code)
            print("SUCCESS: Applied fallback template")
            return True
        except Exception as e:
            print(f"ERROR: Could not write fallback: {e}")
            return False
    
    def run_manim_code(self, filepath: str) -> Tuple[bool, str, str]:
        """Run Manim code with better path handling."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find Scene class
            scene_match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', content)
            if not scene_match:
                return False, "", "No Scene class found in the code"
            
            scene_name = scene_match.group(1)
            
            # Run manim with proper path handling
            abs_filepath = os.path.abspath(filepath)
            parent_dir = os.path.dirname(os.path.dirname(abs_filepath))
            
            cmd = f'python -m manim "{abs_filepath}" {scene_name} -pql --disable_caching'
            print(f" Running: {cmd}")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=parent_dir,
                timeout=60  # 60 second timeout
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Compilation timed out"
        except Exception as e:
            return False, "", str(e)
    
    def create_animation(self, topic: str) -> Optional[str]:
        """Create animation using advanced shot-by-shot approach."""
        print(f"\nCreating professional animation for: '{topic}'")
        print("=" * 70)
        
        # Phase 1: Generate detailed content structure
        content = self.generate_detailed_content_yaml(topic)
        if not content:
            print("ERROR: Failed to generate content structure")
            return None
        
        # Save content for debugging
        content_path = os.path.join(self.content_dir, f"{topic.replace(' ', '_').lower()}_detailed.yaml")
        with open(content_path, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
        print(f"SUCCESS: Detailed content saved to: {content_path}")
        
        # Phase 2: Generate shot-based Manim code
        code = self.generate_shot_based_manim_code(content)
        if not code:
            print("ERROR: Failed to generate Manim code")
            return None
        
        # Clean code formatting
        if "```python" in code:
            code = re.search(r'```python\n(.*?)```', code, re.DOTALL).group(1)
        elif "```" in code:
            code = re.search(r'```\n(.*?)```', code, re.DOTALL).group(1)
        
        # Retry loop with focused error fixing
        filename = f"{topic.replace(' ', '_').lower()}_final.py"
        filepath = os.path.join(self.output_dir, filename)
        
        # Initial code generation - save first version
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f" Initial code saved to: {filepath}")
        
        for attempt in range(1, self.max_retries + 1):
            print(f"\n Compilation attempt {attempt}/{self.max_retries}")

            # Try to compile current version
            success, stdout, stderr = self.run_manim_code(filepath)

            if success:
                print("SUCCESS: Animation created successfully!")
                if stdout:
                    print("SUCCESS: Output:", stdout[-300:])  # Last 300 chars
                return filepath
            else:
                print(f"ERROR: Compilation failed (attempt {attempt}):")
                print("Error:", stderr[-500:])  # Last 500 chars

                if attempt < self.max_retries:
                    # Apply progressive fix strategy matching the attempt number
                    fix_success = self.fix_manim_code_progressive(filepath, stderr, attempt)
                    if fix_success:
                        print(" Fix applied, trying compilation again...")
                    else:
                        print("WARNING: Fix could not be applied, will try next strategy")
                else:
                    # Final fallback on last attempt, then one more immediate compile
                    print(" Applying final fallback template before last compile...")
                    if self._fix_fallback_template(filepath, stderr):
                        success2, stdout2, stderr2 = self.run_manim_code(filepath)
                        if success2:
                            print("SUCCESS: Animation created successfully after fallback!")
                            if stdout2:
                                print("SUCCESS: Output:", stdout2[-300:])
                            return filepath
                        else:
                            print("ERROR: Compilation still failed after fallback:")
                            print("Error:", stderr2[-500:])
                    break
        
        print(f"\nFAILED: Failed after {self.max_retries} attempts (including fallback)")
        print(f" Debug info saved in: {content_path}")
        print(f" Last code version: {filepath}")
        return None

def main():
    """Main function with improved workflow."""
    print(" Final Professional Manim Generator")
    print("=====================================")
    print("Advanced shot-by-shot timeline approach")
    print("Prevents overlapping • Professional quality • 3Blue1Brown style")
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n🔑 OpenAI API key needed")
        api_key = input("Enter your OpenAI API key: ")
    
    if not api_key:
        print("ERROR: API key required")
        return
    
    # Create generator
    generator = FinalManimGenerator(api_key)
    
    while True:
        print("\n" + "="*70)
        topic = input(" Enter topic for professional animation (or 'quit'): ")
        if topic.lower() == 'quit':
            break
        
        if topic.strip():
            result = generator.create_animation(topic)
            if result:
                print(f"\n🏆 SUCCESS! Professional animation created: {result}")
                print(" Check media/videos/ for the final MP4")
                print("📋 Content structure saved for future reference")
            else:
                print("\nFAILED: Animation creation failed")
                print(" Check generated files for debugging")
        else:
            print("WARNING: Please enter a valid topic")

if __name__ == "__main__":
    main()