---
title: "[k8s] Jenkins에서 Credential 등록 불가 에러"

comments: true
categories:
  - Blog
tags:
  - Kubernetes, Jenkins, Nginx
last_modified_at: 2023-03-11T
---

<p align="center"><img src="https://github.com/froggydisk/froggydisk.github.io/blob/master/img/18th.png?raw=true"/></p>


# 📌 Credential을 등록하려해도 등록이 안 될 때

Jenkins와 GitHub Server를 연동하기 위해 Credential을 등록하는데 Add 버튼을 눌러도 제대로 등록이 되지 않았다. 

(단, Username 항목에 연동하려는 서버의 유저 ID를 적고 ID 항목에는 각 Credential을 구분하기 위한 임의의 이름을 적었는지 확인하자. 단어가 헷갈릴 만하다.)

아무런 반응이 없어서 에러 메세지를 보기 위해 크롬에서 F12를 눌러 브라우저 콘솔창을 켰다. 

그랬더니 다음과 같은 메시지를 띄워주고 있었다. 

### 🔒 에러

**`Mixed Content: The page was loaded over HTTPS, but requested an insecure script.`**
**`This request has been blocked; the content must be served over HTTPS.`**

### 🔑 해결

이는 Nginx의 프록시 설정이 제대로 되어 있지 않아서 발생하는 문제이다. nginx.conf 파일 상단에 아래의 설정을 추가해준다. 

참고로 nginx.conf는 일반적으로 /etc/nginx 경로에 존재한다. 혹은 sites-enabled에 있는 .conf 파일에 넣어주어도 무방하다.

```python
# nginx.conf
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header Host $http_host;
proxy_set_header X-Forwarded-Proto $scheme; # <- 중요
```

원인은 암호화된 HTTPS 페이지에 HTTP 프로토콜로 요청을 보내고 있기 때문이다. 

위 설정이 어떠한 의미를 담고 있는지 참고할 만한 글을 두 개 소개한다. 해당 글들은 이에 대한 설명을 담고 있다. 

● [Nginx 서버 설정(프록시, 캐시, 보안)](https://velog.io/@csk917work/Nginx-%EC%84%9C%EB%B2%84-%EC%84%A4%EC%A0%95)  
● [Nginx reverse proxy 설정](https://mchch.tistory.com/234)

이후 nginx를 reload하면 정상적으로 Credential 등록이 가능해진다.

```python
sudo service nginx reload
```

<br>

## 📌 참고할 만한 정보

플러그인을 설치하다가 Jenkins를 재시작해야할 일이 있었는데 이후에 모든 설정이 초기화되는 현상을 만났다. 

### 🔒 에러
혹시라도 `https://[jenkins 도메인]/restart`를 이용해 Jenkins를 재시작할 때 설정이 초기화되는 현상이 있다면 pv 설정이 제대로 되어있나 살펴보자.

### 🔑 해결
`kubectl get pv -A`로 pv 관련 reclaim policy 설정이 **`Retain`**으로 되어 있나 확인한다. 

혹여나 Delete로 되어 있다면 patch 명령어를 통해 설정을 바꾸어준다. ([참고](https://kubernetes.io/ko/docs/tasks/administer-cluster/change-pv-reclaim-policy/))

```python
kubectl patch pv <your-pv-name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
```

이후 pv와 pvc는 삭제한 뒤 다시 만들어준다. 추가로 `kubectl logs` 명령어로 Jenkins 파드에서 에러 메시지를 보내고 있지 않나 확인한다. 

Jenkins를 restart해도 설정이 남아있다면 성공이다. 

이는 비단 Jenkins 뿐만 아니라 pv와 연계해서 k8s 위에서 돌아가고 있는 모든 서비스에도 적용되는 사안이므로 pv 설정은 항상 신중해야한다.

안 그러면 소중한 데이터를 날리는 일이 있을 수 있다. (나의 이야기다...)