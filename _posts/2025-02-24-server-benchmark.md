---
title: "[ML/DL] RTX 4090 2-way 딥러닝 서버 벤치마크"
comments: true
categories:
  - Blog
tags:
  - Deep Learning, Server, GPU
last_modified_at: 2025-02-24T
---

이전 [서버 견적 포스트](https://froggydisk.github.io/server-build/)에서 주문한 부품들이 도착하여 마저 조립을 해주었다.

부품 리스트는 다음과 같다.

```bash
● AMD 라이젠9-5세대 7950X3D (라파엘) (멀티팩(정품)) # CPU
● ASUS ProArt X870E-CREATOR WIFI 대원씨티에스 # 메인보드
● G.SKILL DDR5-5200 CL40 FLARE X5 J 패키지 (96GB(48Gx2)) # 메모리
● RTX 4090 블로워 팬 # GPU
● 마이크론 Crucial T500 M.2 NVMe 아스크텍 (2TB) # SSD
● 리안리 PC-011D EVO RGB Black (미들타워) # 케이스
● 마이크로닉스 ASTRO II GD 1650W 80PLUS GOLD 풀모듈러 ATX 3.0 (PCIE5) # 파워서플라이
● NZXT KRAKEN Elite 360 RGB (black) # CPU 쿨러
● ARCTIC P12 PWM PST ARGB Value Pack # 시스템 쿨러
```

정상적으로 전원이 들어오는 것을 보니, 호환성 이슈는 없는 듯하다.

짧은 감상평을 말하자면, RTX 4090 블로워 모델은 진짜 얇다. 윈드포스 모델보다도 얇다. 팬도 하나뿐이라 나름 고급스러운 느낌이 난다. 외관만 보면 만족스럽다.

조금 더 가성비 견적을 짜면 1,000만원 언더로도 떨어질 수 있을 듯하다. 물론 4090 두 장만 해도 700-800 사이이니 최저는 900 정도는 되지 않을까 생각한다.

2-way 딥러닝 서버 설계에 있어서는 [유튜브](https://www.youtube.com/watch?v=pw-C21bXQb4)를 참고하였다. 라이저 킷을 활용한 2-way 온도 최적화 설계이다.

노파심에 언급하지만, **라이저 킷으로 GPU를 장착하는 경우 브라켓을 같이 구매해주어야 한다.** 헤매는 사람을 여럿 보았다.

## 서버 전면부

![server](/assets/img/server-facade.png)

사진을 보면 가로로 하나, 세로로 하나 총 두 장의 GPU가 달려있는 것을 확인할 수 있다. 공기 흐름은 아래만 흡기로 하고 나머지는 배기로 하였다. 측면에는 남는 팬을 몇 개 더 달아주었다.

## 소음 테스트

영상이라 소음의 정도를 가늠하기는 힘들지만 생각만큼 엄청나지는 않다. 조용한 사무실에서는 쓰기 힘들고 따로 서버실이 있으면 좋을 듯하다.

<video width="100%" controls>
<source src="/assets/img/server-noise.mp4" type="video/mp4">
브라우저가 비디오 태그를 지원하지 않습니다.
</video>

## 성능 테스트

벤치마크는 RTX 4090 GPU 한 장을 기준으로 한다.

### • Steel Nomad Score

![score](/assets/img/steel_nomad_score.png)

### • Time Spy Score

![score](/assets/img/time_spy_score.png)

### • Fire Strike Score

![score](/assets/img/fire_strike_score.png)

### • Night Raid Score

![score](/assets/img/night_raid_score.png)

## 결론

벤치마크 시에는 **GPU 사용률이 90-100% 정도이고, 온도는 대략 70-80도 정도에 위치한다.** 블로워 타입이라고 해서 일반 모델과 비교해 게임 성능의 엄청난 차이를 보이는 것 같지는 않다.

아직 겨울철이라 그나마 온도 관리가 수월한 셈인데, 여름에는 어떨지 궁금하기는 하다.

게임 이외에 `DeepSeek-R1 Dynamic 1.58-bit`와 같은 LLM을 돌렸을 때, 추론 시에는 VRAM만 잔뜩 먹고 GPU 점유율은 10% 미만이라 매우 쾌적하다. 단, DeepSeek가 워낙 큰 모델이다보니 토큰 생성 속도는 매우 느리다. (2 tokens/sec)

물론 모델 훈련 시에는 위의 벤치마크를 돌렸을 때와 비슷한 점유율을 보여주므로 서버 구축의 목적이 LLM 서비스인지, 모델 개발인지에 따라 설계 방식, 구축 방안, 설치 환경의 선택지가 크게 달라지므로 참고하자.

GPU 2장을 동시에 풀로 사용해도 온도는 둘 다 80도 이상 크게 높아지지는 않는다. 아무래도 서로의 간섭이 적어서 발열 관리에 도움이 되는 듯하다.

우선 사용하는데 크게 문제는 없는 듯하니, 운용해 보다가 예상치 못한 문제가 발생하면 포스팅하도록 하겠다.
