import os
import re
import subprocess
import sys
import yaml
from typing import Optional, Tuple, Dict, Any
import openai
from openai import OpenAI

class ImprovedManimGenerator:
    def __init__(self, api_key: str):
        """Initialize the improved Manim generator with two-phase approach."""
        self.client = OpenAI(api_key=api_key)
        self.output_dir = "generated_animations"
        self.content_dir = "generated_content"
        self.max_retries = 5
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.content_dir, exist_ok=True)
    
    def generate_content_yaml(self, topic: str) -> Optional[Dict[Any, Any]]:
        """Phase 1: Generate structured educational content in YAML format."""
        print(f"🧠 Generating educational content structure for: '{topic}'")
        
        prompt = f"""
        Create a comprehensive educational content structure for the topic: "{topic}"
        
        You are an expert educational content creator like 3Blue1Brown. Your job is to:
        1. Break down the topic into clear, logical learning sequences
        2. Identify key concepts that need visual explanation
        3. Plan engaging visual metaphors and animations
        4. Structure the content for maximum learning impact
        5. Include all mathematical formulas and visual elements needed
        
        Return a YAML structure following this format:

        animation:
          metadata:
            topic: "{topic}"
            duration: 60
            difficulty_level: "beginner"  # or intermediate/advanced
            subject_area: "mathematics"   # or physics/computer_science etc.
          
          introduction:
            title: "Clear, engaging title"
            hook: "Opening that grabs attention"
            learning_objectives: 
              - "What viewers will learn - point 1"
              - "What viewers will learn - point 2"
          
          content_sections:
            - section_id: "intro"
              title: "Section title"
              duration: 15
              concepts: ["key concept 1", "key concept 2"]
              visuals:
                - type: "text"  # text, formula, graph, diagram
                  content: "What to display"
                  animation_type: "write"  # write, fade_in, transform
              narration: "Explanation text to show"
            
            # Add 3-4 more sections that build on each other
            
          mathematical_elements:
            formulas: 
              - "\\\\int_a^b f(x) dx"  # LaTeX formulas
            graphs:
              - function: "x**2"
                domain: [-3, 3]
                color: "BLUE"
                
          visual_metaphors:
            - concept: "abstract concept"
              metaphor: "concrete visual representation"
              implementation: "how to show in animation"
              
          conclusion:
            summary_points: ["key point 1", "key point 2"]
            key_takeaway: "Main lesson learned"

        Make this educational, engaging, and mathematically accurate like 3Blue1Brown videos.
        Focus on building understanding step by step.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.7
            )
            
            yaml_content = response.choices[0].message.content.strip()
            
            # Clean YAML content (remove markdown formatting)
            if "```yaml" in yaml_content:
                yaml_content = re.search(r'```yaml\n(.*?)```', yaml_content, re.DOTALL).group(1)
            elif "```" in yaml_content:
                yaml_content = re.search(r'```\n(.*?)```', yaml_content, re.DOTALL).group(1)
            
            # Parse YAML
            content_structure = yaml.safe_load(yaml_content)
            return content_structure
            
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return None
    
    def save_content_yaml(self, content: Dict[Any, Any], topic: str) -> str:
        """Save the content structure to a YAML file."""
        filename = f"{topic.replace(' ', '_').lower()}_content.yaml"
        filepath = os.path.join(self.content_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
        
        return filepath
    
    def generate_manim_from_yaml(self, content: Dict[Any, Any]) -> str:
        """Phase 2: Generate Manim code based on YAML content structure."""
        print("🎬 Generating Manim code from content structure...")
        
        # Convert content to JSON string for the prompt
        import json
        content_json = json.dumps(content, indent=2, ensure_ascii=False)
        
        prompt = f"""
        Generate complete, working Manim code based on this educational content structure:

        {content_json}

        Requirements:
        1. Create a complete Python script that runs with Manim
        2. Follow the content structure exactly - implement each section in order
        3. Use proper Manim imports: from manim import *
        4. Create ONE Scene class that inherits from Scene
        5. Implement all visuals specified in the YAML
        6. Use appropriate Manim objects for each visual type:
           - text -> Text() or Tex()
           - formula -> Tex() with LaTeX
           - graph -> FunctionGraph() or NumberLine()
           - diagram -> geometric shapes (Rectangle, Circle, etc.)
        7. Follow the timing specified in the content structure
        8. Make animations smooth and professional like 3Blue1Brown
        9. Use proper colors and styling
        10. Include all mathematical elements specified
        
        Focus ONLY on implementing the technical Manim code correctly.
        Don't change the educational content - just implement it perfectly.
        
        Return ONLY the Python code, no explanations or markdown formatting.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.3  # Lower temperature for more precise code
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error generating Manim code: {e}")
            return None
    
    def run_manim_code(self, filepath: str) -> Tuple[bool, str, str]:
        """Run Manim code and return success status with output."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find Scene class
            scene_match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', content)
            if not scene_match:
                return False, "", "No Scene class found in the code"
            
            scene_name = scene_match.group(1)
            
            # Use absolute path and run from parent directory
            abs_filepath = os.path.abspath(filepath)
            parent_dir = os.path.dirname(os.path.dirname(abs_filepath))
            
            # Run manim command with proper path handling
            cmd = f'python -m manim "{abs_filepath}" {scene_name} -pql'
            print(f"🎥 Running: {cmd}")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=parent_dir
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except Exception as e:
            return False, "", str(e)
    
    def fix_manim_code(self, code: str, content: Dict[Any, Any], error_message: str) -> str:
        """Fix Manim code using both the original content and error context."""
        print("🔧 Attempting to fix code based on error...")
        
        import json
        content_json = json.dumps(content, indent=2, ensure_ascii=False)
        
        prompt = f"""
        Fix this Manim code based on the error message and original content structure.

        Original Content Structure:
        {content_json}

        Current Code:
        ```python
        {code}
        ```

        Error Message:
        {error_message}

        Instructions:
        1. Analyze the error carefully
        2. Fix the technical Manim issues while preserving the educational content
        3. Ensure all imports are correct
        4. Make sure the Scene class is properly defined
        5. Fix any syntax or Manim API issues
        6. Keep the same educational flow as specified in the content structure
        7. Use only valid Manim objects and methods
        
        Common Manim fixes:
        - Use ShowCreation instead of Write for geometric objects
        - Use Transform, ReplacementTransform for object changes
        - Proper positioning with .next_to(), .to_edge(), .move_to()
        - Correct color constants (BLUE, RED, etc.)
        
        Return ONLY the corrected Python code.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.2
            )
            
            fixed_code = response.choices[0].message.content.strip()
            
            # Clean the fixed code
            if "```python" in fixed_code:
                fixed_code = re.search(r'```python\n(.*?)```', fixed_code, re.DOTALL).group(1)
            elif "```" in fixed_code:
                fixed_code = re.search(r'```\n(.*?)```', fixed_code, re.DOTALL).group(1)
            
            return fixed_code
            
        except Exception as e:
            print(f"❌ Error fixing code: {e}")
            return code
    
    def create_animation(self, topic: str) -> Optional[str]:
        """Main method: Create animation using two-phase approach."""
        print(f"\n🚀 Starting two-phase animation creation for: '{topic}'")
        print("=" * 60)
        
        # Phase 1: Generate content structure
        content = self.generate_content_yaml(topic)
        if not content:
            print("❌ Failed to generate content structure")
            return None
        
        # Save content for debugging/editing
        content_path = self.save_content_yaml(content, topic)
        print(f"✅ Content structure saved to: {content_path}")
        
        # Phase 2: Generate Manim code
        code = self.generate_manim_from_yaml(content)
        if not code:
            print("❌ Failed to generate Manim code")
            return None
        
        # Clean code formatting
        if "```python" in code:
            code = re.search(r'```python\n(.*?)```', code, re.DOTALL).group(1)
        elif "```" in code:
            code = re.search(r'```\n(.*?)```', code, re.DOTALL).group(1)
        
        # Retry loop for compilation
        filename = f"{topic.replace(' ', '_').lower()}_animation.py"
        retry_count = 0
        
        while retry_count < self.max_retries:
            print(f"\n🔄 Compilation attempt {retry_count + 1}/{self.max_retries}")
            
            # Save current code
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            print(f"💾 Code saved to: {filepath}")
            
            # Try to compile
            success, stdout, stderr = self.run_manim_code(filepath)
            
            if success:
                print("🎉 Animation created successfully!")
                if stdout:
                    print("Output:", stdout[-500:])  # Show last 500 chars
                return filepath
            else:
                print(f"❌ Compilation failed:")
                print("Error:", stderr[-1000:])  # Show last 1000 chars
                
                if retry_count < self.max_retries - 1:
                    # Fix the code
                    fixed_code = self.fix_manim_code(code, content, stderr)
                    code = fixed_code
                
                retry_count += 1
        
        print(f"\n💔 Failed to create working animation after {self.max_retries} attempts")
        print(f"🔍 Debug info saved in: {content_path}")
        return None

