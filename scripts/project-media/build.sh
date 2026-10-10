#!/usr/bin/env bash
# /projects/ 카드 영상 재생성. 사용법: scripts/project-media/build.sh [gaze|gc|econix|flight|lens ...]
# 결과: public/img/projects/<slug>.mp4 + 첫 프레임 .webp 포스터 (960x600)
# 필요: ffmpeg, cwebp, Google Chrome, puppeteer-core (npm i --no-save puppeteer-core)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../../public/img/projects"
cd "$HERE"

encode() { # name vf slug [fps] [crf]
  ffmpeg -loglevel error -y -framerate "${4:-30}" -start_number 0 -i "$1" -vf "$2" \
    -c:v libx264 -preset slow -crf "${5:-23}" -pix_fmt yuv420p -movflags +faststart -an "$OUT/$3.mp4"
  # 포스터는 반드시 첫 프레임이다. 다른 프레임을 쓰면 재생이 시작될 때 화면이 튄다
  ffmpeg -loglevel error -y -i "$OUT/$3.mp4" -frames:v 1 "$HERE/poster.png"
  cwebp -quiet -q 80 "$HERE/poster.png" -o "$OUT/$3.webp" && rm "$HERE/poster.png"
}

for n in ${@:-gaze gc econix flight lens}; do
  case $n in
    gaze)   node record-demo.mjs gaze   && encode 'frames-gaze/f%04d.jpg' 'scale=960:600' i-see-you ;;
    gc)     node record-demo.mjs gc     && encode 'frames-gc/f%04d.jpg' 'trim=start=0.3,setpts=PTS-STARTPTS,scale=960:600' gc-symbol ;;
    # econix는 실제로 스크롤하면 screencast 프레임이 찢어진다. 1280x2130 뷰포트로 페이지 전체를
    # 한 번에 찍고, 스크롤은 crop의 y를 움직여 흉내 낸다 (0~3.5초 정지 → 4초간 이동 → 정지)
    # 풍경이 복잡해 crf 23이면 5MB를 넘는다. 끝 0.5초를 어둡게 내려 처음 화면으로 넘어가는 이음매를 감춘다
    flight) node record-demo.mjs flight && encode 'frames-flight/f%04d.jpg' 'scale=960:600,fade=t=out:st=24.5:d=0.5' flight-quest 24 30 ;;
    # 배포 전이면 LENS_URL=http://localhost:8765/augmented-hero.html 처럼 로컬 서버를 가리킨다
    lens)   node record-demo.mjs lens   && encode 'frames-lens/f%04d.jpg' 'scale=960:600' look-up-lens ;;
    econix) node record-demo.mjs econix && encode 'frames-econix/f%04d.jpg' "crop=1280:800:0:'60+940*if(lt(t,3.5),0,if(gt(t,7.5),1,(1-cos(PI*(t-3.5)/4))/2))',scale=960:600" econix ;;
  esac
done
