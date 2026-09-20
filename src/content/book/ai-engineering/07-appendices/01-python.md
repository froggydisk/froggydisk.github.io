---
title: "부록 A. Python 환경과 명령 실행"
description: 예제 환경을 분리하고 동기·비동기·하위 프로세스의 차이와 실패 출력을 읽는 방법을 정리한다.
last_modified_at: 2026-09-08
---

본문은 Python의 함수·딕셔너리·클래스를 읽을 수 있는 개발자를 대상으로 한다. 이 부록은 프로젝트를 실행할 때 필요한 환경과 오류 해석을 보충한다. 명령은 모두 저장소 루트에서 실행한다.

## 가상 환경과 의존성

먼저 실행할 Python을 확인하고 프로젝트 전용 가상 환경을 만든다. 시스템 Python의 패키지를 직접 바꾸지 않는다.

```bash
python3 --version
python3 -m venv books/ai-engineering/examples/.venv
books/ai-engineering/examples/.venv/bin/python -m pip install -r books/ai-engineering/examples/requirements.txt
```

가상 환경의 Python 경로를 그대로 적으면 터미널에서 활성화를 했든 안 했든 늘 같은 Python이 실행된다. Windows에서는 실행 파일 경로가 `.venv/Scripts/python.exe`다. 셸 명령도 Windows에 맞게 바꾼다. Windows 설치는 이 책의 확인 범위 밖이다.

`requirements.txt`는 API 어댑터와 계약 예제를 돌릴 때 쓴다. 로컬 모델에는 `requirements-local.txt`, MCP에는 `requirements-tools.txt`, 매체 예제에는 `requirements-media.txt`를 추가로 설치한다. 모델 가중치와 운영체제 도구는 pip가 설치해 주지 않는다. 운영체제 도구는 그 운영체제의 패키지 관리자로 따로 깔고, 가중치는 예제를 처음 돌릴 때 받아 오므로 그 한 번에 네트워크와 저장 공간이 꽤 든다.

`requirements-final-lock.txt`는 최종 집필 환경에서 설치된 패키지 목록이다. 설치는 `requirements.txt`로 하고 이 목록은 그때 환경을 되짚어 볼 때만 연다. 같은 버전을 지정해도 다른 운영체제에서 해당 Python용 배포 파일이 없을 수 있으므로 설치 가능성을 확인한다.

## 동기·비동기와 실제 동시 실행

일반 함수는 호출한 흐름에서 실행된다. `async def` 함수를 부르면 코루틴 객체가 생기고 `await`하거나 태스크로 돌려야 실행된다. 코루틴은 `await`을 만날 때만 실행권을 내려놓고, 그 틈에 이벤트 루프가 다음 코루틴을 돌린다. 네트워크 응답을 기다리는 사이에 일이 진행되는 것도 이 때문이다. 반대로 코루틴 안에서 CPU를 붙잡고 계산을 돌리면 실행권을 내려놓을 틈이 없어서, `async`를 붙였어도 나머지는 그동안 멈춰 있다.

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

실제 HTTP 클라이언트를 사용하면 클라이언트의 비동기 API와 타임아웃·연결 풀 수명을 함께 관리한다. 이미 실행 중인 이벤트 루프가 있는 노트북에서 `asyncio.run`을 중첩하지 않는다. 그 환경에서 최상위 `await`을 어떻게 쓰는지 확인한다. [Python 코루틴과 태스크](https://docs.python.org/3/library/asyncio-task.html)

코루틴을 취소해도 바깥 시스템에는 티켓이 이미 등록돼 있을 수 있다. 그래서 상태를 다시 조회하거나 같은 멱등성 키로 재시도하도록 업무 흐름을 미리 짜 둔다. 파일과 DB 연결은 `with`나 `try/finally`로 정리한다. 취소 예외를 삼켜서 성공으로 기록하지 않는다.

## 하위 프로세스와 입력

Tesseract·FFmpeg처럼 별도 프로그램을 사용할 때는 인자 목록을 전달한다. 인자 목록으로 넘기면 셸을 거치지 않으므로 파일 이름에 셸 문법이 섞여 있어도 셸이 명령으로 읽지 않는다. 그래도 호출 대상 프로그램이 해석하는 옵션과 경로는 검증해야 한다.

```python
completed = subprocess.run(
    ["program", "--input", str(input_path)],
    capture_output=True, text=True, check=True, timeout=30,
)
```

호출하는 꼴만 보여 주는 예라서 `program`이라는 실행 파일이 실제로 있지는 않다. `check=True`는 0이 아닌 종료 코드를 예외로 만들고 `timeout`은 대기 상한을 둔다. 오래 띄워 두는 서버라면 시작·준비 확인·요청·종료를 따로 관리한다. `service_smoke.py`는 하위 서버 프로세스를 `finally`에서 종료한다.

표준 출력은 기계가 읽을 결과에, 표준 오류는 진단에 사용하면 JSON 결과와 진행 메시지가 섞이는 문제를 줄일 수 있다. 로그에는 자격 증명을 출력하지 않는다. 파일을 읽을 때는 인코딩과 크기를 명시한다. 아무리 큰 입력이라도 통째로 메모리에 올리지 않는다.

## 오류를 읽는 순서

명령이 실패하면 종료 코드부터 확인하고 그다음 예외에서 가장 가까운 원인을 짚는다. 패키지 없음, 모델 파일 없음, 인증 실패, 계약 실패는 손볼 자리가 저마다 따로 있다. `ModuleNotFoundError`가 뜨면 실행 Python과 설치 Python이 같은 환경인지부터 확인한다. 모델을 오프라인으로 불러오다 실패하면 필요한 리비전이 캐시에 있는지 본다.

HTTP 200이 돌아왔는데 `contract_failed`가 찍혔다면 설치가 아니라 모델이 내놓은 답을 본다. 그 답이 JSON·필드·상태·인용 검사를 통과하지 못해 검증기가 막았기 때문이다. 테스트를 통과시키려고 검증을 지우지 말고 남겨 둔 생성 결과와 필수 필드를 맞춰 본다.

실행 기록에는 명령, 환경, 종료 코드, 출력 파일과 실험 조건을 남긴다. 다시 실행해 성공했다고 처음의 실패가 없었던 것처럼 덮어쓰지 않는다. 본문의 전후 비교 파일도 실패한 실행과 다시 성공한 실행을 따로 남겨 뒀다.
