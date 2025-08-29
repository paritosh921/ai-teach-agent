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
from typing import Optional, List, Dict

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
    # Try to use LLM-enhanced book processor first
    try:
        from src.llm_book_adapter import LLMBasedBookProcessor
        from src.book_processor import BookContent, TextSection
        BOOK_PROCESSOR_CLASS = LLMBasedBookProcessor
        print("✅ Using LLM-enhanced book processor")
    except ImportError:
        from src.book_processor import BookProcessor, BookContent, TextSection
        BOOK_PROCESSOR_CLASS = BookProcessor
        print("ℹ️ Using traditional book processor")

    from src.poml_generator import POMLGenerator
    from src.builder_llm import BuilderLLM, BuildRequest
    from src.orchestrator import VideoOrchestrator, WorkflowState
    from src.topic_subdivider import VideoSubtopic
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class BookToVideoProcessor:
    """Main class for processing books into educational videos"""
    
    def __init__(self, books_dir: str = "books", output_dir: str = "output/book_videos"):
        # Use LLM-enhanced processor if available
        self.book_processor = BOOK_PROCESSOR_CLASS(books_dir)
        self.poml_generator = POMLGenerator()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Check for required API keys
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. Video generation will fail.")

        self.builder_llm = BuilderLLM(api_key) if api_key else None
        self.orchestrator = VideoOrchestrator(api_key) if api_key else None
    
    def list_available_books(self, show_format: bool = False) -> List[str]:
        """List all available book topics"""
        if show_format:
            return self.book_processor.get_available_books(include_format_info=True)
        else:
            return self.book_processor.get_available_books()
    
    def show_book_structure(self, book_name: str, show_format_details: bool = False) -> None:
        """Display the structure of a book"""
        try:
            # Show format information
            book_format = self.book_processor.get_book_format(book_name)
            if show_format_details:
                print(f"\nFORMAT: Book format: {book_format}")
                if book_format == "json":
                    print("ENHANCED: + Rich metadata and structured content blocks")
                    print("FEATURES: + Intelligent subdivision hints and learning objectives")
                else:
                    print("ENHANCED: - Basic text format (consider converting to JSON)")
                    if self.book_processor.has_text_version(book_name):
                        print("CONVERT: Use --convert-to-json to upgrade this book")
            
            book = self.book_processor.load_book(book_name)
            print(f"\nBOOKS: Book: {book.title}")
            print(f"FILE: File: {book.filepath}")
            print(f"FORMAT: Format: {book_format}")
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
                print(f"INFO: Available sections in {book_name}:")
                for i, sec in enumerate(book.sections, 1):
                    sec_num = sec.section_number if sec.section_number else "N/A"
                    print(f"  {i}. {sec.title} (section: {sec_num})")
                print(f"\nTry using one of the available section numbers above.")
                return None
            
            print(f"PROCESSING: Processing: {section.title}")
            print(f"TARGET: Section: {section.section_number}")
            print(f"AUDIENCE: Audience: {audience}")
            
            # Skip POML generation - let LLM process book content directly
            print("\nPROCESS: Preparing full book content for LLM processing...")
            
            # Create build request with full book content
            build_request = BuildRequest(
                topic=section.title,
                audience=audience,
                theme=theme,
                poml_content=None,  # No POML - let LLM process content directly
                source_content=section.content  # Full educational content
            )
            
            print(f"CONTENT: Providing {len(section.content)} characters of educational material to LLM")
            
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
    
    def generate_all_videos(self, book_name: str, audience: str = "undergraduate", 
                           enable_subdivision: bool = False) -> List[str]:
        """Generate videos for all sections in a book with optional auto-subdivision"""
        try:
            book = self.book_processor.load_book(book_name)
            print(f"BOOKS: Processing entire book: {book.title}")
            print(f"SECTIONS: Total sections to process: {len(book.sections)}")
            print(f"SUBDIVISION: Auto-subdivision enabled: {enable_subdivision}")
            
            # Progress tracking
            progress_file = self.output_dir / f"{book_name}_progress.log"
            completed_sections = self._load_progress(progress_file)
            
            total_expected_videos = 0
            generated_videos = []
            failed_sections = []
            subdivision_stats = {'subdivided': 0, 'single': 0, 'failed': 0}
            
            for i, section in enumerate(book.sections, 1):
                section_id = f"{section.section_number}_{section.title.replace(' ', '_')}"
                
                if section_id in completed_sections:
                    print(f"SKIP: Section {i}/{len(book.sections)} already completed: {section.title}")
                    generated_videos.extend(completed_sections[section_id])
                    continue
                
                print(f"\n{'='*60}")
                print(f"PROGRESS: Processing section {i}/{len(book.sections)}")
                print(f"SECTION: {section.section_number}: {section.title}")
                
                section_videos = []
                
                try:
                    if enable_subdivision and self.book_processor.should_subdivide_section(section):
                        print(f"SUBDIVISION: Section complexity requires subdivision")
                        analysis = self.book_processor.analyze_section_complexity(section)
                        strategy = analysis['subdivision_recommendation']
                        
                        subdivision_videos = self.generate_subdivided_videos(
                            book_name, section.section_number, strategy, audience
                        )
                        section_videos.extend(subdivision_videos)
                        subdivision_stats['subdivided'] += 1
                        
                        print(f"SUBDIVISION: Generated {len(subdivision_videos)} subdivided videos")
                        
                    else:
                        # Generate single video
                        single_video = self.generate_video_for_section(
                            book_name, section.section_number, audience
                        )
                        if single_video:
                            section_videos.append(single_video)
                            subdivision_stats['single'] += 1
                        else:
                            subdivision_stats['failed'] += 1
                    
                    if section_videos:
                        generated_videos.extend(section_videos)
                        completed_sections[section_id] = section_videos
                        self._save_progress(progress_file, completed_sections)
                        print(f"SAVED: Progress saved for section {section.section_number}")
                    else:
                        failed_sections.append(section)
                        
                except Exception as section_error:
                    print(f"ERROR: Failed to process section {section.section_number}: {section_error}")
                    failed_sections.append(section)
                    subdivision_stats['failed'] += 1
            
            # Final statistics
            print(f"\n{'='*80}")
            print(f"BOOK PROCESSING COMPLETE: {book.title}")
            print(f"SUCCESS: Successfully generated: {len(generated_videos)} total videos")
            print(f"BREAKDOWN:")
            print(f"  - Single videos: {subdivision_stats['single']}")
            print(f"  - Subdivided sections: {subdivision_stats['subdivided']}")
            print(f"  - Failed sections: {subdivision_stats['failed']}")
            
            if failed_sections:
                print(f"\nFAILED SECTIONS ({len(failed_sections)}):")
                for section in failed_sections:
                    print(f"  - {section.section_number}: {section.title}")
            
            return generated_videos
            
        except Exception as e:
            print(f"ERROR: Error processing book: {e}")
            return []
    
    def _load_progress(self, progress_file: Path) -> Dict[str, List[str]]:
        """Load progress from file"""
        if not progress_file.exists():
            return {}
        
        try:
            import json
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"WARNING: Could not load progress file: {e}")
            return {}
    
    def _save_progress(self, progress_file: Path, completed_sections: Dict[str, List[str]]):
        """Save progress to file"""
        try:
            import json
            progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(completed_sections, f, indent=2)
        except Exception as e:
            print(f"WARNING: Could not save progress: {e}")
    
    def resume_book_processing(self, book_name: str, audience: str = "undergraduate") -> List[str]:
        """Resume book processing from where it left off"""
        print(f"RESUME: Resuming book processing for: {book_name}")
        return self.generate_all_videos(book_name, audience, enable_subdivision=True)
    
    def interactive_mode(self, book_name: str) -> None:
        """Interactive mode for selecting sections to process"""
        try:
            book = self.book_processor.load_book(book_name)
            
            while True:
                book_format = self.book_processor.get_book_format(book_name)
                
                print(f"\nBOOKS: Book: {book.title} ({book_format.upper()} format)")
                print("\nAvailable options:")
                print("1. List all sections")
                print("2. Generate video for specific section")
                print("3. Generate videos for entire chapter")
                print("4. Show section details")
                print("5. Analyze section for subdivision")
                print("6. Generate subdivided videos")
                print("7. Generate focused videos")
                print("8. Show format comparison")
                if book_format == "text":
                    print("9. Convert to JSON format")
                print("0. Exit")
                
                choice = input(f"\nEnter your choice (0-{'9' if book_format == 'text' else '8'}): ").strip()
                
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
                    section_num = input("Enter section number to analyze: ").strip()
                    self.analyze_section_for_subdivision(book_name, section_num)
                    
                elif choice == "6":
                    section_num = input("Enter section number: ").strip()
                    audience = input("Enter audience [undergraduate]: ").strip() or "undergraduate"
                    print("Subdivision strategies: auto, by_type, by_length, by_concept")
                    strategy = input("Enter strategy [auto]: ").strip() or "auto"
                    self.generate_subdivided_videos(book_name, section_num, strategy, audience)
                    
                elif choice == "7":
                    section_num = input("Enter section number: ").strip()
                    audience = input("Enter audience [undergraduate]: ").strip() or "undergraduate"
                    print("Available focus types: definitions, examples, applications, theory")
                    focus_input = input("Enter focus types (comma-separated) [definitions,examples]: ").strip()
                    focus_types = [f.strip() for f in (focus_input or "definitions,examples").split(",")]
                    self.generate_focused_videos(book_name, section_num, focus_types, audience)
                    
                elif choice == "8":
                    self.show_format_comparison(book_name)
                    
                elif choice == "9" and book_format == "text":
                    confirm = input("Convert this book to JSON format? (y/n): ").strip().lower()
                    if confirm == 'y':
                        use_llm_confirm = input("Use LLM-powered intelligent conversion? (y/n) [y]: ").strip().lower()
                        use_llm = use_llm_confirm != 'n'  # Default to yes
                        success = self.convert_book_to_json(book_name, enhance_content=True, use_llm=use_llm)
                        if success:
                            print("Book converted! Reloading with enhanced features...")
                            book = self.book_processor.load_book(book_name)  # Reload to get JSON version
                    
                elif choice == "0":
                    print("GOODBYE: Goodbye!")
                    break
                    
                else:
                    max_choice = "9" if book_format == "text" else "8"
                    print(f"ERROR: Invalid choice. Please enter 0-{max_choice}.")
                    
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
    
    def analyze_section_for_subdivision(self, book_name: str, section_number: str) -> None:
        """Analyze a section and show subdivision recommendations"""
        try:
            book = self.book_processor.load_book(book_name)
            section = self.book_processor.get_section_by_number(book, section_number)
            
            if not section:
                print(f"ERROR: Section {section_number} not found in {book_name}")
                return
            
            print(f"\nANALYSIS: Analyzing Section {section.section_number}: {section.title}")
            print("=" * 60)
            
            # Get detailed breakdown
            breakdown = self.book_processor.get_multi_video_breakdown(section)
            original = breakdown['original_section']
            analysis = original['analysis']
            
            print(f"CONTENT: Content Length: {analysis['content_length']} characters")
            print(f"DURATION: Estimated Duration: {analysis['estimated_duration_minutes']} minutes")
            print(f"COMPLEXITY: Complexity Score: {analysis['complexity_score']:.2f}")
            print(f"SUBDIVISION: Should Subdivide: {analysis['should_subdivide']}")
            print(f"RECOMMENDATION: Recommended Strategy: {analysis['subdivision_recommendation']}")
            
            print(f"\nEDUCATIONAL ELEMENTS:")
            for element_type, count in analysis['educational_elements'].items():
                if count > 0:
                    print(f"  - {element_type}: {count}")
            
            if analysis['should_subdivide']:
                print(f"\nSUBDIVISION OPTIONS:")
                
                if 'subdivision_options' in breakdown:
                    for strategy, subtopics in breakdown['subdivision_options'].items():
                        if isinstance(subtopics, list) and subtopics:
                            print(f"\n  {strategy.upper()} Strategy ({len(subtopics)} videos):")
                            for i, subtopic in enumerate(subtopics, 1):
                                print(f"    {i}. {subtopic['title']}")
                                print(f"       Duration: {subtopic['estimated_duration']}min, " 
                                     f"Focus: {subtopic['focus_type']}, "
                                     f"Length: {subtopic['content_length']} chars")
                
                if 'focused_options' in breakdown and breakdown['focused_options']:
                    print(f"\n  FOCUSED VIDEO OPTIONS ({len(breakdown['focused_options'])} videos):")
                    for i, focused in enumerate(breakdown['focused_options'], 1):
                        print(f"    {i}. {focused['title']}")
                        print(f"       Duration: {focused['estimated_duration']}min, "
                             f"Focus: {focused['focus_type']}, "
                             f"Length: {focused['content_length']} chars")
            else:
                print(f"\nRECOMMENDATION: This section is suitable for a single video.")
                
        except Exception as e:
            print(f"ERROR: Error analyzing section: {e}")
    
    def generate_subdivided_videos(self, book_name: str, section_number: str,
                                 subdivision_strategy: str = "auto", 
                                 audience: str = "undergraduate",
                                 theme: str = "3blue1brown") -> List[str]:
        """Generate multiple videos from a subdivided section"""
        try:
            book = self.book_processor.load_book(book_name)
            section = self.book_processor.get_section_by_number(book, section_number)
            
            if not section:
                print(f"ERROR: Section {section_number} not found in {book_name}")
                return []
            
            # Check if subdivision is recommended
            if not self.book_processor.should_subdivide_section(section):
                print(f"NOTICE: Section {section_number} doesn't need subdivision.")
                print(f"FALLBACK: Generating single video instead...")
                single_video = self.generate_video_for_section(book_name, section_number, audience, theme)
                return [single_video] if single_video else []
            
            # Get subdivided topics
            print(f"SUBDIVISION: Subdividing section using '{subdivision_strategy}' strategy...")
            subtopics = self.book_processor.get_subdivided_videos(section, subdivision_strategy)
            
            if not subtopics:
                print(f"ERROR: No subtopics generated for section {section_number}")
                return []
            
            print(f"SUBTOPICS: Generated {len(subtopics)} subtopics for video creation")
            
            generated_videos = []
            
            for i, subtopic in enumerate(subtopics, 1):
                print(f"\n{'='*50}")
                print(f"PROGRESS: Processing subtopic {i}/{len(subtopics)}")
                print(f"TITLE: {subtopic.title}")
                print(f"FOCUS: {subtopic.focus_type}")
                print(f"DURATION: Estimated {subtopic.estimated_duration} minutes")
                
                # Create build request for subtopic
                build_request = BuildRequest(
                    topic=subtopic.title,
                    audience=audience,
                    theme=theme,
                    poml_content=None,
                    source_content=subtopic.content
                )
                
                if self.orchestrator is None:
                    print("ERROR: Cannot generate video - OPENAI_API_KEY is required")
                    continue
                
                result = self.orchestrator.create_video(build_request)
                
                if result.success:
                    print(f"SUCCESS: Subtopic video completed!")
                    print(f"VIDEO: {result.video_path}")
                    generated_videos.append(result.video_path)
                else:
                    print(f"ERROR: Subtopic video failed: {result.error_message}")
            
            print(f"\n{'='*60}")
            print(f"SUBDIVISION COMPLETE:")
            print(f"SUCCESS: Generated {len(generated_videos)}/{len(subtopics)} videos")
            
            return generated_videos
            
        except Exception as e:
            print(f"ERROR: Error in subdivided video generation: {e}")
            return []
    
    def generate_focused_videos(self, book_name: str, section_number: str,
                              focus_types: List[str],
                              audience: str = "undergraduate",
                              theme: str = "3blue1brown") -> List[str]:
        """Generate focused videos for specific content types"""
        try:
            book = self.book_processor.load_book(book_name)
            section = self.book_processor.get_section_by_number(book, section_number)
            
            if not section:
                print(f"ERROR: Section {section_number} not found in {book_name}")
                return []
            
            print(f"FOCUS: Generating focused videos for: {', '.join(focus_types)}")
            
            # Get focused video topics
            focused_topics = self.book_processor.get_focused_videos(section, focus_types)
            
            # Filter out topics with insufficient content
            valid_topics = [ft for ft in focused_topics if len(ft.content.strip()) > 200]
            
            if not valid_topics:
                print(f"ERROR: No valid focused topics found for specified focus types")
                return []
            
            print(f"TOPICS: Found {len(valid_topics)} valid focused topics")
            
            generated_videos = []
            
            for i, topic in enumerate(valid_topics, 1):
                print(f"\n{'='*50}")
                print(f"PROGRESS: Processing focused topic {i}/{len(valid_topics)}")
                print(f"TITLE: {topic.title}")
                print(f"FOCUS: {topic.focus_type}")
                print(f"CONTENT: {len(topic.content)} characters")
                
                # Create build request for focused topic
                build_request = BuildRequest(
                    topic=topic.title,
                    audience=audience,
                    theme=theme,
                    poml_content=None,
                    source_content=topic.content
                )
                
                if self.orchestrator is None:
                    print("ERROR: Cannot generate video - OPENAI_API_KEY is required")
                    continue
                
                result = self.orchestrator.create_video(build_request)
                
                if result.success:
                    print(f"SUCCESS: Focused video completed!")
                    print(f"VIDEO: {result.video_path}")
                    generated_videos.append(result.video_path)
                else:
                    print(f"ERROR: Focused video failed: {result.error_message}")
            
            print(f"\n{'='*60}")
            print(f"FOCUSED GENERATION COMPLETE:")
            print(f"SUCCESS: Generated {len(generated_videos)}/{len(valid_topics)} videos")
            
            return generated_videos
            
        except Exception as e:
            print(f"ERROR: Error in focused video generation: {e}")
            return []
    
    def convert_book_to_json(self, book_name: str, enhance_content: bool = True, 
                            use_llm: bool = True) -> bool:
        """Convert a text book to JSON format with LLM intelligence"""
        try:
            print(f"CONVERT: Converting '{book_name}' from text to JSON format...")
            if enhance_content:
                conversion_type = "LLM-powered intelligent" if use_llm else "rule-based"
                print(f"ENHANCE: Applying {conversion_type} content analysis and enhancement")
            
            # Get API key for LLM conversion
            api_key = os.getenv('OPENAI_API_KEY')
            if use_llm and not api_key:
                print("[WARNING] OPENAI_API_KEY not found. Falling back to rule-based conversion.")
                use_llm = False
            
            success = self.book_processor.convert_text_to_json(
                book_name, enhance_content, use_llm, api_key
            )
            
            if success:
                print(f"SUCCESS: '{book_name}' converted to enhanced JSON format")
                print("NEW FEATURES:")
                print("  + Rich metadata and structured content blocks") 
                print("  + Intelligent educational element detection")
                print("  + Video generation hints and subdivision recommendations")
                print("  + Learning objectives and difficulty levels")
                print(f"LOCATION: JSON book saved to books_json/{book_name}.json")
                return True
            else:
                print(f"FAILED: Conversion unsuccessful")
                return False
                
        except Exception as e:
            print(f"ERROR: Failed to convert book: {e}")
            return False
    
    def list_book_formats(self) -> None:
        """List all books with their format information"""
        books_info = self.book_processor.list_books_with_details()
        
        if not books_info:
            print("No books found in either books/ or books_json/ directories")
            return
        
        print("\nAVAILABLE BOOKS:")
        print("=" * 60)
        
        for book_name, info in sorted(books_info.items()):
            format_indicator = "[JSON]" if info["format"] == "json" else "[TEXT]"
            enhanced_indicator = "+" if info["enhanced"] == "yes" else "-"
            
            print(f"{format_indicator} {book_name} ({info['format'].upper()})")
            print(f"   Enhanced: {enhanced_indicator}")
            print(f"   Path: {info['path']}")
            
            if info["format"] == "text":
                print("   Tip: Convert to JSON for enhanced features")
            print()
    
    def show_format_comparison(self, book_name: str) -> None:
        """Show comparison between text and JSON formats for a book"""
        has_text = self.book_processor.has_text_version(book_name)
        has_json = self.book_processor.has_json_version(book_name)
        
        print(f"\nFORMAT COMPARISON: {book_name}")
        print("=" * 50)
        
        if has_text:
            print("[TEXT] TEXT FORMAT:")
            print("   + Simple markdown structure")
            print("   - Basic educational element detection")
            print("   - Limited metadata support")
            print("   - Fixed content structure")
        
        if has_json:
            print("\n[JSON] JSON FORMAT:")
            print("   + Rich metadata and learning objectives")
            print("   + Structured content blocks (definitions, examples, etc.)")
            print("   + Intelligent educational element extraction")
            print("   + Video generation hints and subdivision strategies")
            print("   + Difficulty levels and complexity scoring")
            print("   + Flexible content organization")
        
        if has_text and not has_json:
            print("\nRECOMMENDATION: Convert to JSON format for enhanced features")
        elif not has_text and not has_json:
            print("\nERROR: No versions found for this book")
        
        print()
    
    def batch_convert_books(self, use_llm: bool = True) -> int:
        """Convert all text books to JSON format with LLM intelligence"""
        books = self.book_processor.get_available_books()
        text_books = [book for book in books if not self.book_processor.has_json_version(book)]
        
        if not text_books:
            print("No text-only books found to convert")
            return 0
        
        conversion_type = "LLM-powered" if use_llm else "rule-based"
        print(f"BATCH CONVERT: Converting {len(text_books)} books to JSON format using {conversion_type} conversion")
        
        converted_count = 0
        for book_name in text_books:
            print(f"\n{'='*50}")
            if self.convert_book_to_json(book_name, enhance_content=True, use_llm=use_llm):
                converted_count += 1
        
        print(f"\n{'='*60}")
        print(f"BATCH COMPLETE: {converted_count}/{len(text_books)} books converted successfully")
        
        return converted_count


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
  
  # New subdivision features:
  python book_to_video.py --book calculus --section 1.1 --analyze            # Analyze subdivision options
  python book_to_video.py --book calculus --section 1.1 --subdivide --strategy auto
  python book_to_video.py --book calculus --section 1.1 --focus definitions,examples
  python book_to_video.py --book calculus --generate-all --auto-subdivide    # Auto-subdivide complex sections
  python book_to_video.py --book calculus --resume                           # Resume interrupted processing
  
  # JSON format features:
  python book_to_video.py --list-formats                                      # List books with format info
  python book_to_video.py --book calculus --convert-to-json                   # Convert text to JSON with LLM
  python book_to_video.py --book calculus --convert-to-json --no-llm          # Convert using rule-based method
  python book_to_video.py --book calculus --show-format-comparison            # Compare text vs JSON
  python book_to_video.py --batch-convert                                     # Convert all text books with LLM
  python book_to_video.py --batch-convert --no-llm                            # Batch convert with rule-based method
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
    
    # New subdivision and focus options
    parser.add_argument("--analyze", action="store_true",
                       help="Analyze section complexity and show subdivision recommendations")
    
    parser.add_argument("--subdivide", action="store_true",
                       help="Generate multiple videos by subdividing the section")
    
    parser.add_argument("--strategy", type=str, default="auto",
                       choices=["auto", "by_type", "by_length", "by_concept"],
                       help="Subdivision strategy (use with --subdivide)")
    
    parser.add_argument("--focus", type=str,
                       help="Generate focused videos for specific content types (comma-separated: definitions,examples,applications,theory)")
    
    parser.add_argument("--auto-subdivide", action="store_true",
                       help="Enable automatic subdivision for complex sections when using --generate-all")
    
    parser.add_argument("--resume", action="store_true",
                       help="Resume book processing from where it left off")
    
    # JSON format options
    parser.add_argument("--list-formats", action="store_true",
                       help="List all books with format information")
    
    parser.add_argument("--convert-to-json", action="store_true",
                       help="Convert specified book from text to JSON format")
    
    parser.add_argument("--show-format-comparison", action="store_true",
                       help="Show comparison between text and JSON formats for a book")
    
    parser.add_argument("--batch-convert", action="store_true",
                       help="Convert all text books to JSON format")
    
    parser.add_argument("--no-enhance", action="store_true",
                       help="Skip content enhancement when converting to JSON (use with --convert-to-json)")
    
    parser.add_argument("--use-llm", action="store_true", default=True,
                       help="Use LLM-powered intelligent conversion (default: enabled)")
    
    parser.add_argument("--no-llm", action="store_true",
                       help="Force rule-based conversion even if LLM is available")
    
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
            print("ERROR: No books found in books/ or books_json/ directories")
            print("TIP: Add some .txt files to books/ directory to get started")
        return
    
    # Handle list formats
    if args.list_formats:
        processor.list_book_formats()
        return
    
    # Handle batch convert
    if args.batch_convert:
        use_llm = args.use_llm and not args.no_llm
        processor.batch_convert_books(use_llm)
        return
    
    # Require book name for other operations
    if not args.book:
        print("ERROR: Please specify a book name with --book")
        parser.print_help()
        return
    
    # Handle show structure
    if args.show_structure:
        processor.show_book_structure(args.book, show_format_details=True)
        return
    
    # Handle format comparison
    if args.show_format_comparison:
        processor.show_format_comparison(args.book)
        return
    
    # Handle convert to JSON
    if args.convert_to_json:
        enhance_content = not args.no_enhance
        use_llm = args.use_llm and not args.no_llm
        processor.convert_book_to_json(args.book, enhance_content, use_llm)
        return
    
    # Handle interactive mode
    if args.interactive:
        processor.interactive_mode(args.book)
        return
    
    # Handle specific operations
    if args.section:
        if args.analyze:
            processor.analyze_section_for_subdivision(args.book, args.section)
        elif args.subdivide:
            processor.generate_subdivided_videos(args.book, args.section, args.strategy, args.audience, args.theme)
        elif args.focus:
            focus_types = [f.strip() for f in args.focus.split(",")]
            processor.generate_focused_videos(args.book, args.section, focus_types, args.audience, args.theme)
        elif args.generate_poml_only:
            processor.generate_poml_for_section_only(args.book, args.section, args.audience)
        else:
            processor.generate_video_for_section(args.book, args.section, args.audience, args.theme)
    elif args.chapter:
        processor.generate_videos_for_chapter(args.book, args.chapter, args.audience)
    elif args.generate_all:
        processor.generate_all_videos(args.book, args.audience, args.auto_subdivide)
    elif args.resume:
        processor.resume_book_processing(args.book, args.audience)
    else:
        print("ERROR: Please specify an operation: --section, --chapter, --generate-all, or --interactive")
        parser.print_help()


if __name__ == "__main__":
    main()