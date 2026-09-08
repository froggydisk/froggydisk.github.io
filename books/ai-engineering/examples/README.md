# AI 엔지니어링 예제

2장: 표준 라이브러리로 샘플링 확률 계산. 3장: Responses API 호출과 모의 HTTP·스트림 검증.

저장소 루트에서 실행한다.

```sh
python3 -m venv books/ai-engineering/examples/.venv
source books/ai-engineering/examples/.venv/bin/activate
python -m pip install -r books/ai-engineering/examples/requirements.txt
python books/ai-engineering/examples/sampling.py
python -m unittest discover -s books/ai-engineering/examples -p 'test_*.py' -v
```

`requirements.txt`는 직접 사용하는 패키지 버전이다. `requirements-lock.txt`는 검증 환경의 전체 설치 목록이며 당시 함께 설치한 httpx 등도 포함한다. 플랫폼별 바이너리 호환성은 별도로 확인한다.

외부 모델 호출에는 실행 환경에 `OPENAI_API_KEY`와 `OPENAI_MODEL`이 필요하다. 키를 파일이나 커밋에 넣지 않는다. 모델은 해당 계정에서 Responses API 텍스트 입력과 요청 인자를 지원하는 식별자로 지정한다.

```sh
python books/ai-engineering/examples/model_client.py "교육비 한도는?"
python books/ai-engineering/examples/model_client.py --stream "교육비 신청 순서는?"
```

모의 테스트는 가짜 키·가짜 모델과 메모리 내 전송을 사용한다. 실제 네트워크 요청이나 모델 추론은 수행하지 않는다. `--stream`도 최종 완료 전에는 답변을 stdout에 출력하지 않는다. 외부 API 통합 실행과 품질 검증은 아직 수행하지 않았다.

검증 결과는 상위 디렉터리의 `VALIDATION.md`에 기록한다.


4장: `context_budget.py`는 권한 검사·문맥 선택·입력 계수·가상 비용 계산을 제공한다. `context_demo.py`는 네트워크 없이 문자 단위로 선택을 시연한다. 시연의 `input_tokens` 값은 모델 토큰 수가 아니며 `count_method`에 명시한다.

```sh
python books/ai-engineering/examples/context_demo.py
```

실제 계수에는 `provider_counter(client, model, INSTRUCTIONS)`를 전달한다. 반환된 계획을 `generate(..., input_text=plan.input_text, output_limit=plan.output_reserve)`에 연결한다. 계수 전에 문서·대화의 접근 범위를 검사하며 `Principal`은 인증·권한 조회를 마친 서버가 만들어야 한다. 전체 비용 한도를 동시 요청에 예약하는 기능은 아직 구현하지 않았다.


5장: `answer_contract.py`는 Pydantic 출력 모델, 생성 스키마, 상태·인용 검증과 앞 장의 통합 함수를 제공한다.

```sh
python books/ai-engineering/examples/answer_demo.py
```

시연은 저자가 작성한 가상 출력을 사용한다. `contract_valid`는 사실성 검증 완료를 뜻하지 않는다. `answer_question`은 계수·생성에 동일한 지시문과 스키마를 전달하고 실제 전송한 문서만 인용 근거로 허용한다. 계수 실패는 호출자에게 예외로 전달한다. 실제 외부 호출은 아직 미검증이다.

사이트는 저장소 루트에서 `npm run build` 후 `python3 books/ai-engineering/verify_site.py`로 원고와 출력 경로·링크·사이트맵을 비교할 수 있다. 이 검사는 브라우저의 시각적 배치나 실제 검색 질의 검사를 대신하지 않는다.


6장: `local_model.py`는 공개 가중치 Qwen3-0.6B를 고정 리비전으로 로드하는 실제 추론 어댑터다. `local_evaluation.py`는 네 가상 사례를 각각 두 번 실행하며 원문 출력과 실행 조건을 JSON으로 기록한다. CPU float32에서 검증했다. `mps` 경로는 미검증이다.

```sh
python -m pip install -r books/ai-engineering/examples/requirements-local.txt
python books/ai-engineering/examples/local_model.py '교육비 한도와 신청 순서를 알려 줘'
python books/ai-engineering/examples/local_evaluation.py > /tmp/local-evaluation-new.json
```

최초 모델 다운로드 이후 평가 스크립트는 로컬 캐시만 사용한다. `.model-cache`는 Git에서 제외한다. 기존 실측 기록은 `../experiments/local-cpu.json`, 최초 다운로드 포함 실행은 `local-first-download.json`, 출력 한도·예산 경계 검사는 `local-boundaries.json`이다. `requirements-local-lock.txt`는 로컬 실행 의존성을 추가한 시점의 전체 설치 목록이다. 기본 `requirements-lock.txt`는 3장 검증 시점의 기록으로 유지한다.

반복 실행의 시간은 달라질 수 있다. 평가 스크립트는 모델 품질을 자동 채점하지 않으며 `expected`는 작성자가 정한 판정 기준이다. 본문의 판정은 실제 출력을 그 기준과 대조한 결과다. 이 로컬 어댑터는 3장의 결과 타입을 공유하지만 5장의 제약 생성·출력 검증 파이프라인을 대체하지 않는다.


