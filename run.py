#!/usr/bin/env python3
"""
Manim LLM Generator - Clean Entry Point

Professional educational animation generator using LLM and Manim.
Creates 3Blue1Brown-style animations with shot-by-shot precision.
"""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generator import FinalManimGenerator

def main():
    """Clean entry point for the Manim LLM Generator."""
    print("Manim LLM Generator")
    print("=====================")
    print("Professional educational animations with AI")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('src/generator.py'):
        print("ERROR: Please run this script from the project root directory")
        print("   Current directory:", os.getcwd())
        return 1
    
    # Get OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("OpenAI API Key Required")
        api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("ERROR: OpenAI API key is required to proceed")
        return 1
    
    # Get Gemini API key (optional for video quality evaluation)
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("\nGemini API Key (Optional)")
        print("For video quality evaluation with Gemini 2.5 Flash-Lite")
        gemini_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
        if gemini_key:
            print("SUCCESS: Video quality evaluation enabled!")
        else:
            print("WARNING: Proceeding without video quality evaluation")
            gemini_key = None
    
    # Create generator instance
    try:
        generator = FinalManimGenerator(api_key, gemini_key)
    except Exception as e:
        print(f"ERROR: Failed to initialize generator: {e}")
        return 1
    
    # Main interaction loop
    print("\nReady to create animations!")
    print("Type 'quit' to exit, or enter a topic to generate an animation.")
    print()
    
    while True:
        try:
            topic = input("Topic: ").strip()
            
            if topic.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not topic:
                print("WARNING: Please enter a topic")
                continue
            
            # Generate animation
            print(f"\nCreating animation for: '{topic}'")
            print("-" * 50)
            
            result = generator.create_animation(topic)
            
            if result:
                print(f"\nSUCCESS: Animation created: {result}")
                print("Check the output/animations/ directory")
                print("Content structure saved in output/content/")
            else:
                print("\nERROR: Failed to create animation")
                print("Check output files for debugging information")
            
            print("\n" + "=" * 50)
            
        except KeyboardInterrupt:
            print("\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\nERROR: Unexpected error: {e}")
            print("You can try again with a different topic")

if __name__ == "__main__":
    sys.exit(main())