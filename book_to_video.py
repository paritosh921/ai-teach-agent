#!/usr/bin/env python3
"""
Book to Video - Educational Content Generation Entry Point

This script converts textbook content from books/topic_name.txt into educational videos
using POML (Prompt Orchestration Markup Language) and the Builder LLM system.

Usage:
    python book_to_video.py --book "calculus" --section "1.1"
    python book_to_video.py --book "physics" --chapter 2 --interactive
    python book_to_video.py --list-books
    python book_to_video.py --book "calculus" --generate-all
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List

# Load .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print("Loaded environment variables from .env file")
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")

# Load .env file at startup
load_env_file()

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.book_processor import BookProcessor, BookContent, TextSection
    from src.poml_generator import POMLGenerator
    from src.builder_llm import BuilderLLM, BuildRequest
    from src.orchestrator import VideoOrchestrator, WorkflowState
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class BookToVideoProcessor:
    """Main class for processing books into educational videos"""
    
    def __init__(self, books_dir: str = "books", output_dir: str = "output/book_videos"):
        self.book_processor = BookProcessor(books_dir)
        self.poml_generator = POMLGenerator()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for required API keys
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. Video generation will fail.")
        
        self.builder_llm = BuilderLLM(api_key) if api_key else None
        self.orchestrator = VideoOrchestrator(api_key) if api_key else None
    
    def list_available_books(self) -> List[str]:
        """List all available book topics"""
        return self.book_processor.get_available_books()
    
    def show_book_structure(self, book_name: str) -> None:
        """Display the structure of a book"""
        try:
            book = self.book_processor.load_book(book_name)
            print(f"\nBOOKS: Book: {book.title}")
            print(f"FILE: File: {book.filepath}")
            print(f"SECTIONS: Total sections: {book.total_sections}")
            
            print("\nSTRUCTURE: Chapter Structure:")
            current_chapter = None
            for section in book.sections:
                if section.level == 2:  # Chapter
                    current_chapter = section.section_number
                    print(f"\n  Chapter {section.section_number}: {section.title}")
                    
                    # Show educational elements
                    elements = section.educational_elements
                    if any(elements.values()):
                        print("    TARGET: Contains:", end=" ")
                        element_summary = []
                        for key, values in elements.items():
                            if values:
                                element_summary.append(f"{len(values)} {key}")
                        print(", ".join(element_summary))
                
                elif section.level == 3:  # Section
                    print(f"      - Section {section.section_number}: {section.title}")
                    
        except FileNotFoundError:
            print(f"ERROR: Book '{book_name}' not found. Available books: {self.list_available_books()}")
        except Exception as e:
            print(f"ERROR: Error processing book: {e}")
    
    def generate_video_for_section(self, book_name: str, section_number: str, 
                                 audience: str = "undergraduate", 
                                 theme: str = "3blue1brown") -> Optional[str]:
        """Generate a video for a specific section"""
        try:
            # Load book and find section
            book = self.book_processor.load_book(book_name)
            section = self.book_processor.get_section_by_number(book, section_number)
            
            if not section:
                print(f"ERROR: Section {section_number} not found in {book_name}")
                return None
            
            print(f"PROCESSING: Processing: {section.title}")
            print(f"TARGET: Section: {section.section_number}")
            print(f"AUDIENCE: Audience: {audience}")
            
            # Generate POML
            print("\nPROCESS: Generating POML specification...")
            poml_content = self.poml_generator.generate_poml_for_section(
                section=section,
                audience=audience
            )
            
            # Save POML for reference
            poml_filename = f"{book_name}_{section.section_number}_{section.title.lower().replace(' ', '_')}.poml"
            poml_path = self.output_dir / "poml" / poml_filename
            self.poml_generator.save_poml_file(poml_content, str(poml_path))
            print(f"SAVED: POML saved to: {poml_path}")
            
            # Create build request
            build_request = BuildRequest(
                topic=section.title,
                audience=audience,
                theme=theme,
                poml_content=poml_content,
                source_content=section.content[:1000]  # First 1000 chars for context
            )
            
            # Generate video using orchestrator
            print("\nGENERATING: Starting video generation...")
            
            if self.orchestrator is None:
                print("ERROR: Cannot generate video - OPENAI_API_KEY is required")
                print("Please set your OpenAI API key:")
                print("  export OPENAI_API_KEY='your-api-key-here'")
                print("Or set it in your environment before running this script")
                return None
            
            result = self.orchestrator.create_video(build_request)
            
            if result.success:
                print(f"SUCCESS: Video generation completed!")
                print(f"VIDEO: Video path: {result.video_path}")
                return result.video_path
            else:
                print(f"ERROR: Video generation failed: {result.error_message}")
                return None
                
        except Exception as e:
            print(f"ERROR: Error generating video: {e}")
            return None
    
    def generate_videos_for_chapter(self, book_name: str, chapter_number: str,
                                  audience: str = "undergraduate") -> List[str]:
        """Generate videos for all sections in a chapter"""
        try:
            book = self.book_processor.load_book(book_name)
            chapter_sections = self.book_processor.get_chapter_sections(book, chapter_number)
            
            if not chapter_sections:
                print(f"ERROR: No sections found for chapter {chapter_number}")
                return []
            
            print(f"BOOKS: Processing Chapter {chapter_number} - {len(chapter_sections)} sections")
            
            generated_videos = []
            for section in chapter_sections:
                print(f"\n{'='*50}")
                video_path = self.generate_video_for_section(
                    book_name, section.section_number, audience
                )
                if video_path:
                    generated_videos.append(video_path)
            
            print(f"\nCOMPLETE: Chapter complete! Generated {len(generated_videos)} videos")
            return generated_videos
            
        except Exception as e:
            print(f"ERROR: Error processing chapter: {e}")
            return []
    
    def generate_all_videos(self, book_name: str, audience: str = "undergraduate") -> List[str]:
        """Generate videos for all sections in a book"""
        try:
            book = self.book_processor.load_book(book_name)
            print(f"BOOKS: Processing entire book: {book.title}")
            print(f"SECTIONS: Total sections to process: {len(book.sections)}")
            
            generated_videos = []
            for i, section in enumerate(book.sections, 1):
                print(f"\n{'='*60}")
                print(f"PROGRESS: Processing section {i}/{len(book.sections)}")
                
                video_path = self.generate_video_for_section(
                    book_name, section.section_number, audience
                )
                if video_path:
                    generated_videos.append(video_path)
            
            print(f"\nFINISHED: Book processing complete!")
            print(f"SUCCESS: Successfully generated: {len(generated_videos)} videos")
            print(f"ERROR: Failed: {len(book.sections) - len(generated_videos)} videos")
            
            return generated_videos
            
        except Exception as e:
            print(f"ERROR: Error processing book: {e}")
            return []
    
    def interactive_mode(self, book_name: str) -> None:
        """Interactive mode for selecting sections to process"""
        try:
            book = self.book_processor.load_book(book_name)
            
            while True:
                print(f"\nBOOKS: Book: {book.title}")
                print("\nAvailable options:")
                print("1. List all sections")
                print("2. Generate video for specific section")
                print("3. Generate videos for entire chapter")
                print("4. Show section details")
                print("5. Exit")
                
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == "1":
                    self.show_book_structure(book_name)
                    
                elif choice == "2":
                    section_num = input("Enter section number (e.g., 1.1): ").strip()
                    audience = input("Enter audience [undergraduate]: ").strip() or "undergraduate"
                    self.generate_video_for_section(book_name, section_num, audience)
                    
                elif choice == "3":
                    chapter_num = input("Enter chapter number: ").strip()
                    audience = input("Enter audience [undergraduate]: ").strip() or "undergraduate"
                    self.generate_videos_for_chapter(book_name, chapter_num, audience)
                    
                elif choice == "4":
                    section_num = input("Enter section number: ").strip()
                    section = self.book_processor.get_section_by_number(book, section_num)
                    if section:
                        print(f"\nPROCESSING: {section.title}")
                        print(f"SECTIONS: Content length: {len(section.content)} characters")
                        print(f"TARGET: Educational elements:")
                        for key, values in section.educational_elements.items():
                            if values:
                                print(f"  - {key}: {len(values)} items")
                        print(f"\nPREVIEW: Content preview:")
                        print(section.content[:300] + "...")
                    else:
                        print(f"ERROR: Section {section_num} not found")
                        
                elif choice == "5":
                    print("GOODBYE: Goodbye!")
                    break
                    
                else:
                    print("ERROR: Invalid choice. Please enter 1-5.")
                    
        except Exception as e:
            print(f"ERROR: Error in interactive mode: {e}")
    
    def generate_poml_for_section_only(self, book_name: str, section_number: str, 
                                     audience: str = "undergraduate") -> Optional[str]:
        """Generate POML for a section without creating video (no API key required)"""
        try:
            # Load book and find section
            book = self.book_processor.load_book(book_name)
            section = self.book_processor.get_section_by_number(book, section_number)
            
            if not section:
                print(f"ERROR: Section {section_number} not found in {book_name}")
                return None
            
            print(f"PROCESSING: Processing: {section.title}")
            print(f"TARGET: Section: {section.section_number}")
            print(f"AUDIENCE: Audience: {audience}")
            
            # Generate POML
            print("\nPROCESS: Generating POML specification...")
            poml_content = self.poml_generator.generate_poml_for_section(
                section=section,
                audience=audience
            )
            
            # Save POML for reference
            poml_filename = f"{book_name}_{section.section_number}_{section.title.lower().replace(' ', '_')}.poml"
            poml_path = self.output_dir / "poml" / poml_filename
            saved_file = self.poml_generator.save_poml_file(poml_content, str(poml_path))
            print(f"SAVED: POML saved to: {saved_file}")
            
            # Show preview of generated POML
            print("\nPREVIEW: POML Content Preview:")
            print("-" * 50)
            print(poml_content[:800] + "..." if len(poml_content) > 800 else poml_content)
            print("-" * 50)
            
            return saved_file
                
        except Exception as e:
            print(f"ERROR: Error generating POML: {e}")
            return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Convert textbook content to educational videos using POML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python book_to_video.py --list-books
  python book_to_video.py --book calculus --show-structure
  python book_to_video.py --book calculus --section 1.1 --generate-poml-only  # No API key needed
  python book_to_video.py --book calculus --section 1.1                       # Requires OPENAI_API_KEY
  python book_to_video.py --book physics --chapter 2
  python book_to_video.py --book calculus --interactive
  python book_to_video.py --book physics --generate-all --audience high_school
        """
    )
    
    parser.add_argument("--list-books", action="store_true",
                       help="List all available books")
    
    parser.add_argument("--book", type=str,
                       help="Book name (without .txt extension)")
    
    parser.add_argument("--show-structure", action="store_true",
                       help="Show the structure of the specified book")
    
    parser.add_argument("--section", type=str,
                       help="Generate video for specific section (e.g., 1.1)")
    
    parser.add_argument("--chapter", type=str,
                       help="Generate videos for all sections in chapter")
    
    parser.add_argument("--generate-all", action="store_true",
                       help="Generate videos for all sections in the book")
    
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Enter interactive mode")
    
    parser.add_argument("--audience", type=str, default="undergraduate",
                       choices=["elementary", "middle_school", "high_school", "undergraduate", "graduate"],
                       help="Target audience for the videos")
    
    parser.add_argument("--theme", type=str, default="3blue1brown",
                       choices=["3blue1brown", "bright", "dark"],
                       help="Visual theme for the videos")
    
    parser.add_argument("--generate-poml-only", action="store_true",
                       help="Generate POML files without creating videos (no API key required)")
    
    args = parser.parse_args()
    
    # Initialize processor
    try:
        processor = BookToVideoProcessor()
    except Exception as e:
        print(f"ERROR: Failed to initialize processor: {e}")
        sys.exit(1)
    
    # Handle list books
    if args.list_books:
        books = processor.list_available_books()
        if books:
            print("Available books:")
            for book in books:
                print(f"  - {book}")
        else:
            print("ERROR: No books found in the books/ directory")
            print("TIP: Add some .txt files to books/ directory to get started")
        return
    
    # Require book name for other operations
    if not args.book:
        print("ERROR: Please specify a book name with --book")
        parser.print_help()
        return
    
    # Handle show structure
    if args.show_structure:
        processor.show_book_structure(args.book)
        return
    
    # Handle interactive mode
    if args.interactive:
        processor.interactive_mode(args.book)
        return
    
    # Handle specific operations
    if args.section:
        if args.generate_poml_only:
            processor.generate_poml_for_section_only(args.book, args.section, args.audience)
        else:
            processor.generate_video_for_section(args.book, args.section, args.audience, args.theme)
    elif args.chapter:
        processor.generate_videos_for_chapter(args.book, args.chapter, args.audience)
    elif args.generate_all:
        processor.generate_all_videos(args.book, args.audience)
    else:
        print("ERROR: Please specify an operation: --section, --chapter, --generate-all, or --interactive")
        parser.print_help()


if __name__ == "__main__":
    main()