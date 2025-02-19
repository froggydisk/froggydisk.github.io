---
title: "[ML/DL] RTX 4090 2-way 딥러닝 서버 견적"
comments: true
categories:
  - Blog
tags:
  - Deep Learning, Server, GPU
last_modified_at: 2025-02-18T
---

간단한 LLM 모델을 돌려보기 위한 딥러닝 서버를 구축해야할 일이 있었다.

우선 예산이 한정되어 있었기에 비용 절감을 위해 최대한 커스텀을 피하고자 하였다. 다만 RTX 4090 한 대 만으로는 VRAM이 부족하기에 두 장까지 장착하는 것을 고려하여 견적을 짰다.

2024년 막바지에 들어서서는 50번대 엔비디아 GPU의 등장으로 인해 시장에서 4090 신품을 구하기가 하늘에 별따기 수준이었다. 더군다나 2-way로 장착해야 하는 상황에서는 최대한 얇은 모델을 구해야했기에 상황은 더욱 어려웠다.

## 🧾 견적

우선 각 부품별로 고려했던 제품 리스트를 나열하자면 다음과 같다.
볼드체로 표시된 항목은 최종적으로 선택한 것들이다.

### CPU

- **AMD 라이젠9-5세대 7950X3D (라파엘) (멀티팩(정품))** ✨
- AMD 라이젠9-6세대 9950X (그래니트 릿지) (정품)
- AMD 라이젠9-5세대 7950X (라파엘) (멀티팩(정품))

### 메인보드

- **ASUS ProArt X870E-CREATOR WIFI 대원씨티에스** ✨
- ASUS TUF Gaming X670E-PLUS WIFI 대원씨티에스
- ASRock X670E Taichi 대원씨티에스

### 메모리

- **G.SKILL DDR5-5200 CL40 FLARE X5 J 패키지 (96GB(48Gx2))** ✨
- ESSENCORE KLEVV DDR5-5600 CL46 파인인포 (32GB)
- ADATA DDR5-5600 CL46-45-45 (32GB)
- PATRIOT DDR5-5600 CL46 EVO (32GB)
- 마이크론 Crucial DDR5-5600 CL46 PRO 패키지 대원씨티에스 (96GB(48Gx2))

### 그래픽카드 (GPU)

- **RTX 4090 블로워 팬** ✨
- GIGABYTE 지포스 RTX 4090 Gaming OC D6X 24GB 피씨디렉트
- MSI 지포스 RTX 4090 게이밍 X 슬림 D6X 24GB 트라이프로져3
- GIGABYTE 지포스 RTX 4090 WINDFORCE V2 D6X 24GB 피씨디렉트

### SSD

- **마이크론 Crucial T500 M.2 NVMe 아스크텍 (2TB)** ✨
- 마이크론 Crucial T705 M.2 NVMe 아스크텍 (1TB)
- Western Digital WD BLACK SN850X M.2 NVMe (2TB)

### 케이스

- **리안리 PC-011D EVO RGB Black (미들타워)** ✨
- 마이크로닉스 ML-420 BTF 화이트 (빅타워)
- Antec PERFORMANCE 1 MESH SILENT (빅타워)
- Fractal Design Meshify 2 XL Dark 강화유리

### 파워서플라이

- **마이크로닉스 ASTRO II GD 1650W 80PLUS GOLD 풀모듈러 ATX 3.0 (PCIE5)** ✨
- HYDRO PTM PRO 1650W Platinum ATX3.0 (12V-2x6)
- (SuperFlower) SF-2000F14HP LEADEX PLATINUM /파워
- SilverStone HELA 2050R Platinum 마이크로닉스

### CPU 쿨러

- **NZXT KRAKEN Elite 360 RGB (black)** ✨
- 발키리 C420 ARGB (BLACK)
- ARCTIC Liquid Freezer III 420 서린
- 3RSYS Socoool RC1900N 솔더링 (BLACK)
- DARKFLASH NEBULA DN-360 ARGB (블랙)
- PentaWave S06D LE ARGB
- Thermalright Peerless Assassin 120 SE 서린

### 시스템 쿨러

- **ARCTIC P12 PWM PST ARGB Value Pack** ✨

하드웨어에 대해서 잘 아는 편이 아니기에 커뮤니티 글을 많이 찾아보면서 선택하였고 호환성 문제가 일어나지 않도록 최대한 신경을 썼다.

## 🔖 선택 이유

각 부품에 대해서 선택 이유를 간단히 이야기하자면 아래와 같다.

