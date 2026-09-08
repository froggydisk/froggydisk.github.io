"""캐시·비밀·바이너리 음성을 제외하고 독자가 받을 예제 묶음을 만든다."""
from pathlib import Path
import hashlib
import json
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'books/ai-engineering'
TARGET = ROOT / 'public/books/ai-engineering/ai-engineering-examples.zip'


def main():
    files = []
    for folder in ('examples', 'experiments'):
        for path in (SOURCE / folder).rglob('*'):
            relative = path.relative_to(SOURCE)
            if any(part.startswith('.') or part == '__pycache__' for part in relative.parts):
                continue
            if path.is_file() and path.suffix in {'.py', '.txt', '.md', '.json', '.jsonl'}:
                files.append(path)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(TARGET, 'w', compression=ZIP_DEFLATED) as archive:
        for path in sorted(files):
            entry = ZipInfo(str(path.relative_to(ROOT)), date_time=(2026, 9, 8, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            archive.writestr(entry, path.read_bytes())
    print(json.dumps({'file': str(TARGET.relative_to(ROOT)), 'files': len(files),
                      'bytes': TARGET.stat().st_size,
                      'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest()}, indent=2))


if __name__ == '__main__':
    main()
