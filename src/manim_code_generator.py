"""
Manim Code Generator with an adaptive slides renderer (default)
and optional structured/legacy fallbacks.

Default path: LLM → slides IR → adaptive renderer template (big, readable,
varied slides with plots/charts/figures). Auto-debug loop persists attempt
code, diffs, and logs for reliable re-editing.
"""

import os
import re
import json
import subprocess
import difflib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
from openai import OpenAI

from .openai_video_generator import TeachingContent


@dataclass
class VideoGenerationResult:
    success: bool
    video_path: Optional[str] = None
    code_path: Optional[str] = None
    error_message: Optional[str] = None
    attempts_made: int = 0
    compilation_logs: List[str] = field(default_factory=list)
    debug_history: List[str] = field(default_factory=list)


class ManimCodeGenerator:
    MANIM_CODE_PROMPT = (
        "You are an expert Manim programmer. Generate fully working Manim Community 0.18.x code in 3Blue1Brown style.\n"
        "Use: from manim import *; one Scene subclass with construct(); keep text font_size>=32; avoid overlaps.\n"
        "Create rich diagrams: Axes/NumberPlane, VGroup layouts, MathTex formulas, arrows, highlights.\n\n"
        "TITLE: {title}\nDIFFICULTY: {difficulty}\nAUDIENCE: {audience}\nDURATION_MIN: {duration}\n"
        "LEARNING_OBJECTIVES:\n{learning_objectives}\n"
        "KEY_CONCEPTS:\n{key_concepts}\n"
        "DETAILS:\n{details}\n"
        "NARRATION:\n{narration}\n"
        "SCENE PLAN (JSON):\n{scene_plan}\n\n"
        "Constraints:\n- No element off-screen; use margins and centered layouts.\n- Stagger animations and use Wait() for pacing.\n- Use Create/Write/FadeIn/Transform appropriately.\n\n"
        "Return ONLY code, no markdown fence."
    )

    ERROR_FIX_PROMPT = (
        "You are a Manim debugging assistant. Fix the provided Manim code to compile successfully.\n"
        "Make minimal edits, preserve structure, keep one Scene with construct().\n"
        "Original error/log shown below. Return ONLY corrected code.\n\n"
        "ERROR/LOG:\n{error_log}\n\nCODE:\n{code}\n"
    )

    def __init__(self, openai_api_key: str, model: str = "gpt-4o", output_dir: str = "output/unified/videos", temp_dir: str = "temp/unified"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.output_dir = Path(output_dir); self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path(temp_dir); self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.max_debug_attempts = 5
        self.manim_quality = "l"  # 480p equivalent for speed
        # New default: slides IR renderer
        self.use_slides_renderer = True
        # Optional alternates
        self.use_blocks_renderer = False
        self.use_structured_renderer = False

    def generate_video(self, teaching_content: TeachingContent, audience: str = "undergraduate", output_name: Optional[str] = None) -> Optional[str]:
        if not output_name:
            safe = re.sub(r"[^\w\s-]", "", teaching_content.title)
            safe = re.sub(r"[-\s]+", "_", safe)
            output_name = f"{safe}_video"

        if self.use_slides_renderer:
            # Slides IR → adaptive renderer
            code = self._generate_manim_code(teaching_content, audience)
            if not code:
                return None
            result = self._compile_with_auto_debug(code, output_name)
            return result.video_path if result.success else None
        elif self.use_blocks_renderer:
            # Preferred: block IR -> component renderer template -> compile with auto-debug
            code = self._generate_manim_code(teaching_content, audience)
            if not code:
                return None
            result = self._compile_with_auto_debug(code, output_name)
            return result.video_path if result.success else None
        elif self.use_structured_renderer:
            # Deterministic, layout-safe path
            bp = self._build_blueprint(teaching_content, audience)
            script = self._generate_structured_script(bp, output_name)
            if not script:
                return None
            result = self._compile_manim_code(Path(script), output_name)
            if result.get('success'):
                return result.get('video_path')
            # Fallback to LLM code path (auto-debug will persist its own artifacts)
            # Optional fallback to LLM code path
            code = self._generate_manim_code(teaching_content, audience)
            if not code:
                return None
            debug_result = self._compile_with_auto_debug(code, output_name)
            return debug_result.video_path if debug_result.success else None
        else:
            # Legacy path: LLM generates code, then auto-debug
            code = self._generate_manim_code(teaching_content, audience)
            if not code:
                return None
            result = self._compile_with_auto_debug(code, output_name)
            if not result.success:
                return None
            return result.video_path

    # ----------------------
    # Blocks IR renderer path
    # ----------------------
    def _generate_blocks_ir(self, tc: TeachingContent, audience: str) -> List[Dict[str, Any]]:
        """Ask the model for a block IR (no coords, only component types). Fallback to heuristic if needed."""
        IR_PROMPT = (
            "You are an educational storyboarder. Return ONLY JSON (no prose).\n"
            "Schema: a JSON array of blocks. Block types:\n"
            "  - {\"type\": \"title\", \"text\": str}\n"
            "  - {\"type\": \"two_column\", \"left\": str, \"right\": str}\n"
            "  - {\"type\": \"formula\", \"latex\": str, \"row_start\": int, \"row_end\": int}\n"
            "Rules:\n- No coordinates, no .shift/.to_edge.\n- Keep text concise.\n- Prefer two_column with summary on left and key points or short formula on right.\n"
            f"TITLE: {tc.title}\nAUDIENCE: {audience}\nDURATION_MIN: {tc.estimated_duration}\n"
            f"OBJECTIVES: {json.dumps(tc.learning_objectives, ensure_ascii=False)}\n"
            f"KEY_CONCEPTS: {json.dumps(tc.key_concepts, ensure_ascii=False)}\n"
            f"FORMULAS: {json.dumps(tc.formulas, ensure_ascii=False)}\n"
            f"SUMMARY: {tc.summary}\n"
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only JSON block list per schema; no code."},
                    {"role": "user", "content": IR_PROMPT},
                ],
                temperature=0.2,
                max_tokens=1500,
            )
            text = resp.choices[0].message.content.strip()
            # Extract JSON array
            start = text.find('['); end = text.rfind(']')
            data = json.loads(text[start:end+1]) if start != -1 and end != -1 else []
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass
        # Fallback: simple mapping from teaching content
        return self._blocks_ir_fallback(tc)

    def _blocks_ir_fallback(self, tc: TeachingContent) -> List[Dict[str, Any]]:
        blocks: List[Dict[str, Any]] = []
        blocks.append({"type": "title", "text": tc.title})
        # Build one or two two_column blocks from objectives and summary
        left = "; ".join([str(x) for x in (tc.learning_objectives or [])[:5]])
        right = (tc.summary or "")[:300]
        if left or right:
            blocks.append({"type": "two_column", "left": left, "right": right})
        # Add up to two formulas
        for f in (tc.formulas or [])[:2]:
            latex = f.get('formula') if isinstance(f, dict) else str(f)
            if latex:
                blocks.append({"type": "formula", "latex": latex, "row_start": 2, "row_end": 3})
        return blocks

    def _render_blocks_code(self, blocks: List[Dict[str, Any]]) -> str:
        """Read renderer template and inject block list as Python literal."""
        template_path = Path(__file__).resolve().parents[1] / 'src' / 'renderer_template.py'
        src = template_path.read_text(encoding='utf-8')
        code = src.replace("__BLOCKS__", f"blocks = {json.dumps(blocks, ensure_ascii=False)}")
        return code

    # ----------------------
    # Slides IR renderer path
    # ----------------------
    def _generate_slides_ir(self, tc: TeachingContent, audience: str) -> List[Dict[str, Any]]:
        """Ask the model for a slides IR. Fallback to a heuristic varied deck if needed."""
        PROMPT = (
            "Return ONLY JSON (no prose). Schema is a JSON array of slide dicts (no wrapper key).\n"
            "Slide types: title/bullets/two_column/equation/plot/bar/figure.\n"
            "Examples:\n"
            "  {\"type\":\"title\",\"text\":str}\n"
            "  {\"type\":\"bullets\",\"title\":str,\"items\":[str,...]}\n"
            "  {\"type\":\"two_column\",\"left_title\":str,\"left\":str,\"right_title\":str,\"right\":str}\n"
            "  {\"type\":\"equation\",\"title\":str,\"lines\":[latex,...]}\n"
            "  {\"type\":\"plot\",\"title\":str,\"expr\":python_expr,\"x_range\":[min,max,step],\"y_range\":[min,max,step]}\n"
            "  {\"type\":\"bar\",\"title\":str,\"labels\":[str],\"values\":[num]}\n"
            "  {\"type\":\"figure\",\"title\":str,\"caption\":str}\n"
            "Rules: keep text concise; no coordinates; ensure slides are varied and readable.\n"
            f"TITLE: {tc.title}\nAUDIENCE: {audience}\nDURATION_MIN: {tc.estimated_duration}\n"
            f"OBJECTIVES: {json.dumps(tc.learning_objectives, ensure_ascii=False)}\n"
            f"KEY_CONCEPTS: {json.dumps(tc.key_concepts, ensure_ascii=False)}\n"
            f"FORMULAS: {json.dumps(tc.formulas, ensure_ascii=False)}\n"
            f"SUMMARY: {tc.summary}\n"
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only JSON list of slides per schema; no code."},
                    {"role": "user", "content": PROMPT},
                ],
                temperature=0.2,
                max_tokens=2200,
            )
            text = resp.choices[0].message.content.strip()
            start = text.find('['); end = text.rfind(']')
            slides = json.loads(text[start:end+1]) if start != -1 and end != -1 else []
            if isinstance(slides, list) and slides:
                return slides
        except Exception:
            pass
        return self._slides_ir_fallback(tc)

    def _slides_ir_fallback(self, tc: TeachingContent) -> List[Dict[str, Any]]:
        slides: List[Dict[str, Any]] = []
        slides.append({"type": "title", "text": tc.title})
        if tc.learning_objectives:
            slides.append({"type": "bullets", "title": "Learning Objectives", "items": tc.learning_objectives[:6]})
        if tc.key_concepts:
            kc0 = tc.key_concepts[0]
            concept = kc0.get('concept') if isinstance(kc0, dict) else str(kc0)
            definition = kc0.get('definition', '') if isinstance(kc0, dict) else ''
            slides.append({
                "type": "two_column",
                "left_title": concept or "Key Concept",
                "left": definition[:400],
                "right_title": "Summary",
                "right": (tc.summary or "")[:400],
            })
        if tc.formulas:
            eq_lines = [f.get('formula') if isinstance(f, dict) else str(f) for f in tc.formulas[:3]]
            slides.append({"type": "equation", "title": "Key Equations", "lines": [s for s in eq_lines if s]})
        slides.append({"type": "figure", "title": "Diagram", "caption": tc.summary[:200] if tc.summary else ""})
        return slides

    def _render_slides_code(self, slides: List[Dict[str, Any]]) -> str:
        template_path = Path(__file__).resolve().parents[1] / 'src' / 'adaptive_renderer.py'
        src = template_path.read_text(encoding='utf-8')
        return src.replace("__SLIDES__", json.dumps(slides, ensure_ascii=False))

    # ----------------------
    # Structured renderer path
    # ----------------------
    def _build_blueprint(self, tc: TeachingContent, audience: str) -> Dict[str, Any]:
        """Create a robust, layout-safe blueprint from teaching content.

        Strategy:
        - Slide 1: Title + learning objectives (<=5) + first formula (if any)
        - Next slides: Key concepts, examples, and short explanations split into bullets
        - Cap slides to keep near the target duration.
        """
        def sanitize(s: str) -> str:
            return re.sub(r"\s+", " ", (s or "").strip())

        def sentences(text: str) -> List[str]:
            txt = sanitize(text)
            if not txt:
                return []
            parts = re.split(r"(?<=[.!?])\s+", txt)
            return [p for p in parts if p]

        slides: List[Dict[str, Any]] = []

        # Slide 1
        bullets1 = [sanitize(x) for x in (tc.learning_objectives or [])][:5]
        formulas_all = [f.get('formula', '') if isinstance(f, dict) else str(f) for f in (tc.formulas or [])]
        slide1 = {
            "title": tc.title,
            "bullets": bullets1,
            "formulas": [f for f in formulas_all if f][:1],
        }
        slides.append(slide1)

        # Key concepts slides
        for kc in (tc.key_concepts or [])[:4]:
            concept = sanitize(kc.get('concept') if isinstance(kc, dict) else str(kc))
            definition = sanitize(kc.get('definition') if isinstance(kc, dict) else "")
            if not concept:
                continue
            b = [concept] + (sentences(definition)[:3] if definition else [])
            slides.append({
                "title": concept,
                "bullets": b[:5],
                "formulas": [f for f in formulas_all if f][:1],
            })

        # Examples / Explanations slides
        for ex in (tc.examples or [])[:4]:
            title = sanitize(ex.get('title') if isinstance(ex, dict) else "Example")
            content = sanitize(ex.get('content') if isinstance(ex, dict) else str(ex))
            b = sentences(content)[:6]
            slides.append({"title": title or "Example", "bullets": b, "formulas": []})

        for de in (tc.detailed_explanations or [])[:3]:
            title = sanitize(de.get('section') if isinstance(de, dict) else "Detail")
            expl = sanitize(de.get('explanation') if isinstance(de, dict) else str(de))
            b = sentences(expl)[:6]
            slides.append({"title": title or tc.title, "bullets": b, "formulas": []})

        # Trim slide count to keep near target minutes (~1.2 slides/minute)
        target = max(8, int(tc.estimated_duration * 1.2))
        slides = slides[:target]

        blueprint = {
            "title": tc.title,
            "slides": slides,
            "meta": {
                "audience": audience,
                "estimated_duration": tc.estimated_duration,
                "difficulty": tc.difficulty_level,
            },
        }
        # Persist for debugging
        bp_dir = self.output_dir.parent / 'blueprints'
        bp_dir.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^\w\s-]", "", tc.title)
        safe = re.sub(r"[-\s]+", "_", safe)
        (bp_dir / f"{safe}_blueprint.json").write_text(json.dumps(blueprint, ensure_ascii=False, indent=2), encoding='utf-8')
        return blueprint

    def _generate_structured_script(self, blueprint: Dict[str, Any], output_name: str) -> Optional[str]:
        """Write a small scene file that imports the structured renderer and renders the blueprint."""
        json_blob = json.dumps(blueprint, ensure_ascii=False)
        # Escape for safe embedding inside single-quoted Python string
        json_blob = json_blob.replace('\\', r'\\').replace("'", r"\'")
        code = f"""
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{json_blob}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
"""
        path = self.temp_dir / f"{output_name}.py"
        path.write_text(code, encoding='utf-8')
        return str(path)

    def _generate_manim_code(self, tc: TeachingContent, audience: str) -> Optional[str]:
        if self.use_slides_renderer:
            slides = self._generate_slides_ir(tc, audience)
            return self._render_slides_code(slides)
        if self.use_blocks_renderer:
            ir = self._generate_blocks_ir(tc, audience)
            return self._render_blocks_code(ir)
        objs = "\n".join(f"- {o}" for o in tc.learning_objectives)
        concepts = "\n".join(f"- {k.get('concept','')}: {k.get('definition','')}" for k in tc.key_concepts)
        details = "\n".join((d.get('section','Section')+":\n"+d.get('explanation','')) for d in tc.detailed_explanations)
        prompt = self.MANIM_CODE_PROMPT.format(
            title=tc.title, difficulty=tc.difficulty_level, audience=audience, duration=tc.estimated_duration,
            learning_objectives=objs, key_concepts=concepts, details=details, narration=tc.narration_script,
            scene_plan=json.dumps(tc.to_dict().get('scenes', []), ensure_ascii=False)
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role":"system","content":"Write correct, modern Manim CE code."}, {"role":"user","content":prompt}],
            temperature=0.1, max_tokens=3500
        )
        code = resp.choices[0].message.content.strip()
        return self._clean_generated_code(code)

    def _clean_generated_code(self, code: str) -> str:
        code = re.sub(r"```python\s*\n|```$", "", code).strip()
        if "from manim import *" not in code:
            code = "from manim import *\n\n" + code
        if "random.seed(" not in code and "np.random.seed(" not in code:
            code = code.replace("from manim import *\n\n", "from manim import *\nimport random, numpy as np\nrandom.seed(42); np.random.seed(42)\n\n", 1)
        return code

    def _compile_with_auto_debug(self, manim_code: str, output_name: str) -> VideoGenerationResult:
        result = VideoGenerationResult(success=False)
        current = manim_code
        code_path = self.temp_dir / f"{output_name}.py"
        for attempt in range(1, self.max_debug_attempts + 1):
            print(f"         ?? Compilation attempt {attempt}/{self.max_debug_attempts}")
            # Snapshot current code for this attempt
            snap_path = self.temp_dir / f"{output_name}_attempt_{attempt}.py"
            snap_path.write_text(current, encoding="utf-8")
            # Compile using canonical filename (to keep output stable), but persist snapshot
            code_path.write_text(current, encoding="utf-8")
            comp = self._compile_manim_code(code_path, output_name)
            result.attempts_made = attempt
            result.compilation_logs.append(comp.get('log') or '')
            log_path = self._persist_log(output_name, attempt, comp.get('log') or '')
            # Also persist the code snapshot alongside the log for inspection
            snap_report_path = self._persist_code_snapshot(output_name, attempt, current)
            if comp['success']:
                result.success = True
                result.video_path = comp['video_path']
                result.code_path = str(code_path)
                print(f"         ? Compilation successful on attempt {attempt}")
                return result
            print(f"         ? Compilation failed, attempting fix...")
            errlog = (comp.get('error') or '') + "\n\n" + (comp.get('log') or '')
            fixed = self._fix_code_with_openai(current, errlog)
            if not fixed or fixed == current:
                fixed = self._apply_fallback_fixes(current)
            if fixed and fixed != current:
                # Persist a diff for visibility
                diff_path, changed = self._persist_diff(output_name, attempt, current, fixed)
                current = fixed
                # Surface artifact info for operator visibility
                print(f"         ?? Applied fix (+/- {changed} lines). Snapshot: {snap_report_path}")
                print(f"         ?? Log: {log_path} | Diff: {diff_path}")
                continue
            result.error_message = f"Could not fix compilation errors after {attempt} attempts"
            if attempt == self.max_debug_attempts:
                break
        result.error_message = result.error_message or f"Maximum debug attempts ({self.max_debug_attempts}) exceeded"
        return result

    def _compile_manim_code(self, code_path: Path, output_name: str) -> Dict[str, Any]:
        try:
            # Detect scene name
            code = code_path.read_text(encoding="utf-8")
            m = re.search(r"class\s+(\w+)\s*\(Scene\)", code)
            scene_name = m.group(1) if m else "Scene"
            # Call manim from temp_dir (use filename)
            cmd = [
                'manim', code_path.name, scene_name,
                '-q', self.manim_quality,
                '-o', output_name, '--format', 'mp4', '--disable_caching'
            ]
            env = os.environ.copy()
            # Ensure src/ is importable by the generated script
            repo_root = Path(__file__).resolve().parents[1]
            env['PYTHONPATH'] = (env.get('PYTHONPATH', '') + (os.pathsep if env.get('PYTHONPATH') else '') + str(repo_root))
            proc = subprocess.run(cmd, cwd=str(self.temp_dir), capture_output=True, text=True, timeout=240, env=env)
            video_path = None
            if proc.returncode == 0:
                # locate produced mp4
                cands = sorted(self.temp_dir.rglob(f"*{output_name}*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
                if cands:
                    video_path = str(cands[0])
            success = proc.returncode == 0 and bool(video_path)
            final_path = None
            if success:
                try:
                    import shutil
                    final = self.output_dir / f"{output_name}.mp4"
                    final.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(video_path, final)
                    final_path = str(final)
                except Exception:
                    final_path = video_path
            return {
                'success': success,
                'video_path': final_path,
                'error': proc.stderr if proc.returncode != 0 else None,
                'log': (proc.stdout or '') + (proc.stderr or ''),
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'video_path': None, 'error': 'Compilation timeout', 'log': 'Timeout'}
        except Exception as e:
            return {'success': False, 'video_path': None, 'error': str(e), 'log': str(e)}

    def _fix_code_with_openai(self, code: str, error_log: str) -> Optional[str]:
        try:
            prompt = self.ERROR_FIX_PROMPT.format(error_log=error_log[:8000], code=code)
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role":"system","content":"Fix Manim code to compile, minimal changes."}, {"role":"user","content":prompt}],
                temperature=0.1, max_tokens=3500
            )
            fixed = resp.choices[0].message.content.strip()
            return self._clean_generated_code(fixed)
        except Exception:
            return None

    def _apply_fallback_fixes(self, code: str) -> str:
        fixed = code
        # common small fixes
        fixes = [
            (r"Text\(([^\)]*)size\s*=\s*\d+([^\)]*)\)", r"Text(\1\2)"),
            (r"(Write|Create)\(([^\)]*),\s*run_time\s*=\s*[^\)]*\)", r"\1(\2)"),
            (r"\.to_edge\(([^\)]*),\s*buff\s*=\s*[^\)]*\)", r".to_edge(\1)"),
            (r"ShowCreation\(", r"Create("),
            (r"ReplacementTransform\(", r"Transform("),
            # Replace external assets with simple placeholders
            (r"SVGMobject\([^\)]*\)", r"Text('diagram', font_size=36)"),
            (r"ImageMobject\([^\)]*\)", r"Text('image', font_size=36)"),
            # Defensive: ensure Scene subclass exists
            (r"class\s+(\w+)\s*\((?:MovingCamera)?Scene\)\s*:\s*pass", r"class \1(Scene):\n    def construct(self):\n        self.add(Text('Placeholder', font_size=36))"),
        ]
        for pat, rep in fixes:
            fixed = re.sub(pat, rep, fixed)
        return fixed

    def _persist_log(self, output_name: str, attempt: int, log: str) -> str:
        reports = self.output_dir.parent / 'reports'
        reports.mkdir(parents=True, exist_ok=True)
        p = reports / f"{output_name}_attempt_{attempt}.log"
        p.write_text(log, encoding='utf-8')
        return str(p)

    def _persist_code_snapshot(self, output_name: str, attempt: int, code: str) -> str:
        reports = self.output_dir.parent / 'reports'
        reports.mkdir(parents=True, exist_ok=True)
        p = reports / f"{output_name}_attempt_{attempt}.py"
        p.write_text(code, encoding='utf-8')
        return str(p)

    def _persist_diff(self, output_name: str, attempt: int, before: str, after: str) -> tuple[str, int]:
        reports = self.output_dir.parent / 'reports'
        reports.mkdir(parents=True, exist_ok=True)
        diff = list(difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"{output_name}_attempt_{attempt}_before.py",
            tofile=f"{output_name}_attempt_{attempt}_after.py",
            lineterm=''
        ))
        p = reports / f"{output_name}_attempt_{attempt}_fix.diff"
        p.write_text('\n'.join(diff), encoding='utf-8')
        changed = sum(1 for ln in diff if (ln.startswith('+') or ln.startswith('-')) and not ln.startswith('+++') and not ln.startswith('---'))
        return str(p), changed
