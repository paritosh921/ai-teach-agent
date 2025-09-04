# Repository Guidelines

## Project Structure & Module Organization
- `src/`: Core modules — `intelligent_chunker.py`, `openai_video_generator.py`, `manim_code_generator.py`, `unified_book_processor.py`.
- `unified_video_generator.py`: Single entry point for the OpenAI‑based pipeline.
- `books/`: Input sources (e.g., `calculus.txt`). Create if absent.
- `output/unified/`: Generated artifacts (videos, blueprints); auto‑created.
- `temp/`: Intermediate build files; safe to delete.
- `.env`: Local secrets (see `env_template.txt`). Do not commit.

## Build, Test, and Development Commands
- Install: `pip install -r requirements.txt`
- Configure env: `cp env_template.txt .env` then set `OPENAI_API_KEY`.
- Run (book to video): `python unified_video_generator.py --book "calculus"`
- List books: `python unified_video_generator.py --list-books`
- Clean intermediates: remove `temp/` and `output/unified/` subfolders as needed.

## Coding Style & Naming Conventions
- Language: Python 3.8+; 4‑space indentation; prefer type hints and `@dataclass`.
- Names: modules `snake_case.py`, functions/vars `snake_case`, classes `PascalCase`.
- Imports: absolute from `src` when used as a path (see script’s path injection).
- Docstrings: concise module/function docstrings (triple‑quoted) explaining intent.
- Avoid one‑letter identifiers; keep functions focused and small.

## Testing Guidelines
- Current repo has no formal test suite. If adding tests, prefer `pytest` with layout:
  - `tests/test_chunker.py`, `tests/test_codegen.py`, etc.
  - Fast unit tests for pure helpers; mark LLM/Manim integrations as slow.
- Run: `pytest -q` (if added to requirements).

## Commit & Pull Request Guidelines
- Commits: imperative mood and scope, e.g., `chunker: refine fuzzy matching`.
- Group related changes; keep diffs small; reference issues (`Fixes #123`).
- PRs: include purpose, before/after behavior, reproduction steps, and sample inputs in `books/` if relevant.
- For video changes, attach logs or paths from `output/unified/videos/` and note any layout fixes.

## Security & Configuration Tips
- Secrets: keep API keys only in `.env`; never hard‑code or commit.
- Large artifacts: do not commit files from `output/` or `temp/`.
- Manim/ffmpeg: installed via requirements; system `ffmpeg` optional.
