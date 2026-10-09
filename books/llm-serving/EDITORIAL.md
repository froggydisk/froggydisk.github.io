# 편집 및 검증 기록

기준일: 2026-10-09. 이 파일은 독자용 본문과 별도의 작업 기록이다. 뒤 장을 쓸 때 설정과 숫자를 여기서 맞춘다.

## 방침

- 독자: 인프라·ML 엔지니어
- 측정은 하지 않는다. 숫자는 공개 사양에서 계산하거나 출처가 있는 값만 쓴다. 출처는 그 숫자가 나오는 문장에 링크로 단다
- 코드와 실행 절차는 싣지 않는다 (book-chapter 스킬 §7과 같다). 계산식은 `text` 블록으로 둔다
- **전문가 문체로 쓴다 (2026-10-09 저자 지시).** 처음에 가상 회사(가람마켓) 장면으로 1부를 썼다가
  저자가 "이런 문체가 아니라 전문가 문체로 쓰는게 좋은데"라고 해서 다시 썼다. 현재형 설명문이고 장면·인물·
  화자 부사·감정어를 쓰지 않는다. `korean.md`의 번역투 목록은 그대로 걸고, 장면 전용 규칙(복선·시간축·
  장면 결어)은 걸지 않는다. `check-book.py`의 `NARRATIVE`에 넣지 않는다
- 기준 장비·모델은 H100 SXM 80GB 한 장 + Llama 3.1 8B Instruct(BF16)로 고정해 장끼리 숫자를 맞춘다.
  지연 목표 예시는 TTFT p99 1초 · TPOT p99 100ms이고, 본문에 예시라고 밝힌다

## 사양과 계산

