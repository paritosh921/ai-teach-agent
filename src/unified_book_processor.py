"""
Unified Book Processor - minimal implementation

Loads plain text books from the books/ directory and exposes a simple
BookContent model used by the unified pipeline.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class BookSection:
    title: str
    content: str
    level: int = 1
    section_number: str = ""
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    educational_elements: Dict[str, List[str]] = field(default_factory=dict)
    word_count: int = 0

    def __post_init__(self):
        if not self.word_count:
            self.word_count = len(self.content.split())


@dataclass
class BookContent:
    title: str
    content: str
    format: str
    filepath: str
    sections: List[BookSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    word_count: int = 0
    estimated_read_time: int = 0

    def __post_init__(self):
        if not self.word_count:
            self.word_count = len(self.content.split())
        if not self.estimated_read_time:
            self.estimated_read_time = max(1, self.word_count // 200)


class UnifiedBookProcessor:
    def __init__(self, books_dir: str = "books"):
        self.books_dir = Path(books_dir)
        self.books_dir.mkdir(exist_ok=True)

    def load_book(self, book_name: str, format_hint: Optional[str] = None) -> Optional[BookContent]:
        # prefer .txt
        candidates = [self.books_dir / f"{book_name}.txt",
                      self.books_dir / f"{book_name}.md",
                      self.books_dir / f"{book_name}.json"]
        for p in candidates:
            if p.exists():
                if p.suffix.lower() == ".json":
                    # Minimal JSON support: read text field if present
                    import json
                    data = json.loads(p.read_text(encoding="utf-8"))
                    content = data.get("content") or data.get("text") or ""
                    title = data.get("title") or p.stem.replace("_", " ")
                    sections = [BookSection(title=title, content=content)]
                    return BookContent(title=title, content=content, format="json", filepath=str(p), sections=sections, metadata=data)
                else:
                    content = p.read_text(encoding="utf-8")
                    title = self._infer_title(content, p.stem)
                    sections = [BookSection(title=title, content=content)]
                    fmt = "markdown" if p.suffix.lower() == ".md" else "text"
                    return BookContent(title=title, content=content, format=fmt, filepath=str(p), sections=sections, metadata={"source": fmt})
        return None

    def _infer_title(self, content: str, fallback: str) -> str:
        for line in content.splitlines():
            t = line.strip().strip("# ")
            if len(t) > 3:
                return t
        return fallback.replace("_", " ")