7장: `vector_search.py`는 코사인·전수 검색, `embedding_model.py`는 고정 리비전의 실제 다국어 E5 어댑터다. 6장의 requirements-local.txt 환경을 사용한다. `embedding_demo.py`는 가상 문서 다섯 개와 질의 다섯 개를 실행한다.

```sh
python books/ai-engineering/examples/embedding_demo.py > /tmp/embedding-new.json
python books/ai-engineering/examples/embedding_checks.py
python books/ai-engineering/examples/vector_applications.py
```

최초 다운로드 이후 `embedding_demo.py --offline`을 사용할 수 있다. `embedding_checks.py`는 로컬 캐시를 요구하며 실제 모델의 차원·정규화·단독/배치 입력 일치·입력 오류를 확인한다. 기본 unittest 발견 실행은 이 스크립트를 실행하거나 모델 파일을 다운로드하지 않는다.

실측은 `../experiments/embedding-cpu.json`, 실제 경계 검증은 `embedding-checks.json`이다. 검색의 relevant는 ‘답변 근거를 담은 문서’ 기준이며 주제가 비슷하다는 뜻과 다르다. `vector_applications.py`의 분류·추천·이상 후보는 저자가 만든 2차원 숫자 시연이고 텍스트 모델 품질 실험이 아니다.


8장: `document_store.py`는 SQLite에 원문 청크·시행 구간·벡터·ACL·문서 순번을 저장한다. 벡터는 JSON이며 검색은 Python 전수 계산이다. 네이티브 ANN 색인을 설치한 구현은 아니다.

```sh
python books/ai-engineering/examples/store_demo.py
```

E5 캐시가 필요하다. 시연은 fixtures/policies의 UTF-8 파일 두 개를 읽고 임시 DB에 저장한다. 실제 기록은 `../experiments/store-lifecycle.json`이다. 기본 unittest는 실제 임시 SQLite 파일과 대역 임베딩으로 원자성·시행일·권한·순번·삭제·입력 처리를 검사한다.

Store.replace는 신뢰된 수집 계층이 보내는 문서 전체 리비전 스냅샷을 받는다. sequence는 문서별 원본 변경 순번이며 오래된 작업을 차단한다. 빈 revisions는 삭제다. 삭제 후 복원 시 읽기 권한은 다시 부여해야 한다. grant/revoke/replace는 사용자나 모델에 직접 공개할 도구가 아니다. 검색 시 DB ACL과 Principal.readable_docs의 교집합을 적용한다. 최종 응답 직전의 권한 경쟁 검사와 원본 시스템 연동은 후속 통합 범위다.


9장: `rag_service.py`의 respond가 SQLite 검색, 문맥 예산, 생성, 인용 검증과 출처 재확인을 연결한다. `rag_local_backend.py`는 기존 LocalModel의 입력 준비 경로를 공유한다. JSON은 프롬프트로 요청하고 사후 검사하며 제약 디코딩을 구현하지 않았다.

```sh
python books/ai-engineering/examples/rag_demo.py > /tmp/rag-v1-new.json
python books/ai-engineering/examples/rag_demo.py --prompt-version rag-local-v2 > /tmp/rag-v2-new.json
```

E5와 Qwen 모델 캐시가 필요하다. 실험은 임시 SQLite와 가상 자료만 사용한다. 기존 기록 `../experiments/rag-local.json`과 `rag-local-v2.json`에는 원본 생성문이 포함돼 있다. 서비스 실패 결과에는 원본 답변·출처를 남기지 않는다.

두 프롬프트 모두 실제 세 생성 사례에서 필수 clarification 필드를 누락해 contract_failed였다. v1은 코드 블록도 포함했다. 숙박비 오답과 상충 문서의 임의 선택은 별도의 의미 실패다. R04는 권한 회수 후 생성 호출 없이 insufficient_evidence였다. 정상 출처 연결의 자동 테스트는 대역 생성기의 결과를 사용하므로 모델 품질 검증과 구분한다. responded status answered는 구조·인용 계약 통과이며 의미 정확성의 인증이 아니다.


10장: hybrid_search.py는 FTS5 키워드 검색과 RRF 순위 융합, hybrid_demo.py는 실제 E5와의 비교다.

```sh
python books/ai-engineering/examples/hybrid_demo.py > /tmp/hybrid-new.json
```

키워드 함수는 이미 권한·시행일 검사를 마친 자료를 입력받아야 한다. 실험은 모든 자료가 허용된 가상 주체를 사용하며 지속 색인/9장 서비스 연결은 아직 없다. 매번 메모리 색인을 만드므로 keyword 시간에는 색인 생성이 포함된다. dense 시간에는 질문 임베딩이, fusion 시간에는 융합만 포함된다. 원본 결과 hybrid-unsegmented.json과 전처리 수정 후 hybrid-baseline.json을 experiments에 보존했다. RRF는 이 자료에서 의미 검색보다 나은 1위 결과를 보이지 않았다.


