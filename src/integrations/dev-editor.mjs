import { readFile, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * dev 서버 전용 원고 편집 엔드포인트. `npm run dev`에서만 붙고 빌드 결과에는 아무것도 남기지 않는다.
 *
 *   GET  /__dev-edit?path=src/content/...md   → { content, mtime }
 *   POST /__dev-edit  { path, content, mtime } → { mtime }
 *
 * 읽고 쓰는 범위는 src/content 아래 .md/.mdx 로 막고, 루프백에서 온 요청만 받는다
 * (`astro dev --host`로 LAN에 열어 두어도 다른 기기에서는 원고를 쓸 수 없다).
 * 저장할 때 mtime을 비교해, 그사이 에디터에서 같은 파일을 고쳤으면 덮어쓰지 않고 409를 돌려준다.
 */
export default function devEditor() {
  let root = '';
  return {
    name: 'dev-editor',
    hooks: {
      'astro:config:done': ({ config }) => {
        root = fileURLToPath(config.root);
      },
      'astro:server:setup': ({ server }) => {
        const contentDir = path.join(root, 'src', 'content') + path.sep;

        const resolve = (rel) => {
          if (typeof rel !== 'string') return null;
          const abs = path.resolve(root, rel);
          if (!abs.startsWith(contentDir)) return null;
          if (!/\.mdx?$/.test(abs)) return null;
          return abs;
        };

        const send = (res, status, body) => {
          res.statusCode = status;
          res.setHeader('Content-Type', 'application/json; charset=utf-8');
          res.end(JSON.stringify(body));
        };

        server.middlewares.use('/__dev-edit', async (req, res) => {
          const addr = req.socket.remoteAddress ?? '';
          if (!['127.0.0.1', '::1', '::ffff:127.0.0.1'].includes(addr)) {
            return send(res, 403, { error: 'localhost에서만 편집할 수 있습니다' });
          }
          try {
            if (req.method === 'GET') {
              const url = new URL(req.url ?? '', 'http://localhost');
              const abs = resolve(url.searchParams.get('path'));
              if (!abs) return send(res, 400, { error: '편집할 수 없는 경로입니다' });
              const [content, st] = await Promise.all([readFile(abs, 'utf-8'), stat(abs)]);
              return send(res, 200, { content, mtime: st.mtimeMs });
            }

            if (req.method === 'POST') {
              let raw = '';
              for await (const chunk of req) raw += chunk;
              const { path: rel, content, mtime } = JSON.parse(raw);
              const abs = resolve(rel);
              if (!abs || typeof content !== 'string') {
                return send(res, 400, { error: '편집할 수 없는 경로입니다' });
              }
              const current = await stat(abs);
              if (typeof mtime === 'number' && Math.abs(current.mtimeMs - mtime) > 1) {
                return send(res, 409, { error: '그사이 파일이 바뀌었습니다. 다시 불러온 뒤 저장하세요' });
              }
              await writeFile(abs, content, 'utf-8');
              const after = await stat(abs);
              return send(res, 200, { mtime: after.mtimeMs });
            }

            send(res, 405, { error: 'GET 또는 POST만 받습니다' });
          } catch (err) {
            send(res, 500, { error: String(err?.message ?? err) });
          }
        });
      },
    },
  };
}
