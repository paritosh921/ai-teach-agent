"""
Enhanced Video Orchestrator with AI Agent Integration

This module integrates all the enhanced components:
- AIAgent with autonomous debugging
- Enhanced video evaluator with frame-by-frame analysis
- Position mapping system for layout management  
- Intelligent content subdivision with 10-minute segments
- Content reflow system for scene continuity
"""

import os
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from .ai_agent import AIAgent, AgentTask, AgentResult
from .simple_video_evaluator import EnhancedVideoEvaluator, VideoEvaluationResult
from .position_mapper import PositionMapper, SafeFrame
from .topic_subdivider import TopicSubdivider, VideoSubtopic
from .content_reflow import ContentReflowManager, ElementContinuity, ContinuityType
from .builder_llm import BuildRequest, BuildResponse
from .book_processor import BookProcessor, TextSection
from .intelligent_book_processor import IntelligentBookProcessor, IntelligentBookContent


@dataclass
class EnhancedBuildRequest:
    """Enhanced build request with additional features"""
    topic: str
    content: str
    audience: str = "undergraduate"
    target_duration: int = 10  # minutes
    max_videos: Optional[int] = None
    subdivision_strategy: str = "optimal_10min"
    enable_continuity: bool = True
    enable_position_mapping: bool = True
    enable_reflow: bool = True
    quality_threshold: float = 0.8


@dataclass 
class EnhancedVideoResult:
    """Enhanced result with comprehensive analysis"""
    success: bool
    videos_generated: List[str] = field(default_factory=list)
    total_duration: float = 0.0
    quality_scores: List[float] = field(default_factory=list)
    agent_results: List[AgentResult] = field(default_factory=list)
    evaluation_reports: List[VideoEvaluationResult] = field(default_factory=list)
    layout_reports: List[Dict[str, Any]] = field(default_factory=list)
    reflow_reports: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    processing_time: float = 0.0
    subdivision_info: Dict[str, Any] = field(default_factory=dict)


