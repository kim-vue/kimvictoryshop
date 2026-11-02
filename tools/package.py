"""Produce a portable source ZIP; never include credentials, caches or Git data."""
from hashlib import sha256
from pathlib import Path
import zipfile


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "dist"
    output.mkdir(exist_ok=True)
    archive = output / "ZOOMCONNECT5-mixed-v0.3.zip"
    files = [root / name for name in ("README.md", "AGENTS.md", "pyproject.toml", ".gitignore")]
    for directory in ("zoomconnect", "tests", "tools", "docs"):
        files.extend(path for path in (root / directory).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts and path.suffix not in (".pyc", ".pyo"))
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(files):
            bundle.write(path, path.relative_to(root).as_posix())
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
    digest = sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".zip.sha256").write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    print(f"{archive.name}: {archive.stat().st_size} bytes; {len(files)} files")
    print(f"SHA256 {digest}")


if __name__ == "__main__":
    main()
