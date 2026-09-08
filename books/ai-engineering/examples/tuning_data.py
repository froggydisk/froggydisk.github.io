"""13장: 교육용 학습 표본의 계약과 분할 누수를 검사한다. 학습은 실행하지 않는다."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import unicodedata
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from answer_contract import Answer, unique_object, validate_answer


class Sample(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(min_length=1)
    split: Literal["train", "dev", "test"]
    family: str = Field(min_length=1)
    question: str = Field(min_length=1)
    evidence: dict[str, str]
    target: Answer


def normalized(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def fingerprint(sample: Sample) -> str:
    # 근거의 별칭이나 순서를 바꿔도 동일 입력으로 간주한다.
    payload = [normalized(sample.question),
               sorted(normalized(text) for text in sample.evidence.values())]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False).encode()).hexdigest()


def validate_samples(rows: list[dict]) -> dict:
    ids = set()
    families = {}
    inputs = {}
    counts = Counter()
    for row in rows:
        sample = Sample.model_validate(row)
        if any(not value.strip() for value in
               [sample.id, sample.family, sample.question, *sample.evidence.keys(),
                *sample.evidence.values()]):
            raise ValueError("blank_field")
        if sample.id in ids:
            raise ValueError("duplicate_id")
        ids.add(sample.id)
        validate_answer(sample.target.model_dump_json(), sample.evidence)
        # 분할 이름은 데이터 작성자가 지정한다. 검사가 임의로 고치지 않는다.
        for registry, key, error in (
            (families, normalized(sample.family), "family_leak"),
            (inputs, fingerprint(sample), "input_leak"),
        ):
            if key in registry and registry[key] != sample.split:
                raise ValueError(error)
            registry[key] = sample.split
        counts[sample.split] += 1
    if set(counts) != {"train", "dev", "test"}:
        raise ValueError("missing_split")
    return {"samples": len(ids), "families": len(families),
            "splits": dict(sorted(counts.items())),
            "scope": "structure_and_exact_input_leakage_only"}


def load_rows(path: Path) -> list[dict]:
    if path.stat().st_size > 1_000_000:
        raise ValueError("file_too_large")
    return [json.loads(line, object_pairs_hook=unique_object)
            for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    path = Path(__file__).parent / "fixtures" / "tuning-samples.jsonl"
    print(json.dumps(validate_samples(load_rows(path)), ensure_ascii=False, indent=2))
