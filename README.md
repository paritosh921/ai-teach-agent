# 🎬 Manim LLM Generator

Professional educational animation generator that creates 3Blue1Brown-style videos using AI and Manim.

## ✨ **Features**

- 🧠 **AI-Powered Content Creation** - GPT-4 generates educational content structure  
- 🎯 **Shot-by-Shot Precision** - Film-quality timeline prevents overlapping visuals
- 🔧 **Smart Error Fixing** - Automatic code repair with focused context
- 🎨 **Professional Quality** - 3Blue1Brown educational standards
- 📚 **Wide Topics** - Mathematics, Physics, Chemistry, Computer Science

## 🚀 **Quick Start**

### **Installation**
```bash
# Clone or download this project
cd manim-llm-generator

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key (optional - will prompt if not set)
export OPENAI_API_KEY="your-api-key-here"
```

### **Usage**
```bash
# Run the generator
python run.py

# Enter topics when prompted:
Topic: Integration
Topic: Chemical Bonding
Topic: Fourier Transform
```

## 📁 **Project Structure**

```
manim-llm-generator/
├── src/
│   ├── generator.py              # Main generator logic
│   ├── config/
│   │   ├── content_schema.yaml   # Shot-by-shot template
│   │   └── manim_api.yaml       # Manim API reference
│   └── __init__.py
├── examples/
│   └── chemical_bonding.yaml    # Example content structure
├── output/                      # Generated files (ignored by git)
│   ├── animations/              # Python animation files
│   └── content/                 # YAML content structures
├── media/                       # Manim video output (ignored by git)
├── requirements.txt
├── run.py                       # Simple entry point
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