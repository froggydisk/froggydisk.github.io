---
title: "[k8s] 사설 저장소에서 도커 이미지 받아오기 실패"

comments: true
categories:
  - Blog
tags:
  - Kubernetes, Harbor
last_modified_at: 2023-03-22T
---

## 🔒 에러
쿠버네티스에서 yaml 파일을 작성할 때 도커 이미지를 사용하는 파드를 생성하려고 했으나 제대로 생성이 되지 않고 계속해서 `ImagePullBackOff` 상태가 되었다. Kubernetes Dashboard를 통해서 보니 다음과 같은 **401 Unauthorized** 에러 메시지가 떠있었다.
```
Failed to pull image: rpc error: code = Unknown desc = failed to pull and unpack image: 
failed to resolve reference: pulling from host failed with status code [manifests latest]: 
401 Unauthorized
```

사설 저장소(Private Registry)에서 이미지를 받아올 때 Secret을 사용해서 인증을 하게 되는데 아무래도 인증에 계속 실패하고 있는 듯하다. 분명 Secret을 등록해 두었는데도 에러가 사라지지 않아서 오랜시간 삽질을 하였다. Nginx를 통해서 들어올 때도 https 프로토콜로 요청하고 있으니 아무런 문제가 없는데 이상했다. 

## 🔑 해결 

결국 구글링을 계속한 끝에 다음과 같은 글을 발견했다.  
**`Secrets의 경우 파드와 같은 네임스페이스에 존재해야합니다.`** ([참고](https://velog.io/@numerok/harbor-사용-시-unauthorized-unauthorized-to-access-repository))

정신이 번쩍 들었다. 개발에는 꼼꼼함이 필수라는 것을 다시금 느낀다. 빠르게 Secret을 다시 만들었다.   
아래는 Secret을 만드는 명령어이다. 필자는 저장소로 Harbor를 사용하고 있다. 
```
kubectl create secret docker-registry harbor --docker-server=[저장소주소] 
--docker-username=[저장소ID] --docker-password=[저장소비밀번호] -n [네임스페이스]
```
마지막에 `-n [네임스페이스]`가 가장 중요하다. 이는 파드를 생성하는 네임스페이스와 같아야한다!
`kubectl get secrets -n [네임스페이스]` 명령어로 Secret이 잘 생성되었는지 확인해본다.  
이해를 돕기 위해 아래에 yaml 파일 예시도 함께 첨부한다.

```python
# deployment.yaml 예
...
    template:
      metadata:
        labels:
          app: test            
      spec:
        imagePullSecrets: 
        - name: harbor
        containers:
          - name: test
            image: harbor.io/testImage:latest
...                        
```
누군가는 시간을 아꼈기를 바란다.