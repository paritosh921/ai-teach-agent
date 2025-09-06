
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{"title": "Understanding the Octet Rule", "slides": [{"title": "Understanding the Octet Rule", "bullets": ["Understand the basic principle of the octet rule.", "Identify how atoms achieve stable electron configurations through bonding.", "Recognize the limitations and exceptions to the octet rule."], "formulas": ["Electron Count = 8"]}, {"title": "Octet Rule", "bullets": ["Octet Rule", "Atoms tend to gain, lose, or share electrons to achieve a full set of eight valence electrons, similar to noble gases."], "formulas": ["Electron Count = 8"]}, {"title": "Noble Gas Configuration", "bullets": ["Noble Gas Configuration", "A stable electron configuration with a full outer shell of electrons, typically eight."], "formulas": ["Electron Count = 8"]}, {"title": "Ionic Bonding in NaCl", "bullets": ["Sodium donates an electron to chlorine, resulting in Na⁺ and Cl⁻ ions, both achieving octet configurations."], "formulas": []}, {"title": "Covalent Bonding in CH₄", "bullets": ["Carbon shares electrons with four hydrogen atoms, achieving a stable octet through shared electron pairs."], "formulas": []}, {"title": "6.1 Definition", "bullets": ["The octet rule is based on the observation that atoms are most stable when they have eight electrons in their valence shell.", "This stability is akin to the electron configuration of noble gases, which are inert due to their full valence shells."], "formulas": []}, {"title": "6.2 Examples", "bullets": ["Atoms can achieve an octet through ionic or covalent bonding.", "In ionic bonding, electrons are transferred to achieve full outer shells, as seen in NaCl.", "In covalent bonding, atoms share electrons, as in CH₄."], "formulas": []}, {"title": "6.3 Limitations", "bullets": ["The octet rule has limitations.", "Some atoms like hydrogen achieve stability with fewer electrons.", "Others, like sulfur in SF₆, can have expanded octets.", "Additionally, molecules like NO have an odd number of electrons."], "formulas": []}], "meta": {"audience": "undergraduate", "estimated_duration": 10, "difficulty": "intermediate"}}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
