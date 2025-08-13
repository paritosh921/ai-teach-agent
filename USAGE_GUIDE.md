# Improved Manim Generator - Usage Guide

## 🎯 How It Works

The improved system uses a **two-phase approach**:

1. **Phase 1: Content Planning** 📋
   - LLM creates structured educational content in YAML format
   - Focuses on pedagogy, learning objectives, and visual planning
   - Separates content design from technical implementation

2. **Phase 2: Code Generation** 🔧
   - LLM generates Manim code based on the YAML structure
   - Focuses purely on technical implementation
   - Results in better, more consistent animations

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the improved generator
python improved_manim_generator.py
```

## 📋 What You'll Get

For each topic, the system creates:

1. **`generated_content/topic_content.yaml`** - Educational content structure
2. **`generated_animations/topic_animation.py`** - Manim code
3. **`media/videos/`** - Final rendered video

## 🎨 Content Structure Features

The YAML content includes:
- **Learning objectives** and educational flow
- **Visual metaphors** for complex concepts  
- **Mathematical elements** (formulas, graphs)
- **Timing and pacing** for each section
- **Animation specifications** for each visual

## 🔧 Technical Improvements

- ✅ Fixed path handling issues
- ✅ Added ffmpeg support via imageio-ffmpeg
- ✅ Better error detection and auto-fixing
- ✅ Structured content planning
- ✅ Separation of concerns (content vs code)

## 📖 Example Usage

```python
# The system will prompt you for topics like:
"Integration"
"Fourier Transform" 
"Neural Networks"
"Quantum Mechanics"
"Graph Theory"
```

## 🎭 3Blue1Brown Style Features

- **Progressive revelation** of concepts
- **Visual metaphors** for abstract ideas
- **Mathematical rigor** with intuitive explanations
- **Smooth animations** and professional styling
- **Logical story flow** from simple to complex

## 🐛 Debugging

If animations fail:
1. Check the generated YAML file for content issues
2. Review the Python code for Manim syntax errors  
3. The system will auto-retry up to 5 times with fixes
4. Content and code are saved separately for manual editing

## 🎥 Video Output

Videos are saved in: `media/videos/[resolution]/[filename].mp4`

The system uses `-pql` (preview quality, low resolution) by default for faster testing.

## 💡 Pro Tips

1. **Start simple** - Test with basic math topics first
2. **Check YAML** - Review the content structure if results aren't good
3. **Manual editing** - You can edit the YAML and re-run code generation
4. **ffmpeg** - Install ffmpeg properly for best video quality