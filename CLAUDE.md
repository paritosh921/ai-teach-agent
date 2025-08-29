# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**🆕 Enhanced AI-Powered Video System (Recommended):**
```bash
# Generate optimal 10-minute video segments with full AI pipeline
python enhanced_book_to_video.py --book "calculus" --section "1.1" --audience "high_school"

# Generate entire chapter with autonomous debugging
python enhanced_book_to_video.py --book "physics" --chapter 2 --quality-threshold 0.8

# Interactive mode with enhanced features
python enhanced_book_to_video.py --book "calculus" --interactive --enhanced

# Generate from custom content with AI agent
python enhanced_book_to_video.py --content "Your educational content here" --topic "Custom Topic"

# Show enhanced system status
python enhanced_book_to_video.py --status

# List available books
python enhanced_book_to_video.py --list-books
```

**Book-to-Video System (Original Interface):**
```bash
# List available books
python book_to_video.py --list-books

# Generate video for specific section
python book_to_video.py --book "calculus" --section "1.1"

# Generate videos for entire chapter
python book_to_video.py --book "physics" --chapter 2

# Interactive mode for book exploration
python book_to_video.py --book "calculus" --interactive

# Generate all videos for a book
python book_to_video.py --book "calculus" --generate-all --audience "high_school"

# Show book structure
python book_to_video.py --book "calculus" --show-structure
```

**Direct Builder LLM Access (Advanced):**
```bash
# Direct access to Builder LLM for custom topics
python builder_run.py --topic "Chemical Bonding" --interactive
```

**Install dependencies:**
```bash
# Enhanced system with AI capabilities
pip install -r requirements_enhanced.txt

# Original system (basic)
pip install -r requirements.txt
```

**Testing commands:**
```bash
# Test book-to-video system with sample content
python book_to_video.py --book "calculus" --section "1.1" --audience "undergraduate"

# Test POML generation and validation
python -c "from src.book_processor import BookProcessor; from src.poml_generator import POMLGenerator; bp = BookProcessor(); pg = POMLGenerator(); book = bp.load_book('calculus'); print(pg.generate_poml_for_section(book.sections[0]))"

# Test Builder LLM system directly
python builder_run.py --topic "Basic Math" --interactive
```

**Environment variables:**
- `OPENAI_API_KEY` - Required for GPT-4 content generation
- `OPENAI_MODEL` - Optional OpenAI model selection (defaults to gpt-5-mini)
- `GEMINI_API_KEY` - Optional for video quality evaluation with Gemini 1.5 Flash

**OpenAI Model Compatibility:**
- `gpt-5-mini` (default): No temperature parameter support, reasoning-optimized
- `gpt-4-turbo`: Full parameter support including temperature
- `gpt-4o`: Full parameter support including temperature  
- `gpt-4`: Full parameter support including temperature
- System automatically falls back to compatible models on parameter errors

**Important Notes:**
- The Gemini API has been updated to use `google-generativeai` package and Gemini 1.5 Flash model
- Progressive error fixing now properly handles `get_graph` color parameter issues
- Video evaluation includes educational effectiveness assessment

**Output locations:**
```bash
# Book-to-video outputs
books/                   # Input: Textbook content (.txt files)
output/book_videos/      # Generated videos from book content
output/book_videos/poml/ # Generated POML specifications
output/builder/          # Builder LLM artifacts (code, YAML, patches)
output/builder/media/    # Final video files
media/videos/           # Manim video output
```

## High-Level Architecture

This repository contains **a comprehensive AI-powered tutorial video pipeline** with advanced autonomous capabilities:

