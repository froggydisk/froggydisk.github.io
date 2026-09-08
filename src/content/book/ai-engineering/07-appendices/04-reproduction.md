---
title: "부록 D. 실행 환경과 재현 명령"
description: 집필에 사용한 패키지·모델 리비전·실행 순서와 검증 기록의 범위를 한곳에서 확인한다.
last_modified_at: 2026-09-08
---

이 책의 확인 기준일은 2026-09-08이다. 문서의 현재 버전과 고정한 실험 버전은 다를 수 있다. 아래 버전은 최신 권장 목록이 아니라 실제 집필 실행의 기준이다.

[예제 코드와 실험 기록 다운로드](/books/ai-engineering/ai-engineering-examples.zip)를 풀면 `books/ai-engineering/examples`와 `experiments` 디렉터리가 생긴다. 명령은 압축을 푼 최상위 디렉터리에서 실행한다. 모델 가중치·가상 환경·비밀·합성 음성 파일은 포함하지 않는다. 사이트 빌드 명령은 예제 묶음이 아니라 전체 사이트 저장소에서 실행한다.

## 실행 환경

| 항목 | 집필 기준 |
|---|---|
| 운영체제·아키텍처 | macOS, arm64 |
| Python | 3.14.6 |
| OpenAI Python SDK | 3.8.0 |
| httpx2 / Pydantic | 2.12.0 / 2.13.5 |
| Transformers / PyTorch | 5.16.1 / 2.14.0 |
| huggingface-hub / safetensors | 1.30.0 / 0.8.0 |
| MCP Python SDK | 1.30.0 |
| 실제 MCP 협상 버전 | 2025-11-25 |
| Pillow / Tesseract | 12.3.0 / 5.5.3 |
| 로컬 추론 | CPU, float32, PyTorch 스레드 4 |

MCP 패키지는 v1 예제 계약을 고정했다. 다른 버전으로 업데이트할 때는 연결·도구 결과의 구조를 다시 검증한다. 최종 설치 환경 전체는 `requirements-final-lock.txt`에 있다. 운영체제 명령·폰트·모델 파일은 이 목록에 포함되지 않는다.

## 모델과 자료 리비전

| 용도 | 모델·자료 | 고정 리비전 |
|---|---|---|
| 텍스트 생성 | `Qwen/Qwen3-0.6B` | `c1899de289a04d12100db370d81485cdf75e47ca` |
| 임베딩 | `intfloat/multilingual-e5-small` | `614241f622f53c4eeff9890bdc4f31cfecc418b3` |
| 음성 인식 | `openai/whisper-tiny` | `169d4a4341b33bc18d8881c4b69c2e104e1cc0af` |
| 한국어 OCR | `tesseract-ocr/tessdata_fast` | `87416418657359cb625c412a48b6e1d6d41c29bd` |

모델 캐시는 `examples/.model-cache`에 둔다. 실행 코드에서 모델 리비전과 함께 토크나이저·풀링·정규화 설정을 읽는다. E5는 질문과 문서의 접두사, 평균 풀링과 정규화가 검색 공간의 일부다. 다른 설정으로 만든 벡터를 같은 저장소에 섞지 않는다.

## 빠른 검증과 실제 모델 실행

먼저 가벼운 테스트를 실행한다. 테스트 검색은 모델 다운로드나 추론을 자동으로 수행하지 않는다.

```bash
books/ai-engineering/examples/.venv/bin/python -m unittest discover -s books/ai-engineering/examples -p 'test_*.py' -q
books/ai-engineering/examples/.venv/bin/python books/ai-engineering/examples/tuning_data.py
books/ai-engineering/examples/.venv/bin/python books/ai-engineering/examples/operations_demo.py
```

실제 모델을 처음 준비할 때는 로컬 의존성을 설치하고 다운로드가 허용된 예제를 실행한다. `local_model.py`의 기본 실행과 `embedding_demo.py`가 각각의 모델을 준비한다. 네트워크·디스크 사용은 모델 카드와 파일 목록에서 확인한다.

```bash
books/ai-engineering/examples/.venv/bin/python -m pip install -r books/ai-engineering/examples/requirements-local.txt
books/ai-engineering/examples/.venv/bin/python books/ai-engineering/examples/local_model.py '교육비 신청 순서는?'
books/ai-engineering/examples/.venv/bin/python books/ai-engineering/examples/embedding_demo.py
```

캐시를 준비한 뒤 다음 시연을 실행한다. 기존 기록과 비교하려면 새 파일로 저장하고 원본 실험을 덮어쓰지 않는다.

```bash
books/ai-engineering/examples/.venv/bin/python books/ai-engineering/examples/store_demo.py
books/ai-engineering/examples/.venv/bin/python books/ai-engineering/examples/rag_demo.py --prompt-version rag-local-v2
books/ai-engineering/examples/.venv/bin/python books/ai-engineering/examples/hybrid_demo.py
books/ai-engineering/examples/.venv/bin/python books/ai-engineering/examples/service_smoke.py
```

실제 MCP 연결은 추가 의존성 설치 후 실행한다. 가상 티켓 DB와 테스트용 승인 이벤트를 사용한다.

```bash
books/ai-engineering/examples/.venv/bin/python -m pip install -r books/ai-engineering/examples/requirements-tools.txt
books/ai-engineering/examples/.venv/bin/python books/ai-engineering/examples/mcp_ticket_demo.py
```

매체 실습은 Python 환경 외에 Tesseract·FFmpeg와 macOS의 Yuna 음성·폰트 경로가 필요하다. `requirements-media.txt` 설치 뒤 `media_demo.py`를 실행한다. 다른 운영체제의 호환성은 확인 범위 밖이다.

## 기록을 해석하는 방법

| 기록 | 확인한 범위 |
|---|---|
| `local-cpu.json` | 실제 로컬 생성의 작은 질문 집합 |
| `embedding-cpu.json` | 실제 E5 유사도 검색 |
| `store-lifecycle.json` | 파일 저장소의 갱신·권한·삭제 |
| `rag-local.json`, `rag-local-v2.json` | 실제 RAG 생성 실패와 프롬프트 비교 |
| `hybrid-baseline.json` | E5·FTS5·RRF의 작은 자료 비교 |
| `mcp-tickets.json` | 실제 서버·클라이언트 프로세스 연결 |
| `agent-control.json` | 대역 계획기의 제어 흐름 |
| `media-local.json` | 실제 OCR·합성 음성 인식 |
| `evaluation-v2.json` | 보존된 RAG 기록의 재채점 |
| `operations-local.json` | 합성 대기의 과부하·마감·복귀 |
| `service-local.json` | 실제 모델 HTTP·CLI·파일 DB 연결 |

호스팅 모델의 유료 API 호출, 파인튜닝, 영상·이미지 생성 모델, 실제 모델의 동시 부하와 인터넷 공개 배포는 실행 기록에 포함하지 않는다. 모의 HTTP 전송으로 검증한 SDK 동작과 실제 제공자 호출을 구분한다.

## 책 사이트 검증

원고는 `src/content/book/ai-engineering`에 있고 예제·실험·편집 기록은 `books/ai-engineering`에 있다. 정적 사이트를 빌드한 뒤 경로와 링크를 검사한다.

```bash
npm run build
python3 books/ai-engineering/verify_site.py
```

검사기는 본문·표지·내부 링크·앵커·canonical·두 사이트맵을 비교한다. 실제 브라우저의 이동·검색·모바일 표시 검증은 별도의 절차이며 최종 편집 기록에 결과를 남긴다. 정적 책 사이트의 배포와 Python 예제 서버의 배포는 서로 다른 작업이다.
