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
        self.output_dir = "generated_animations"
        self.content_dir = "generated_content"
        self.max_retries = 5
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.content_dir, exist_ok=True)
        
        # Load Manim API reference
        self.manim_api = self._load_manim_api_reference()
    
    def _load_manim_api_reference(self) -> Dict[str, Any]:
        """Load the Manim API reference for accurate code generation."""
        try:
            with open('manim_api_reference.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print("⚠️ Manim API reference not found, using basic reference")
            return {
                "animations": {
                    "Create": {"note": "Use Create, not ShowCreation"},
                    "Write": {"for_objects": ["Text", "Tex"]},
                    "FadeIn": {"for_objects": ["any object"]},
                    "FadeOut": {"for_objects": ["any object"]}
                }
            }
    
    def generate_detailed_content_yaml(self, topic: str) -> Optional[Dict[Any, Any]]:
        """Generate detailed shot-by-shot content structure."""
        print(f"🎬 Generating detailed shot-by-shot content for: '{topic}'")
        
        # Load advanced schema as template
        try:
            with open('advanced_content_schema.yaml', 'r', encoding='utf-8') as f:
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
        
        1. **Timeline with precise shots:**
           - Each shot: start_time, end_time, scene_state
           - scene_state: "clean" (clear previous) or "build_on_previous"
           - NO overlapping visual elements
           
        2. **Element specifications:**
           - Exact position (center, top_left, bottom_right, etc.)
           - Layer (1=background, 2=main, 3=foreground)
           - Animation timing (entry_duration, stay_duration, exit_duration)
           
        3. **Object lifecycle:**
           - When each object is created
           - When it's transformed
           - When it's removed from scene
           
        4. **Educational flow:**
           - Introduce concept → Show visual → Explain → Clear → Next
           - Each concept gets its own clean shot
           - Build complexity step by step
           
        Create a comprehensive YAML structure for "{topic}" that prevents visual overlapping
        and creates a smooth, professional educational experience.
        
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
                return content_structure
            except yaml.YAMLError as e:
                print(f"❌ YAML parsing error: {e}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return None
    
    def generate_shot_based_manim_code(self, content: Dict[Any, Any]) -> str:
        """Generate Manim code with shot-by-shot structure and proper API usage."""
        print("🔧 Generating shot-based Manim code...")
        
        # Extract key info for focused prompt
        timeline = content.get('animation', {}).get('timeline', {})
        shots = timeline.get('shots', [])[:5]  # Limit to first 5 shots to stay under token limit
        topic = content.get('animation', {}).get('metadata', {}).get('topic', 'Topic')
        
        # Create focused content summary
        content_summary = {
            'topic': topic,
            'shots': shots,
            'technical_specs': content.get('technical_specs', {}),
            'positioning': self.manim_api.get('positioning', {})
        }
        
        prompt = f"""
        Generate clean, working Manim code using this shot-by-shot structure:

        Content: {yaml.dump(content_summary, default_flow_style=False)}
        
        MANIM API REQUIREMENTS (CRITICAL):
        
        1. **Correct Animation Names:**
           - Use Create (NOT ShowCreation) 
           - Use Write for text
           - Use FadeIn/FadeOut for appearance
           - Use GrowFromCenter/ShrinkToCenter for scaling
           
        2. **Proper Object Management:**
           - Create objects in one shot
           - Use them in that shot  
           - FadeOut or clear before next shot
           - NO overlapping elements
           
        3. **Single construct() method:**
           ```python
           from manim import *
           
           class EducationalScene(Scene):
               def construct(self):
                   # Shot 1: clean slate
                   # ... shot 1 code ...
                   self.play(FadeOut(*self.mobjects))  # Clear all
                   
                   # Shot 2: clean slate  
                   # ... shot 2 code ...
                   self.play(FadeOut(*self.mobjects))  # Clear all
           ```
           
        4. **Positioning System:**
           - center: ORIGIN
           - top: UP * 3
           - bottom: DOWN * 3
           - top_left: UP * 2 + LEFT * 4
           - etc.
           
        5. **Timing Control:**
           - Add run_time parameter: self.play(Write(text), run_time=2)
           - Add waits: self.wait(1)
           - Clear between sections: self.play(FadeOut(*self.mobjects))
           
        Generate COMPLETE working code that follows this shot structure exactly.
        Each shot should be a distinct code block with clear scene state management.
        
        Return ONLY the Python code.
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
            print(f"❌ Error generating Manim code: {e}")
            return None
    
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
    
    def fix_manim_code_focused(self, code: str, error_message: str) -> str:
        """Fix Manim code with focused context to avoid token limits."""
        print("🔧 Fixing code with focused context...")
        
        # Truncate to essential context
        context_code, truncated_error = self._truncate_error_context(code, error_message)
        
        # Get relevant API info
        api_notes = {
            "correct_animations": "Use Create (not ShowCreation), Write, FadeIn, FadeOut",
            "positioning": "UP*3, DOWN*3, LEFT*6, RIGHT*6, ORIGIN",
            "clearing": "self.play(FadeOut(*self.mobjects)) to clear scene"
        }
        
        prompt = f"""
        Fix this Manim code error:
        
        Error: {truncated_error}
        
        Code context:
        ```python
        {context_code}
        ```
        
        API Reference:
        {yaml.dump(api_notes, default_flow_style=False)}
        
        Common fixes:
        1. ShowCreation → Create
        2. Missing imports
        3. Wrong positioning syntax
        4. Missing scene clearing
        
        Return ONLY the corrected code section.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,  # Small focused fix
                temperature=0.2
            )
            
            fixed_code = response.choices[0].message.content.strip()
            
            # Clean formatting
            if "```python" in fixed_code:
                fixed_code = re.search(r'```python\n(.*?)```', fixed_code, re.DOTALL).group(1)
            elif "```" in fixed_code:
                fixed_code = re.search(r'```\n(.*?)```', fixed_code, re.DOTALL).group(1)
            
            # Apply fix to original code
            return self._apply_focused_fix(code, fixed_code, error_message)
            
        except Exception as e:
            print(f"❌ Error fixing code: {e}")
            return code
    
    def _apply_focused_fix(self, original_code: str, fix: str, error_message: str) -> str:
        """Apply a focused fix to the original code."""
        # Simple replacement strategy - replace problematic patterns
        common_fixes = [
            ("ShowCreation", "Create"),
            ("DrawBorderThenFill", "Create"), 
            ("self.play(Create(", "self.play(Create("),  # ensure proper Create usage
        ]
        
        fixed_code = original_code
        for old, new in common_fixes:
            fixed_code = fixed_code.replace(old, new)
        
        return fixed_code
    
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
            print(f"🎥 Running: {cmd}")
            
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
        print(f"\n🚀 Creating professional animation for: '{topic}'")
        print("=" * 70)
        
        # Phase 1: Generate detailed content structure
        content = self.generate_detailed_content_yaml(topic)
        if not content:
            print("❌ Failed to generate content structure")
            return None
        
        # Save content for debugging
        content_path = os.path.join(self.content_dir, f"{topic.replace(' ', '_').lower()}_detailed.yaml")
        with open(content_path, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
        print(f"✅ Detailed content saved to: {content_path}")
        
        # Phase 2: Generate shot-based Manim code
        code = self.generate_shot_based_manim_code(content)
        if not code:
            print("❌ Failed to generate Manim code")
            return None
        
        # Clean code formatting
        if "```python" in code:
            code = re.search(r'```python\n(.*?)```', code, re.DOTALL).group(1)
        elif "```" in code:
            code = re.search(r'```\n(.*?)```', code, re.DOTALL).group(1)
        
        # Retry loop with focused error fixing
        filename = f"{topic.replace(' ', '_').lower()}_final.py"
        filepath = os.path.join(self.output_dir, filename)
        
        for attempt in range(self.max_retries):
            print(f"\n🔄 Compilation attempt {attempt + 1}/{self.max_retries}")
            
            # Save current code
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"💾 Code saved to: {filepath}")
            
            # Try to compile
            success, stdout, stderr = self.run_manim_code(filepath)
            
            if success:
                print("🎉 Animation created successfully!")
                if stdout:
                    print("✅ Output:", stdout[-300:])  # Last 300 chars
                return filepath
            else:
                print(f"❌ Compilation failed (attempt {attempt + 1}):")
                print("Error:", stderr[-500:])  # Last 500 chars
                
                if attempt < self.max_retries - 1:
                    # Apply focused fix
                    code = self.fix_manim_code_focused(code, stderr)
        
        print(f"\n💔 Failed after {self.max_retries} attempts")
        print(f"🔍 Debug info saved in: {content_path}")
        print(f"📄 Last code version: {filepath}")
        return None

def main():
    """Main function with improved workflow."""
    print("🎬 Final Professional Manim Generator")
    print("=====================================")
    print("Advanced shot-by-shot timeline approach")
    print("Prevents overlapping • Professional quality • 3Blue1Brown style")
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n🔑 OpenAI API key needed")
        api_key = input("Enter your OpenAI API key: ")
    
    if not api_key:
        print("❌ API key required")
        return
    
    # Create generator
    generator = FinalManimGenerator(api_key)
    
    while True:
        print("\n" + "="*70)
        topic = input("🎯 Enter topic for professional animation (or 'quit'): ")
        if topic.lower() == 'quit':
            break
        
        if topic.strip():
            result = generator.create_animation(topic)
            if result:
                print(f"\n🏆 SUCCESS! Professional animation created: {result}")
                print("🎥 Check media/videos/ for the final MP4")
                print("📋 Content structure saved for future reference")
            else:
                print("\n💔 Animation creation failed")
                print("🔍 Check generated files for debugging")
        else:
            print("⚠️ Please enter a valid topic")

if __name__ == "__main__":
    main()