### 🆕 Enhanced AI-Powered System (Latest)
**AUTONOMOUS-AGENT-PIPELINE**: Complete autonomous video generation with learning capabilities
- **Workflow**: TEXT → SUBDIVISION → AI-AGENT → DEBUG-LOOP → EVALUATION → QUALITY-CHECK → VIDEO
- **Components**: `enhanced_book_to_video.py`, `src/enhanced_orchestrator.py`, `src/ai_agent.py`
- **Key Features**: Autonomous debugging, frame-by-frame analysis, 10-minute optimization, scene continuity
- **Input**: Textbook content, custom text, or structured educational material
- **Output**: Professional educational video series with comprehensive quality reports

### 🎯 AI Agent System (Core Innovation)
**AUTONOMOUS-CODE-GENERATION**: Self-debugging AI agent with memory and learning
- **Capabilities**: Generates Manim code, debugs compilation errors autonomously, learns from failures
- **Components**: `src/ai_agent.py`, `src/position_mapper.py`, `src/content_reflow.py`
- **Memory System**: Persistent learning database that improves over time
- **Error Recovery**: 5-level progressive error fixing with fallback strategies

### 🔍 Enhanced Video Evaluation (Gemini Integration)
**FRAME-BY-FRAME-ANALYSIS**: Comprehensive video quality assessment
- **Technology**: Gemini 1.5 Flash integration with OpenCV frame extraction
- **Analysis**: Content overlap detection, out-of-frame elements, educational effectiveness
- **Components**: `src/simple_video_evaluator.py` (enhanced version)
- **Output**: Detailed quality reports with actionable recommendations

### 📐 Position Mapping & Layout System
**INTELLIGENT-LAYOUT-MANAGEMENT**: Advanced collision detection and resolution
- **Features**: Element tracking across time, overlap prevention, automatic reflow
- **Components**: `src/position_mapper.py`, `src/layout/safe_layout_manager.py`
- **Algorithms**: Dynamic programming for optimal positioning, multi-strategy conflict resolution

### 🎬 Content Subdivision System  
**OPTIMAL-10MIN-SEGMENTATION**: Smart content breaking with part numbering
- **Algorithm**: Natural boundary detection, complexity analysis, duration optimization
- **Component**: `src/topic_subdivider.py` (enhanced with 10-minute optimization)
- **Output**: Intelligently named parts (e.g., "Limits - Part 1: Theory", "Limits - Part 2: Applications")

### 🔄 Content Reflow System
**SCENE-CONTINUITY-MANAGEMENT**: Element persistence and intelligent transitions
- **Features**: Cross-scene element tracking, automatic content reflow, priority-based element management
- **Component**: `src/content_reflow.py`
- **Strategies**: Scale-down, redistribute, paginate, stack-vertical, prioritize

### 📊 Comprehensive Reporting System
**DETAILED-ANALYTICS**: Complete pipeline performance analysis
- **Reports**: Agent performance, quality scores, layout analysis, reflow operations
- **Storage**: JSON reports with timestamps, searchable analysis data
- **Insights**: Learning patterns, common errors, optimization recommendations

---

### Legacy System Components

This repository also contains **the original book-to-video educational system** for compatibility:

### 🆕 Book-to-Video System (Primary Interface)
**TEXTBOOK-TO-MANIM**: Complete workflow from textbook content to educational videos
- **Workflow**: TEXT → POML → YAML → CODE → VIDEO
- **Components**: `src/book_processor.py`, `src/poml_generator.py`, `src/builder_llm.py`
- **Entry point**: `book_to_video.py`
- **Input**: Textbook files in `books/topic_name.txt` format
- **Output**: Professional educational animations with POML specifications

### 🎯 POML (Prompt Orchestration Markup Language) Layer
**Structured educational content description**
- **Purpose**: Bridge between raw text content and video generation
- **Components**: `src/schemas/poml_schema.py`, XML-based specification format
- **Features**: Educational roles, learning objectives, scene requirements, mathematical content
- **Validation**: Comprehensive POML validation and error reporting