11장: ticket_tools.py는 가상 티켓의 초안·승인·등록·조회와 멱등성·감사를 제공한다. mcp_ticket_server.py가 준비/등록/조회만 stdio 도구로 노출하고 mcp_ticket_demo.py가 실제 하위 프로세스에 연결한다.

```sh
python -m pip install -r books/ai-engineering/examples/requirements-tools.txt
python books/ai-engineering/examples/mcp_ticket_demo.py
```

MCP SDK는 1.30.0 고정, 실제 협상 프로토콜은 2025-11-25다. requirements-tools-lock.txt는 로컬 모델 패키지도 포함한 설치 환경 전체 기록이다. 시연은 임시 DB만 사용하며 승인 이벤트는 테스트 픽스처로 주입한다. 실제 사용자 확인·모델의 도구 선택·외부 티켓 등록을 검증한 것이 아니다. 결과는 experiments/mcp-tickets.json이다.

approve/grant/revoke는 신뢰된 호스트 관리 경로이며 모델 도구로 노출하지 않는다. 서버의 hanul/demo 고정 주체는 단일 로컬 실습용이다. 원격 인증, 승인 만료/취소, 다중 사용자 서비스는 미구현이다.


12장: agent_loop.py는 허용 행동·입출력 스키마·반복·단계·가상 크레딧·마감 검사를 포함한다. agent_demo.py는 대역 계획기와 실제 임시 티켓 DB를 연결한다.

```sh
python books/ai-engineering/examples/agent_demo.py
```

실제 모델 추론이나 다중 에이전트 실행은 아니다. 확인 이벤트도 테스트 픽스처다. 기록은 experiments/agent-control.json. 계획 1단위·도구 2단위는 가상 정책 예산이며 가격/토큰 요금이 아니다. 동기 호출을 강제로 취소하지 않으며 도구 호출 후 오류·마감 초과는 execution_unknown으로 중단한다. 프로세스 재시작 후 복구할 체크포인트는 아직 없다.

13장: tuning_data.py는 교육용 JSONL의 응답 계약·식별자·문서 계열 분리·정규화된 동일 입력 누수를 검사한다.

```sh
python books/ai-engineering/examples/tuning_data.py
```

fixtures/tuning-samples.jsonl의 9행은 형식과 검사 실습용이며 실제 학습 준비가 끝난 데이터가 아니다. 문서 계열은 5개, train/dev/test는 4/2/3행이다. 근접 중복·정답 의미·개인정보·출처 권한은 자동으로 검증하지 않는다. test_tuning_data.py는 의미적 오답이 구조 검사를 통과하는 한계도 확인한다. 학습은 실행하지 않았으며 학습 전후 향상률은 없다. 판단은 experiments/fine-tuning-decision.md, 검사 결과는 experiments/tuning-data-check.json에 기록했다.

14–18장과 부록:

- `media_demo.py`: macOS의 Yuna·AppleSDGothicNeo로 가상 매체를 만들고 Tesseract와 실제 Whisper tiny를 실행한다. `requirements-media.txt`, 별도 Tesseract/FFmpeg 설치가 필요하다. 최초 모델/OCR 데이터 다운로드가 있으며 바이너리 표본은 Git에서 제외한다. OCR와 전사 결과는 `experiments/media-local.json`.
- `test_security.py`: 다른 조직 자료의 계수 전 차단, 없는 출처 인용 거부, 모델 승인 사칭의 실행 차단. 모델의 실제 주입 저항성 점수가 아니다.
- `evaluation.py RECORD`: R01–R04의 중복·누락을 거부하고 상태 일치를 채점한다. 의미 평가는 `not_scored`, 채택은 보류다. `experiments/evaluation-v2.json`.
- `operations_demo.py`: 실제 asyncio 큐에 합성 대기 부하를 넣고 과부하·마감·버전 복귀를 확인한다. 실제 모델 처리량이 아니다.
- `book_service.py`: `--state DIRECTORY init`, `serve`, `prepare`, `confirm`, `get`. 실제 E5/Qwen과 파일 SQLite를 연결한 로컬 단일 사용자 교육용 HTTP 서버·관리 CLI. `serve`에는 24자 이상 ASCII `BOOK_LOCAL_TOKEN`이 필요하다. 외부 공개 운영용 서버가 아니다. 모델의 RAG 생성 품질은 여전히 채택 보류다.
- `service_smoke.py`: 임시 상태·임시 로컬 토큰·실제 가중치로 전체 HTTP/CLI 경로를 확인한다. v2 실행 후 v1 재시작, 인증/필드 거부, 티켓 재실행을 검사한다. 확인은 테스트 픽스처이며 실제 사용자 UI 평가가 아니다.

모든 명령은 저장소 루트 기준이다. 최종 설치 패키지는 `requirements-final-lock.txt`, 전체 원고의 실행 안내는 부록 D에 있다. 외부 API 과금 호출·파인튜닝·영상/이미지 생성 모델·인터넷 공개 배포를 실행한 것으로 설명하지 않는다.
