#!/usr/bin/env python3
"""
Enhanced Book-to-Video System with Full AI Pipeline

Complete autonomous tutorial video generation system with:
- AI agent for autonomous code generation and debugging
- Frame-by-frame video quality evaluation with Gemini 2.5 Flash-Lite
- Intelligent position mapping and layout management
- Smart content subdivision for optimal 10-minute segments
- Content reflow and scene continuity management

Usage Examples:
    # Generate video series for a specific section with 10-minute segments
    python enhanced_book_to_video.py --book "calculus" --section "1.1" --audience "high_school"
    
    # Generate entire chapter with autonomous agent
    python enhanced_book_to_video.py --book "physics" --chapter 2 --ai-agent
    
    # Interactive mode with enhanced features
    python enhanced_book_to_video.py --book "calculus" --interactive --enhanced
    
    # Generate from custom text content
    python enhanced_book_to_video.py --content "Your educational content here" --topic "Custom Topic"
    
    # Generate with quality evaluation
    python enhanced_book_to_video.py --book "calculus" --section "1.2" --quality-threshold 0.8
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.enhanced_orchestrator import EnhancedVideoOrchestrator, EnhancedBuildRequest

# Try to use LLM-enhanced book processor
try:
    from src.llm_book_adapter import LLMBasedBookProcessor as BookProcessor
    print("✅ Enhanced: Using LLM-powered book processor")
except ImportError:
    from src.book_processor import BookProcessor
    print("ℹ️ Enhanced: Using traditional book processor")


def setup_api_keys() -> tuple[str, Optional[str]]:
    """Setup API keys from environment variables"""
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not openai_key:
        print("ERROR: OPENAI_API_KEY environment variable is required")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    if not gemini_key:
        print("WARNING: GEMINI_API_KEY not found - video evaluation will use basic mode")
        print("For enhanced evaluation, set: export GEMINI_API_KEY='your-key-here'")
    
    return openai_key, gemini_key


def display_system_status(orchestrator: EnhancedVideoOrchestrator):
    """Display comprehensive system status"""
    print("\n" + "="*70)
    print("ENHANCED VIDEO GENERATION SYSTEM STATUS")
    print("="*70)
    
    status = orchestrator.get_system_status()
    
    for component, info in status.items():
        component_name = component.replace('_', ' ').title()
        availability = "✅ Available" if info['available'] else "❌ Unavailable"
        component_type = info.get('type', 'Standard')
        
        print(f"{component_name:25} {availability:15} ({component_type})")
    
    print("="*70)


def generate_video_series(orchestrator: EnhancedVideoOrchestrator, args) -> bool:
    """Generate video series based on arguments"""
    
    if args.content and args.topic:
        # Generate from custom content
        print(f"CONTENT: Generating from custom content")
        print(f"TOPIC: {args.topic}")
        
        request = EnhancedBuildRequest(
            topic=args.topic,
            content=args.content,
            audience=args.audience,
            target_duration=args.duration,
            subdivision_strategy=args.subdivision_strategy,
            enable_continuity=args.enable_continuity,
            enable_position_mapping=args.enable_position_mapping,
            enable_reflow=args.enable_reflow,
            quality_threshold=args.quality_threshold
        )
        
        result = orchestrator.create_video_series(request)
        
    elif args.book and args.chapter:
        # Generate entire chapter
        print(f"CHAPTER: Generating videos for {args.book} Chapter {args.chapter}")
        
        result = orchestrator.create_chapter_series(
            book_name=args.book,
            chapter_number=str(args.chapter),
            audience=args.audience
        )
        
    elif args.book and args.section:
        # Generate specific section using intelligent processing
        print(f"SECTION: Generating videos for {args.book} Section {args.section}")
        
        result = orchestrator.create_section_video(
            book_name=args.book,
            section_number=args.section,
            audience=args.audience
        )
            
    else:
        print("ERROR: Must specify either:")
        print("  - --book and --section")  
        print("  - --book and --chapter")
        print("  - --content and --topic")
        return False
    
    # Display results
    print("\n" + "="*70)
    print("GENERATION RESULTS")
    print("="*70)
    
    if result.success:
        print(f"✅ SUCCESS: Generated {len(result.videos_generated)} videos")
        print(f"⏱️  Processing time: {result.processing_time:.1f} seconds")
        
        if result.quality_scores:
            avg_quality = sum(result.quality_scores) / len(result.quality_scores)
            print(f"📊 Average quality score: {avg_quality:.2f}")
        
        print(f"📁 Videos saved to: output/enhanced/")
        
        # List generated videos
        for i, video_path in enumerate(result.videos_generated, 1):
            video_name = Path(video_path).name
            print(f"   {i}. {video_name}")
        
        # Display subdivision info
        if result.subdivision_info:
            subtopics = result.subdivision_info.get('subtopics', [])
            if len(subtopics) > 1:
                print(f"\n📹 Content subdivided into {len(subtopics)} optimal segments:")
                for i, subtopic in enumerate(subtopics, 1):
                    print(f"   {i}. {subtopic.title} ({subtopic.estimated_duration}min)")
        
        # Display agent performance
        if result.agent_results:
            successful_agents = sum(1 for ar in result.agent_results if ar.success)
            total_attempts = sum(ar.attempts_made for ar in result.agent_results)
            print(f"\n🤖 AI Agent Performance:")
            print(f"   Success rate: {successful_agents}/{len(result.agent_results)}")
            print(f"   Total debug attempts: {total_attempts}")
        
    else:
        print(f"❌ FAILED: {result.error_message}")
        
        if result.agent_results:
            print(f"\n🤖 Agent Results:")
            for i, agent_result in enumerate(result.agent_results, 1):
                status = "✅" if agent_result.success else "❌"
                print(f"   Video {i}: {status} ({agent_result.attempts_made} attempts)")
                if not agent_result.success:
                    print(f"      Error: {agent_result.error_message}")
    
    print("="*70)
    return result.success


def interactive_mode(orchestrator: EnhancedVideoOrchestrator, args):
    """Interactive mode for enhanced video generation"""
    print("\n🎬 ENHANCED INTERACTIVE VIDEO GENERATION")
    print("="*50)
    
    book_processor = BookProcessor()
    
    while True:
        print("\nOptions:")
        print("1. Generate from book section")
        print("2. Generate from book chapter") 
        print("3. Generate from custom content")
        print("4. Show available books")
        print("5. System status")
        print("6. Exit")
        
        try:
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == '1':
                book_name = input("Enter book name: ").strip()
                
                if book_name:
                    # Show available sections using intelligent processor
                    try:
                        print(f"\n📖 Loading '{book_name}' to show available sections...")
                        book_content = orchestrator._load_book_intelligently(book_name)
                        available_sections = orchestrator._list_available_sections(book_content)
                        
                        print(f"\n📋 Available sections in '{book_name}':")
                        for i, (num, title) in enumerate(available_sections[:15], 1):  # Show first 15
                            print(f"  {i:2d}. {num}: {title[:60]}{'...' if len(title) > 60 else ''}")
                        
                        if len(available_sections) > 15:
                            print(f"  ... and {len(available_sections) - 15} more sections")
                        
                        section_number = input(f"\nEnter section number: ").strip()
                        
                        if section_number:
                            temp_args = argparse.Namespace(**{
                                **vars(args),
                                'book': book_name,
                                'section': section_number,
                                'chapter': None,
                                'content': None,
                                'topic': None
                            })
                            generate_video_series(orchestrator, temp_args)
                    
                    except Exception as e:
                        print(f"Error loading book: {e}")
                        section_number = input("Enter section number anyway: ").strip()
                        if section_number:
                            temp_args = argparse.Namespace(**{
                                **vars(args),
                                'book': book_name,
                                'section': section_number,
                                'chapter': None,
                                'content': None,
                                'topic': None
                            })
                            generate_video_series(orchestrator, temp_args)
            
            elif choice == '2':
                book_name = input("Enter book name: ").strip()
                chapter_number = input("Enter chapter number: ").strip()
                
                if book_name and chapter_number:
                    temp_args = argparse.Namespace(**{
                        **vars(args),
                        'book': book_name,
                        'chapter': int(chapter_number),
                        'section': None,
                        'content': None,
                        'topic': None
                    })
                    generate_video_series(orchestrator, temp_args)
            
            elif choice == '3':
                topic = input("Enter topic title: ").strip()
                print("Enter content (press Ctrl+D or Ctrl+Z when done):")
                
                content_lines = []
                try:
                    while True:
                        line = input()
                        content_lines.append(line)
                except EOFError:
                    pass
                
                content = '\n'.join(content_lines).strip()
                
                if topic and content:
                    temp_args = argparse.Namespace(**{
                        **vars(args),
                        'book': None,
                        'section': None,
                        'chapter': None,
                        'content': content,
                        'topic': topic
                    })
                    generate_video_series(orchestrator, temp_args)
            
            elif choice == '4':
                print("\n📚 Available Books:")
                books = book_processor.list_available_books()
                for book in books:
                    print(f"   - {book}")
            
            elif choice == '5':
                display_system_status(orchestrator)
            
            elif choice == '6':
                print("Goodbye! 👋")
                break
            
            else:
                print("Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Book-to-Video Generation System with Full AI Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Content selection
    content_group = parser.add_mutually_exclusive_group(required=False)
    content_group.add_argument('--book', type=str,
                              help='Book name to process')
    
    parser.add_argument('--section', type=str,
                       help='Specific section number (e.g., 1.1)')
    parser.add_argument('--chapter', type=int,
                       help='Chapter number to process entirely')
    
    content_group.add_argument('--content', type=str,
                              help='Custom educational content text')
    parser.add_argument('--topic', type=str,
                       help='Topic title (required with --content)')
    
    # Generation options
    parser.add_argument('--audience', type=str, default='undergraduate',
                       choices=['elementary', 'high_school', 'undergraduate', 'graduate'],
                       help='Target audience level (default: undergraduate)')
    parser.add_argument('--duration', type=int, default=10,
                       help='Target duration per video in minutes (default: 10)')
    parser.add_argument('--subdivision-strategy', type=str, default='optimal_10min',
                       choices=['auto', 'by_type', 'by_length', 'by_concept', 'optimal_10min'],
                       help='Content subdivision strategy (default: optimal_10min)')
    
    # Enhanced features
    parser.add_argument('--quality-threshold', type=float, default=0.8,
                       help='Minimum quality threshold (0.0-1.0, default: 0.8)')
    parser.add_argument('--enable-continuity', action='store_true', default=True,
                       help='Enable scene continuity management')
    parser.add_argument('--enable-position-mapping', action='store_true', default=True,
                       help='Enable intelligent position mapping')
    parser.add_argument('--enable-reflow', action='store_true', default=True,
                       help='Enable content reflow system')
    
    # Interface options
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--enhanced', action='store_true', default=True,
                       help='Use enhanced features (default: True)')
    parser.add_argument('--status', action='store_true',
                       help='Show system status and exit')
    
    # List operations
    parser.add_argument('--list-books', action='store_true',
                       help='List available books')
    
    args = parser.parse_args()
    
    # Setup API keys
    openai_key, gemini_key = setup_api_keys()
    
    # Initialize enhanced orchestrator
    print("🚀 Initializing Enhanced Video Generation System...")
    orchestrator = EnhancedVideoOrchestrator(openai_key, gemini_key)
    
    # Handle list operations
    if args.list_books:
        print("\n📚 Available Books:")
        book_processor = BookProcessor()
        books = book_processor.list_available_books()
        for book in books:
            print(f"   - {book}")
        return
    
    # Show status if requested
    if args.status:
        display_system_status(orchestrator)
        return
    
    # Interactive mode
    if args.interactive:
        interactive_mode(orchestrator, args)
        return
    
    # Validate required arguments for non-interactive mode
    if not any([
        args.book and (args.section or args.chapter),
        args.content and args.topic
    ]):
        print("ERROR: For non-interactive mode, specify either:")
        print("  - --book with --section or --chapter")
        print("  - --content with --topic")
        print("Use --interactive for guided mode")
        sys.exit(1)
    
    # Show system status
    display_system_status(orchestrator)
    
    # Generate video series
    success = generate_video_series(orchestrator, args)
    
    if success:
        print(f"\n🎉 Enhanced video generation completed successfully!")
        print(f"📁 Check the output/enhanced/ directory for your videos")
    else:
        print(f"\n❌ Enhanced video generation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()