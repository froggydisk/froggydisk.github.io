---
title: "[H/W] Mac에서 시리얼 통신하기"
comments: true
categories:
  - Blog
tags:
  - Serial Port
last_modified_at: 2024-04-21T
---

![image](/assets/img/serial-com.webp)

의료 장비를 맥북과 연결해서 시리얼 통신으로 데이터를 주고 받을 일이 있었다.

요즘은 평소에 시리얼 포트를 보는 것도 드문 일이거니와 과연 M1 칩 이후로는 연동이 잘 되는지도 알 수 없었다.

일단 `RS232-RS232` 케이블로 의료 기기에 하나를 꽂아주고 반대편 포트는 맥북의 허브 포트에 꽂을 수 있게 `Serial to USB` 어댑터를 연결해준다. 

그대로 맥북에 연결하면 다음과 같이 `설정 > 일반 > 시스템 리포트` 상에 USB-Serial Controller가 나타난다. 즉, 하드웨어 상으로는 자동으로 연결을 인식해준다.

![image](/assets/img/serial-port-setting.png)

하지만 코드 상에서 시리얼 통신을 하기 위해서는 `/dev` 폴더 아래에 나타나는 장치 코드를 알아내야한다. 보통 `tty~`로 시작한다.

터미널에서 검색해보면 아직은 아무것도 나타나지 않는다. 

```bash
$ ls /dev/tty*
# /dev/tty.Bluetooth-Incoming-Port
```

아무래도 드라이버가 필요한 듯해서 찾아보았다.

일단 시스템 리포트에 찍히는 `Prolific Technology`에서 만든 시리얼 포트를 인식하기 위해서는 드라이버를 다운로드해야 한다.

중국에서 만들었는지 중국어로 된 사이트로 연결이 된다. 관련 macOS(구OSX) 전용 드라이버는 [Prolific PL2303](https://www.prolific.com.tw/US/ShowProduct.aspx?pcid=41&showlevel=0041-0041)이다. 

하지만 설치를 완료해도 여전히 `/dev`에는 아무것도 나타나지 않는다?!

좀 더 검색을 해보니 `Serial to USB` 어댑터에도 드라이버가 필요한 듯하다...

이번에는 `FTDI`라는 홈페이지에 가서 `Virtual COM port(VCP)` 드라이버를 다운받는다.

> **FTDI(Future Technology Devices International)**  
> USB를 시리얼 포트로 변환하는 장치를 생산하는 회사. FTDI의 USB-시리얼 변환기는 컴퓨터의 USB 포트에 연결되어 있고, 시리얼 통신을 지원하는 장치와 통신할 수 있도록 시리얼 데이터를 USB 데이터로 변환한다. 이는 특히 시리얼 포트가 없는 현대의 컴퓨터나 장치와 통신하기 위해 사용된다.

해당 드라이버는 컴퓨터가 USB 포트로 시리얼 통신을 할 수 있도록 도와주는 역할을 한다.

ARM 전용 dmg 파일을 다운받아서 설치한다. **단, 주의해야할 점은 /Applications 폴더 아래에 놓고 실행을 해야 설치가 된다는 것이다. 이후 `설정 > 개인정보 보호 및 보안`에서 관련 권한을 허용해 주어야 한다.**

관련 이슈를 [Reddit](https://www.reddit.com/r/MacOS/comments/17bnhvr/m2_mac_on_macos_sonoma_issues_with_prolific/?utm_source=embedv2&utm_medium=post_embed&utm_content=post_body&embed_host_url=https://embed.notion.co/api/iframe)에서도 잘 설명해주고 있다.

이제 `/dev` 폴더를 살펴보자.

```bash
$ ls /dev/tty*
# /dev/tty.Bluetooth-Incoming-Port
# /dev/tty.PL2303G-USBtoUART2130
```

짜잔! 연결된 포트가 나타난다. 이제 관련 라이브러리(예 [Node.js](https://serialport.io))를 이용해서 시리얼 통신을 진행하면 된다.

맥에서 시리얼 통신을 할 때는 드라이버가 필수라는 사실만 알아두자.