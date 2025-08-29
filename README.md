# 🎬 Manim LLM Generator

Professional educational animation generator that creates 3Blue1Brown-style videos using AI and Manim.

## ✨ **Features**

- 🧠 **AI-Powered Content Creation** - GPT-4 generates educational content structure
- 🎯 **Shot-by-Shot Precision** - Film-quality timeline prevents overlapping visuals
- 🔧 **Smart Error Fixing** - Automatic code repair with focused context
- 🎨 **Professional Quality** - 3Blue1Brown educational standards
- 📚 **Wide Topics** - Mathematics, Physics, Chemistry, Computer Science
- 🚀 **LLM-Powered Text Processing** - Intelligently processes ANY text format
- 🎭 **Format Agnostic** - Works with academic papers, lecture notes, blog posts, etc.
- 📊 **Smart Content Extraction** - Automatically identifies concepts, formulas, and visuals

## 🚀 **Quick Start**

### **Installation**
```bash
# Navigate to the project directory
cd "path/to/manim-llm-generator"

# Install dependencies
pip install -r requirements.txt

# Copy environment template and set your API keys
cp env_template.txt .env
# Edit .env file with your API keys
```

### **Setup API Keys**
1. Copy `env_template.txt` to `.env`
2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   GEMINI_API_KEY=your-gemini-api-key-here  # Optional
   ```

### **Usage**
```bash
# Test that everything is working
python test_simple_generation.py

# Generate video from book content
python book_to_video.py --book "calculus" --section "1.1"

# Generate entire chapter with enhanced features
python enhanced_book_to_video.py --book "physics" --chapter 2

# List available books
python book_to_video.py --list-books

# Interactive mode
python enhanced_book_to_video.py --book "calculus" --interactive

# Test LLM-powered processing capabilities
python demo_llm_book_processor.py

# Full LLM processing test (requires API key)
python test_llm_book_processor.py
```

## 🧠 **LLM-Powered Text Processing**

The system now uses advanced AI to intelligently process **any text format**, eliminating the need for rigid structure requirements.

### **What It Can Process**
- ✅ **Academic Papers**: "In this paper, we demonstrate..."
- ✅ **Lecture Notes**: "Today we'll cover: 1. Topic A 2. Topic B"
- ✅ **Blog Posts**: "Let me explain this concept..."
- ✅ **Textbooks**: Traditional structured format
- ✅ **Mixed Formats**: Combination of different styles
- ✅ **Handwritten Notes**: Scanned or transcribed content

### **Intelligent Extraction**
- 🎯 **Automatic Section Detection** - Identifies chapters and subsections
- 💡 **Concept Recognition** - Finds key educational concepts
- 📐 **Formula Detection** - Extracts mathematical expressions
- 👁️ **Visual Suggestions** - Recommends animations and diagrams
- 📊 **Difficulty Assessment** - Gauges content complexity
- 🎯 **Learning Objectives** - Generates pedagogical goals

### **Example**
**Input**: Any educational text in any format
**Output**: Structured content ready for video generation

## 📁 **Project Structure**

```
manim-llm-generator/
├── src/
│   ├── llm_book_processor.py     # LLM-powered text processing
│   ├── llm_book_adapter.py       # Backward compatibility adapter
│   ├── book_processor.py         # Traditional text processor
│   ├── enhanced_orchestrator.py  # Enhanced video generation
│   ├── orchestrator.py           # Main video orchestrator
│   ├── builder_llm.py            # AI content generation
│   ├── poml_generator.py         # Content structure generation
│   ├── config/
│   │   ├── content_schema.yaml   # Shot-by-shot template
│   │   ├── manim_api.yaml        # Manim API reference
│   │   ├── manim_parameter_fixes.yaml  # Common fixes
│   │   └── video_evaluation_schema.yaml # Evaluation schema
│   └── autolayout/               # Layout management
├── books/                        # Educational content files
├── cache/                        # LLM-processed content cache
├── output/                       # Generated files (auto-created)
├── media/                        # Manim video output (auto-created)
├── requirements.txt
├── enhanced_book_to_video.py     # Enhanced generation script
├── book_to_video.py              # Basic generation script
├── demo_llm_book_processor.py    # LLM capabilities demo
├── test_llm_book_processor.py    # Full LLM processor test
├── .gitignore
└── README.md
```

## 🎯 **How It Works**

### **Two-Phase Approach**
1. **Content Planning** - AI creates detailed educational structure
2. **Code Generation** - AI converts structure to working Manim code

### **Shot-by-Shot Timeline**
Each animation is broken into precise shots:
```yaml
shots:
  - shot_id: "intro_01"
    start_time: 0
    end_time: 5
    scene_state: "clean"    # Prevents overlapping
    elements:
      - type: "text"
        position: "center"
        animation: "write"
```

### **Smart Error Handling**
- Focused error context (no token limits)
- Modern Manim API usage (`Create` not `ShowCreation`)
- Automatic retry with targeted fixes

## 📊 **Example Topics**

**Mathematics:**
- "Derivatives and Tangent Lines"
- "Fourier Series Visualization"
- "Linear Algebra Transformations"
- "Integration by Parts"

**Physics:**
- "Wave Interference"
- "Electromagnetic Fields" 
- "Quantum Superposition"
- "Thermodynamics"

**Chemistry:**
- "Chemical Bonding"
- "Molecular Orbital Theory"
- "Reaction Kinetics"

**Computer Science:**
- "Sorting Algorithms"
- "Neural Networks"
- "Graph Theory"

## 🔧 **Requirements**

- **Python 3.8+**
- **Manim 0.19.0+** - Animation library
- **OpenAI API Key** - For GPT-4 access
- **ffmpeg** - For video rendering (auto-installed via imageio-ffmpeg)

## 🎨 **Output Quality**

The generator creates:
- **Clean visual layouts** with no overlapping elements
- **Professional timing** and smooth transitions  
- **Educational effectiveness** with clear concept progression
- **3Blue1Brown style** mathematics visualization
- **HD video files** ready for sharing

## 🔍 **Debugging**

If generation fails:
1. **Content YAML** saved in `output/content/` for review
2. **Python code** saved in `output/animations/` for manual fixes
3. **Focused error messages** for specific issues
4. **Video files** in `media/videos/` when successful

## 🏆 **Advanced Features**

### **Professional Animation Patterns**
- Automatic scene clearing between concepts
- Coordinated object positioning  
- Proper Manim API usage
- Educational flow optimization

### **Content Structure**
- Learning objectives and key concepts
- Visual metaphors for abstract ideas
- Mathematical formulas with LaTeX
- Shot-by-shot timing control

### **Error Recovery**
- Token limit management
- API reference integration
- Common mistake prevention
- Iterative improvement

## 🤝 **Contributing**

This is a clean, structured project ready for:
- Adding new content templates
- Improving error handling
- Extending to other animation libraries
- Creating specialized educational modules

## 📄 **License**

Educational use encouraged. Professional 3Blue1Brown-quality animations made accessible through AI.

---

**Ready to create professional educational animations?**
```bash
python run.py
```