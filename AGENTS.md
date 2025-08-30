# Repository Guidelines

## Project Structure & Module Organization
- Root scripts: `unified_video_generator.py`, `book_to_video.py`, `enhanced_book_to_video.py`.
- Source code: `src/` (key areas)
  - `src/config/` YAML schemas and fix lists (e.g., `content_schema.yaml`).
  - `src/schemas/` Python data schemas (book/poml/video).
  - `src/codegen/` Manim code generation utilities.
  - `src/autolayout/` layout safety, validators, scaling.
  - `src/layout/` high‑level layout managers.
  - Core modules: `orchestrator.py`, `llm_book_processor.py`, `manim_code_generator.py`, etc.
- Assets: `books/` (input .txt). Generated: `output/`, `media/`, `temp/`, `test_output/`.
- Env/config: `.env` (secrets), `requirements*.txt`.

## Build, Test, and Development Commands
- Install: `pip install -r requirements.txt` (or `requirements_enhanced.txt` for dev tools).
- Configure: copy `env_template.txt` to `.env` and set `OPENAI_API_KEY=...`.
- List books: `python unified_video_generator.py --list-books`.
- Generate: `python unified_video_generator.py --book calculus --audience undergraduate`.
- Smoke test: `python test_system.py`.
- Unified tests: `python test_unified_system.py --all` (see script help for options).

## Coding Style & Naming Conventions
- Language: Python 3.10+ recommended; 4‑space indentation.
- Names: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Type hints and short doctrings for public functions/classes.
- Formatting: prefer Black; lint with Flake8 (available via `requirements_enhanced.txt`).
- Keep modules small; place shared utilities under `src/codegen/`, schemas in `src/schemas/`.

## Testing Guidelines
- Test scripts: `test_system.py` and `test_unified_system.py` (integration/E2E).
- Create throwaway inputs under `test_output/books/`; outputs go to `test_output/`.
- If adding unit tests, follow `test_*.py` pattern and avoid network unless mocked.
- Aim to cover: chunking, layout safety, codegen structure, and failure paths.

## Commit & Pull Request Guidelines
- Commits: use Conventional Commits (feat, fix, refactor, test, chore).
  Example: `feat(chunker): add audience-aware heuristics`.
- PRs: include a clear description, linked issues, reproduction steps, and before/after notes (attach sample book and resulting outputs if visual).
- Keep changes focused; update README or config references when paths or behaviors change.

## Security & Configuration Tips
- Never commit secrets; keep API keys in `.env` (gitignored).
- Don’t commit generated `media/`, `output/`, or `test_output/` artifacts.
- Prefer smaller sample books for tests; avoid sending proprietary text to APIs.

