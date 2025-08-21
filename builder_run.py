#!/usr/bin/env python3
"""
Builder LLM Entry Point - Clean Interface for Deterministic Video Generation

This is the main entry point for the Builder LLM system that creates professional
educational animations with strict layout safety and 3Blue1Brown quality.
"""

import os
import sys
import argparse
from typing import Optional

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.orchestrator import create_orchestrator, OrchestrationConfig
from src.builder_llm import BuildRequest


def main():
    """Main entry point for Builder LLM video generation"""
    parser = argparse.ArgumentParser(
        description="Builder LLM - Professional Educational Video Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --topic "Integration Basics" --audience "undergraduate"
  %(prog)s --interactive
  %(prog)s --topic "Chemical Bonding" --voice "professional" --theme "3blue1brown"

The Builder LLM system follows a strict workflow:
1. OUTLINE → hierarchical breakdown of the topic
2. YAML → structured video specification with layout safety
3. CODE → Manim Python code with collision avoidance
4. COMPILE → 480p compilation with error repair
5. EVALUATE → Gemini visual quality assessment (optional)
6. PROMOTE → Final 1080p compilation

All generated content follows non-negotiable layout rules:
- Safe margins: ≥ 6% on all sides
- No overlaps between visual elements
- Text legibility: ≥ 24px equivalent at 480p
- Deterministic positioning and timing
        """)
    
    # Core arguments
    parser.add_argument('--topic', '-t', type=str, 
                       help='Topic for the educational video')
    parser.add_argument('--audience', '-a', type=str, default='general',
                       help='Target audience (default: general)')
    parser.add_argument('--voice', type=str, default='professional',
                       choices=['professional', 'casual', 'academic'],
                       help='Narration voice style (default: professional)')
    parser.add_argument('--pace-wpm', type=int, default=150,
                       help='Speaking pace in words per minute (default: 150)')
    parser.add_argument('--theme', type=str, default='3blue1brown',
                       choices=['3blue1brown', 'minimal', 'academic'],
                       help='Visual theme (default: 3blue1brown)')
    
    # Mode selection
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--batch', type=str,
                       help='Process batch of topics from file')
    
    # Configuration
    parser.add_argument('--max-repair-attempts', type=int, default=3,
                       help='Maximum code repair attempts (default: 3)')
    parser.add_argument('--max-evaluation-iterations', type=int, default=2,
                       help='Maximum visual evaluation iterations (default: 2)')
    parser.add_argument('--disable-evaluation', action='store_true',
                       help='Disable Gemini video quality evaluation')
    parser.add_argument('--output-dir', type=str, default='output/builder',
                       help='Output directory for generated files')
    
    # API keys
    parser.add_argument('--openai-key', type=str,
                       help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--gemini-key', type=str,
                       help='Gemini API key (or set GEMINI_API_KEY env var)')
    
    # Debug options
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output and validation')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate code without compilation')
    
    args = parser.parse_args()
    
    # Display banner
    print_banner()
    
    # Get API keys
    openai_key = get_api_key('OpenAI', args.openai_key, 'OPENAI_API_KEY', required=True)
    gemini_key = get_api_key('Gemini', args.gemini_key, 'GEMINI_API_KEY', required=False)
    
    if args.disable_evaluation:
        gemini_key = None
    
    # Create orchestration configuration
    config = OrchestrationConfig(
        max_repair_attempts=args.max_repair_attempts,
        max_evaluation_iterations=args.max_evaluation_iterations,
        enable_quality_evaluation=gemini_key is not None,
        output_dir=args.output_dir
    )
    
    # Initialize orchestrator
    try:
        orchestrator = create_orchestrator(openai_key, gemini_key, config)
        print("OK: Builder LLM system initialized successfully")
        
        if config.enable_quality_evaluation:
            print("CLAPPER: Video quality evaluation enabled with Gemini 2.5 Flash-Lite")
        else:
            print("LIST: Video quality evaluation disabled")
            
    except Exception as e:
        print(f"NO: Failed to initialize Builder LLM system: {e}")
        return 1
    
    # Execute based on mode
    if args.interactive:
        return run_interactive_mode(orchestrator)
    elif args.batch:
        return run_batch_mode(orchestrator, args.batch)
    elif args.topic:
        return run_single_video(orchestrator, args)
    else:
        print("NO: Error: Must specify --topic, --interactive, or --batch mode")
        parser.print_help()
        return 1


def print_banner():
    """Print the Builder LLM banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                            CLAPPER: BUILDER LLM                                   ║
║                    Deterministic Educational Video Generator                 ║
║                                                                              ║
║  MANIM-AUTOPILOT: Clean, Overlap-Free, Professional Quality                 ║
║  • Strict layout safety with ≥6% margins                                    ║
║  • Zero visual overlaps with automatic collision resolution                  ║
║  • Text legibility guaranteed at 480p (≥24px)                               ║
║  • 3Blue1Brown professional standards                                       ║
║  • Gemini 2.5 Flash-Lite visual evaluation                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def get_api_key(service_name: str, arg_value: Optional[str], 
               env_var: str, required: bool = True) -> Optional[str]:
    """Get API key from argument or environment"""
    key = arg_value or os.getenv(env_var)
    
    if not key and required:
        print(f"\n🔑 {service_name} API key required")
        key = input(f"Enter your {service_name} API key: ").strip()
        
        if not key:
            print(f"NO: Error: {service_name} API key is required")
            sys.exit(1)
    
    if key:
        print(f"OK: {service_name} API key configured")
    elif not required:
        print(f"WARN: {service_name} API key not provided (optional)")
    
    return key


def run_single_video(orchestrator, args) -> int:
    """Generate a single video from command line arguments"""
    print(f"\nTARGET: Generating video for topic: '{args.topic}'")
    print("=" * 60)
    
    # Create build request
    request = BuildRequest(
        topic=args.topic,
        audience=args.audience,
        voice=args.voice,
        pace_wpm=args.pace_wpm,
        theme=args.theme
    )
    
    # Execute workflow
    try:
        result = orchestrator.create_video(request)
        
        if result.success:
            print(f"\nPARTY: SUCCESS: Video generated successfully!")
            print(f"CLAPPER: Video file: {result.video_path}")
            print(f"CHART: Attempts: {result.attempts}")
            
            if result.evaluation_reports:
                print(f"SEARCH: Evaluations: {len(result.evaluation_reports)} quality checks performed")
            
            return 0
        else:
            print(f"\nBOOM: FAILED: {result.error_message}")
            print("LIST: Check output directory for debugging information")
            return 1
            
    except KeyboardInterrupt:
        print("\nWARN: Generation interrupted by user")
        return 1
    except Exception as e:
        print(f"\nBOOM: Unexpected error: {e}")
        return 1


def run_interactive_mode(orchestrator) -> int:
    """Run in interactive mode for multiple video generation"""
    print("\nCYCLE: Interactive Mode - Generate Multiple Videos")
    print("=" * 60)
    print("Commands:")
    print("  • Enter a topic to generate a video")
    print("  • 'status' - Show system status")  
    print("  • 'quit' or 'exit' - Exit interactive mode")
    print("  • 'help' - Show this help")
    print()
    
    video_count = 0
    success_count = 0
    
    try:
        while True:
            # Get user input
            try:
                user_input = input("Builder LLM> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'help':
                print_interactive_help()
                continue
            elif user_input.lower() == 'status':
                print_status(orchestrator, video_count, success_count)
                continue
            
            # Treat input as topic
            topic = user_input
            
            print(f"\nCLAPPER: Generating video for: '{topic}'")
            print("-" * 40)
            
            # Create request with default settings
            request = BuildRequest(
                topic=topic,
                audience='general',
                voice='professional',
                pace_wpm=150,
                theme='3blue1brown'
            )
            
            try:
                result = orchestrator.create_video(request)
                video_count += 1
                
                if result.success:
                    success_count += 1
                    print(f"OK: Success! Video: {result.video_path}")
                else:
                    print(f"NO: Failed: {result.error_message}")
                    
            except Exception as e:
                print(f"BOOM: Error: {e}")
                video_count += 1
            
            print()
        
    except KeyboardInterrupt:
        print("\nWARN: Interactive mode interrupted")
    
    # Final summary
    print(f"\nCHART: Session Summary:")
    print(f"   Videos attempted: {video_count}")
    print(f"   Successful: {success_count}")
    print(f"   Success rate: {(success_count/video_count*100):.1f}%" if video_count > 0 else "   Success rate: N/A")
    print("\n👋 Goodbye!")
    
    return 0


def run_batch_mode(orchestrator, batch_file: str) -> int:
    """Process a batch of topics from file"""
    print(f"\nLIST: Batch Mode - Processing topics from: {batch_file}")
    
    # Read topics from file
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            topics = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"NO: Error: Batch file not found: {batch_file}")
        return 1
    except Exception as e:
        print(f"NO: Error reading batch file: {e}")
        return 1
    
    if not topics:
        print("NO: Error: No topics found in batch file")
        return 1
    
    print(f"PAGE: Found {len(topics)} topics to process")
    print("=" * 60)
    
    # Process each topic
    results = []
    for i, topic in enumerate(topics, 1):
        print(f"\nCLAPPER: [{i}/{len(topics)}] Generating: '{topic}'")
        print("-" * 40)
        
        request = BuildRequest(
            topic=topic,
            audience='general',
            voice='professional', 
            pace_wpm=150,
            theme='3blue1brown'
        )
        
        try:
            result = orchestrator.create_video(request)
            results.append((topic, result.success, result.video_path, result.error_message))
            
            if result.success:
                print(f"OK: Success: {result.video_path}")
            else:
                print(f"NO: Failed: {result.error_message}")
                
        except Exception as e:
            print(f"BOOM: Error: {e}")
            results.append((topic, False, None, str(e)))
    
    # Summary report
    successful = sum(1 for _, success, _, _ in results if success)
    
    print(f"\nCHART: Batch Processing Complete")
    print("=" * 60)
    print(f"Total topics: {len(topics)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(topics) - successful}")
    print(f"Success rate: {(successful/len(topics)*100):.1f}%")
    
    # Detailed results
    print(f"\nLIST: Detailed Results:")
    for topic, success, video_path, error in results:
        status = "OK:" if success else "NO:"
        print(f"  {status} {topic}")
        if success and video_path:
            print(f"      → {video_path}")
        elif not success and error:
            print(f"      → {error}")
    
    return 0 if successful == len(topics) else 1


def print_interactive_help():
    """Print help for interactive mode"""
    help_text = """
TOOL: Interactive Mode Commands:

  Topic Generation:
    • Simply type any topic to generate a video
    • Example: "Introduction to Calculus"
    • Example: "Quantum Mechanics Basics"
    • Example: "Chemical Bonding"

  System Commands:
    • status     - Show system status and statistics
    • help       - Show this help message
    • quit/exit  - Exit interactive mode

  Notes:
    • All videos use default settings (professional voice, 3Blue1Brown theme)
    • Generated videos are saved to output/builder/
    • Check console output for detailed progress information
    • Press Ctrl+C to interrupt current generation
"""
    print(help_text)


def print_status(orchestrator, video_count: int, success_count: int):
    """Print current system status"""
    status = orchestrator.get_status()
    
    print(f"\nCHART: Builder LLM System Status")
    print("=" * 40)
    print(f"Current state: {status['state']}")
    print(f"Session videos: {video_count}")
    print(f"Session successes: {success_count}")
    
    if status['current_build']:
        build_info = status['current_build']
        print(f"\nCurrent Build:")
        print(f"  Success: {build_info['success']}")
        print(f"  Attempts: {build_info['attempts']}")
        if build_info['video_path']:
            print(f"  Video: {build_info['video_path']}")
        if build_info['error_message']:
            print(f"  Error: {build_info['error_message']}")
    
    print(f"\nConfiguration:")
    config_info = status['config']
    print(f"  Max repair attempts: {config_info['max_repair_attempts']}")
    print(f"  Max evaluation iterations: {config_info['max_evaluation_iterations']}")
    print(f"  Evaluation enabled: {config_info['evaluation_enabled']}")


if __name__ == "__main__":
    sys.exit(main())