| 값 | 출처 |
|---|---|
| 32층 · 어텐션 헤드 32 · KV 헤드 8 · 은닉 4,096 · MLP 14,336 · 어휘 128,256 · BF16 · 문맥 128k | [모델 카드](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct), `config.json` |
| 메모리 80GB · 대역폭 3.35TB/s · BF16 1,979 TFLOPS(희소성 가정, 밀집은 절반인 약 989) | [H100 제품 페이지](https://www.nvidia.com/en-us/data-center/h100/) |
| GPU 사용률 = 샘플 구간 중 커널이 하나 이상 돌던 시간의 비율 | [NVML](https://docs.nvidia.com/deploy/nvml-api/structnvmlUtilization__t.html) |
| SM_ACTIVE · PIPE_TENSOR_ACTIVE · DRAM_ACTIVE 정의 | [DCGM 기능 개요](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html) |
| TTFT · TPOT · 굿풋 | [DistServe](https://arxiv.org/abs/2401.09670) (OSDI 2024) |
| 프롬프트 계산은 연산 집약, 토큰 생성은 메모리 집약 | [Splitwise](https://arxiv.org/abs/2311.18677) |
| 반복 단위 스케줄링 | [Orca](https://www.usenix.org/conference/osdi22/presentation/yu) (OSDI 2022) — 2부에서 쓴다 |
| 연산 강도와 루프라인 | Williams·Waterman·Patterson, CACM 52(4), 2009. 본문 링크는 [기술 보고서판](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.html) |
| 반복 단위 스케줄링·선택적 배치 | Orca (OSDI 2022) |
| 청크 프리필 | [SARATHI](https://arxiv.org/abs/2308.16369), [Sarathi-Serve](https://arxiv.org/abs/2403.02310) (OSDI 2024) |
| PagedAttention. 기존 시스템 KV 메모리 실사용 20.4~38.2%, 처리량 2~4배 | [vLLM 논문](https://arxiv.org/abs/2309.06180) (SOSP 2023). "60~80% 낭비"는 블로그 수치라 쓰지 않았다 |
| RadixAttention | [SGLang](https://arxiv.org/abs/2312.07104) (NeurIPS 2024) |
| 자동 프리픽스 캐시 해시 방식 | [vLLM 설계 문서](https://docs.vllm.ai/en/latest/design/prefix_caching/) |
| GQA | [Ainslie 등](https://arxiv.org/abs/2305.13245) (EMNLP 2023) |
| GPTQ · AWQ(중요 가중치 1%) · LLM.int8() · SmoothQuant | 2210.17323 (ICLR 2023) · 2306.00978 (MLSys 2024) · 2208.07339 (NeurIPS 2022) · 2211.10438 (ICML 2023) |
| FP8 E4M3 최대 448, E5M2 최대 57,344 | [FP8 Formats](https://arxiv.org/abs/2209.05433) |
| KIVI (키 채널별·값 토큰별, 2비트) | [2402.02750](https://arxiv.org/abs/2402.02750) (ICML 2024) |
| 투기적 디코딩 2~3배(T5-XXL), 2~2.5배(Chinchilla 70B), 기대 토큰 수 식 | [Leviathan 등](https://arxiv.org/abs/2211.17192) (ICML 2023), [Chen 등](https://arxiv.org/abs/2302.01318) |
| Medusa 2.2배+ / 2.3~3.6배, EAGLE 2.7~3.5배 | 2401.10774 · 2401.15077 (둘 다 ICML 2024) |
| FlashAttention 1·2·3, FA3 FP16 740 TFLOPS(75%), FA2 35% | 2205.14135 · 2307.08691 · 2407.08608 |
| 텐서 병렬(열→행 분할, 층당 올리듀스 2회), GPipe | 1909.08053 · 1811.06965 |
| H100 SXM NVLink 900GB/s | H100 제품 페이지. PCIe판은 현재 페이지에 없다 |
| Llama 3.1 70B: 80층 · 헤드 64 · KV 헤드 8 · 은닉 8,192 · MLP 28,672 → 약 705억, 141GB, KV 320KiB/토큰 | unsloth 미러 config.json |
| Mooncake (arXiv 제목과 FAST 2025 제목이 다르다) | [2407.00079](https://arxiv.org/abs/2407.00079) |
| 리틀의 법칙 | Operations Research 9(3), 1961, doi 10.1287/opre.9.3.383 |
| vLLM 설정·지표 이름 (`max_num_seqs`, `max_num_batched_tokens`, `gpu_memory_utilization` 기본 0.92, `scheduling_policy`, `kv_cache_usage_perc`, `num_requests_waiting`) | engine_args · metrics 문서 (2026-10-09 확인) |

```text
파라미터  임베딩 525M + 출력층 525M + 층당 (어텐션 41.9M + MLP 176.2M) × 32 ≈ 80억 3천만
가중치    ≈ 16.06GB (BF16)
능선      989 TFLOPS ÷ 3.35TB/s ≈ 295 FLOP/바이트
디코드    배치 1 연산 강도 ≈ 1, 스텝 하한 ≈ 4.8ms, 단일 스트림 초당 약 200토큰, 연산기 0.3%
          배치 40 연산 강도 ≈ 40 (능선의 7분의 1, 연산기 열에 하나 남짓)
프리필    2,000토큰 ≈ 3.2 × 10¹³ FLOP ≈ 32ms (어텐션 제외 이상치), 디코드 스텝 예닐곱 번
KV 캐시   토큰당 2 × 32층 × 8헤드 × 128차원 × 2바이트 = 128KiB  (3부 1장에서 쓴다)
```

## 진행 상태

- 완료: 18장 전부 초고 (처음 계획의 "19장"은 개수를 잘못 센 것) (2026-10-09). 1부는 장면 문체 → 전문가 문체로 다시 썼다
- 저자 평: "어색한 한국어들이 너무 많기는 한데 끝까지 써 보자" → 다음 단계는 책 전체 문장 교정
- 쉼표: 장별 ending_comma z가 +3을 넘는 장이 몇 개 남았다 (2~5). 긴 문장의 절 경계라 일괄 삭제하지 않았다
- 그림은 1부 문체가 확정된 뒤 넣는다. 후보: 프리필/디코드 타임라인, 루프라인 위의 두 점, 배치 크기에 따른 처리량·토큰 간격
- 표지: 더미 시절 표지(`public/img/llm-serving-cover.webp`)를 저자 요청으로 그대로 쓴다 (2026-10-09). 그림 속 부제는 옛 부제다
