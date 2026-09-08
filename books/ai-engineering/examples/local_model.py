"""6장: 고정한 공개 가중치를 로드해 텍스트를 생성한다. 최초 실행은 다운로드한다."""
from dataclasses import asdict
import argparse
import json
from pathlib import Path
import time

from model_client import DOCUMENT, INSTRUCTIONS, GenerationResult


MODEL_ID = "Qwen/Qwen3-0.6B"
REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"


class LocalModel:
    def __init__(self, *, device="cpu", offline=False):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        if device not in ("cpu", "mps"):
            raise ValueError("이 예제는 cpu 또는 mps를 사용한다")
        if device == "mps" and not torch.backends.mps.is_available():
            raise ValueError("MPS를 사용할 수 없다")
        torch.set_num_threads(4)
        self.torch = torch
        self.device = device
        cache = Path(__file__).parent / ".model-cache"
        options = dict(revision=REVISION, cache_dir=str(cache),
                       trust_remote_code=False, local_files_only=offline, token=False)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, **options)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, dtype=torch.float32, **options).to(device)
        self.model.eval()

    def prepare(self, question, *, instructions=INSTRUCTIONS, context=DOCUMENT):
        messages = [{"role": "system", "content": instructions},
                    {"role": "user", "content": f"{context}\n\n[사용자 질문]\n{question}"}]
        return self.tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True,
            enable_thinking=False, return_dict=True, return_tensors="pt").to(self.device)

    def generate(self, question: str, *, instructions=INSTRUCTIONS,
                 context=DOCUMENT, output_limit=128) -> GenerationResult:
        if not question.strip() or type(output_limit) is not int or not 1 <= output_limit <= 512:
            raise ValueError("질문과 1~512 사이의 출력 한도가 필요하다")
        inputs = self.prepare(question, instructions=instructions, context=context)
        size = inputs["input_ids"].shape[-1]
        # 모델 최대치와 별도로 이 실습의 메모리·대기 비용을 제한한다.
        if size + output_limit > min(4096, self.model.config.max_position_embeddings):
            raise ValueError("이 실습의 입력·출력 예산을 초과한다")
        with self.torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=output_limit,
                                         do_sample=False)
        tokens = output[0, size:].tolist()
        eos = self.model.generation_config.eos_token_id
        eos_ids = {eos} if isinstance(eos, int) else set(eos or [])
        completed = bool(tokens) and tokens[-1] in eos_ids
        text = self.tokenizer.decode(tokens, skip_special_tokens=True).strip()
        if not completed:
            return GenerationResult(status="incomplete", input_tokens=size,
                                    output_tokens=len(tokens), error_code="output_limit")
        if not text:
            return GenerationResult(status="unexpected_output", input_tokens=size,
                                    output_tokens=len(tokens))
        return GenerationResult(status="ok", text=text, input_tokens=size, output_tokens=len(tokens))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--device", choices=["cpu", "mps"], default="cpu")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    start = time.perf_counter()
    model = LocalModel(device=args.device, offline=args.offline)
    loaded = time.perf_counter()
    result = model.generate(args.question)
    print(json.dumps({"model": MODEL_ID, "revision": REVISION, "device": args.device,
        "load_seconds": loaded-start, "generation_seconds": time.perf_counter()-loaded,
        "result": asdict(result)}, ensure_ascii=False, indent=2))
    return 0 if result.status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
