"""
POML Generator for Educational Content

This module generates POML (Prompt Orchestration Markup Language) files
from processed book sections for structured scene descriptions.
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
try:
    from .book_processor import TextSection, BookContent
except ImportError:
    from book_processor import TextSection, BookContent


@dataclass
class POMLTemplate:
    """Template for generating POML content"""
    subject_area: str  # math, physics, chemistry, etc.
    educational_level: str  # undergraduate, graduate, high_school
    role_template: str
    task_template: str
    output_format_template: str


class POMLGenerator:
    """Generates POML files from educational content sections"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.subject_keywords = {
            'math': ['derivative', 'integral', 'limit', 'function', 'equation', 'theorem', 'proof'],
            'physics': ['force', 'velocity', 'acceleration', 'energy', 'momentum', 'wave', 'field'],
            'chemistry': ['molecule', 'atom', 'reaction', 'bond', 'element', 'compound'],
            'biology': ['cell', 'organism', 'gene', 'protein', 'evolution', 'metabolism'],
            'computer_science': ['algorithm', 'data structure', 'complexity', 'programming', 'software']
        }
    
    def _initialize_templates(self) -> Dict[str, POMLTemplate]:
        """Initialize POML templates for different subject areas"""
        templates = {}
        
        # Mathematics template
        templates['math'] = POMLTemplate(
            subject_area='math',
            educational_level='undergraduate',
            role_template="""You are an expert mathematics educator specializing in visual learning through animations. You create clear, step-by-step explanations that build mathematical intuition through visual representations. Your animations follow the 3Blue1Brown aesthetic with smooth transitions and elegant mathematical visualizations.""",
            task_template="""Create a Manim animation that teaches {concept} by:
1. Introducing the concept with clear visual context
2. Showing step-by-step mathematical development
3. Providing concrete examples with visual demonstrations
4. Highlighting key insights and connections
5. Using smooth animations to reveal mathematical relationships

Focus on building intuitive understanding through visual representation.""",
            output_format_template="""Generate clean, educational Manim code following these requirements:
- Use 3Blue1Brown dark theme aesthetic
- Implement smooth animations (run_time=2-3 seconds)
- Include clear mathematical notation with proper LaTeX formatting
- Follow safe layout positioning with no overlapping elements
- Add explanatory text animations synchronized with visual elements
- Ensure all content fits within frame boundaries
- Use appropriate colors: BLUE for primary concepts, YELLOW for highlights, WHITE for text

YAML STRUCTURE REQUIREMENTS:
- Include ALL required fields: topic, audience, style, global, scenes
- Each scene MUST have: id, goal, time_budget_s, narration, layout, checks
- Text elements MUST have: key, type, column, and text/content field
- Use template: "single" (not "singl")"""
        )
        
        # Physics template
        templates['physics'] = POMLTemplate(
            subject_area='physics',
            educational_level='undergraduate',
            role_template="""You are an expert physics educator who specializes in making abstract physical concepts concrete through dynamic visualizations. You excel at showing the relationship between mathematical descriptions and physical reality through animated demonstrations.""",
            task_template="""Create a Manim animation that demonstrates {concept} by:
1. Setting up the physical scenario with clear visual context
2. Showing the mathematical relationships governing the physics
3. Animating the physical behavior and changes over time
4. Connecting equations to observable phenomena
5. Highlighting cause-and-effect relationships

Emphasize the connection between mathematical formulation and physical intuition.""",
            output_format_template="""Generate educational Manim code with these specifications:
- Use realistic physical representations and motion
- Implement time-based animations showing evolution of physical systems
- Include vector representations for forces, velocities, and fields
- Use appropriate physics color coding (red=force, blue=velocity, green=acceleration)
- Add real-time parameter displays and measurements
- Ensure accurate scale relationships and proportions
- Follow 3Blue1Brown aesthetic standards

YAML STRUCTURE REQUIREMENTS:
- Include ALL required fields: topic, audience, style, global, scenes
- Each scene MUST have: id, goal, time_budget_s, narration, layout, checks
- Text elements MUST have: key, type, column, and text/content field
- Use template: "single" (not "singl")"""
        )
        
        # General template for other subjects
        templates['general'] = POMLTemplate(
            subject_area='general',
            educational_level='general',
            role_template="""You are an expert educational animator who creates engaging visual content for learning. You specialize in breaking down complex concepts into clear, digestible visual sequences that promote understanding and retention.""",
            task_template="""Create a Manim animation that explains {concept} by:
1. Introducing the topic with engaging visual hooks
2. Breaking down complex ideas into simple components
3. Using visual metaphors and analogies where appropriate
4. Providing clear examples and demonstrations
5. Building up to the complete understanding step by step

Focus on clarity, engagement, and educational effectiveness.""",
            output_format_template="""Generate educational Manim code with these standards:
- Use clean, professional visual design
- Implement smooth, purposeful animations
- Include clear typography and readable text
- Follow consistent color scheme and styling
- Ensure proper pacing and timing
- Maintain visual hierarchy and focus
- Follow layout safety guidelines

YAML STRUCTURE REQUIREMENTS:
- Include ALL required fields: topic, audience, style, global, scenes
- Each scene MUST have: id, goal, time_budget_s, narration, layout, checks
- Text elements MUST have: key, type, column, and text/content field
- Use template: "single" (not "singl")"""
        )
        
        return templates
    
    def detect_subject_area(self, section: TextSection) -> str:
        """Detect the subject area of a text section based on keywords"""
        content_lower = (section.title + " " + section.content).lower()
        
        subject_scores = {}
        for subject, keywords in self.subject_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                subject_scores[subject] = score
        
        if subject_scores:
            return max(subject_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'general'
    
    def generate_poml_for_section(self, section: TextSection, 
                                subject_override: Optional[str] = None,
                                duration: int = 45,
                                audience: str = "undergraduate") -> str:
        """Generate a POML file for a given text section"""
        
        # Detect or use override subject
        subject = subject_override or self.detect_subject_area(section)
        template = self.templates.get(subject, self.templates['general'])
        
        # Extract key concepts and formulas
        key_formulas = section.educational_elements.get('formulas', [])
        key_concepts = section.educational_elements.get('key_concepts', [])
        definitions = section.educational_elements.get('definitions', [])
        
        # Generate concept description for templates
        concept_description = section.title
        if key_concepts:
            concept_description += f" focusing on {', '.join(key_concepts[:3])}"
        
        # Build POML content
        poml_content = self._build_poml_structure(
            section=section,
            template=template,
            concept_description=concept_description,
            duration=duration,
            audience=audience,
            formulas=key_formulas,
            definitions=definitions
        )
        
        return poml_content
    
    def _build_poml_structure(self, section: TextSection, template: POMLTemplate,
                            concept_description: str, duration: int, audience: str,
                            formulas: List[str], definitions: List[str]) -> str:
        """Build the complete POML structure"""
        
        # Format templates with section-specific content
        role_content = template.role_template
        task_content = template.task_template.format(concept=concept_description)
        output_format_content = template.output_format_template
        
        # Build scene requirements based on content
        scene_elements = self._generate_scene_elements(section, template.subject_area)
        
        poml_content = f"""<poml version="1.0">
  
  <role>
    {role_content}
  </role>
  
  <task>
    {task_content}
  </task>
  
  <content source="book_section" title="{section.title}" section_number="{section.section_number}">
    {self._escape_xml_content(section.content[:500])}...
  </content>
  
  <educational-context>
    <subject>{template.subject_area}</subject>
    <audience>{audience}</audience>
    <duration>{duration} seconds</duration>
    <learning-objectives>
      {self._generate_learning_objectives(section)}
    </learning-objectives>
  </educational-context>
  
  <scene-requirements>
    <duration>{duration} seconds</duration>
    <elements>
{scene_elements}
    </elements>
    <animations>
      <style>smooth</style>
      <timing>synchronized</timing>
      <transitions>fade</transitions>
    </animations>
  </scene-requirements>
  
  {self._generate_mathematical_content(formulas, definitions)}
  
  <visual-guidelines>
    <theme>3blue1brown</theme>
    <background>dark</background>
    <colors>
      <primary>BLUE</primary>
      <accent>YELLOW</accent>
      <text>WHITE</text>
      <highlight>GREEN</highlight>
    </colors>
    <layout>
      <margins>safe</margins>
      <positioning>grid-based</positioning>
      <overlap-prevention>enabled</overlap-prevention>
    </layout>
  </visual-guidelines>
  
  <output-format>
    {output_format_content}
    
    Ensure the generated code:
    - Creates exactly one scene class called 'EducationalScene'
    - Implements the construct() method with the complete animation
    - Uses proper Manim imports and syntax
    - Follows the educational flow: setup → explanation → examples → conclusion
    - Includes appropriate wait times between concepts
  </output-format>
  
</poml>"""
        
        return poml_content
    
    def _generate_scene_elements(self, section: TextSection, subject: str) -> str:
        """Generate scene elements based on content and subject"""
        elements = []
        
        # Add title
        elements.append(f'      <text position="top" style="title">{section.title}</text>')
        
        # Add subject-specific elements
        if subject == 'math':
            if section.educational_elements.get('formulas'):
                elements.append('      <mathtex position="center" style="formula">Key mathematical expressions</mathtex>')
            elements.append('      <axes position="center_right" style="coordinate_system"/>')
            
        elif subject == 'physics':
            elements.append('      <diagram position="center" style="physics_scenario"/>')
            elements.append('      <vector position="center_left" style="force_vector"/>')
            elements.append('      <text position="bottom" style="measurement">Measurements and values</text>')
            
        else:
            elements.append('      <diagram position="center" style="conceptual"/>')
            elements.append('      <text position="center_left" style="explanation">Step-by-step explanation</text>')
        
        # Add definitions if present
        if section.educational_elements.get('definitions'):
            elements.append('      <text position="bottom_left" style="definition">Key definitions</text>')
        
        return '\n'.join(elements)
    
    def _generate_learning_objectives(self, section: TextSection) -> str:
        """Generate learning objectives from section content"""
        objectives = []
        
        # Extract key concepts as objectives
        key_concepts = section.educational_elements.get('key_concepts', [])
        for concept in key_concepts[:3]:
            objectives.append(f"      - Understand the concept of {concept.lower()}")
        
        # Add formula-based objectives
        formulas = section.educational_elements.get('formulas', [])
        if formulas:
            objectives.append("      - Apply relevant mathematical formulas")
        
        # Add general comprehension objective
        objectives.append(f"      - Explain the key ideas in {section.title.lower()}")
        
        return '\n'.join(objectives) if objectives else "      - Understand the main concepts"
    
    def _generate_mathematical_content(self, formulas: List[str], definitions: List[str]) -> str:
        """Generate mathematical content section if applicable"""
        if not formulas and not definitions:
            return ""
        
        content = "  <mathematical-content>\n"
        
        if formulas:
            content += "    <formulas>\n"
            for i, formula in enumerate(formulas[:3]):  # Limit to 3 formulas
                escaped_formula = self._escape_xml_content(formula)
                content += f'      <formula id="f{i+1}">{escaped_formula}</formula>\n'
            content += "    </formulas>\n"
        
        if definitions:
            content += "    <definitions>\n"
            for i, definition in enumerate(definitions[:2]):  # Limit to 2 definitions
                escaped_def = self._escape_xml_content(definition)
                content += f'      <definition id="d{i+1}">{escaped_def}</definition>\n'
            content += "    </definitions>\n"
        
        content += "  </mathematical-content>\n"
        return content
    
    def _escape_xml_content(self, content: str) -> str:
        """Escape XML special characters in content"""
        content = content.replace('&', '&amp;')
        content = content.replace('<', '&lt;')
        content = content.replace('>', '&gt;')
        content = content.replace('"', '&quot;')
        content = content.replace("'", '&apos;')
        return content
    
    def save_poml_file(self, poml_content: str, output_path: str) -> str:
        """Save POML content to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(poml_content)
        
        return str(output_file)
    
    def generate_poml_batch(self, book: BookContent, 
                          sections_filter: Optional[List[str]] = None,
                          output_dir: str = "output/poml") -> List[str]:
        """Generate POML files for multiple sections"""
        
        # Determine which sections to process
        if sections_filter:
            sections_to_process = [
                s for s in book.sections 
                if any(f in s.section_number for f in sections_filter)
            ]
        else:
            sections_to_process = book.sections
        
        generated_files = []
        
        for section in sections_to_process:
            # Generate POML content
            poml_content = self.generate_poml_for_section(section)
            
            # Create filename
            safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', section.title.lower())
            filename = f"{section.section_number}_{safe_title}.poml"
            output_path = Path(output_dir) / book.title.lower().replace(' ', '_') / filename
            
            # Save file
            saved_file = self.save_poml_file(poml_content, str(output_path))
            generated_files.append(saved_file)
        
        return generated_files


def main():
    """Test the POML generator"""
    from .book_processor import BookProcessor
    
    # Initialize components
    book_processor = BookProcessor()
    poml_generator = POMLGenerator()
    
    # Load a book
    books = book_processor.get_available_books()
    if not books:
        print("No books available. Add some .txt files to the books/ directory.")
        return
    
    book = book_processor.load_book(books[0])
    print(f"Loaded book: {book.title}")
    
    # Generate POML for first section
    if book.sections:
        section = book.sections[0]
        print(f"\nGenerating POML for: {section.title}")
        
        poml_content = poml_generator.generate_poml_for_section(section)
        
        # Save to file
        output_path = f"temp/test_{section.title.lower().replace(' ', '_')}.poml"
        saved_file = poml_generator.save_poml_file(poml_content, output_path)
        print(f"Saved POML to: {saved_file}")
        
        # Show preview
        print("\n--- POML Preview ---")
        print(poml_content[:500] + "...")


if __name__ == "__main__":
    main()