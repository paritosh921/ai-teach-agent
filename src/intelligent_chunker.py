"""
IntelligentChunker - OpenAI-driven content segmentation with robust fallbacks.

Plans ~10-minute segments using OpenAI (for semantic boundaries) and extracts
chunk text from the original content with fuzzy matching and safe fallbacks.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import re
import json
import math
from openai import OpenAI

from .unified_book_processor import BookContent


@dataclass
class ContentChunk:
    title: str
    content: str
    chunk_index: int
    total_chunks: int
    estimated_duration: int  # minutes
    educational_focus: str
    learning_objectives: List[str] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    continuation_notes: Optional[str] = None
    word_count: int = 0

    def __post_init__(self):
        if not self.word_count:
            self.word_count = len(self.content.split())


class IntelligentChunker:
    """OpenAI-planned chunking with robust extraction and fallbacks."""

    CONTENT_ANALYSIS_PROMPT = (
        "You are an expert educational content analyst. Plan a chunking strategy for a long teaching text.\n"
        "Target about {target_duration} minutes per chunk (approx {words_per_chunk} words).\n"
        "Audience: {audience}. Ensure natural topic boundaries and progressive learning.\n\n"
        "Return JSON with keys: chunks (list). Each chunk has: title, rationale, estimated_duration (min),\n"
        "word_count_estimate, educational_focus, learning_objectives (list), key_concepts (list), prerequisites (list),\n"
        "content_start (first 8-15 exact words as they appear), content_end (last 8-15 exact words).\n\n"
        "TEXT (truncated if long):\n{content}\n"
    )

    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.words_per_minute = 150
        self.content_expansion = 1.5

    def chunk_content(self, book_content: BookContent, target_duration: int = 10, audience: str = "undergraduate") -> List[ContentChunk]:
        try:
            print("?? Analyzing content for optimal chunking...")
            print(f"   ?? Content: {book_content.word_count:,} words")
            print(f"   ?? Target: {target_duration} minutes per video")
            print(f"   ?? Audience: {audience}")

            words_per_chunk = max(300, int(target_duration * self.words_per_minute / self.content_expansion))
            analysis_content = self._prepare_content_for_analysis(book_content.content)
            prompt = self.CONTENT_ANALYSIS_PROMPT.format(
                target_duration=target_duration,
                words_per_chunk=words_per_chunk,
                audience=audience,
                content=analysis_content,
            )
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Plan coherent chunk boundaries for teaching videos."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=3000,
            )
            data = self._parse_json(resp.choices[0].message.content)
            if not data or 'chunks' not in data or not isinstance(data['chunks'], list):
                print("   ?? OpenAI chunking returned no plan; using fallback")
                return self._fallback_chunking(book_content, target_duration)

            planned_chunks = data['chunks']
            total = len(planned_chunks) if planned_chunks else 1
            chunks: List[ContentChunk] = []
            for i, ch in enumerate(planned_chunks, 1):
                text = self._extract_chunk_content(
                    book_content.content,
                    ch.get('content_start', ''),
                    ch.get('content_end', ''),
                    ch.get('word_count_estimate', words_per_chunk),
                    i,
                    total,
                )
                if not text:
                    # fallback proportional slice
                    text = self._extract_proportional_chunk(book_content.content, i, total)
                chunks.append(
                    ContentChunk(
                        title=ch.get('title', f"{book_content.title} - Part {i}"),
                        content=text,
                        chunk_index=i,
                        total_chunks=total,
                        estimated_duration=int(ch.get('estimated_duration', target_duration)),
                        educational_focus=ch.get('educational_focus', 'mixed'),
                        learning_objectives=ch.get('learning_objectives', []),
                        key_concepts=ch.get('key_concepts', []),
                        prerequisites=ch.get('prerequisites', []),
                    )
                )
            # Validate and refine
            refined = self._validate_and_refine_chunks(chunks, target_duration)
            if refined:
                print(f"   ? Created {len(refined)} optimized chunks")
                return refined
            return self._fallback_chunking(book_content, target_duration)
        except Exception as e:
            print(f"   ? Error in chunking: {e}")
            return self._fallback_chunking(book_content, target_duration)

    # Helpers
    def _prepare_content_for_analysis(self, content: str, max_chars: int = 12000) -> str:
        if len(content) <= max_chars:
            return content
        truncated = content[:max_chars]
        last_para = truncated.rfind("\n\n")
        if last_para > max_chars * 0.8:
            truncated = truncated[:last_para]
        else:
            last_sentence = truncated.rfind('.')
            if last_sentence > max_chars * 0.9:
                truncated = truncated[: last_sentence + 1]
        return truncated + f"\n\n[CONTENT TRUNCATED - total {len(content)} chars]"

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        m = re.search(r"```json\s*(.*?)```", text, re.DOTALL)
        raw = m.group(1) if m else text[text.find('{') : text.rfind('}') + 1]
        try:
            return json.loads(raw)
        except Exception:
            return None

    def _extract_chunk_content(self, full: str, start_marker: str, end_marker: str, target_words: int, idx: int, total: int) -> str:
        start_marker = (start_marker or '').strip()
        end_marker = (end_marker or '').strip()
        if not start_marker or not end_marker:
            return ''
        s_clean = self._clean_marker(start_marker)
        e_clean = self._clean_marker(end_marker)
        start = full.find(start_marker)
        if start == -1:
            start = full.find(s_clean)
        if start == -1:
            start = self._fuzzy_find(full, s_clean)
        if start == -1:
            return ''
        end_pos = full.find(end_marker, start)
        if end_pos == -1:
            end_pos = full.find(e_clean, start)
        if end_pos == -1:
            end_pos = self._fuzzy_find(full, e_clean, start)
        if end_pos == -1:
            end_pos = self._estimate_end_by_words(full, start, target_words)
        else:
            end_pos += len(end_marker)
        end_pos = max(start + 1, min(end_pos, len(full)))
        extracted = full[start:end_pos].strip()
        if len(extracted.split()) < max(80, int(0.3 * target_words)):
            return ''
        return extracted

    def _fuzzy_find(self, text: str, pattern: str, start_pos: int = 0) -> int:
        pos = text.find(pattern, start_pos)
        if pos >= 0:
            return pos
        p_norm = ' '.join(self._clean_marker(pattern).split())
        t_norm = ' '.join(text.split())
        pos = t_norm.find(p_norm, start_pos)
        return pos

    def _estimate_end_by_words(self, content: str, start_pos: int, target_words: int) -> int:
        remaining = content[start_pos:]
        words = remaining.split()
        if len(words) <= target_words:
            return len(content)
        target_text = ' '.join(words[:target_words])
        lower = max(0, len(target_text) - 200)
        for i in range(max(0, len(target_text) - 2), lower - 1, -1):
            if i + 1 < len(target_text) and target_text[i] in '.!?' and target_text[i + 1].isspace():
                return start_pos + i + 1
        return start_pos + len(target_text)

    def _extract_proportional_chunk(self, full: str, idx: int, total: int) -> str:
        start_ratio = (idx - 1) / total
        end_ratio = idx / total
        s = int(len(full) * start_ratio)
        e = int(len(full) * end_ratio)
        s = self._adjust_to_boundary(full, s, 'start')
        e = self._adjust_to_boundary(full, e, 'end')
        return full[s:e].strip()

    def _adjust_to_boundary(self, content: str, pos: int, direction: str) -> int:
        if direction == 'start':
            while pos < len(content) and not content[pos].isspace():
                pos += 1
            while pos < len(content) and content[pos].isspace():
                pos += 1
        else:
            while pos > 0 and not content[pos - 1].isspace():
                pos -= 1
        return max(0, min(pos, len(content)))

    def _clean_marker(self, s: str) -> str:
        s = s.replace('…', '...')
        s = re.sub(r'[.]{3,}', ' ', s)
        s = re.sub(r'\s+', ' ', s)
        return s.strip()

    def _fallback_chunking(self, book_content: BookContent, target_duration: int) -> List[ContentChunk]:
        words = book_content.content.split()
        if not words:
            return []
        words_per_chunk = max(300, int(target_duration * self.words_per_minute / self.content_expansion))
        total = max(1, math.ceil(len(words) / words_per_chunk))
        chunks: List[ContentChunk] = []
        for i in range(total):
            s = i * words_per_chunk
            e = min((i + 1) * words_per_chunk, len(words))
            txt = ' '.join(words[s:e])
            chunks.append(ContentChunk(
                title=f"{book_content.title} - Part {i+1}",
                content=txt,
                chunk_index=i + 1,
                total_chunks=total,
                estimated_duration=target_duration,
                educational_focus='mixed',
                learning_objectives=[f"Understand: {book_content.title}"],
                key_concepts=[]
            ))
        return chunks

    def _validate_and_refine_chunks(self, chunks: List[ContentChunk], target_duration: int) -> List[ContentChunk]:
        refined: List[ContentChunk] = []
        for ch in chunks:
            if ch.word_count < 50:
                continue
            refined.append(ch)
        return refined
