---
title: "[쿠버네티스] error: The connection to the server 192.168.x.x:6443 was refused - did you specify the right host or port?"

comments: true
categories:
  - Blog
tags:
  - Kubernetes, systemd
last_modified_at: 2024-03-05T
---

IDC에 서버를 구축하면서 오랜만에 순정 서버에 쿠버네티스를 설치할 일이 생겼다. 우분투는 이전에도 수없이 지우고 깔고 해봤기에 수월하게 넘어갔지만 오랜만에 하는 쿠버네티스 클러스터 구축에서 에러를 만나버렸다.

`kubeadm init` 이후에 `kubectl get node`를 했을 때 처음에는 결과가 잘 나타나다가 시간이 조금 지나면 아래와 같은 에러가 나타나기 시작한다.

```javascript
error: The connection to the server 192.168.x.x:6443 was refused - did you specify the right host or port?
```

`6443`은 쿠버네티스에서 주로 사용하는 포트이고 192.168.x.x는 localhost니깐 위의 에러는 자기 자신에 연결할 수 없다는 이야기가 된다. 6443 포트를 통해서 자기 내부에서 돌고 있는 쿠버네티스 시스템과 통신을 하게 되는데 그게 불가능하다는 것은 쿠버네티스가 제대로 돌고 있지 않다는 것이다.

처음에는 UTM의 방화벽 정책 문제인가 싶었는데 조금 생각해보니 전혀 상관없는 문제였다.

컨테이너 런타임으로 containerd를 사용할 때는 [공식문서](https://kubernetes.io/ko/docs/setup/production-environment/container-runtimes/)에서 말하길,

> 리눅스 배포판의 init 시스템이 systemd인 경우, systemd를 kubelet과 컨테이너 런타임의 cgroup 드라이버로 사용해야한다.

라고 한다.

관련 설정 없이는 `systemd`와 `cgroupfs`가 cgroup driver로 혼용되기 때문에 이는 쿠버네티스 시스템에 큰 혼란을 초래하게 된다.

실제로도 watch 명령어를 통해서 kubeadm init 뒤에 초기 시스템 파드들이 어떻게 실행되는지 보았더니 계속 죽었다 살아나기를 반복하고 있었다.

해결 방법은 간단하다. 공식 문서에도 잘 나와있지만 아래를 참고해도 좋다. 컨테이너 런타임의 cgroup 드라이버를 설정해준다.

```javascript
containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml
sudo service containerd restart
```

공식 문서를 꼼꼼하게 읽자.
