"""빌드 후 새 책의 원고·라우트·내부 링크·사이트맵을 비교한다. 시각 검사는 별도다."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.canonical = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")


def main():
    root = Path(__file__).resolve().parents[2]
    source = root / "src/content/book/ai-engineering"
    dist = root / "dist"
    prefix = "/books/ai-engineering/"
    host = "https://froggydisk.github.io"
    expected = {prefix}
    for path in source.rglob("*"):
        if path.suffix not in (".md", ".mdx"):
            continue
        if re.search(r"^draft:\s*true\s*$", path.read_text(), re.M):
            continue
        segments = path.relative_to(source).with_suffix("").parts
        expected.add(prefix + "/".join(re.sub(r"^\d+[-_.]", "", s) for s in segments) + "/")
    pages = {}
    for path in (dist / "books/ai-engineering").rglob("index.html"):
        url = "/" + str(path.parent.relative_to(dist)) + "/"
        page = Page()
        page.feed(path.read_text())
        pages[url] = page
    assert set(pages) == expected, "원고와 출력 페이지 목록 불일치"
    for url, page in pages.items():
        assert page.canonical == host + url, (url, "canonical")
        for href in page.links:
            link = urlsplit(href)
            if link.scheme or link.netloc:
                continue
            target = link.path or url
            if target.startswith(prefix):
                if target not in pages and not link.fragment:
                    asset = (dist / unquote(target).lstrip('/')).resolve()
                    if asset.is_relative_to(dist.resolve()) and asset.is_file():
                        continue
                assert target in pages, (url, href)
                if link.fragment:
                    assert unquote(link.fragment) in pages[target].ids, (url, href)
    for url in expected - {prefix}:
        assert url in pages[prefix].links, (url, "표지 목차 누락")
    for name in ("sitemap.xml", "sitemap-0.xml"):
        urls = {node.text for node in ET.parse(dist / name).iter()
                if node.tag.endswith("}loc") and node.text and node.text.startswith(host + prefix)}
        assert urls == {host + url for url in expected}, (name, "사이트맵 불일치")
    print(f"PASS: {len(expected)-1}장, 표지, 내부 링크·앵커·canonical·두 사이트맵")


if __name__ == "__main__":
    main()
