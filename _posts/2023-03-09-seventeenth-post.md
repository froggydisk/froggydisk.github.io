---
title: "[k8s] 로컬에서 원격 하버 저장소로 도커 이미지 업로드"

comments: true
categories:
categories:
  - Blog
tags:
  - Kubernetes, Harbor, Helm, Docker
last_modified_at: 2023-03-09T
---

# 📌 도커 원격 로그인

쿠버네티스 상에 하버 서비스를 띄우는데 성공했다면 로컬에서 도커 이미지를 보낼 준비가 된 것이다.

로그인 방법은 간단하다. 단, 기본적으로 로컬에 도커가 돌고 있어야 한다. 

```python
sudo docker login [https://하버도메인]
```

만약 이 과정에서 로그인 에러가 발생했다면 해결 방법은 두 가지이다. ([참고](https://qkqhxla1.tistory.com/1123))

### 🔒 에러
**`Error saving credentials: error storing credentials - err: exit status 1, out: ''`**

### 🔑 해결
● `~/.docker/config.json` 파일에서 `"credsStore":`의 내용을 `""`로 수정한다.

● 혹은 `~/.docker/config.json` 파일을 삭제해준다. 

이후 도커를 재시작하고 다시 로그인을 시도한다. 


# 📌 도커 이미지 업로드

로그인에 성공하였다면 실제로 push를 해 볼 차례이다. push 순서는 다음과 같다.
1. 원격 하버 저장소에 로그인
2. 원하는 도커 이미지의 태그 생성
3. 저장소에 push

```python
# 로그인
sudo docker login [https://하버도메인]
# push할 이미지를 찾는다. 없으면 허브에서 pull 해온다.
sudo docker images 
# 도커 이미지에 tag를 붙여준다.
sudo docker tag [선택한 도커이미지] [하버도메인]/[프로젝트명]/[도커이미지]:[버전명]
# 저장소에 push
sudo docker push [하버도메인]/[프로젝트명]/[도커이미지]:[버전명]
```

주의할 점은 하버 포탈에 해당 프로젝트가 이미 생성된 상태여야 한다는 것이다. 다만 버전명은 꼭 숫자가 아니어도 된다.

예를 들면 다음과 같다.

    sudo docker tag harbor.domain.io/my-project/busybox:0.1

### 🔒 에러
만약 push가 정상적으로 되지 않고 **`Retrying in 5 seconds`**와 같은 메시지가 반복된다면 아래와 같이 해결한다.

### 🔑 해결
헬름을 통해 다운받았다면 하버의 deployment yaml 파일이 존재할 것이다. 파일 내용의 한 부분만 수정해주면 된다. ([참고](https://www.claudiokuenzler.com/blog/958/running-harbor-registry-behind-reverse-proxy-solve-docker-push-errors))

```python
...
registry:
	...
	relativeurls: true # false에서 true로 변경
```

그 이후에는 변경 사항을 적용해 주면 된다.
```python
helm upgrade --install harbor harbor/harbor -f my-values.yaml -n harbor
```

온프레미스 관련 에러는 항상 레퍼런스가 적어 해결이 어렵다. 누군가에게는 도움이 되었길 빈다.



