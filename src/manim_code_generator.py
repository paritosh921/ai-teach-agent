"""
Manim Code Generator with auto-debug loop.

Generates Manim code from teaching content via OpenAI, compiles with manim,
and applies bounded auto-fixes using OpenAI and fallback regex edits.
"""

import re
import json
import subprocess
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

    def generate_video(self, teaching_content: TeachingContent, audience: str = "undergraduate", output_name: Optional[str] = None) -> Optional[str]:
        if not output_name:
            safe = re.sub(r"[^\w\s-]", "", teaching_content.title)
            safe = re.sub(r"[-\s]+", "_", safe)
            output_name = f"{safe}_video"

        code = self._generate_manim_code(teaching_content, audience)
        if not code:
            return None
        result = self._compile_with_auto_debug(code, output_name)
        if not result.success:
            return None
        # Move/copy final video to output_dir already resolved in compile
        return result.video_path

    def _generate_manim_code(self, tc: TeachingContent, audience: str) -> Optional[str]:
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
            code_path.write_text(current, encoding="utf-8")
            comp = self._compile_manim_code(code_path, output_name)
            result.attempts_made = attempt
            result.compilation_logs.append(comp.get('log') or '')
            self._persist_log(output_name, attempt, comp.get('log') or '')
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
                current = fixed
                print(f"         ?? Applied fix, retrying...")
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
            proc = subprocess.run(cmd, cwd=str(self.temp_dir), capture_output=True, text=True, timeout=180)
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
        ]
        for pat, rep in fixes:
            fixed = re.sub(pat, rep, fixed)
        return fixed

    def _persist_log(self, output_name: str, attempt: int, log: str) -> None:
        reports = self.output_dir.parent / 'reports'
        reports.mkdir(parents=True, exist_ok=True)
        (reports / f"{output_name}_attempt_{attempt}.log").write_text(log, encoding='utf-8')
