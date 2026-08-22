---
title: "[k8s] 새로운 워커노드를 추가하여 서버 증설하기"

comments: true
categories:
  - Blog
tags:
  - Kubernetes, On-premise
last_modified_at: 2023-07-04T
---

마스터 노드의 설정이 이미 되어 있고 추가할 워커노드의 OS가 우분투 20.04 버전인 경우를 기준으로 설명하겠다.

## 📖 요약
● docker  
● kubelet  
● kubeadm  
● kubectl  
새로운 워커노드에 위 4가지를 설치해준다.  
그리고 마스터 노드에서 토큰을 발급하여 새로 연결할 워커노드에 입력해주면 끝이다.

## 🎬 진행
생각보다 몹시 간단하다. 이제 하나하나 차근차근 진행해보자.

#### docker 설치
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
sudo docker version
sudo systemctl enable docker
sudo systemctl start docker
```

#### kubelet, kubeadm, kubectl 설치
한 줄씩 잘 입력해준다.
```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```

#### 토큰 발급 및 등록
우선, 마스터 노드에서 토큰을 발급한다.
```bash
sudo kubeadm token create --print-join-command
```
이렇게 하면 `kubeadm join <Kubernetes API Server:PORT> --token <Token 값> --discovery-token-ca-cert-hash sha256:<Hash 값>` 이러한 형태의 결과값이 나오는데 그대로 복사해서 새로운 워커노드 터미널에 붙여넣기 해주면 된다.
  
각각의 값은 다음과 같이 확인할 수 있다.
```bash
# kubectl이 바라보는 API 서버 주소
kubectl cluster-info
# token 값 확인
kubeadm token list
# hash 값 확인
openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | openssl dgst -sha256 -hex | sed 's/^.* //'
```

#### 🔒 에러
위의 과정에서 아마도 다음과 같은 에러가 발생할 것이다.
```bash
error execution phase preflight: [preflight] Some fatal errors occurred:
[ERROR CRI]: container runtime is not running: output: time="2020-11-25T12:58:32Z" level=fatal msg="getting status of runtime failed: rpc error: code = Unimplemented desc = unknown service runtime.v1alpha2.RuntimeService"
, error: exit status 1
```

#### 🔑 해결
아래와 같이 해결하면 된다.
```bash
sudo rm /etc/containerd/config.toml
sudo systemctl restart containerd
```

항상 느끼지만 대부분의 쿠버네티스 오류는 kubelet, docker, containerd, calico 이 네가지에서 자주 발생하는 것 같다.  
마지막으로 마스터노드에 들어가서 `kubectl get node`를 해보자. 잘 인식이 된다면 성공이다. 

## 참고
[Ubuntu에서 쿠버네티스(k8s) 설치 가이드](https://confluence.curvc.com/pages/releaseview.action?pageId=98048155)