- CPU (AMD 라이젠 9-5세대 7950X3D 라파엘)  
  기존에 쓰던 CPU가 있어서 재활용하였다. 사실 3D 모델이라 게임에 좀 더 적합하긴 하다.
- 메인보드 (ASUS ProArt X870E-CREATOR WIFI STCOM)  
  보통 ASRock도 많이 선택하는 것 같은데 개인적 경험에서는 ASUS가 더 튼튼한 느낌이다.
- 메모리 (G.SKILL DDR5-5200 CL40 FLARE X5 J 패키지 48GB x 2)  
  32, 64, 128 단위가 24, 48, 96 보다는 안정성이 좋다는 말이 있어서 32GB를 4개 꽂을까 하다가 풀뱅크보다는 아무래도 48GB 두 개가 나을 것 같아 선택하였다. 하지만 LLM을 고려한다면 결국 48GB로 풀뱅크를 해야할 수도 있지 않을까 생각한다.
- 그래픽카드 (RTX 4090 블로워 팬)  
  윈드포스 모델이 제일 얇아서 그걸로 찾고 있었지만 40번대 단종 문제로 아무것도 구할 수가 없어서 용산에 쭉 연락을 돌리다가 블로워 모델 재고만 있어서 울며 겨자 먹기로 주문하였다. 블로워 모델은 게임용이 아니기에 RPM이 일반 모델보다 높게 올라가므로(대략 5,200rpm) 온도 관리는 수월하지만 엄청난 소음 문제가 존재한다. 하지만 실제로 성능 100%를 사용하는 게임 및 AI 훈련을 돌렸보았지만 생각보다는 큰 소리가 아니어서 한시름 놓았다. 물론 가정용이라면 극구 반대한다.
- SSD (마이크론 Crucial T500 M.2 NVMe 대원씨티에스 2TB)  
  이건 취향 문제라 별 생각없이 구매하였다.
- 케이스 (리안리 PC-O11D EVO RGB Black 미들타워)  
  온도 관리가 제일 중요한 이슈여서 빅타워로 해야하나 했지만 리안리 미들타워도 꽤나 커서 이걸로 사길 잘했다고 생각한다. 미들 타워에서는 꽤 유명하고 어항 감성이 있어서 좋다.
- 파워서플라이 (마이크로닉스 ASTRO II GD 1650W 80PLUS GOLD 풀모듈러 ATX 3.0)  
  보통 파워는 1650W 또는 2000W로 갈리는데, 4090이 워낙 전력 적게 먹기로 소문난 놈이라 아마 괜찮겠지하고 싼 걸로 골랐다.
- CPU 쿨러 (NZXT KRAKEN Elite 360 RGB black)  
  돈을 아끼려면 아낄 수 있었지만 화면 나오는 쿨러가 가지고 싶어서 구매하였다. 물론 크라켄 수냉 쿨러는 유명하므로 성능에 대한 의심은 없다.
- 시스템 쿨러 (ARCTIC P12 PWM PST ARGB Value Pack 서린 black)  
  GPU가 2장이라 온도 관리가 중요하므로 케이스 아래쪽 흡기에 쓸 생각으로 구매하였다.

## 🐌 후기

기존에 있던 CPU를 써야했고 GPU는 따로 구매하였기에, 조립 서비스를 이용하였으나 반절은 다시 직접 작업해야 하였다. 그렇지만 이용할 수 있으면 무조건 조립 해달라고 하는 것이 편하다.

리스트에는 없지만 GPU 한 장은 수직 장착을 하기에 라이저 킷과 브라켓도 구매해 주었다 ([참고](https://lian-li.com/product/o11d-evo-rgb/)). 시간적 여유만 된다면 알리에서 싸게 구할 수 있다. 리안리 PC-O11D EVO RGB(미들타워)의 경우 보통 업라이트 킷만 사고 브라켓을 구매하지 않아서 조립할 때 헤매는 듯 싶다 ([브라켓](https://lian-li.com/product/o11d-evo-upright-gpu-bracket-for-40-series-gpu/)).

2025년 초 기준, CPU와 GPU를 제외한 비용은 250만원 정도선이고, 총 비용은 1,000만원 조금 넘는 정도라고 볼 수 있다. 만약, 커스텀이나 완성품을 사게 된다면 비용은 훨씬 올라갈 것이므로 되도록이면 드래곤볼 하는 것을 추천한다.

이후 조립기나 사용기도 간간이 올릴 생각이다.