def install_ffmpeg():
    """Helper function to install ffmpeg if needed."""
    try:
        import subprocess
        # Check if ffmpeg is available
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg is already installed")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️ ffmpeg not found. Please install it:")
    print("1. Download from: https://ffmpeg.org/download.html")
    print("2. Add to PATH environment variable")
    print("3. Or use conda: conda install ffmpeg")
    print("4. Or use chocolatey: choco install ffmpeg")
    return False

def main():
    """Main function with improved workflow."""
    print("🎨 Improved LLM-Based Manim Generator")
    print("=====================================")
    print("Two-phase approach: Content Structure → Manim Code → Video")
    
    # Check ffmpeg
    if not install_ffmpeg():
        print("\n⚠️ Warning: ffmpeg not found. Videos may not render properly.")
        input("Press Enter to continue anyway...")
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n🔑 OpenAI API key needed")
        api_key = input("Please enter your OpenAI API key: ")
    
    if not api_key:
        print("❌ API key required")
        return
    
    # Create generator
    generator = ImprovedManimGenerator(api_key)
    
    while True:
        print("\n" + "="*60)
        topic = input("🎯 Enter topic for animation (or 'quit'): ")
        if topic.lower() == 'quit':
            break
        
        if topic.strip():
            result = generator.create_animation(topic)
            if result:
                print(f"\n🎊 SUCCESS! Animation created at: {result}")
                print("🎥 Look for the MP4 file in the media/videos folder")
            else:
                print("💔 Failed to create animation")
        else:
            print("⚠️ Please enter a valid topic")

if __name__ == "__main__":
    main()