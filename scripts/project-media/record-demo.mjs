import puppeteer from 'puppeteer-core';
import fs from 'fs';
const [,, name] = process.argv;
const W=1280,H=800;
const CURSOR = `(()=>{const c=document.createElement('div');c.id='__cur';c.style.cssText='position:fixed;left:0;top:0;width:22px;height:22px;z-index:2147483647;pointer-events:none;transform:translate(-100px,-100px);transition:none';c.innerHTML='<svg width="22" height="22" viewBox="0 0 24 24"><path d="M4 2l16 9.5-7 1.6-3.8 6.9z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';document.documentElement.appendChild(c);const r=document.createElement('div');r.id='__ring';r.style.cssText='position:fixed;left:0;top:0;width:40px;height:40px;margin:-20px 0 0 -20px;border-radius:50%;border:2px solid rgba(20,20,20,.5);z-index:2147483646;pointer-events:none;opacity:0';document.documentElement.appendChild(r);addEventListener('mousemove',e=>{c.style.transform='translate('+(e.clientX-3)+'px,'+(e.clientY-2)+'px)'},true);addEventListener('mousedown',e=>{r.style.left=e.clientX+'px';r.style.top=e.clientY+'px';r.animate([{opacity:1,transform:'scale(.4)'},{opacity:0,transform:'scale(1.6)'}],{duration:600,easing:'ease-out'})},true);})()`;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const scenes = {
  gaze: { url:'https://gallery-lime-chi.vercel.app/footer-gaze.html', dur:6400, cursor:true,
    async setup(p){ await p.mouse.move(640,120); await sleep(1500); },
    // 눈(640,415)을 중심으로 한 바퀴 반 — 끝이 시작과 같은 자리라 루프가 이어진다
    async frame(p,t){ const a=-Math.PI/2 + (t/6400)*Math.PI*2; await p.mouse.move(640+Math.cos(a)*430, 415+Math.sin(a)*300); } },
  gc: { url:'https://gallery-lime-chi.vercel.app/gc-logo-intro.html', dur:11000, cursor:false,
    async setup(p){ await p.mouse.move(640,400); await sleep(2000); },
    async frame(p,t,st){ const target=Math.min(1,t/10500)*5200; const cur=await p.evaluate(()=>scrollY); const d=target-cur; if(d>4) await p.mouse.wheel({deltaY:d}); } },
  // 스크롤 한 번이 다음 정거장까지 미끄러진다. 첫 화면 → 퀘스트 시작 → 비행으로 두 번 굴린다
  // 비행 영상은 24fps라 카드도 24fps로 뽑는다. 30fps로 맞추면 네 장마다 한 장이 겹쳐 덜컥거린다.
  // 비행 15초를 다 담고 퀘스트 완료 카드까지 찍어야 루프가 비행 도중에 잘리지 않는다
  flight: { url:'https://gallery-lime-chi.vercel.app/flight-quest.html', dur:25000, fps:24, cursor:false, headful:true,
    async setup(p){ await p.mouse.move(640,400); await sleep(3000); },
    async frame(p,t,st){ for (const at of [1800, 5200]) if (t>=at && !st[at]) { st[at]=1; await p.mouse.wheel({deltaY:240}); } } },
  econix: { url:'https://econix.ai.kr', dur:9000, cursor:false, vh:2130,
    async setup(p){ await sleep(2000); await p.evaluate(()=>{ for (const b of document.querySelectorAll('button')) if (b.getAttribute('aria-label')?.match(/닫기|close/i)) b.click(); }); await sleep(1500); },
    async frame(p,t){ } },
};
const s = scenes[name];
// 헤드리스는 고해상도 영상 디코딩을 못 따라가 프레임이 겹친다. 영상이 주인 장면은 창을 띄워 GPU로 찍는다
const b = await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: s.headful ? false : 'new', defaultViewport:null, args:['--use-angle=metal','--enable-gpu','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required','--hide-scrollbars']});
const p = await b.newPage(); await p.setViewport({width:W,height:s.vh||H,deviceScaleFactor:1});
await p.goto(s.url,{waitUntil:'networkidle2',timeout:60000});
if (s.cursor) await p.evaluate(CURSOR);
await s.setup(p);
const dir=`frames-${name}`; fs.rmSync(dir,{recursive:true,force:true}); fs.mkdirSync(dir);
const cdp = await p.createCDPSession(); const frames=[];
cdp.on('Page.screencastFrame', async f=>{ frames.push({ts:f.metadata.timestamp,data:f.data}); cdp.send('Page.screencastFrameAck',{sessionId:f.sessionId}).catch(()=>{}); });
await cdp.send('Page.startScreencast',{format:'jpeg',quality:92,maxWidth:W,maxHeight:s.vh||H,everyNthFrame:1});
const t0=Date.now(); const st={};
while(Date.now()-t0 < s.dur){ await s.frame(p, Date.now()-t0, st); await sleep(12); }
await cdp.send('Page.stopScreencast'); await sleep(300);
// 타임스탬프 기준으로 30fps에 다시 맞춘다 (screencast는 화면이 바뀔 때만 프레임을 준다)
const start=frames[0].ts, fps=s.fps||30, n=Math.floor(s.dur/1000*fps); let j=0;
for(let i=0;i<n;i++){ const tt=start+i/fps; while(j+1<frames.length && frames[j+1].ts<=tt) j++; fs.writeFileSync(`${dir}/f${String(i).padStart(4,'0')}.jpg`, Buffer.from(frames[j].data,'base64')); }
console.log(name,'captured',frames.length,'raw →',n);
await b.close();
