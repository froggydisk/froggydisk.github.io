---
title: "PyQt5가 다운로드 되지 않는 M1 맥북 이슈"

comments: true
categories:
  - Blog
tags:
  - Python, pip
last_modified_at: 2023-05-09T
---

### 🔒 에러

**pip install PyQt5를 해도 Preparing metadata(pyproject.toml)에서 넘어가지 않는 M1 맥북 이슈**를 만났다. _(metadata-generation-failed, subprocess-exited-with-error)_  
문제 해결에 앞서 라이브러리 선택의 여유가 있는 사람들은 `Pyside6나 PyQt6`도 고려해보길 권한다.

여러가지로 테스트 해본 결과는 다음과 같다.

📄 테스트 리스트

- pip install pyqt5 (실패)
- pip3 install pyqt5 (실패)
- python -m pip install pyqt5 (실패)
- python3 -m pip install pyqt5 (실패)

### 🔑 해결

결국 해결방안은 `Homebrew`를 이용하는 것이었다.

```bash
arch -arm64 brew install pyqt5
```

`brew list`로 잘 설치가 되었는지 확인한다. 설치가 안되었다면 `brew reinstall`로 재설치를 진행한다.  
만약 가상환경을 사용한다면 `python -m pip list` 와 `python3 -m pip list`를 둘 다 확인하여 어느곳에 설치되었는지 보고 상황에 맞게 `python 또는 python3` 명령어를 사용해야한다. 루트 환경에서는 보통 `python`과 `python3` 명령어가 같은 경로를 가리키고 있으므로 어느쪽을 사용하든 결과는 같다. 이후로 다른 라이브러리를 설치할 때도 명령어 버전에 맞게 설치해 주면 된다.

```bash
python -m pip install [라이브러리]
혹은
python3 -m pip install [라이브러리]
```

### 🤔 원인 분석

`PyQt5`는 Qt의 C++ 라이브러리를 필요로 하는데, 기본적으로 macOS에는 설치되어 있지 않다. Qt 및 필요한 라이브러리들이 `brew install` 시에 설치되고 이후 `pip install` 시에 해당 라이브러리를 사용함으로써 오류가 사라졌을 가능성이 높다.
