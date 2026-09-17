---
title: "부록 A. Python 환경과 명령 실행"
description: 예제 환경을 분리하고 동기·비동기·하위 프로세스의 차이와 실패 출력을 읽는 방법을 정리한다.
last_modified_at: 2026-09-08
---

본문은 Python의 함수·딕셔너리·클래스를 읽을 수 있는 개발자를 대상으로 한다. 이 부록은 프로젝트를 실행할 때 필요한 환경과 오류 해석을 보충한다. 명령의 기준 위치는 저장소 루트다.

## 가상 환경과 의존성

먼저 실행할 Python을 확인하고 프로젝트 전용 가상 환경을 만든다. 시스템 Python의 패키지를 직접 바꾸지 않는다.

```bash
python3 --version
python3 -m venv books/ai-engineering/examples/.venv
books/ai-engineering/examples/.venv/bin/python -m pip install -r books/ai-engineering/examples/requirements.txt
```

가상 환경의 Python 경로를 명시하면 터미널 활성화 상태에 따른 혼동을 줄일 수 있다. Windows에서는 실행 파일의 경로가 `.venv/Scripts/python.exe`이며 셸 명령도 환경에 맞게 바꾼다. Windows 설치는 이 책의 확인 범위 밖이다.

기본 요구 파일은 API 어댑터와 계약 예제용이다. 로컬 모델에는 `requirements-local.txt`, MCP에는 `requirements-tools.txt`, 매체 예제에는 `requirements-media.txt`를 추가로 설치한다. 모델 가중치와 운영체제 도구는 pip 의존성과 별개다. 최초 다운로드에는 네트워크와 저장 공간이 필요하다.

`requirements-final-lock.txt`는 최종 집필 환경에서 설치된 패키지 목록이다. 직접 의존성을 읽기 위한 파일과 환경 전체 기록을 구분한다. 같은 버전을 지정해도 다른 운영체제에서 해당 Python용 배포 파일이 없을 수 있으므로 설치 가능성을 확인한다.

## 동기·비동기와 실제 동시 실행

일반 함수는 호출한 흐름에서 실행된다. `async def` 함수를 부르면 코루틴 객체가 생기고 `await`하거나 태스크로 돌려야 실행된다. 네트워크 응답을 기다리는 동안 다른 작업이 진행될 수 있지만 CPU 계산을 코루틴 안에 넣었다고 자동으로 병렬 계산이 되지는 않는다.

```python
import asyncio

async def fetch_status():
    await asyncio.sleep(0.01)  # 실제 네트워크 대기 대신
    return "ready"

async def main():
    result = await fetch_status()
    print(result)

asyncio.run(main())
```

위 예제의 대기는 네트워크 성능 측정이 아니다. 실제 HTTP 클라이언트를 사용하면 클라이언트의 비동기 API와 타임아웃·연결 풀 수명을 함께 관리한다. 이미 실행 중인 이벤트 루프가 있는 노트북에서 `asyncio.run`을 중첩하지 않는다. 해당 환경의 최상위 `await` 방식 등을 확인한다. [Python 코루틴과 태스크](https://docs.python.org/3/library/asyncio-task.html)

취소는 거래의 롤백과 다르다. 기다리던 코루틴이 취소돼도 외부 티켓 등록이 완료됐을 수 있다. 조회로 상태를 확인하거나 같은 멱등성 키로 재시도하는 업무 설계가 필요하다. 파일과 DB 연결은 `with`나 `try/finally`로 정리하고 취소 예외를 임의 성공으로 바꾸지 않는다.

## 하위 프로세스와 입력

Tesseract·FFmpeg처럼 별도 프로그램을 사용할 때는 인자 목록을 전달한다. 기본적으로 셸을 통하지 않으면 파일명에 들어 있는 셸 문법이 명령으로 해석되지 않는다. 그래도 호출 대상 프로그램이 해석하는 옵션과 경로는 검증해야 한다.

```python
completed = subprocess.run(
    ["program", "--input", str(input_path)],
    capture_output=True, text=True, check=True, timeout=30,
)
```

호출 형태를 보이는 예라서 `program`이라는 실행 파일이 따로 있지는 않다. `check=True`는 0이 아닌 종료 코드를 예외로 만들고 `timeout`은 대기 상한을 둔다. 장시간 서버는 시작·준비 확인·요청·종료를 따로 관리한다. `service_smoke.py`는 하위 서버 프로세스를 `finally`에서 종료한다.

표준 출력은 기계가 읽을 결과에, 표준 오류는 진단에 사용하면 JSON 결과와 진행 메시지가 섞이는 문제를 줄일 수 있다. 로그에는 자격 증명을 출력하지 않는다. 파일을 읽을 때는 인코딩과 크기를 명시하고 대용량 입력을 무제한으로 메모리에 올리지 않는다.

## 오류를 읽는 순서

명령이 실패하면 먼저 종료 코드와 가장 가까운 예외 원인을 확인한다. 패키지 없음, 모델 파일 없음, 인증 실패, 계약 실패는 해결 위치가 다르다. `ModuleNotFoundError`는 실행 Python과 설치 Python이 같은 환경인지부터 확인한다. 오프라인 모델 로드 실패는 필요한 리비전이 캐시에 있는지 본다.

HTTP 200 뒤의 `contract_failed`는 설치 오류가 아니다. 모델이 만든 내용이 서비스 계약을 통과하지 못한 결과다. 테스트 성공을 위해 검증을 삭제하지 말고 보존된 생성 결과와 필수 필드를 비교한다.

실행 기록에는 명령, 환경, 종료 코드, 출력 파일과 실험 조건을 남긴다. 다시 실행해 성공했다고 처음의 실패가 없었던 것처럼 덮어쓰지 않는다. 본문의 전후 비교 파일도 이 원칙대로 나눠 두었다.
