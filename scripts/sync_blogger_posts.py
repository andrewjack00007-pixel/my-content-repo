from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


DEFAULT_BLOG_URL = "https://myanmarcasinoguide.blogspot.com/"
BLOCK_TAGS = {"article", "aside", "blockquote", "div", "figure", "figcaption", "p", "section"}
SKIP_TAGS = {"script", "style", "iframe", "object", "embed", "form"}


class BloggerHTMLToMarkdown(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[str] = []
        self.list_stack: list[dict[str, int | str]] = []
        self.skip_depth = 0
        self.in_pre = False

    def append(self, value: str) -> None:
        if not self.skip_depth:
            self.parts.append(value)

    def newline(self, count: int = 1) -> None:
        if self.skip_depth:
            return
        current = "".join(self.parts[-3:])
        existing = len(current) - len(current.rstrip("\n"))
        if existing < count:
            self.parts.append("\n" * (count - existing))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attributes = {key.lower(): value or "" for key, value in attrs}
        if tag in SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in BLOCK_TAGS:
            self.newline(2)
        elif re.fullmatch(r"h[1-6]", tag):
            self.newline(2)
            self.append("#" * int(tag[1]) + " ")
        elif tag == "br":
            self.newline()
        elif tag in {"strong", "b"}:
            self.append("**")
        elif tag in {"em", "i"}:
            self.append("*")
        elif tag == "code" and not self.in_pre:
            self.append("`")
        elif tag == "pre":
            self.newline(2)
            self.append("```\n")
            self.in_pre = True
        elif tag == "a":
            self.links.append(attributes.get("href", ""))
            self.append("[")
        elif tag == "img":
            source = attributes.get("src", "")
            if source:
                alt = attributes.get("alt", "Image").replace("]", "\\]")
                self.append(f"![{alt}]({source})")
        elif tag in {"ul", "ol"}:
            self.list_stack.append({"tag": tag, "count": 0})
            self.newline()
        elif tag == "li":
            self.newline()
            indent = "  " * max(0, len(self.list_stack) - 1)
            marker = "- "
            if self.list_stack and self.list_stack[-1]["tag"] == "ol":
                self.list_stack[-1]["count"] = int(self.list_stack[-1]["count"]) + 1
                marker = f"{self.list_stack[-1]['count']}. "
            self.append(indent + marker)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag in BLOCK_TAGS or re.fullmatch(r"h[1-6]", tag):
            self.newline(2)
        elif tag in {"strong", "b"}:
            self.append("**")
        elif tag in {"em", "i"}:
            self.append("*")
        elif tag == "code" and not self.in_pre:
            self.append("`")
        elif tag == "pre":
            self.append("\n```\n")
            self.in_pre = False
        elif tag == "a":
            href = self.links.pop() if self.links else ""
            self.append(f"]({href})" if href else "]")
        elif tag in {"ul", "ol"}:
            if self.list_stack:
                self.list_stack.pop()
            self.newline(2)

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_pre:
            self.append(data)
            return
        cleaned = re.sub(r"[\t\f\v ]+", " ", data.replace("\xa0", " "))
        self.append(cleaned)

    def markdown(self) -> str:
        text = "".join(self.parts).replace("\r", "")
        text = "\n".join(line.rstrip() for line in text.splitlines())
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def get_text(mapping: dict, key: str) -> str:
    return str(mapping.get(key, {}).get("$t", "")).strip()


def get_plain_text(mapping: dict, key: str) -> str:
    return unescape(get_text(mapping, key))


def alternate_url(entry: dict) -> str:
    for link in entry.get("link", []):
        if link.get("rel") == "alternate":
            return str(link.get("href", ""))
    return ""


def post_id(entry: dict) -> str:
    match = re.search(r"\.post-(\d+)$", get_text(entry, "id"))
    return match.group(1) if match else "unknown"


def post_slug(entry: dict) -> str:
    path_name = Path(urllib.parse.urlparse(alternate_url(entry)).path).name
    candidate = path_name.removesuffix(".html")
    slug = re.sub(r"[^a-z0-9]+", "-", candidate.lower()).strip("-")
    return slug[:100] or f"blogger-post-{post_id(entry)}"


def fetch_entries(blog_url: str) -> tuple[str, list[dict]]:
    feed_url = urllib.parse.urljoin(blog_url.rstrip("/") + "/", "feeds/posts/default")
    start_index = 1
    page_size = 150
    entries: list[dict] = []
    feed_title = "Blogger"
    total = None

    while total is None or start_index <= total:
        query = urllib.parse.urlencode(
            {"alt": "json", "start-index": start_index, "max-results": page_size}
        )
        request = urllib.request.Request(
            f"{feed_url}?{query}", headers={"User-Agent": "my-content-repo-blogger-sync/1.0"}
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        feed = payload.get("feed", {})
        feed_title = get_plain_text(feed, "title") or feed_title
        batch = feed.get("entry", [])
        total = int(get_text(feed, "openSearch$totalResults") or len(batch))
        if not batch:
            break
        entries.extend(batch)
        start_index += len(batch)

    unique = {post_id(entry): entry for entry in entries}
    ordered = sorted(unique.values(), key=lambda entry: get_text(entry, "published"), reverse=True)
    return feed_title, ordered


def render_post(entry: dict, blog_title: str) -> tuple[str, str]:
    title = get_plain_text(entry, "title") or f"Blogger post {post_id(entry)}"
    published = get_text(entry, "published")
    updated = get_text(entry, "updated")
    source_url = alternate_url(entry)
    parser = BloggerHTMLToMarkdown()
    parser.feed(get_text(entry, "content"))
    body = parser.markdown()
    file_name = f"{published[:10]}-{post_slug(entry)}-{post_id(entry)}.md"
    document = f"""<!--
source: Blogger
blog: {blog_title}
blogger_id: {post_id(entry)}
published: {published}
updated: {updated}
canonical: {source_url}
-->

# {title}

**Published:** {published[:10]}
**Original:** [{source_url}]({source_url})

{body}

---

> **18+ archive notice / 理性娱乐提醒：** This copy is for adult information only. Games cannot guarantee profit; set budget and time limits, never chase losses, and stop if participation affects health, work or family. / 本存档仅供成年人参考；任何游戏均不能保证盈利，请设定预算与时间限制，切勿追损，如参与影响健康、工作或家庭应立即停止。

Archived automatically from [{blog_title}]({source_url}). The Blogger page remains the canonical version.
"""
    return file_name, document


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def sync(blog_url: str, output_dir: Path) -> tuple[int, int]:
    blog_title, entries = fetch_entries(blog_url)
    output_dir.mkdir(parents=True, exist_ok=True)
    changed = 0
    index_rows: list[str] = []

    for entry in entries:
        file_name, document = render_post(entry, blog_title)
        if write_if_changed(output_dir / file_name, document):
            changed += 1
        safe_title = get_plain_text(entry, "title").replace("[", "\\[").replace("]", "\\]")
        index_rows.append(
            f"- [{safe_title}]({urllib.parse.quote(file_name)}) — {get_text(entry, 'published')[:10]} "
            f"· [Blogger]({alternate_url(entry)})"
        )

    index = f"""# Google Blogger archive

Automatic Markdown archive of published posts from [{blog_title}]({blog_url}).

- Blogger blog ID: `5807824031985687769`
- Published posts found: {len(entries)}
- Canonical source: Blogger
- Sync behavior: add or update; archived files are not automatically deleted

## Posts

{chr(10).join(index_rows)}
"""
    if write_if_changed(output_dir / "README.md", index):
        changed += 1
    return len(entries), changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive public Blogger posts as Markdown.")
    parser.add_argument("--blog-url", default=DEFAULT_BLOG_URL)
    parser.add_argument("--output-dir", type=Path, default=Path("google"))
    args = parser.parse_args()
    total, changed = sync(args.blog_url, args.output_dir)
    print(f"Blogger posts found: {total}")
    print(f"Files added or updated: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
