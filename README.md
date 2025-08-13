# LLM-Based Manim Code Generator

An automated tool that generates 3Blue1Brown-style Manim animations using OpenAI's GPT-4. Simply provide a topic, and the system will generate, compile, and fix Manim code automatically until it produces a working video.

## Features

- **AI-Powered Code Generation**: Uses GPT-4 to create educational Manim animations
- **Automatic Error Detection**: Reads compilation errors and identifies issues
- **Self-Healing Code**: Automatically fixes errors and retries compilation
- **3Blue1Brown Style**: Generates high-quality mathematical visualizations
- **Retry Logic**: Attempts up to 5 times to create a working animation

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key as an environment variable:
```bash
set OPENAI_API_KEY=your_api_key_here
```

Alternatively, the program will prompt you to enter the API key when you run it.

## Usage

Run the main script:
```bash
python manim_code_generator.py
```

Then enter topics when prompted, for example:
- "Pythagorean theorem"
- "Fourier transform visualization"
- "Prime numbers and the Riemann zeta function"
- "Linear algebra transformations"

## How It Works

1. **Code Generation**: GPT-4 generates a complete Manim script for your topic
2. **Compilation**: The system attempts to compile the animation
3. **Error Detection**: If errors occur, they are captured and analyzed
4. **Auto-Fixing**: GPT-4 analyzes the error and generates a fixed version
5. **Retry Loop**: This process repeats up to 5 times until success

## Output

Generated animations are saved in the `generated_animations/` directory as both Python files and rendered videos.

## Example Topics

- Mathematical concepts (calculus, linear algebra, statistics)
- Physics simulations (waves, oscillations, mechanics)
- Computer science algorithms (sorting, graph theory)
- Data visualization concepts