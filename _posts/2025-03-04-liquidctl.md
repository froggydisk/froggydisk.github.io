---
title: "[H/W] Kraken ELITE RGB를 위한 Liquidctl 사용법"
comments: true
categories:
  - Blog
tags:
  - Server, Cooler
last_modified_at: 2025-03-04T
---

다음의 상황인 분들을 위한 글이다.

## 상황

- 쿨러에 화면을 띄우고 싶은데 OS가 리눅스 계열이어서 공식 프로그램을 사용할 수 없을 때
- Kraken ELITE RGB를 사용할 때
- [공식문서](https://github.com/liquidctl/liquidctl)가 너무 복잡하다고 느낄 때

## 설치

아래 코드는 [공식문서](https://github.com/liquidctl/liquidctl)를 참고하며 `Manual Installation > Working locally`의 설치 순서를 따른다.

설치는 파이썬 가상 환경 위에서 진행된다.

```bash
python3 -m venv liquidctl # 전용 파이썬 환경 생성
source liquidctl/bin/activate # 해당 환경으로 접속
python3 -m pip install git+https://github.com/liquidctl/liquidctl#egg=liquidctl
git clone https://github.com/liquidctl/liquidctl # 소스코드 다운
cd liquidctl
python3 -m pip install --upgrade pip setuptools setuptools_scm wheel
python3 -m pip install --upgrade colorlog crcmod==1.7 docopt hidapi pillow pytest pyusb
python3 -m pip install --upgrade "libusb-package; sys_platform == 'win32' or sys_platform == 'cygwin'"
python3 -m pip install --upgrade "smbus; sys_platform == 'linux'"
python3 -m pip install --upgrade "winusbcdc>=1.5; sys_platform == 'win32'"
python3 -m pytest # 테스트
python3 -m pip install .
```

## 사용

sudo 명령어를 사용하게 되면 기본적으로 root 환경을 바라보고 있으므로 `$(which python3)`를 사용해주어야 현재 환경에서 liquidctl을 사용할 수 있다.

```bash
sudo $(which python3) -m liquidctl initialize all
sudo $(which python3) -m liquidctl list # 인식된 기기 리스트
sudo $(which python3) -m liquidctl status # 인식된 기기 현재 정보
sudo $(which python3) -m liquidctl -m NZXT set lcd screen gif [gif 이미지] # gif 적용
sudo $(which python3) -m liquidctl -m ASUS set sync color rainbow # 쿨링팬 색 변경
```

-m 옵션은 인식된 제품이 여러 개일 경우에 해당 단어로 타겟을 필터링 해주는 역할이다. grep 명령어와 비슷하다고 생각하면 된다.