class EnhancedVideoOrchestrator:
    """
    Enhanced Video Orchestrator with Full AI Pipeline
    
    Integrates all advanced features:
    - Autonomous AI agent for code generation and debugging
    - Frame-by-frame video quality evaluation
    - Intelligent position mapping and layout management
    - Smart content subdivision for optimal 10-minute segments
    - Content reflow and scene continuity management
    """
    
    def __init__(self, openai_api_key: str, gemini_api_key: Optional[str] = None,
                 work_dir: str = "temp/enhanced", output_dir: str = "output/enhanced"):
        """
        Initialize enhanced orchestrator
        
        Args:
            openai_api_key: OpenAI API key for AI agent
            gemini_api_key: Optional Gemini API key for evaluation
            work_dir: Working directory for processing
            output_dir: Output directory for final videos
        """
        self.work_dir = Path(work_dir)
        self.output_dir = Path(output_dir)
        
        # Create directories
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.ai_agent = AIAgent(
            openai_api_key=openai_api_key,
            gemini_api_key=gemini_api_key,
            work_dir=str(self.work_dir / "agent")
        )
        
        self.video_evaluator = EnhancedVideoEvaluator(gemini_api_key)
        self.position_mapper = PositionMapper()
        self.topic_subdivider = TopicSubdivider()
        self.content_reflow_manager = ContentReflowManager()
        self.book_processor = BookProcessor()
        
        # Initialize intelligent book processor with fallback
        try:
            self.intelligent_book_processor = IntelligentBookProcessor(openai_api_key)
            self.use_intelligent_processor = True
            print("INTELLIGENT: LLM-powered book processor initialized")
        except Exception as e:
            print(f"WARNING: Intelligent book processor failed to initialize: {e}")
            print("         Falling back to traditional pattern-based processor")
            self.intelligent_book_processor = None
            self.use_intelligent_processor = False
        
        print("SUCCESS: Enhanced Video Orchestrator initialized")
        print(f"WORKSPACE: Working directory: {self.work_dir}")
        print(f"OUTPUT: Output directory: {self.output_dir}")
        
        # Print component status
        print(f"AI AGENT: Ready")
        print(f"VIDEO EVALUATOR: {'Available' if self.video_evaluator.is_available() else 'Basic mode'}")
        print(f"POSITION MAPPER: Ready")
        print(f"CONTENT SUBDIVISION: Ready")
        print(f"REFLOW MANAGER: Ready")
        print(f"BOOK PROCESSOR: {'Intelligent (LLM-powered)' if self.use_intelligent_processor else 'Traditional (Pattern-based)'}")
    
    def create_video_series(self, request: EnhancedBuildRequest) -> EnhancedVideoResult:
        """
        Create a complete video series from educational content
        
        Args:
            request: Enhanced build request with content and preferences
            
        Returns:
            EnhancedVideoResult with comprehensive results
        """
        print(f"SERIES: Starting enhanced video series creation")
        print(f"TOPIC: {request.topic}")
        print(f"TARGET DURATION: {request.target_duration} minutes per video")
        print(f"CONTENT LENGTH: {len(request.content)} characters")
        print("=" * 70)
        
        start_time = time.time()
        result = EnhancedVideoResult(success=False)
        
        try:
            # Phase 1: Intelligent Content Analysis and Subdivision
            subdivision_info = self._analyze_and_subdivide_content(request)
            result.subdivision_info = subdivision_info
            
            if not subdivision_info['subtopics']:
                result.error_message = "No valid subtopics generated from content"
                return result
            
            subtopics = subdivision_info['subtopics']
            print(f"SUBDIVISION: Generated {len(subtopics)} video segments")
            
            # Phase 2: Generate Videos with AI Agent
            agent_results = []
            videos_generated = []
            
            for i, subtopic in enumerate(subtopics, 1):
                print(f"\nVIDEO {i}/{len(subtopics)}: {subtopic.title}")
                print("-" * 50)
                
                video_result = self._generate_single_video(subtopic, request, i)
                agent_results.append(video_result)
                
                if video_result.success:
                    videos_generated.append(video_result.video_path)
                    print(f"SUCCESS: Video {i} generated: {video_result.video_path}")
                else:
                    print(f"FAILED: Video {i} generation failed: {video_result.error_message}")
            
            result.agent_results = agent_results
            result.videos_generated = videos_generated
            
            # Phase 3: Comprehensive Quality Evaluation
            if videos_generated and request.quality_threshold > 0:
                print(f"\nQUALITY: Starting comprehensive evaluation...")
                evaluation_results = self._evaluate_video_series(videos_generated, subtopics)
                result.evaluation_reports = evaluation_results
                
                # Calculate average quality scores
                quality_scores = []
                for eval_result in evaluation_results:
                    if eval_result.overall_quality_score > 0:
                        quality_scores.append(eval_result.overall_quality_score)
                
                result.quality_scores = quality_scores
                
                if quality_scores:
                    avg_quality = sum(quality_scores) / len(quality_scores)
                    print(f"QUALITY: Average quality score: {avg_quality:.2f}")
                    
                    if avg_quality < request.quality_threshold:
                        print(f"WARNING: Quality below threshold ({request.quality_threshold})")
            
            # Phase 4: Generate Reports and Statistics
            self._generate_comprehensive_reports(result, request)
            
            # Success if at least one video was generated
            result.success = len(videos_generated) > 0
            result.processing_time = time.time() - start_time
            
            if result.success:
                print(f"\nSUCCESS: Enhanced video series completed!")
                print(f"GENERATED: {len(videos_generated)} videos")
                print(f"PROCESSING TIME: {result.processing_time:.1f} seconds")
            else:
                result.error_message = "No videos were successfully generated"
                print(f"\nFAILED: No videos generated successfully")
            
        except Exception as e:
            print(f"ERROR: Unexpected error in enhanced orchestrator: {e}")
            import traceback
            traceback.print_exc()
            result.error_message = f"Unexpected error: {e}"
            result.processing_time = time.time() - start_time
        
        return result
    
    def _analyze_and_subdivide_content(self, request: EnhancedBuildRequest) -> Dict[str, Any]:
        """Analyze and subdivide content into optimal video segments"""
        print("PHASE 1: Content Analysis & Subdivision")
        print("-" * 40)
        
        # Create a text section from the request
        text_section = TextSection(
            title=request.topic,
            content=request.content,
            level=2,  # Chapter level
            section_number="1.0",
            educational_elements={}
        )
        
        # Analyze content complexity
        should_subdivide = self.topic_subdivider.should_subdivide_section(text_section)
        estimated_duration = self.topic_subdivider._estimate_duration(request.content)
        
        print(f"ANALYSIS: Content should subdivide: {should_subdivide}")
        print(f"ANALYSIS: Estimated total duration: {estimated_duration} minutes")
        
        subdivision_info = {
            'should_subdivide': should_subdivide,
            'estimated_duration': estimated_duration,
            'strategy_used': request.subdivision_strategy,
            'subtopics': []
        }
        
        if should_subdivide or estimated_duration > request.target_duration:
            # Use intelligent subdivision
            subtopics = self.topic_subdivider.subdivide_section(text_section, request.subdivision_strategy)
            subdivision_info['subtopics'] = subtopics
            print(f"SUBDIVISION: Created {len(subtopics)} subtopics using {request.subdivision_strategy} strategy")
            
            # Apply video series optimization if requested
            if len(subtopics) > 1:
                optimized_subtopics = self.topic_subdivider._optimize_video_series(subtopics, request.target_duration)
                subdivision_info['subtopics'] = optimized_subtopics
                print(f"OPTIMIZATION: Optimized to {len(optimized_subtopics)} final videos")
        else:
            # Single video
            single_subtopic = VideoSubtopic(
                title=request.topic,
                content=request.content,
                focus_type="comprehensive",
                parent_section="1.0",
                subtopic_index="1.0",
                educational_elements={},
                complexity_score=self.topic_subdivider._calculate_content_complexity(request.content),
                estimated_duration=estimated_duration
            )
            subdivision_info['subtopics'] = [single_subtopic]
            print("SUBDIVISION: Single video sufficient for content")
        
        return subdivision_info
    
    def _generate_single_video(self, subtopic: VideoSubtopic, 
                              request: EnhancedBuildRequest, video_index: int) -> AgentResult:
        """Generate a single video using the AI agent"""
        
        # Create agent task
        task = AgentTask(
            task_id=f"{request.topic}_{video_index}",
            topic=subtopic.title,
            content=subtopic.content,
            target_duration=subtopic.estimated_duration,
            audience=request.audience,
            requirements=[
                "Use 3Blue1Brown aesthetic",
                "Ensure no content overlap",
                "Keep all elements within frame",
                "Provide complete explanations from basics to advanced"
            ],
            constraints=[
                f"Target duration: {subtopic.estimated_duration} minutes",
                "Minimum font size: 24px at 480p",
                "Safe margins: 6% on all sides"
            ]
        )
        
        # Execute task with AI agent
        print(f"AI AGENT: Starting autonomous generation for {subtopic.title}")
        agent_result = self.ai_agent.execute_task(task)
        
        if agent_result.success:
            print(f"AI AGENT: ✅ Success - {agent_result.attempts_made} attempts")
        else:
            print(f"AI AGENT: ❌ Failed - {agent_result.error_message}")
        
        return agent_result
    
    def _evaluate_video_series(self, video_paths: List[str], 
                              subtopics: List[VideoSubtopic]) -> List[VideoEvaluationResult]:
        """Evaluate all videos in the series"""
        print("PHASE 3: Comprehensive Video Evaluation")
        print("-" * 45)
        
        evaluation_results = []
        
        for i, (video_path, subtopic) in enumerate(zip(video_paths, subtopics)):
            print(f"EVALUATING: Video {i+1}: {subtopic.title}")
            
            # Create content context for evaluation
            content_context = {
                'topic': subtopic.title,
                'focus_type': subtopic.focus_type,
                'estimated_duration': subtopic.estimated_duration,
                'content_length': len(subtopic.content)
            }
            
            # Evaluate video
            try:
                evaluation_result = self.video_evaluator.evaluate_video(video_path, content_context)
                evaluation_results.append(evaluation_result)
                
                print(f"EVALUATION: Quality: {evaluation_result.overall_quality_score:.2f}, "
                      f"Issues: {evaluation_result.issues_found}, "
                      f"Status: {evaluation_result.status}")
                
            except Exception as e:
                print(f"EVALUATION ERROR: {e}")
                # Create error evaluation result
                error_result = VideoEvaluationResult(
                    success=False,
                    overall_quality_score=0.0,
                    educational_effectiveness=0.0,
                    layout_safety_score=0.0,
                    issues_found=1,
                    critical_issues=1,
                    recommendations=[f"Evaluation failed: {e}"],
                    detailed_issues=[],
                    status="error"
                )
                evaluation_results.append(error_result)
        
        return evaluation_results
    
    def _generate_comprehensive_reports(self, result: EnhancedVideoResult, 
                                      request: EnhancedBuildRequest):
        """Generate comprehensive analysis reports"""
        print("\nREPORTS: Generating comprehensive analysis...")
        
        # Agent memory statistics
        if hasattr(self.ai_agent, 'get_memory_stats'):
            agent_stats = self.ai_agent.get_memory_stats()
            print(f"AGENT MEMORY: {agent_stats.get('learned_patterns', 0)} patterns learned")
        
        # Position mapping report
        if request.enable_position_mapping:
            layout_report = self.position_mapper.get_layout_report()
            result.layout_reports.append(layout_report)
            print(f"LAYOUT: {layout_report.get('total_elements', 0)} elements positioned")
        
        # Content reflow report  
        if request.enable_reflow:
            reflow_report = self.content_reflow_manager.generate_reflow_report()
            result.reflow_reports.append(reflow_report)
            print(f"REFLOW: {reflow_report.get('total_reflow_operations', 0)} operations performed")
        
        # Save detailed reports to files
        self._save_reports_to_files(result, request)
    
    def _save_reports_to_files(self, result: EnhancedVideoResult, request: EnhancedBuildRequest):
        """Save detailed reports to files"""
        reports_dir = self.output_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = int(time.time())
        
        # Save main report (handle VideoSubtopic serialization)
        subdivision_info_serializable = None
        if result.subdivision_info:
            subdivision_info_serializable = {}
            for key, value in result.subdivision_info.items():
                if key == 'subtopics' and isinstance(value, list):
                    # Convert VideoSubtopic objects to dictionaries
                    subdivision_info_serializable[key] = [
                        subtopic.to_dict() if hasattr(subtopic, 'to_dict') else str(subtopic)
                        for subtopic in value
                    ]
                else:
                    subdivision_info_serializable[key] = value
        
        main_report = {
            'topic': request.topic,
            'timestamp': timestamp,
            'success': result.success,
            'videos_generated': len(result.videos_generated),
            'total_duration': result.total_duration,
            'average_quality': sum(result.quality_scores) / len(result.quality_scores) if result.quality_scores else 0,
            'processing_time': result.processing_time,
            'subdivision_info': subdivision_info_serializable
        }
        
        import json
        
        with open(reports_dir / f"main_report_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(main_report, f, indent=2, ensure_ascii=False)
        
        # Save agent results
        agent_report = []
        for agent_result in result.agent_results:
            agent_report.append({
                'task_id': agent_result.task_id,
                'success': agent_result.success,
                'attempts_made': agent_result.attempts_made,
                'execution_time': agent_result.execution_time,
                'quality_score': agent_result.quality_score,
                'error_message': agent_result.error_message
            })
        
        with open(reports_dir / f"agent_results_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(agent_report, f, indent=2, ensure_ascii=False)
        
        # Save evaluation results
        eval_report = []
        for eval_result in result.evaluation_reports:
            eval_report.append({
                'success': eval_result.success,
                'overall_quality_score': eval_result.overall_quality_score,
                'educational_effectiveness': eval_result.educational_effectiveness,
                'layout_safety_score': eval_result.layout_safety_score,
                'issues_found': eval_result.issues_found,
                'critical_issues': eval_result.critical_issues,
                'status': eval_result.status,
                'evaluation_summary': eval_result.evaluation_summary
            })
        
        with open(reports_dir / f"evaluation_results_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(eval_report, f, indent=2, ensure_ascii=False)
        
        print(f"REPORTS: Saved to {reports_dir}")
    
    def create_single_video(self, topic: str, content: str, 
                          audience: str = "undergraduate") -> EnhancedVideoResult:
        """
        Create a single video (convenience method)
        
        Args:
            topic: Video topic
            content: Educational content
            audience: Target audience
            
        Returns:
            EnhancedVideoResult
        """
        request = EnhancedBuildRequest(
            topic=topic,
            content=content,
            audience=audience,
            target_duration=10,
            subdivision_strategy="auto"
        )
        
        return self.create_video_series(request)
    
    def create_chapter_series(self, book_name: str, chapter_number: str,
                            audience: str = "undergraduate") -> EnhancedVideoResult:
        """
        Create video series for entire chapter
        
        Args:
            book_name: Name of the book
            chapter_number: Chapter number to process
            audience: Target audience
            
        Returns:
            EnhancedVideoResult
        """
        try:
            # Load book using intelligent processor with fallback
            book_content = self._load_book_intelligently(book_name)
            
            # Find chapter sections
            chapter_sections = self._get_chapter_sections_intelligently(book_content, chapter_number)
            
            if not chapter_sections:
                return EnhancedVideoResult(
                    success=False,
                    error_message=f"No sections found for chapter {chapter_number}"
                )
            
            # Merge chapter content
            chapter_content = []
            chapter_title = f"Chapter {chapter_number}"
            
            for section in chapter_sections:
                chapter_content.append(f"## {section.title}\n\n{section.content}")
                if chapter_title == f"Chapter {chapter_number}":
                    # Use first section's parent for chapter title
                    chapter_title = f"Chapter {chapter_number}: {section.title.split()[0] if section.title else 'Content'}"
            
            merged_content = "\n\n".join(chapter_content)
            
            request = EnhancedBuildRequest(
                topic=chapter_title,
                content=merged_content,
                audience=audience,
                target_duration=10,
                subdivision_strategy="optimal_10min",
                enable_continuity=True
            )
            
            return self.create_video_series(request)
            
        except Exception as e:
            return EnhancedVideoResult(
                success=False,
                error_message=f"Failed to create chapter series: {e}"
            )
    
    def create_section_video(self, book_name: str, section_number: str,
                           audience: str = "undergraduate") -> EnhancedVideoResult:
        """
        Create video for a specific section using intelligent processing
        
        Args:
            book_name: Name of the book
            section_number: Section number to process (flexible matching)
            audience: Target audience
            
        Returns:
            EnhancedVideoResult
        """
        try:
            # Load book using intelligent processor
            book_content = self._load_book_intelligently(book_name)
            
            # Find section with flexible matching
            section = self._find_section_intelligently(book_content, section_number)
            
            if not section:
                # List available sections for user
                available_sections = self._list_available_sections(book_content)
                error_msg = f"Section {section_number} not found in {book_name}.\n"
                error_msg += "Available sections:\n"
                for num, title in available_sections[:10]:  # Show first 10
                    error_msg += f"  {num}: {title}\n"
                
                return EnhancedVideoResult(
                    success=False,
                    error_message=error_msg
                )
            
            print(f"INTELLIGENT: Found section - {section.section_number}: {section.title}")
            
            # Create request for this section
            request = EnhancedBuildRequest(
                topic=section.title,
                content=section.content,
                audience=audience,
                target_duration=10,
                subdivision_strategy="optimal_10min",
                enable_continuity=True
            )
            
            return self.create_video_series(request)
            
        except Exception as e:
            return EnhancedVideoResult(
                success=False,
                error_message=f"Failed to create section video: {e}"
            )
    
    def _load_book_intelligently(self, book_name: str):
        """Load book using intelligent processor with fallback"""
        try:
            if self.use_intelligent_processor and self.intelligent_book_processor:
                print(f"INTELLIGENT: Loading '{book_name}' with LLM analysis...")
                book_content = self.intelligent_book_processor.load_book(book_name)
                
                # Show content summary
                print("INTELLIGENT: Content Analysis Summary:")
                print(f"  Document type: {book_content.structure.document_type}")
                print(f"  Subject area: {book_content.structure.subject_area}")
                print(f"  Educational level: {book_content.structure.educational_level}")
                print(f"  Total sections: {book_content.total_sections}")
                print(f"  Processing confidence: {book_content.structure.structure_confidence:.2f}")
                
                return book_content
            else:
                print(f"FALLBACK: Loading '{book_name}' with traditional processor...")
                return self.book_processor.load_book(book_name)
                
        except Exception as e:
            print(f"ERROR: Intelligent loading failed: {e}")
            if self.book_processor:
                print("FALLBACK: Trying traditional book processor...")
                return self.book_processor.load_book(book_name)
            else:
                raise e
    
    def _find_section_intelligently(self, book_content, section_number: str):
        """Find section using intelligent matching"""
        if hasattr(book_content, 'structure') and self.intelligent_book_processor:
            # Use intelligent processor's flexible matching
            return self.intelligent_book_processor.find_section_by_number(book_content, section_number)
        else:
            # Use traditional processor's method
            return self.book_processor.get_section_by_number(book_content, section_number)
    
    def _list_available_sections(self, book_content):
        """List available sections from book content"""
        if hasattr(book_content, 'structure') and self.intelligent_book_processor:
            return self.intelligent_book_processor.list_available_sections(book_content)
        else:
            # Traditional format
            return [(section.section_number, section.title) for section in book_content.sections]
    
    def _get_chapter_sections_intelligently(self, book_content, chapter_number: str):
        """Get chapter sections using intelligent matching"""
        chapter_sections = []
        
        for section in book_content.sections:
            # More flexible chapter matching
            if (section.section_number.startswith(f"{chapter_number}.") or 
                section.section_number == str(chapter_number) or
                (hasattr(section, 'level') and section.level == 2 and 
                 chapter_number in section.section_number)):
                chapter_sections.append(section)
        
        return chapter_sections
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'ai_agent': {
                'available': True,
                'memory_stats': self.ai_agent.get_memory_stats() if hasattr(self.ai_agent, 'get_memory_stats') else {}
            },
            'video_evaluator': {
                'available': self.video_evaluator.is_available(),
                'type': 'Enhanced with Gemini 1.5 Flash' if self.video_evaluator.is_available() else 'Basic'
            },
            'position_mapper': {
                'available': True,
                'type': 'Intelligent with collision detection'
            },
            'topic_subdivider': {
                'available': True,
                'type': 'Optimal 10-minute segmentation'
            },
            'content_reflow_manager': {
                'available': True,
                'type': 'Intelligent scene continuity'
            },
            'book_processor': {
                'available': True,
                'type': 'Intelligent LLM-powered' if self.use_intelligent_processor else 'Traditional pattern-based',
                'intelligent_available': self.use_intelligent_processor
            }
        }


def create_enhanced_orchestrator(openai_api_key: str, 
                               gemini_api_key: Optional[str] = None) -> EnhancedVideoOrchestrator:
    """Factory function to create enhanced orchestrator"""
    return EnhancedVideoOrchestrator(openai_api_key, gemini_api_key)