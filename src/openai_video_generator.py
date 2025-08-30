"""
OpenAI Video Generator - creates structured teaching content JSON
from a content chunk. Saves blueprints used by code generator.
"""

import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from openai import OpenAI

from .intelligent_chunker import ContentChunk


@dataclass
class TeachingContent:
    # Non-default fields first
    title: str
    content_chunk: ContentChunk
    introduction: str
    learning_objectives: List[str]
    key_concepts: List[Dict[str, str]]
    detailed_explanations: List[Dict[str, str]]
    examples: List[Dict[str, str]]
    applications: List[Dict[str, str]]
    formulas: List[Dict[str, str]]
    summary: str
    narration_script: str
    visual_cues: List[Dict[str, str]]
    animation_suggestions: List[str]
    estimated_duration: int
    difficulty_level: str
    audience: str
    # Defaulted fields last
    scenes: List[Dict[str, Any]] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "introduction": self.introduction,
            "learning_objectives": self.learning_objectives,
            "key_concepts": self.key_concepts,
            "detailed_explanations": self.detailed_explanations,
            "examples": self.examples,
            "applications": self.applications,
            "formulas": self.formulas,
            "summary": self.summary,
            "narration_script": self.narration_script,
            "visual_cues": self.visual_cues,
            "animation_suggestions": self.animation_suggestions,
            "scenes": self.scenes,
            "estimated_duration": self.estimated_duration,
            "difficulty_level": self.difficulty_level,
            "audience": self.audience,
            "prerequisites": self.prerequisites,
        }


class OpenAIVideoGenerator:
    TEACH_PROMPT = (
        "You are an expert educational content creator. Use the book content as reference, but expand deeply with your own knowledge. "
        "Generate a structured JSON plan for a {duration}-minute video in 3Blue1Brown style. Prioritize clarity, rigor, and visuals.\n\n"
        "TITLE: {title}\nAUDIENCE: {audience}\nCONTENT (REFERENCE):\n{content}\n\n"
        "REQUIREMENTS:\n"
        "- Build from first principles; add intuitive explanations, analogies, and misconceptions to avoid.\n"
        "- Include multiple worked examples and step-by-step derivations.\n"
        "- Include a detailed SCENES plan with diagrams and exact visual instructions for Manim.\n"
        "- Target scene density ~ 1-2 scenes per minute. Each scene includes diagram instructions and animation steps.\n"
        "- Do not copy the text; synthesize a better teaching flow.\n\n"
        "OUTPUT JSON KEYS:\n"
        "- introduction: string\n- learning_objectives: [strings]\n- key_concepts: [{{concept, definition}}]\n"
        "- detailed_explanations: [{{section, explanation}}]\n- examples: [{{title, content}}]\n- applications: [{{area, description}}]\n- formulas: [{{formula, explanation}}]\n- summary: string\n- narration_script: string\n"
        "- visual_cues: [{{time_hint, cue}}]\n- animation_suggestions: [strings]\n"
        "- scenes: [{{title, duration_sec, goal, diagram_instructions, manim_objects, layout, animation_sequence}}]\n"
    )

    ENRICH_PROMPT = (
        "Enrich the following teaching JSON to reach a more detailed, scene-rich plan.\n"
        "- Ensure at least {min_scenes} scenes and scene density ~1-2 per minute.\n"
        "- Expand derivations, add more diagrams (axes, number lines, vectors, graphs), and more examples.\n"
        "- Each scene must have diagram_instructions, manim_objects (Text, MathTex, Axes, NumberPlane, VGroup, Dot, Line, Arrow, Table, etc.), and animation_sequence.\n"
        "Return the entire updated JSON.\n\nJSON:\n{json}"
    )

    def __init__(self, openai_api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def generate_teaching_content(self, content_chunk: ContentChunk, audience: str = "undergraduate") -> Optional[TeachingContent]:
        prompt = self.TEACH_PROMPT.format(
            title=content_chunk.title,
            duration=content_chunk.estimated_duration,
            audience=audience,
            content=content_chunk.content[:16000],
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You create rigorous yet intuitive teaching plans."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=3000,
        )
        text = resp.choices[0].message.content.strip()
        data = self._extract_json(text)
        # Enrich if not detailed enough
        data = self._ensure_detail(data, content_chunk)
        if not data:
            return None
        tc = TeachingContent(
            title=content_chunk.title,
            content_chunk=content_chunk,
            introduction=data.get("introduction", ""),
            learning_objectives=data.get("learning_objectives", []),
            key_concepts=[kc if isinstance(kc, dict) else {"concept": str(kc), "definition": ""} for kc in data.get("key_concepts", [])],
            detailed_explanations=data.get("detailed_explanations", []),
            examples=data.get("examples", []),
            applications=data.get("applications", []),
            formulas=data.get("formulas", []),
            summary=data.get("summary", ""),
            narration_script=data.get("narration_script", ""),
            visual_cues=data.get("visual_cues", []),
            animation_suggestions=data.get("animation_suggestions", []),
            scenes=data.get("scenes", []),
            estimated_duration=content_chunk.estimated_duration,
            difficulty_level=data.get("difficulty_assessment", "intermediate"),
            audience=audience,
            prerequisites=content_chunk.prerequisites,
        )
        # Auto-save blueprint for downstream reference
        try:
            out_path = self.save_teaching_content(tc, "output/unified/teaching_content")
            if out_path:
                print(f"         ?? Blueprint saved: {out_path}")
        except Exception as e:
            print(f"         ?? Blueprint save failed: {e}")
        return tc

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        m = re.search(r"```json\s*(.*?)```", text, re.DOTALL)
        j = m.group(1) if m else text[text.find("{") : text.rfind("}") + 1]
        try:
            return json.loads(j)
        except Exception:
            return None

    def _ensure_detail(self, data: Optional[Dict[str, Any]], chunk: ContentChunk) -> Optional[Dict[str, Any]]:
        if not data:
            return None
        # Compute targets
        target_minutes = max(8, chunk.estimated_duration)
        min_scenes = max(8, int(target_minutes * 1.2))
        scenes = data.get('scenes', [])
        narration = data.get('narration_script', '')
        # Criteria: minimum scenes and minimum narration length
        needs_enrich = (not isinstance(scenes, list) or len(scenes) < min_scenes or len(narration) < 800)
        attempts = 0
        current = data
        while needs_enrich and attempts < 2:
            try:
                enriched = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Expand and enrich the teaching plan with more scenes and diagrams."},
                        {"role": "user", "content": self.ENRICH_PROMPT.format(min_scenes=min_scenes, json=json.dumps(current, ensure_ascii=False))}
                    ],
                    temperature=0.3,
                    max_tokens=3200
                )
                cur_text = enriched.choices[0].message.content.strip()
                cur_json = self._extract_json(cur_text)
                if cur_json:
                    current = cur_json
                    scenes = current.get('scenes', [])
                    narration = current.get('narration_script', '')
                    needs_enrich = (not isinstance(scenes, list) or len(scenes) < min_scenes or len(narration) < 800)
                else:
                    break
            except Exception:
                break
            attempts += 1
        return current

    def save_teaching_content(self, teaching_content: TeachingContent, output_dir: str = "output/unified/teaching_content") -> str:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^\w\s-]", "", teaching_content.title)
        safe = re.sub(r"[-\s]+", "_", safe)
        path = out / f"{safe}_teaching_content.json"
        path.write_text(json.dumps(teaching_content.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return str(path)