### 🤖 Builder LLM System (Core Engine)
**MANIM-AUTOPILOT**: Deterministic code-writing assistant with strict layout safety
- **Workflow**: POML/OUTLINE → YAML → CODE → ACTION (480p → evaluation → 1080p)
- **Non-negotiable rules**: ≥6% safe margins, zero overlaps, ≥24px text legibility
- **Components**: `src/builder_llm.py`, `src/orchestrator.py`, `src/compiler.py`
- **POML Integration**: Enhanced to process structured educational content specifications

## Book Processing System Architecture

### Educational Content Workflow
**BookProcessor → POMLGenerator → BuilderLLM → VideoOrchestrator**

**src/book_processor.py (`BookProcessor`)**
- Parses textbook files from `books/topic_name.txt`
- Extracts structured sections (chapters, subsections) with hierarchical numbering
- Identifies educational elements: formulas, definitions, examples, key concepts
- Provides section filtering and search capabilities

**src/poml_generator.py (`POMLGenerator`)**
- Converts text sections into structured POML specifications
- Auto-detects subject areas (math, physics, chemistry, etc.) from content
- Generates educational roles, learning objectives, and scene requirements
- Creates subject-specific templates for optimal educational flow

**src/schemas/poml_schema.py (`POMLValidator`)**
- Validates POML structure and educational content requirements
- Ensures proper XML structure and semantic correctness
- Provides detailed error reporting with suggestions
- Validates educational effectiveness patterns

### Book Content Structure
Books should be formatted as plain text with markdown-style headers:
```
# Book Title
## Chapter X: Chapter Title
### Section X.Y: Section Title
Content with **key concepts**, formulas, and examples...
```

**Supported content types:**
- Mathematical formulas and equations
- Physics laws and relationships
- Definitions marked with bold text
- Examples and demonstrations
- Hierarchical learning progressions

## Builder LLM System Architecture

### State Machine Workflow
**VideoOrchestrator** manages the complete pipeline:
1. **BUILDING**: `BuilderLLM` generates OUTLINE → YAML → CODE → ACTION  
2. **COMPILING_480P**: `ManimCompiler` attempts 480p compilation with repair loop
3. **EVALUATING**: `EnhancedVideoEvaluator` performs frame-by-frame Gemini analysis
4. **PATCHING**: Apply fixes based on compilation errors or visual feedback
5. **COMPILING_1080P**: Final high-resolution compilation
6. **COMPLETED**: Workflow finished successfully

### Key Builder LLM Components

**src/builder_llm.py (`BuilderLLM`)**
- Master system prompt with deterministic instructions
- YAML specification generation with strict schema validation
- Unified diff patching for error repair
- Visual feedback repair integration

**src/orchestrator.py (`VideoOrchestrator`)**  
- Complete workflow state machine management
- Bounded retry logic with progressive repair strategies
- Integration between Builder LLM, compiler, and evaluator
- Comprehensive logging and debugging artifact storage

**src/compiler.py (`ManimCompiler`)**
- 480p → 1080p progressive compilation
- Scene detection and validation
- Comprehensive error analysis with suggestions
- Timeout handling and output file management

