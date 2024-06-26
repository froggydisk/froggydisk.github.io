---
title: "iOS 앱 심사상태를 디스코드로 공유하기 🍎"

comments: true
categories:
  - Blog
tags:
  - API, Discord
last_modified_at: 2022-02-28T
---

# 개발중인 앱의 심사 상태 확인
개발자라면 `Appstore Connect` 사이트에 들어가면 현재 앱의 심사 상태를 확인할 수 있다. 하지만 엔지니어링 팀이 아니라면 권한이 없는 경우도 많기 때문에 모든 팀원이 앱의 현재 상태를 알고 있기란 쉽지 않다. 일일이 공유를 해주는 것도 하나의 방법이기는 하지만 이런 것들이 하나둘씩 쌓이기 시작하면 업무량이 계속해서 늘어나기 때문에 미리미리 자동화를 해두면 나중에 눈물의 작업을 하게 되는 것을 방지할 수 있다. 빠르게 오픈소스를 찾아보았더니 다행히도 `Slack`으로 심사 상태를 보내주는 툴이 이미 있었다.   
오늘은 [Fernando](https://fernando.kr/ios/2020-11-08-ios-appstore-status-bot/)님의 코드를 참고하여 `Discord`로 앱의 심사 상태를 보내주는 툴을 만들어보자. 

# 사용하는 기능
● [Appstore Connect API](https://developer.apple.com/documentation/appstoreconnectapi)  
● [fastlane Spaceship](https://github.com/fastlane/fastlane/tree/master/spaceship)  
● [GitHub Actions](https://docs.github.com/en/actions)  
● [GitHub Gist](https://gist.github.com)  
● [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

# 코드의 흐름
1. Appstore Connect 사이트에서 API key를 발급받는다. 
2. Spaceship 라이브러리를 이용하여 앱 심사 정보를 받아오는 코드를 짠다. 
3. GitHub Actions를 사용하여 일정시간마다 위의 코드를 반복적으로 돌릴 수 있게 한다.
4. 코드가 실행될 때마다 GitHub Gist에 앱의 현재 정보가 저장된다. 
5. 이전에 등록된 정보와 현재 앱의 정보가 다르면 Webhook을 이용하여 현재 앱의 심사 상태를 Discord로 보낸다.  

# 툴의 특징
● 설정이 직관적이고 간단  
● 개인 서버가 없어도 작동 가능  
<br>
`Fernando`님의 글에서도 알 수 있듯이 **간편함**이 제일 중요하기에 봇 개발에 리소스를 쓰고 싶지 않은 분들을 위해 레포지토리 [Fork](https://github.com/froggydisk/app-status-bot)만으로 작동할 수 있게 하였다. 

# 사용법
1. 깃허브 레포지토리를 [Fork](https://github.com/froggydisk/app-status-bot)합니다. 
2. Appstore Connect에서 key ID, issuer ID, bundle ID, API Key file (.p8)을 발급받습니다. 
3. Discord에서 Webhook url을 발급받습니다.
4. GitHub token을 발급받습니다. (발급시 gists와 repo 항목에 체크해주세요.)
5. 앱 정보를 저장할 Gist의 url에서 맨 뒤의 ID만 저장해둡니다.  
e.g.) https://gist.github.com/froggydisk/[이부분]
6. 위에서 저장한 총 7개의 key를 Fork한 레포지토리의 secret에 하나씩 입력합니다.  
`Settings` → `Secrets` → `Actions` → `New repositoy secret`  
>● PRIVATE_KEY: Appstore Connect API Key file (.p8)  
● KEY_ID : Appstore Connect key ID  
● ISSUER_ID : Appstore Connect issuer ID   
● BUNDLE_ID : Appstore Connect bundle ID with comma  
● DISCORD_WEBHOOK : Discord Webhook url  
● GH_TOKEN: GitHub token  
● GIST_ID: Gist url ID
>
7. 마지막으로 레포지토리의 `Actions` 섹션으로 가서 workflow를 활성화해주면 끝!

# 주의점
일단 discord로 메세지를 보내는 라이브러리는 정말 다양하게 있다! [npm](https://www.npmjs.com)에서 마음에 드는 것을 찾아보자. npm으로 다운받은 뒤에는 discord.js의 코드를 사용법에 맞추어 바꿔주어야한다. Slack이나 Discord 이외에 다른 툴을 사용하는 경우에는 참고하자.  
<br>
다음은 `Fernando`님의 [레포지토리](https://github.com/techinpark/appstore-status-bot)를 그대로 사용하다보면 가끔씩 오작동하는 이슈가 있어서 원인을 찾아보았다. 
#### 1. js의 비동기 처리
GitHub Actions에서 fetch.yml을 실행하다보면 우선적으로 Gist의 store.db 정보를 쭉 불러온다. 하지만 store.db 안의 내용이 길어지기 시작하면서 request.get 할 때 시간이 오래걸리기 시작하더니 store.db를 다 읽기 전에 현재 앱 상태와의 비교가 끝나버리는 경우가 있었다. 실제 심사 상태는 변화가 없는데 Discord로 알림이 가버렸다. 해결을 위해 앞에 async/await를 사용하였다. 
```python
async function main() {
    await getGist();
    (생략)
}
```
#### 2. 최신 버전만 체크
반대로 상태가 바뀌었는데도 알림이 안오는 경우도 있었다. 해결을 위해 현재 코드에서는 가장 최신 버전에 대해 모든 상태 변화를 체크하도록 수정했는데 혹시나 특정 상태에 대해서만 알림을 보내고 싶다면 [Spaceship](https://github.com/fastlane/fastlane/blob/master/spaceship/docs/AppStoreConnect.md)의 문서를 잘 살펴보는 것을 추천한다. 아래는 Spaceship에서 버전을 가져오는 함수들이다. 
```python
app.get_live_app_store_version # the version that's currently available in the App Store
app.get_edit_app_store_version # the version that's in `Prepare for Submission`, `Metadata Rejected`, `Rejected`, `Developer Rejcted`, `Waiting for Review`, `Invalid Binary` mode
app.get_latest_app_store_version # the version that's the latest one
app.get_pending_release_app_store_version # the version that's in `Pending Developer Release` or `Pending Apple Release` mode
app.get_in_review_app_store_version # the version that is in `In Review` mode
```

# 결과
<img src="https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/discord-noti.png?raw=true" width="600">  
제 때 알림이 온다!! 다만 GitHub Actions는 계정당 쓸 수 있는 시간이 한계가 있으므로 Cron Job을 너무 자주 돌리진 말자.  
<br>
📍 [코드 보러가기](https://github.com/froggydisk/app-status-bot)

