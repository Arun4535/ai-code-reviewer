from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Iterable, Iterator

from app.schemas.review import ChangedFile

FUNCTION_BOUNDARY_RE = re.compile(r"^([ +-])?\s*(async\s+def |def |class |fn |function |struct |public |private |protected )")


@dataclass(frozen=True)
class ReviewChunk:
    filename: str
    chunk_index: int
    patch: str
    file_index: int


def prioritize_changed_files(changed_files: list[ChangedFile], max_files: int) -> list[ChangedFile]:
    def score(filename: str, status: str) -> int:
        path = filename.lower()
        score = 0
        high_priority = ["auth", "security", "password", "token", "jwt", "oauth", "session", "login", "admin", "permission", "role", "sql", "database", "db", "payment", "billing", "checkout", "credit", "order", "invoice", "crypto"]
        low_priority = ["test", "spec", "mock", "fixture", "docs", "doc", "readme", "changelog", "config", "settings", "yaml", "yml", "json", "md", "txt", "lock"]
        for term in high_priority:
            if term in path:
                score += 20
        for term in low_priority:
            if term in path:
                score -= 15
        if path.endswith(".py"):
            score += 5
        if path.endswith(('.sql', '.db', '.ddl')):
            score += 10
        if path.endswith(('.yaml', '.yml', '.json', '.md', '.txt', '.cfg', '.ini')):
            score -= 5
        if path.startswith("tests/") or "/tests/" in path or path.endswith("_test.py") or path.endswith("test.py"):
            score -= 10
        if status.lower() == "removed":
            score -= 2
        return score

    scored = [(-score(file.filename, file.status), index, file) for index, file in enumerate(changed_files)]
    scored.sort()
    prioritized = [file for _, _, file in scored][:max_files]
    return prioritized


def build_review_chunks(
    changed_files: list[ChangedFile],
    max_files: int,
    max_lines_per_chunk: int,
    max_chars_per_chunk: int,
) -> list[ReviewChunk]:
    prioritized = prioritize_changed_files(changed_files, max_files)
    chunks: list[ReviewChunk] = []
    for file_index, file in enumerate(prioritized):
        if file.status == "omitted" or file.filename.startswith("[review payload"):
            continue
        if not file.patch:
            chunks.append(
                ReviewChunk(
                    filename=file.filename,
                    chunk_index=len(chunks),
                    patch="[Diff unavailable for this file. Review the file metadata and changed file path.]",
                    file_index=file_index,
                )
            )
            continue
        for chunk_patch in _split_patch_into_chunks(file.patch, max_lines_per_chunk):
            if len(chunk_patch) > max_chars_per_chunk:
                chunk_patch = chunk_patch[:max_chars_per_chunk] + "\n\n[Diff chunk truncated: too large for review chunk.]"
            chunks.append(
                ReviewChunk(
                    filename=file.filename,
                    chunk_index=len(chunks),
                    patch=chunk_patch,
                    file_index=file_index,
                )
            )
    return chunks


def _split_patch_into_chunks(patch: str, max_lines: int) -> list[str]:
    lines = patch.splitlines()
    if len(lines) <= max_lines:
        return [patch]

    hunks = list(_split_patch_into_hunks(lines))
    chunks: list[list[str]] = []
    current: list[str] = []

    for hunk in hunks:
        if not current:
            current = hunk.copy()
            continue
        if len(current) + len(hunk) <= max_lines:
            current.extend(hunk)
            continue
        chunks.extend(_split_large_block(current, max_lines))
        current = hunk.copy()
    if current:
        chunks.extend(_split_large_block(current, max_lines))
    return ["\n".join(chunk) for chunk in chunks]


def _split_patch_into_hunks(lines: list[str]) -> Iterator[list[str]]:
    current: list[str] = []
    for line in lines:
        if line.startswith("@@") and current:
            yield current
            current = [line]
        else:
            current.append(line)
    if current:
        yield current


def _split_large_block(lines: list[str], max_lines: int) -> list[list[str]]:
    if len(lines) <= max_lines:
        return [lines]
    boundaries = [i for i, line in enumerate(lines) if FUNCTION_BOUNDARY_RE.match(line.lstrip(' +-'))]
    boundaries = [index for index in boundaries if 1 < index < len(lines) - 1]
    if not boundaries:
        return [lines[i : i + max_lines] for i in range(0, len(lines), max_lines)]

    chunks: list[list[str]] = []
    start = 0
    for boundary in boundaries:
        if boundary - start > max_lines:
            chunks.extend([lines[start : start + max_lines]])
            start += max_lines
            continue
        if boundary - start <= max_lines:
            chunks.append(lines[start:boundary])
            start = boundary
    if start < len(lines):
        chunks.extend([lines[start : start + max_lines]])
    return [chunk for chunk in chunks if chunk]
