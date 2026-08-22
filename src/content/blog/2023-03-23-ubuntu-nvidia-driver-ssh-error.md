---
title: "[Ubuntu] Nvidia 드라이버 설치 후 ssh 접속 불가 문제"

comments: true
categories:
  - Blog
tags:
  - Linux, Ubuntu, Nvidia
last_modified_at: 2023-03-23T
---


## 대상
이 글은 Nvidia GPU가 설치된 우분투 서버에 ssh 접속을 하기 위해 세팅을 하시는 분들을 대상으로 합니다. 

## 1. Nvidia 드라이버 설치

#### 장치 확인
먼저 GPU 장치가 잘 인식되어 있는지 확인한다.
```python
lshw -C display
```

#### 설치
Nvidia 드라이버 설치를 위해서는 우선 `ubuntu-drivers`가 필요합니다.
```python
sudo apt install ubuntu-drivers-common
```
이후 ubuntu-drivers를 이용하여 권장 설치를 진행한다.
```python
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update
sudo ubuntu-drivers autoinstall
```
시간이 조금 걸리므로 조급해하지 말자. 설치가 완료되었다면 재부팅으로 마무리한다.
```python
sudo reboot
```
이제 `nvidia-smi` 명령어로 GPU의 현재 상태를 볼 수 있다.

혹시라도 귀찮아서 재부팅을 안하는 분은 아래와 같은 에러를 만날 수 있으니 귀찮더라도 꼭 하자.

⚠️ **NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.**  
**Make sure that the latest NVIDIA driver is installed and running.**


nvidia-smi보다 좀 더 간단하게 볼 수 있는 툴로는 `gpustat`을 추천한다. 설치도 간단하다.

```python
pip install gpustat
```
`gpustat`을 입력하면 GPU 상태를 보여준다.

#### 참고
[Nvidia드라이버 설치하기](https://pstudio411.tistory.com/entry/Ubuntu-2004-Nvidia%EB%93%9C%EB%9D%BC%EC%9D%B4%EB%B2%84-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0)

<br>

## 2. 설치 이후 만나는 상황

#### 🔒 문제

📍 **`처음에는 ssh가 잘 되다가 어느 순간부터 접속이 되지 않는다`**

Nvidia 드라이버의 호환성 문제로 인해 컴퓨터가 다운되는 것이라고 예상해서 여러번의 재설치를 거쳤으나 해결되지 않았다.

이는 모니터를 연결해 놓지 않는 서버 컴퓨터의 특성상 놓치기 쉬운 부분인데 알고 보니 단순히 절전 모드에 들어간 것이었다.

Nvidia 드라이버를 설치하면 재부팅시 디폴트 모드가 GUI 모드로 변경되고 절전 모드도 자동으로 세팅된다. 

이를 해결하기 위해서는 컴퓨터의 절전 모드 진입을 막아야 하는데 가능한 방법은 총 두 가지이다.

#### 🔑 해결 

📍 **`명령어로 절전 모드를 끈다`** ([참고](https://heekangpark.github.io/linux/ubuntu-server-sleep))

한 줄이면 가능하다.

```python
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

아래 명령어로 설정이 잘 되었는지 확인한다.

```python
systemctl status sleep.target suspend.target hibernate.target hybrid-sleep.target
```  
<br>

📍 **`기본 모드를 CLI 모드로 전환한다`** ([참고](https://booiljung.github.io/technical_articles/linux/switch_gui_and_cli.html))

관련 설정 파일은 아래의 위치에 있다.

```python
sudo vim /etc/default/grub
```

다음 3가지 사항에 대해 수정한다.
- `GRUB_CMDLINE_LINUX_DEFAULT=""`를 주석 처리
- `GRUB_CMDLINE_LINUX="text"`로 변경
- `GRUB_TERMINAL=console`의 주석 제거

esc → :wq → enter 순으로 변경 사항을 저장한 뒤 아래 명령어로 적용한다.

```python
sudo update-grub # 변경 사항 적용
sudo systemctl set-default multi-user.target
sudo reboot # 재부팅
```