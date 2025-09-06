
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{"title": "Covalent Bonds: Lewis\'s Perspective", "slides": [{"title": "Covalent Bonds: Lewis\'s Perspective", "bullets": ["Understand the concept of covalent bonding and its purpose.", "Identify and differentiate between single, double, and triple covalent bonds.", "Learn to draw Lewis structures for simple molecules.", "Recognize the properties of covalent compounds."], "formulas": ["Lewis Structure Notation"]}, {"title": "Covalent Bond", "bullets": ["Covalent Bond", "A chemical bond formed when two atoms share one or more pairs of electrons to achieve a full outer shell."], "formulas": ["Lewis Structure Notation"]}, {"title": "Lewis Structure", "bullets": ["Lewis Structure", "A diagrammatic representation of molecules showing how atoms share electrons."], "formulas": ["Lewis Structure Notation"]}, {"title": "Hydrogen Molecule (H₂)", "bullets": ["Each hydrogen atom shares one electron, forming a single covalent bond: H–H."], "formulas": []}, {"title": "Oxygen Molecule (O₂)", "bullets": ["Each oxygen atom shares two electrons, forming a double covalent bond: O=O."], "formulas": []}, {"title": "Nitrogen Molecule (N₂)", "bullets": ["Each nitrogen atom shares three electrons, forming a triple covalent bond: N≡N."], "formulas": []}, {"title": "Formation of Covalent Bonds", "bullets": ["Covalent bonds form when atoms share electrons to fill their outer electron shells, achieving a stable electron configuration similar to noble gases."], "formulas": []}, {"title": "Types of Covalent Bonds", "bullets": ["Single bonds involve one pair of shared electrons, double bonds involve two pairs, and triple bonds involve three pairs, each with increasing bond strength and decreasing bond length."], "formulas": []}], "meta": {"audience": "undergraduate", "estimated_duration": 10, "difficulty": "intermediate"}}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
