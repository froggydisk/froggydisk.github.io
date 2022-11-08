---
title: "[Multer] Error: ENOENT: no such file or directory"

comments: true
categories:
categories:
  - Blog
tags:
  - React Native, NodeJS, Multer
last_modified_at: 2022-11-08T
---

● 서버 코드  
```javascript
const multer = require("multer");
const fs = require("fs");

var storage = multer.diskStorage({
  destination: async (req, file, callback) => {
    const userId = JSON.parse(JSON.stringify(req.body)).userId;
    const dir = "./upload/" + userId; // See here!
    try {
      if (!fs.existsSync(dir)) { // 해당 유저의 디렉토리가 있는지 확인
        fs.mkdirSync(dir, { recursive: true }); // 없다면 디렉토리를 생성
      }
    } catch (err) {
      console.error(err);
    }
    return callback(null, dir);
  },
  filename: (req, file, callback) => {
    callback(null, `${Date.now()}_${file.originalname}`); 
  },
});
var save = multer({ storage: storage }).array("profileImage");
// 한 장만 보낼 때는 .single("profileImage");를 써도 된다.
```
Multer를 사용하여 이미지를 업로드할 때 유저별로 폴더를 만들어서 따로 저장하려고 하는데 자꾸 에러가 났다. 
<br>
디렉토리를 생성하지 못하는 걸로 보아 함수를 fs쪽 함수를 잘못 사용하고 있나 싶어서 열심히 찾아보았으나 아무런 진전이 없었다. 
<br>
오랜 시간 끝에 아무생각 없이 /upload/로 되어 있던 절대경로에 마침표를 붙여 상대경로로 만들어주었더니 정상적으로 작동하였다. 
<br>
서버 설정에 따라 마침표가 필요할 때가 있고 아닐 때가 있으므로 둘 다 해보고 되는 것으로 하면 되겠다. 
<br>
여기서 중요한 것은 항상 경로 체크를 선택지에 넣어두는 것이 무의미한 시간 낭비를 피할 수 있다는 것이다. 
<br>
참고를 위해 클라이언트쪽 코드도 남겨둔다.

● 클라이언트 코드
```javascript
const createFormData = (image, body) => {
    const data = new FormData();
    Object.keys(body).forEach(key => {
      data.append(key, body[key]);
    });
    data.append('profileImage', { // 필드명으로서, 서버에서 정의된 것과 동일해야한다.
      name: image.name
      type: 'multipart/form-data',
      uri: image.uri,
    });
    return data;
  };

const photoUpload = async () => {
    try {
      fetch('http://localhost:8080/user/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        body: createFormData(image, {
          userId: "tester",
        }),
      })
        .then(response => response.text())
        .then(response => {
          console.log('upload success', response);
        })
        .catch(error => {
          console.log('upload error', error);
        });
    } catch {
      error => {
        console.log(error);
      };
    }
  };
```

### 참고
[Error: ENOENT: no such file or directory, mkdir when trying to create directory](https://stackoverflow.com/questions/68254686/error-enoent-no-such-file-or-directory-mkdir-when-trying-to-create-directory)
