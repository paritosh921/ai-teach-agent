
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{"title": "Contributions of Gilbert N. Lewis", "slides": [{"title": "Contributions of Gilbert N. Lewis", "bullets": ["Understand the concept of covalent bonding as proposed by Gilbert N. Lewis.", "Learn how to represent molecules using Lewis dot structures.", "Differentiate between ionic and covalent bonds.", "Apply Lewis\'s concepts to predict molecular stability."], "formulas": ["Electron Pair Bond"]}, {"title": "Covalent Bonding", "bullets": ["Covalent Bonding", "A type of chemical bond where two atoms share pairs of electrons to achieve a stable electron configuration."], "formulas": ["Electron Pair Bond"]}, {"title": "Lewis Dot Structures", "bullets": ["Lewis Dot Structures", "A visual representation of the valence electrons in an atom or molecule, using dots around the element symbols."], "formulas": ["Electron Pair Bond"]}, {"title": "Water Molecule (H₂O)", "bullets": ["In H₂O, each hydrogen atom shares one electron with the oxygen atom, forming two covalent bonds.", "The oxygen atom also has two lone pairs of electrons."], "formulas": []}, {"title": "Methane (CH₄)", "bullets": ["In CH₄, the carbon atom shares one electron with each of the four hydrogen atoms, forming four covalent bonds."], "formulas": []}, {"title": "Covalent Bonding", "bullets": ["Unlike ionic bonds where electrons are transferred, covalent bonds involve the sharing of electron pairs between atoms.", "This sharing allows each atom to attain the electron configuration of a noble gas, achieving stability."], "formulas": []}, {"title": "Lewis Dot Structures", "bullets": ["Lewis dot structures provide a simple way to visualize the valence electrons in an atom.", "By arranging dots around the element symbols, we can depict how atoms bond and form molecules."], "formulas": []}], "meta": {"audience": "undergraduate", "estimated_duration": 10, "difficulty": "intermediate"}}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
