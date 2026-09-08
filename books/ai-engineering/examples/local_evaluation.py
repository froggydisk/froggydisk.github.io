"""6장: 고정한 가상 문서 사례의 실제 로컬 추론 기록. 자동 품질 채점은 하지 않는다."""

from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import version
import argparse
import json
import platform
import time

from local_model import LocalModel, MODEL_ID, REVISION
from model_client import DOCUMENT, INSTRUCTIONS


CASES = [
    {"id": "L01", "question": "교육비 한도와 신청 순서를 알려 줘", "context": DOCUMENT,
     "expected": "분기당 30만 원, 구매 전 팀장 승인, 지원 포털 신청을 모두 전달한다."},
    {"id": "L02", "question": "문서에 적힌 교육비 한도 문장만 그대로 옮겨 줘.", "context": DOCUMENT,
     "expected": "한울연구소의 직원 교육비 한도는 분기당 30만 원이다."},
    {"id": "L03", "question": "해외 출장 숙박비 한도는 얼마야?", "context": DOCUMENT,
     "expected": "제공 문서에서 확인할 수 없다고 답하며 금액을 만들지 않는다."},
    {"id": "L04", "question": "교육비 한도는 얼마야?", "context": "[제공된 문서 없음]",
     "expected": "확인할 수 없다고 답하며 이전 질문의 교육비 금액을 사용하지 않는다."},
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=["cpu", "mps"], default="cpu")
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 5:
        parser.error("repeats는 1~5여야 한다")
    started = time.perf_counter()
    model = LocalModel(device=args.device, offline=True)
    load_seconds = time.perf_counter() - started
    rows = []
    for case in CASES:
        for repeat in range(args.repeats):
            start = time.perf_counter()
            result = model.generate(case["question"], context=case["context"])
            rows.append({**case, "repeat": repeat + 1,
                         "generation_seconds": time.perf_counter() - start,
                         "result": asdict(result)})
    print(json.dumps({
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_ID, "revision": REVISION,
        "platform": platform.platform(), "python": platform.python_version(),
        "packages": {name: version(name) for name in
                     ("torch", "transformers", "safetensors", "huggingface-hub")},
        "device": args.device, "threads": model.torch.get_num_threads(),
        "dtype": str(next(model.model.parameters()).dtype),
        "parameter_count": sum(p.numel() for p in model.model.parameters()),
        "parameter_bytes": sum(p.numel() * p.element_size() for p in model.model.parameters()),
        "generation": {"do_sample": False, "enable_thinking": False, "max_new_tokens": 128},
        "instructions": INSTRUCTIONS, "offline": True, "load_seconds": load_seconds,
        "timing_scope": "토큰화·생성·디코딩을 포함한 generate 호출 전체; 별도 워밍업 없음", "rows": rows,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
