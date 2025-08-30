#!/usr/bin/env python3
"""
Unified OpenAI-Based Video Generation Pipeline

This is the single entry point for generating educational videos from books.
All LLM operations use OpenAI API exclusively for consistent, reliable results.

Key Features:
- Processes any book format from books/ folder
- Automatically chunks large content into 10-minute video segments  
- Uses OpenAI for content analysis, structuring, and Manim code generation
- Built-in auto-debugging with bounded retries
- Generates professional 3Blue1Brown-style educational videos
- Handles layout safety and collision detection

Usage Examples:
    # Generate video for specific book
    python unified_video_generator.py --book "calculus" 
    
    # Generate with custom audience 
    python unified_video_generator.py --book "physics" --audience "high_school"
    
    # Interactive mode for book exploration
    python unified_video_generator.py --interactive
    
    # List available books
    python unified_video_generator.py --list-books
"""

import os
import sys
import argparse
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def setup_environment():
    """Setup environment and validate requirements"""
    print("🚀 UNIFIED VIDEO GENERATOR - OpenAI Pipeline")
    print("=" * 60)
    # Load .env if present (do not log secrets)
    try:
        env_file = Path('.env')
        if env_file.exists():
            for line in env_file.read_text(encoding='utf-8').splitlines():
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value and key not in os.environ:
                        os.environ[key] = value
            print("? Loaded environment from .env")
    except Exception as _e:
        print(f"? Warning: Could not load .env: {_e}")

    # Check for OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ ERROR: OPENAI_API_KEY environment variable is required")
        print()
        print("Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-openai-api-key-here'")
        print("   # or add it to your .env file")
        print()
        sys.exit(1)
    
    print("✅ OpenAI API key found")
    
    # Create required directories
    dirs_to_create = [
        "books",
        "output/unified",
        "temp/unified",
        "output/unified/videos",
        "output/unified/reports"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure initialized")
    return openai_key

def list_available_books() -> List[str]:
    """List all available books in the books/ directory"""
    books_dir = Path("books")
    if not books_dir.exists():
        return []
    
    books = []
    for file_path in books_dir.glob("*.txt"):
        books.append(file_path.stem)
    
    return sorted(books)

def display_system_info():
    """Display system information and capabilities"""
    print("\n📊 SYSTEM INFORMATION")
    print("-" * 40)
    print("📂 Book Directory: books/")
    print("📁 Output Directory: output/unified/")
    print("⚙️  Processing: OpenAI-powered pipeline")
    print("🎬 Video Style: 3Blue1Brown aesthetic")
    print("⏱️  Target Duration: 10 minutes per segment")
    print("🔧 Features: Auto-chunking, Auto-debugging, Layout safety")
    
    # List available books
    books = list_available_books()
    if books:
        print(f"\n📚 AVAILABLE BOOKS ({len(books)})")
        print("-" * 40)
        for book in books:
            print(f"   📖 {book}")
    else:
        print(f"\n📚 NO BOOKS FOUND")
        print("-" * 40)
        print("   Add .txt files to books/ directory to get started")
        print("   Example: books/calculus.txt, books/physics.txt")

def interactive_mode(openai_key: str):
    """Interactive mode for video generation"""
    print("\n🎬 INTERACTIVE VIDEO GENERATION MODE")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Generate video from book")
        print("2. List available books") 
        print("3. System information")
        print("4. Exit")
        
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                # Show available books
                books = list_available_books()
                if not books:
                    print("❌ No books found in books/ directory")
                    print("   Add some .txt files to get started")
                    continue
                
                print(f"\n📚 Available books:")
                for i, book in enumerate(books, 1):
                    print(f"   {i}. {book}")
                
                # Get book selection
                try:
                    book_choice = input(f"\nEnter book number (1-{len(books)}): ").strip()
                    book_index = int(book_choice) - 1
                    
                    if 0 <= book_index < len(books):
                        selected_book = books[book_index]
                        
                        # Get audience preference
                        print(f"\n🎯 Target audiences:")
                        audiences = ["elementary", "high_school", "undergraduate", "graduate"]
                        for i, audience in enumerate(audiences, 1):
                            print(f"   {i}. {audience}")
                        
                        audience_choice = input(f"\nEnter audience (1-{len(audiences)}) [3]: ").strip()
                        if audience_choice:
                            audience_index = int(audience_choice) - 1
                            audience = audiences[audience_index] if 0 <= audience_index < len(audiences) else "undergraduate"
                        else:
                            audience = "undergraduate"
                        
                        # Start generation
                        print(f"\n🚀 Starting video generation...")
                        print(f"   📖 Book: {selected_book}")
                        print(f"   🎯 Audience: {audience}")
                        
                        success = generate_book_video(openai_key, selected_book, audience)
                        
                        if success:
                            print(f"\n🎉 Video generation completed successfully!")
                            print(f"📁 Check output/unified/videos/ for your video files")
                        else:
                            print(f"\n❌ Video generation failed")
                            
                    else:
                        print("❌ Invalid book selection")
                        
                except ValueError:
                    print("❌ Invalid input - please enter a number")
                
            elif choice == "2":
                books = list_available_books()
                if books:
                    print(f"\n📚 Available books ({len(books)}):")
                    for book in books:
                        print(f"   📖 {book}")
                else:
                    print("\n📚 No books found in books/ directory")
                    
            elif choice == "3":
                display_system_info()
                
            elif choice == "4":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def generate_book_video(openai_key: str, book_name: str, audience: str = "undergraduate") -> bool:
    """
    Generate video for a book using the unified OpenAI pipeline
    
    Args:
        openai_key: OpenAI API key
        book_name: Name of the book (without .txt extension)  
        audience: Target audience level
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n📚 PROCESSING BOOK: {book_name}")
        print("=" * 50)
        
        # Import unified components (will be created next)
        from src.unified_book_processor import UnifiedBookProcessor
        from src.intelligent_chunker import IntelligentChunker  
        from src.openai_video_generator import OpenAIVideoGenerator
        from src.manim_code_generator import ManimCodeGenerator
        
        # Initialize components
        print("🔧 Initializing unified pipeline...")
        
        book_processor = UnifiedBookProcessor()
        chunker = IntelligentChunker(openai_key)
        video_generator = OpenAIVideoGenerator(openai_key)
        code_generator = ManimCodeGenerator(openai_key)
        
        # Phase 1: Load and process book
        print(f"\n📖 PHASE 1: Loading book '{book_name}'...")
        book_content = book_processor.load_book(book_name)
        
        if not book_content:
            print(f"❌ Failed to load book '{book_name}'")
            return False
            
        print(f"✅ Book loaded: {len(book_content.content)} characters")
        
        # Phase 2: Intelligent chunking for large content
        print(f"\n🧩 PHASE 2: Analyzing content for optimal chunking...")
        chunks = chunker.chunk_content(book_content, target_duration=10, audience=audience)
        
        if not chunks:
            print("❌ Failed to chunk content")
            return False
            
        print(f"✅ Content chunked into {len(chunks)} optimal video segments")
        
        # Phase 3: Generate comprehensive teaching content for each chunk
        print(f"\n🎓 PHASE 3: Generating comprehensive teaching content...")
        teaching_contents = []
        
        for i, chunk in enumerate(chunks, 1):
            print(f"   Processing chunk {i}/{len(chunks)}: {chunk.title}")
            
            teaching_content = video_generator.generate_teaching_content(
                chunk, audience=audience
            )
            
            if teaching_content:
                teaching_contents.append(teaching_content)
                print(f"   ✅ Teaching content generated for chunk {i}")
            else:
                print(f"   ❌ Failed to generate teaching content for chunk {i}")
        
        if not teaching_contents:
            print("❌ No teaching content was generated")
            return False
        
        print(f"✅ Generated teaching content for {len(teaching_contents)} videos")
        
        # Phase 4: Generate Manim code and create videos
        print(f"\n🎬 PHASE 4: Generating Manim videos...")
        generated_videos = []
        
        for i, teaching_content in enumerate(teaching_contents, 1):
            print(f"   Generating video {i}/{len(teaching_contents)}...")
            
            video_path = code_generator.generate_video(
                teaching_content, 
                audience=audience,
                output_name=f"{book_name}_part_{i:02d}"
            )
            
            if video_path:
                generated_videos.append(video_path)
                print(f"   ✅ Video {i} generated: {Path(video_path).name}")
            else:
                print(f"   ❌ Failed to generate video {i}")
        
        # Results summary
        print(f"\n🎉 GENERATION COMPLETE!")
        print("=" * 50)
        print(f"📚 Book: {book_name}")
        print(f"🎯 Audience: {audience}")  
        print(f"🎬 Videos generated: {len(generated_videos)}/{len(teaching_contents)}")
        print(f"📁 Output location: output/unified/videos/")
        
        if generated_videos:
            print(f"\n📹 Generated video files:")
            for video in generated_videos:
                print(f"   📄 {Path(video).name}")
        
        return len(generated_videos) > 0
        
    except ImportError as e:
        print(f"❌ Missing component: {e}")
        print("   The unified pipeline components are still being built.")
        print("   Please wait for the full implementation to be completed.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Unified OpenAI-Based Video Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Book selection
    parser.add_argument("--book", type=str,
                       help="Book name to process (without .txt extension)")
    
    # Generation options  
    parser.add_argument("--audience", type=str, default="undergraduate",
                       choices=["elementary", "high_school", "undergraduate", "graduate"],
                       help="Target audience level (default: undergraduate)")
    
    # Interface options
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run in interactive mode")
    parser.add_argument("--list-books", action="store_true",
                       help="List all available books")
    parser.add_argument("--info", action="store_true", 
                       help="Show system information")
    
    args = parser.parse_args()
    
    # Setup environment
    openai_key = setup_environment()
    
    # Handle list books
    if args.list_books:
        books = list_available_books()
        if books:
            print(f"\n📚 Available books ({len(books)}):")
            for book in books:
                print(f"   📖 {book}")
        else:
            print("\n📚 No books found in books/ directory")
            print("   Add some .txt files to get started")
        return
    
    # Handle system info
    if args.info:
        display_system_info()
        return
    
    # Interactive mode
    if args.interactive:
        interactive_mode(openai_key)
        return
    
    # Direct book processing
    if args.book:
        success = generate_book_video(openai_key, args.book, args.audience)
        if not success:
            sys.exit(1)
        return
    
    # No arguments provided - show help
    parser.print_help()
    print(f"\n💡 TIP: Try 'python {sys.argv[0]} --interactive' for guided mode")

if __name__ == "__main__":
    main()
