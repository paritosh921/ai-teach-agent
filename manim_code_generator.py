import os
import re
import subprocess
import sys
from typing import Optional, Tuple
import openai
from openai import OpenAI

class ManimCodeGenerator:
    def __init__(self, api_key: str):
        """Initialize the Manim code generator with OpenAI API key."""
        self.client = OpenAI(api_key=api_key)
        self.output_dir = "generated_animations"
        self.max_retries = 5
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_manim_code(self, topic: str) -> str:
        """Generate Manim code for a given topic."""
        prompt = f"""
        Create a complete Manim animation script for the topic: "{topic}"
        
        Requirements:
        1. Write a complete Python script that can run with Manim
        2. Include proper imports (from manim import *)
        3. Create a Scene class that inherits from Scene
        4. Use appropriate Manim objects and animations
        5. Make it educational and visually appealing like 3Blue1Brown style
        6. Include comments explaining what each part does
        7. The animation should be between 30-60 seconds long
        8. Use high-quality mathematical visualization techniques
        
        Return ONLY the Python code, no additional text or explanations.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating code: {e}")
            return None
    
    def save_code_to_file(self, code: str, filename: str) -> str:
        """Save generated code to a file."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        return filepath
    
    def run_manim_code(self, filepath: str) -> Tuple[bool, str, str]:
        """Run the Manim code and return success status, stdout, and stderr."""
        try:
            # Extract scene class name from the file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            scene_match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', content)
            if not scene_match:
                return False, "", "No Scene class found in the code"
            
            scene_name = scene_match.group(1)
            
            # Run manim command
            cmd = f'python -m manim "{filepath}" {scene_name} -pql'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.output_dir
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except Exception as e:
            return False, "", str(e)
    
    def fix_code_with_llm(self, code: str, error_message: str) -> str:
        """Use LLM to fix the code based on error message."""
        prompt = f"""
        The following Manim code has an error. Please fix it and return the corrected code.
        
        Original code:
        ```python
        {code}
        ```
        
        Error message:
        {error_message}
        
        Please:
        1. Analyze the error and identify the issue
        2. Fix the code while maintaining its educational purpose
        3. Ensure all imports are correct
        4. Make sure the Scene class is properly defined
        5. Return ONLY the corrected Python code, no explanations
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error fixing code: {e}")
            return code
    
    def create_animation(self, topic: str) -> Optional[str]:
        """Create a Manim animation for the given topic with auto-fixing."""
        print(f"Generating Manim animation for topic: '{topic}'")
        
        # Generate initial code
        code = self.generate_manim_code(topic)
        if not code:
            print("Failed to generate initial code")
            return None
        
        # Clean the code (remove markdown formatting if present)
        if "```python" in code:
            code = re.search(r'```python\n(.*?)```', code, re.DOTALL).group(1)
        elif "```" in code:
            code = re.search(r'```\n(.*?)```', code, re.DOTALL).group(1)
        
        filename = f"{topic.replace(' ', '_').lower()}_animation.py"
        retry_count = 0
        
        while retry_count < self.max_retries:
            print(f"Attempt {retry_count + 1}/{self.max_retries}")
            
            # Save current version of code
            filepath = self.save_code_to_file(code, filename)
            print(f"Code saved to: {filepath}")
            
            # Try to run the code
            success, stdout, stderr = self.run_manim_code(filepath)
            
            if success:
                print("Animation created successfully!")
                print("Output:", stdout)
                return filepath
            else:
                print(f"Error occurred: {stderr}")
                
                if retry_count < self.max_retries - 1:
                    print("Attempting to fix the code...")
                    # Try to fix the code using LLM
                    fixed_code = self.fix_code_with_llm(code, stderr)
                    
                    # Clean the fixed code
                    if "```python" in fixed_code:
                        fixed_code = re.search(r'```python\n(.*?)```', fixed_code, re.DOTALL).group(1)
                    elif "```" in fixed_code:
                        fixed_code = re.search(r'```\n(.*?)```', fixed_code, re.DOTALL).group(1)
                    
                    code = fixed_code
                
                retry_count += 1
        
        print(f"Failed to create working animation after {self.max_retries} attempts")
        return None

def main():
    """Main function to run the Manim code generator."""
    # Get OpenAI API key from environment or user input
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("Please enter your OpenAI API key: ")
    
    if not api_key:
        print("API key is required to proceed.")
        return
    
    # Create generator instance
    generator = ManimCodeGenerator(api_key)
    
    while True:
        topic = input("\nEnter a topic for the Manim animation (or 'quit' to exit): ")
        if topic.lower() == 'quit':
            break
        
        if topic.strip():
            result = generator.create_animation(topic)
            if result:
                print(f"Animation file created at: {result}")
            else:
                print("Failed to create animation")
        else:
            print("Please enter a valid topic")

if __name__ == "__main__":
    main()