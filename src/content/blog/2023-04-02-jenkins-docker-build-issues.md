---
title: "[Jenkins] 젠킨스에서 도커 이미지를 빌드할 때 발생하는 이슈들"

comments: true
categories:
  - Blog
tags:
  - Jenkins, Docker, Harbor
last_modified_at: 2023-04-02T
---

## 작업 환경
---
젠킨스를 통해 깃허브에서 도커 이미지를 빌드하여 이미지 저장소로 올리는 과정에서 발생하는 이슈들을 다룹니다.  
이 글은 CI 파이프라인 구축을 설명하고 있지 않습니다. 환경 구축은 아래 출처를 참고해주세요.

● [Jenkins로 Docker 이미지 빌드하기](https://smoh.tistory.com/420)  
● [젠킨스 연동 및 push 하기](https://zunoxi.tistory.com/131)

## 설정 파일
---

젠킨스가 깃허브에서 코드를 받아와서 도커 이미지를 빌드할 때 필요로 하는 파일이 두 가지 존재한다. 하나는 Jenkinsfile이고 나머지는 Dockerfile이다. 두 파일은 코드의 루트 경로에 위치하고 있어야 한다.  
처음 작성할 때 막막했던 기억이 있어 누군가는 필요할 것 같아 첨부해 둔다. 

#### 📌 Jenkinsfile

```python
def app
node {        
    stage('Checkout'){            
        checkout scm            
    }
    
    stage('Build image'){                       
        app = docker.build("[저장소도메인]/[프로젝트명]/[이미지명]")
        # 예를 들면 "harbor.test.io/example-project/test-image"
        # 하버의 경우 프로젝트는 사전에 생성해 놓아야하지만 이미지는 자동 생성된다.
    }
	
    # withRegistry 안에는 저장소 도메인과 젠킨스에 미리 등록해 놓은 Credential의 ID를 적어준다.
    # 예를 들면 docker.withRegistry('https://harbor.test.io', 'Harbor')
    stage('Push image'){ 
        docker.withRegistry('https://[저장소도메인]', '[CredID]'){
            app.push("${env.BUILD_NUMBER}")
            app.push("latest")
        }                
    }		
}
```

모든 이미지에는 젠킨스 프로세스 번호가 붙고 가장 최근에 올라간 도커 이미지에만 latest 태그가 붙는다. 

#### 📌 Dockerfile
Dockerfile은 구축하고자 하는 환경에 따라 이미지 파일이 다를 수 있다. 본인의 환경에 맞는 이미지를 가져오자.  
아래는 python이 깔려있는 nodeJS 이미지를 이용하여 서버를 실행하는 예시이다.
```python
FROM nikolaik/python-nodejs:python3.8-nodejs16 

WORKDIR /app

COPY . /app

RUN npm install && pip install -r requirements.txt

EXPOSE 8080

CMD [ "node", "app.js" ]
```
COPY를 할 때에는 COPY [복사해 올 곳] [복사해 갈 곳] 순으로 적는데 복사해 올 곳은 상대경로로, 복사해 갈 곳은 절대경로로 적는 것이 원칙이다. 꼭 지키지 않아도 동작에는 이상이 없긴 하다. 

## 에러
---

다음은 위의 구축 과정에서 발생하기 쉬운 에러와 그 해결 방안을 설명한다.

#### 🔒 에러 1

**`groovy.lang.missingpropertyexception: No such property: docker for class: groovy.lang.Binding`**

🔑 해결: Jenkins에서 Docker Pipeline 플러그인 설치 ([참고](https://may9noy.tistory.com/990))

#### 🔒 에러 2

**`/var/run/docker.sock: connect: permission denied`**

🔑 해결: 모든 노드에서 sudo chmod 666 /var/run/docker.sock로 접근 권한 허용([참고](https://may9noy.tistory.com/990))

#### 🔒 에러 3

**`script.sh 1 docker not found`**

🔑 해결: jenkins deployment 파일에서 volume mount를 추가 ([참고](https://anfrhrl5555.tistory.com/137))
```python
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        ports:
          - name: httpe-port
            containerPort: 8080
          - name: jnlp-port
            containerPort: 50000
        volumeMounts:
          - name: jenkins-data
            mountPath: /var/jenkins_home
          - name: docker-socket
            mountPath: /var/run/docker.sock
          - name: docker-bin
            mountPath: /usr/bin/docker 
      volumes:
        - name: jenkins-data
          persistentVolumeClaim:
            claimName: jenkins-pvc
        - name: docker-socket
          hostPath:
            path: /var/run/docker.sock
            type: Socket
        - name: docker-bin
          hostPath:
            path: /usr/bin/docker
            type: File
```

#### 🔒 에러 4

**`stat /var/lib/docker/tmp: no such file or directory`**

🔑 해결: Jenkins 파드가 돌고 있는 노드에 도커가 제대로 실행되고 있지 않는 상태일 가능성이 높다. 해당 노드에서 sudo service docker restart를 한 뒤 /var/lib/docker 파일 안에 파일이 제대로 생성되어 있는지 확인한다. docker파일은 sudo chmod 755 docker로 접근 권한을 주어야 확인이 가능하다. 

## 결과

33번만에 성공했다. 