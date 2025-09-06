
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{"title": "Introduction to Chemical Bonding", "slides": [{"title": "Introduction to Chemical Bonding", "bullets": ["Understand the Kössel–Lewis approach to chemical bonding", "Identify the role of valence electrons in bonding", "Differentiate between ionic and covalent bonds", "Recognize the stability of noble gases and its influence on bonding theories"], "formulas": ["Lewis Dot Structure"]}, {"title": "Valence Electrons", "bullets": ["Valence Electrons", "Electrons in the outermost shell of an atom that are involved in forming bonds."], "formulas": ["Lewis Dot Structure"]}, {"title": "Noble Gases", "bullets": ["Noble Gases", "Elements with full valence shells, exhibiting minimal reactivity."], "formulas": ["Lewis Dot Structure"]}, {"title": "Ionic Bond", "bullets": ["Ionic Bond", "A chemical bond formed through the transfer of electrons from one atom to another."], "formulas": ["Lewis Dot Structure"]}, {"title": "Covalent Bond", "bullets": ["Covalent Bond", "A chemical bond formed by the sharing of electron pairs between atoms."], "formulas": ["Lewis Dot Structure"]}, {"title": "Formation of NaCl", "bullets": ["Sodium (Na) transfers one electron to Chlorine (Cl), forming an ionic bond.", "Na becomes Na⁺ and Cl becomes Cl⁻, resulting in NaCl."], "formulas": []}, {"title": "Formation of H2O", "bullets": ["Oxygen shares electrons with two hydrogen atoms, forming covalent bonds to create a water molecule."], "formulas": []}, {"title": "Kössel–Lewis Approach", "bullets": ["Walter Kössel and Gilbert N.", "Lewis independently proposed that atoms achieve stability by attaining a noble gas electron configuration, either by transferring or sharing electrons."], "formulas": []}, {"title": "Noble Gas Stability", "bullets": ["Noble gases are chemically inert due to their full valence electron shells, serving as a model for understanding atomic stability in bonding."], "formulas": []}], "meta": {"audience": "undergraduate", "estimated_duration": 10, "difficulty": "intermediate"}}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