**src/schemas/** (YAML Validation System)
- `video_schema.py`: Strict YAML specification validation
- `layout_templates.py`: Grid templates (single, two_column, three_column)
- Template-based positioning with capacity enforcement

**src/layout/** (Safety Engine)
- `safe_layout_manager.py`: ≥6% margin enforcement, overlap prevention
- `collision_detector.py`: Frame-by-frame collision detection and resolution

**src/codegen/** (Code Generation)
- `manim_generator.py`: Template-based code generation with safety utilities
- `helper_utilities.py`: Inline safety functions embedded in generated code

**src/enhanced_video_evaluator.py**
- Extends existing evaluator with Builder LLM YAML format
- Frame-by-frame analysis for layout safety validation
- Structured issue reporting with actionable fix suggestions

### Legacy System Components

**src/generator.py (`FinalManimGenerator`)**
- Main orchestrator class that handles the complete animation generation pipeline
- Implements advanced shot-by-shot approach with layout safety
- Contains progressive error fixing strategies (5 levels of fixes)
- Integrates with video quality evaluation system

**src/video_evaluator.py (`VideoEvaluator`)**
- Gemini 2.5 Flash-Lite integration for video quality assessment
- Detects overlapping elements, out-of-frame content, and visual correctness issues
- Provides structured feedback for automated quality fixes

### Three-Phase Generation Process

1. **Content Planning Phase** - GPT-4 creates detailed educational structure using `content_schema.yaml`
2. **Code Generation Phase** - GPT-4 converts structure to working Manim code using `manim_api.yaml`  
3. **Video Quality Evaluation Phase** - Gemini evaluates output and applies fixes if needed

### Configuration System

**src/config/content_schema.yaml** - Shot-by-shot template defining:
- Global layout rules preventing overlapping elements
- Educational flow progression (hook → foundations → concepts → examples → applications)
- Safe area margins and positioning constraints

**src/config/manim_api.yaml** - Modern Manim API reference containing:
- Correct animation names (`Create` not `ShowCreation`)
- Safe positioning system with named regions
- Layout safety rules and best practices

**src/config/manim_parameter_fixes.yaml** - Parameter correction database:
- Common parameter errors and their fixes
- Progressive fix strategies for compilation errors
- Fallback templates for last-resort recovery

**src/config/video_evaluation_schema.yaml** - Quality assessment criteria:
- Visual correctness standards
- Overlap detection requirements  
- Frame boundary constraints

### Error Recovery System

The generator implements **progressive error fixing** with 5 strategies:
1. Parameter corrections using fix database
2. API modernization (deprecated → modern calls)
3. Object simplification (remove problematic elements)
4. Targeted LLM repair with error context
5. Fallback to working template

### Layout Safety Architecture

- **Safe area margins**: 0.7 units from left/right, 0.5 units from top/bottom
- **Per-region capacity**: Maximum 1 element per screen region simultaneously  
- **Minimum gap**: 0.6 units between all visible elements
- **Region system**: `center`, `top`, `bottom`, `left`, `right`, `top_left`, `top_right`, `bottom_left`, `bottom_right`

### Output Structure

```
output/
├── animations/          # Generated Python animation files
├── content/            # YAML content structures  
├── feedback/           # Video evaluation feedback
media/videos/           # Final MP4 video output
```

## Key Integration Points

**For content generation:** Use `generate_detailed_content_yaml()` which enforces layout rules and educational flow patterns.

**For code generation:** Use `generate_shot_based_manim_code()` which applies modern Manim API and positioning constraints.

**For error handling:** The system automatically applies progressive fixes - avoid manual error correction.

**For quality assurance:** Video evaluation runs automatically if `GEMINI_API_KEY` is provided, with up to 3 quality improvement iterations.

## Important Constraints

- **No external assets**: System cannot use `ImageMobject` or external files
- **Token limits**: Error context is intelligently truncated to stay within API limits  
- **Educational focus**: All content must follow structured educational patterns
- **3Blue1Brown standards**: Dark minimalist aesthetic with smooth animations

## Development Workflow

**For adding new features:**
1. Understand the dual-system architecture (Builder LLM vs Legacy)
2. Check configuration files in `src/config/` for schema and API references
3. Layout safety is enforced by `src/layout/` and `src/autolayout/` modules
4. Test changes with both `python run.py` and `python run.py --builder`

**For debugging video generation issues:**
1. Check `output/` directories for generated artifacts 
2. Use `--debug` flag with Builder LLM for detailed logs
3. Progressive error fixing happens automatically - avoid manual intervention
4. Video evaluation reports are saved in `output/feedback/`

**Key file patterns:**
- `src/config/*.yaml` - Configuration schemas and API references
- `src/schemas/` - YAML validation and templates
- `src/layout/` + `src/autolayout/` - Layout safety enforcement
- `src/codegen/` - Code generation templates and utilities