from app.agents.chunking import build_review_chunks
from app.schemas.review import ChangedFile


def test_build_review_chunks_splits_large_patch_by_hunk():
    patch = (
        "@@ -1,3 +1,4 @@\n"
        "-old line\n"
        "+new line\n"
        "+added line\n"
        "@@ -10,3 +10,4 @@\n"
        "-removed line\n"
        "+inserted line\n"
    )
    chunks = build_review_chunks(
        [ChangedFile(filename="app.py", status="modified", patch=patch)],
        max_files=1,
        max_lines_per_chunk=2,
        max_chars_per_chunk=1000,
    )

    assert len(chunks) >= 2
    assert chunks[0].filename == "app.py"
    assert "@@" in chunks[0].patch


def test_build_review_chunks_prioritizes_high_risk_files():
    files = [
        ChangedFile(filename="tests/test_app.py", status="modified", patch="+print('x')"),
        ChangedFile(filename="auth/login.py", status="modified", patch="+print('y')"),
        ChangedFile(filename="db/migration.sql", status="modified", patch="+CREATE TABLE users"),
    ]
    chunks = build_review_chunks(files, max_files=2, max_lines_per_chunk=100, max_chars_per_chunk=1000)
    assert chunks[0].filename in {"auth/login.py", "db/migration.sql"}
    assert all(chunk.filename != "tests/test_app.py" for chunk in chunks)
