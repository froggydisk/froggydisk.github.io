---
title: "[ML/DL] GPU Unknown Error (Not Supported)"
comments: true
categories:
  - Blog
tags:
  - Deep Learning, Server, GPU, Riser Kit
last_modified_at: 2025-04-13T
---

아무것도 안 돌렸는데 갑자기 GPU 팬이 엄청난 속도로 돌 때가 있다.

서버컴의 경우 GUI가 없기에 이 현상만 나타나지만 그래픽 드라이버를 쓰는 OS의 경우 갑자기 **검은 화면**(Black Screen)이 뜨면서 컴퓨터를 재부팅해야하는 상황이 나타날 수 있다.

gpustat으로 상태를 확인해보니 다음과 같다.

```bash
[0] ((Unknown Error)) | ?℃, ?% | ?/?MB | (Not Supported)
```

일단 재부팅하면 일시적으로 해결이 가능하다.

## 📍 원인 분석

로그를 찾아보니 아무래도 **GPU has fallen off the bus**가 원인일 것으로 추정되었다.

로그 내용은 다음과 같다.

```bash
kernel: NVRM: GPU has fallen off the bus.
kernel: NVRM: A GPU crash dump has been created. If possible, please run
kernel: NVRM: nvidia-bug-report.sh as root to collect this data before
kernel: NVRM: the NVIDIA kernel module is unloaded.
```

[Git 이슈 #3363](https://github.com/pop-os/pop/issues/3363)에서도 위와 같은 내용을 다루고 있다.

## 📍 해결 시도

### 1. NVIDIA 드라이버 업데이트 (실패 🔴)

가장 많이 나오는 내용인데, 이미 `latest`라서 이 부분은 건너뛰었다. 과거 드라이버 특정 버전에서도 관련 문제가 나타나는 듯하다.

### 2. GPU의 절전 모드를 완전히 비활성화 (실패 🔴)

`GRUB(/etc/default/grub)`에 아래 내용을 추가한다.

```bash
GRUB_CMDLINE_LINUX_DEFAULT="nvidia.NVreg_EnableGpuSleep=0"
```

이후 `sudo update-grub`를 하였으나 해당 옵션이 지원이 안되는 듯 하였다.

```bash
nvidia: unknown parameter 'NVreg_EnableGpuSleep' ignored
```

### 3. NVIDIA 드라이버 설정 변경 (실패 🔴)

`/etc/modprobe.d/nvidia.conf` 파일을 수정한다. (파일이 없다면 추가)

```bash
options nvidia NVreg_PreserveVideoMemoryAllocations=1 NVreg_EnableGpuFirmware=0
```

이후에 업데이트를 적용한다.

```bash
sudo update-initramfs -u # 적용
sudo reboot # 적용
sudo modinfo -p nvidia | grep NVreg_ # 옵션 지원 확인
sudo dmesg | grep -i nvidia # 적용 확인
cat /proc/driver/nvidia/params # 적용 확인
```

리스트에 해당 내용이 나타난다면 적용이 완료된 것이다. 이후 하루정도는 조용했으나, 다시 같은 문제가 발생하였다.

### 4. 라이저 케이블 교체 (성공 🟢)

케이블 불량이 의심되어 라이저 킷(Riser Kit)을 이용한 수직 배치를 포기하고 4090 GPU 2-way 수평 배치를 시도하였다. 블로워 타입이라 매우 얇기 때문에 다행히 열관리에 있어서 엄청난 성능 저하가 있을 것 같지는 않다.

그러자 거짓말처럼 `Unknow Error` 이슈는 사라졌다.

## 결론

구글링 혹은 GPT에게 물어보면 이러한 이슈의 원인이 하드웨어, 소프트웨어 어느쪽에 한정되어 있지 않다고 한다. 하지만 보통 케이블을 다시 꽂거나 하는 물리적인 방법으로 해결되었다는 글이 많이 보이는 걸로 보아 **아무래도 하드웨어 원인이 많은 듯하다.**

한번은 GPU가 버스에서 떨어져 풀로드 걸렸을 때 재부팅 명령어로도 종료가 안되어서 물리적으로 전원을 내린 적이 있다. 이후 전원을 다시 켜면서 파워에 오버로드가 걸려 퓨즈가 나가는 불상사가 있었다. 이처럼 하드웨어 관련 이슈는 잠재적인 위험을 가지고 있기에 항상 조심해야 한다.

혹여 같은 증상을 겪고 있는 분들은 케이블 불량을 먼저 확인하시어 이러한 시행 착오를 피하시길 바란다.
