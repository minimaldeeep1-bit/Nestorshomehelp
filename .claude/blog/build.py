"""Static blog builder for nestorshomehelp.ca (no dependencies, Python 3.9+).

Source:  .claude/blog/posts/<slug>.html   (front matter + article body HTML)
Output:  blog/<slug>.html, blog/index.html, sitemap.xml, robots.txt, _redirects,
         and the "Latest from the blog" block in index.html (between BLOG:START/END markers).

Front matter (between --- lines, one `key: value` per line):
  title, description, date (YYYY-MM-DD), category, image (file in assets/blog/)
  optional: updated (YYYY-MM-DD)

Run from the repo root:  python .claude/blog/build.py
Netlify publishes the repo root as-is, so commit the generated files.
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS = ROOT / ".claude" / "blog" / "posts"
MERGED = ROOT / ".claude" / "blog" / "merged.txt"
SITE = "https://nestorshomehelp.ca"
PHONE, PHONE_TEL = "(403) 461-4332", "+14034614332"
AUTHOR = "Vitalii Nestorenko"
GTAG = "G-55TCNTEBM8"

CATS = {
    "plumbing": ("Plumbing & Bathroom", "fa-wrench"),
    "electrical": ("Lights & Electrical", "fa-bolt"),
    "mounting": ("Mounting & Assembly", "fa-tv"),
    "interior": ("Walls, Doors & Floors", "fa-hammer"),
    "outdoor": ("Outdoor & Cleanup", "fa-seedling"),
    "home-bar": ("Home Bar & Kegerator", "fa-beer"),
    "guides": ("Homeowner Guides", "fa-book-open"),
}
# where each category sends readers on the main site
CAT_LINK = {
    "home-bar": ("../home-bar-installation.html", "Home bar & kegerator installation"),
}
DEFAULT_LINK = ("../index.html#comprehensive-services", "See all handyman services")
STATIC_PAGES = ["", "airdrie-handyman.html", "okotoks-handyman.html", "home-bar-installation.html"]
REQUIRED = ["title", "description", "date", "category", "image"]


def esc(s):
    return html.escape(s, quote=True)


def parse(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not m:
        raise ValueError(f"{path.name}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    missing = [k for k in REQUIRED if not meta.get(k)]
    if missing:
        raise ValueError(f"{path.name}: missing {missing}")
    if meta["category"] not in CATS:
        raise ValueError(f"{path.name}: unknown category {meta['category']} (use one of {list(CATS)})")
    date.fromisoformat(meta["date"])
    if not (ROOT / "assets" / "blog" / meta["image"]).exists():
        raise ValueError(f"{path.name}: image assets/blog/{meta['image']} not found")
    meta["slug"] = path.stem
    meta["body"] = m.group(2).strip()
    meta["words"] = len(re.sub(r"<[^>]+>", " ", meta["body"]).split())
    meta["minutes"] = max(1, round(meta["words"] / 220))
    meta.setdefault("updated", meta["date"])
    return meta


def nice_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%B %d, %Y").replace(" 0", " ")


HEAD = """<!DOCTYPE html>
<html lang="en-CA">
<head>
    <script async src="https://www.googletagmanager.com/gtag/js?id={gtag}"></script>
    <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{gtag}');</script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:type" content="{ogtype}">
    <meta property="og:title" content="{ogtitle}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{ogimage}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="theme-color" content="#1E3A5F">
    <link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-96x96.png">
    <link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {{ --navy:#1E3A5F; --orange:#FF6B35; }}
        body {{ font-family:'Roboto',sans-serif; background:#F5F5F5; -webkit-font-smoothing:antialiased; }}
        .navy-bg {{ background-color:var(--navy); }}
        .text-orange {{ color:var(--orange); }}
        .bg-orange {{ background-color:var(--orange); }}
        .prose-blog {{ color:#334155; font-size:1.075rem; line-height:1.8; }}
        .prose-blog h2 {{ color:#1E3A5F; font-weight:900; font-size:1.6rem; line-height:1.3; margin:2.2rem 0 .8rem; }}
        .prose-blog h3 {{ color:#1E3A5F; font-weight:700; font-size:1.25rem; margin:1.6rem 0 .6rem; }}
        .prose-blog p {{ margin:0 0 1.1rem; }}
        .prose-blog ul, .prose-blog ol {{ margin:0 0 1.2rem 1.4rem; }}
        .prose-blog ul {{ list-style:disc; }} .prose-blog ol {{ list-style:decimal; }}
        .prose-blog li {{ margin:.35rem 0; }}
        .prose-blog a {{ color:#FF6B35; text-decoration:underline; text-underline-offset:3px; }}
        .prose-blog strong {{ color:#1E293B; }}
    </style>
{jsonld}
</head>
<body class="text-gray-800">
    <header class="navy-bg text-white shadow-lg">
        <div class="container mx-auto px-4 sm:px-6 py-2 flex justify-between items-center text-sm border-b border-white/10">
            <div class="flex items-center space-x-4">
                <a href="https://www.instagram.com/nestorshomehelp/" target="_blank" rel="noopener" aria-label="Instagram" class="hover:text-orange"><i class="fab fa-instagram"></i></a>
                <a href="https://www.facebook.com/profile.php?id=61583910731270" target="_blank" rel="noopener" aria-label="Facebook" class="hover:text-orange"><i class="fab fa-facebook"></i></a>
            </div>
            <a href="tel:{tel}" class="hover:text-orange flex items-center"><i class="fas fa-phone-alt mr-2"></i><span class="hidden sm:inline mr-1">Call/Text:</span>{phone}</a>
        </div>
        <nav class="container mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
            <a href="../index.html"><img src="../assets/logo 11.png" alt="Nestor's Home Help" class="h-12 sm:h-14 w-auto"></a>
            <div class="flex items-center gap-4 sm:gap-6 text-sm sm:text-base font-medium">
                <a href="../index.html#comprehensive-services" class="hover:text-orange hidden sm:inline">Services</a>
                <a href="../index.html#pricing" class="hover:text-orange hidden sm:inline">Pricing</a>
                <a href="index.html" class="hover:text-orange">Blog</a>
                <a href="../index.html#request" class="bg-orange hover:opacity-90 text-white px-4 py-2 rounded-full font-bold">Free Quote</a>
            </div>
        </nav>
    </header>
"""

FOOTER = """
    <footer class="navy-bg text-white py-12 mt-16">
        <div class="container mx-auto px-6 text-center">
            <img src="../assets/logo 11.png" alt="Nestor's Home Help" class="h-12 w-auto mx-auto mb-5">
            <p class="text-gray-300 mb-2">Licensed &amp; insured handyman serving Calgary, Airdrie, Chestermere, Okotoks and Cochrane.</p>
            <p class="text-gray-400 text-sm mb-6">Mon-Fri 2-10 PM &middot; Sat-Sun 8 AM-8 PM</p>
            <div class="flex flex-wrap justify-center gap-x-6 gap-y-2 mb-6 text-gray-300">
                <a href="tel:{tel}" class="hover:text-white"><i class="fas fa-phone mr-2"></i>{phone}</a>
                <a href="mailto:nestorshomehelp@gmail.com" class="hover:text-white"><i class="fas fa-envelope mr-2"></i>Email</a>
                <a href="../index.html" class="hover:text-white">Home</a>
                <a href="index.html" class="hover:text-white">Blog</a>
                <a href="../airdrie-handyman.html" class="hover:text-white">Handyman Airdrie</a>
                <a href="../okotoks-handyman.html" class="hover:text-white">Handyman Okotoks</a>
                <a href="../home-bar-installation.html" class="hover:text-white">Home Bar Installation</a>
            </div>
            <p class="text-gray-500 text-sm">&copy; {year} Nestor's Home Help. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
"""


def page_head(title, desc, canonical, ogtitle, ogimage, ogtype, jsonld_objs):
    jsonld = "\n".join(
        '    <script type="application/ld+json">\n' + json.dumps(o, ensure_ascii=False, indent=2) + "\n    </script>"
        for o in jsonld_objs)
    return HEAD.format(gtag=GTAG, title=esc(title), desc=esc(desc), canonical=canonical, ogtitle=esc(ogtitle),
                       ogimage=ogimage, ogtype=ogtype, jsonld=jsonld, tel=PHONE_TEL, phone=PHONE)


def card(p, root="../"):
    """root = relative path from the page to the site root."""
    label, icon = CATS[p["category"]]
    return f"""
            <a href="{root}blog/{p['slug']}.html" class="group bg-white rounded-2xl shadow-md hover:shadow-xl transition overflow-hidden flex flex-col" data-cat="{p['category']}">
                <div class="aspect-[3/2] overflow-hidden bg-gray-100">
                    <img src="{root}assets/blog/{p['image']}" alt="{esc(p['title'])}" loading="lazy" width="1536" height="1024" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                </div>
                <div class="p-5 flex flex-col flex-1">
                    <span class="text-xs font-bold uppercase tracking-wider text-orange mb-2"><i class="fas {icon} mr-1"></i>{label}</span>
                    <h3 class="font-bold text-lg text-[#1E3A5F] leading-snug mb-2 group-hover:text-orange">{esc(p['title'])}</h3>
                    <p class="text-gray-600 text-sm leading-relaxed flex-1">{esc(p['description'])}</p>
                    <span class="text-xs text-gray-400 mt-4">{nice_date(p['date'])} &middot; {p['minutes']} min read</span>
                </div>
            </a>"""


def related(p, posts, n=3):
    same = [q for q in posts if q["slug"] != p["slug"] and q["category"] == p["category"]]
    words = set(p["slug"].split("-")) - {"calgary", "how", "to", "a", "the", "for", "and", "service", "vs"}
    same.sort(key=lambda q: (-len(words & set(q["slug"].split("-"))), q["date"]), reverse=False)
    pick = same[:n]
    if len(pick) < n:
        pick += [q for q in posts if q["slug"] != p["slug"] and q not in pick][: n - len(pick)]
    return pick


def build_post(p, posts):
    url = f"{SITE}/blog/{p['slug']}.html"
    img_url = f"{SITE}/assets/blog/{p['image']}"
    label, icon = CATS[p["category"]]
    link, link_label = CAT_LINK.get(p["category"], DEFAULT_LINK)
    title_tag = p["title"] if len(p["title"]) > 52 else f"{p['title']} | Nestor's Home Help"
    jsonld = [
        {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["description"],
         "image": img_url, "datePublished": p["date"], "dateModified": p["updated"], "mainEntityOfPage": url,
         "author": {"@type": "Person", "name": AUTHOR, "url": f"{SITE}/#about"},
         "publisher": {"@type": "Organization", "name": "Nestor's Home Help",
                       "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/logo%2011.png"}}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]},
    ]
    rel = "".join(card(q) for q in related(p, posts))
    out = page_head(title_tag, p["description"], url, p["title"], img_url, "article", jsonld)
    out += f"""
    <main class="container mx-auto px-4 sm:px-6 pt-8">
        <nav class="text-sm text-gray-500 max-w-3xl mx-auto mb-4" aria-label="Breadcrumb">
            <a href="../index.html" class="hover:text-orange">Home</a> <span class="mx-1">/</span>
            <a href="index.html" class="hover:text-orange">Blog</a> <span class="mx-1">/</span>
            <span class="text-gray-400">{esc(label)}</span>
        </nav>
        <article class="max-w-3xl mx-auto bg-white rounded-2xl shadow-md overflow-hidden">
            <img src="../assets/blog/{p['image']}" alt="{esc(p['title'])}" width="1536" height="1024" class="w-full aspect-[3/2] object-cover">
            <div class="p-6 sm:p-10">
                <span class="text-xs font-bold uppercase tracking-wider text-orange"><i class="fas {icon} mr-1"></i>{label}</span>
                <h1 class="text-3xl sm:text-4xl font-black text-[#1E3A5F] leading-tight mt-2 mb-3">{esc(p['title'])}</h1>
                <p class="text-sm text-gray-500 mb-8">By {AUTHOR} &middot; {nice_date(p['date'])} &middot; {p['minutes']} min read</p>
                <div class="prose-blog">
{p['body']}
                </div>
                <aside class="mt-10 rounded-2xl navy-bg text-white p-6 sm:p-8">
                    <h2 class="text-2xl font-black mb-2">Need a hand with this?</h2>
                    <p class="text-gray-200 mb-5">Licensed &amp; insured handyman in Calgary, Airdrie, Chestermere, Okotoks and Cochrane. C$60/hour, free estimates, same-day service when available.</p>
                    <div class="flex flex-wrap gap-3">
                        <a href="tel:{PHONE_TEL}" class="bg-orange hover:opacity-90 text-white font-bold px-6 py-3 rounded-full"><i class="fas fa-phone-alt mr-2"></i>Call/Text {PHONE}</a>
                        <a href="../index.html#request" class="border-2 border-white hover:bg-white hover:text-[#1E3A5F] font-bold px-6 py-3 rounded-full">Request a free quote</a>
                        <a href="{link}" class="underline underline-offset-4 self-center text-gray-200 hover:text-white">{link_label}</a>
                    </div>
                </aside>
                <div class="mt-8 flex items-start gap-4 border-t pt-6">
                    <div class="w-12 h-12 rounded-full bg-orange text-white flex items-center justify-center font-black text-lg flex-shrink-0">VN</div>
                    <p class="text-sm text-gray-600"><strong class="text-[#1E3A5F]">{AUTHOR}</strong> is the owner of Nestor's Home Help, a licensed and insured handyman business in Calgary. He holds a Master's degree in mechanical engineering and does every job himself.</p>
                </div>
            </div>
        </article>
        <section class="max-w-6xl mx-auto mt-14">
            <h2 class="text-2xl font-black text-[#1E3A5F] mb-6 text-center">Keep reading</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">{rel}
            </div>
        </section>
    </main>
"""
    out += FOOTER.format(tel=PHONE_TEL, phone=PHONE, year=date.today().year)
    (ROOT / "blog" / f"{p['slug']}.html").write_text(out, encoding="utf-8", newline="\n")


def build_index(posts):
    url = f"{SITE}/blog/"
    desc = ("Practical home repair and maintenance tips for Calgary, Airdrie, Chestermere, Okotoks and Cochrane homeowners "
            "from a licensed local handyman.")
    jsonld = [{"@context": "https://schema.org", "@type": "Blog", "name": "Nestor's Home Help Blog", "url": url,
               "description": desc, "publisher": {"@type": "Organization", "name": "Nestor's Home Help"},
               "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}.html",
                             "datePublished": p["date"]} for p in posts[:20]]}]
    used = [c for c in CATS if any(p["category"] == c for p in posts)]
    buttons = '<button class="cat-btn bg-orange text-white px-4 py-2 rounded-full text-sm font-medium" data-filter="all">All</button>' + "".join(
        f'<button class="cat-btn bg-white text-gray-700 px-4 py-2 rounded-full text-sm font-medium shadow-sm hover:bg-orange hover:text-white" data-filter="{c}"><i class="fas {CATS[c][1]} mr-1"></i>{CATS[c][0]}</button>'
        for c in used)
    cards = "".join(card(p) for p in posts)
    out = page_head("Home Repair Tips for Calgary Homeowners | Nestor's Home Help Blog", desc, url,
                    "Nestor's Home Help Blog", f"{SITE}/assets/blog/{posts[0]['image']}", "website", jsonld)
    out += f"""
    <main>
        <section class="navy-bg text-white pb-14 pt-10">
            <div class="container mx-auto px-4 sm:px-6 text-center max-w-3xl">
                <h1 class="text-4xl sm:text-5xl font-black mb-4">Home Repair Tips for <span class="text-orange">Calgary Homeowners</span></h1>
                <p class="text-gray-300 text-lg">Straight answers from a local, licensed handyman: what to fix, when to call a pro, and how to keep your home in shape through Calgary's seasons.</p>
            </div>
        </section>
        <div class="container mx-auto px-4 sm:px-6 -mt-6">
            <div class="flex flex-wrap justify-center gap-2 mb-10">{buttons}</div>
            <div id="posts" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">{cards}
            </div>
        </div>
    </main>
    <script>
      document.querySelectorAll('.cat-btn').forEach(function(b){{b.addEventListener('click',function(){{
        var f=b.dataset.filter;
        document.querySelectorAll('.cat-btn').forEach(function(x){{x.classList.remove('bg-orange','text-white');x.classList.add('bg-white','text-gray-700');}});
        b.classList.add('bg-orange','text-white');b.classList.remove('bg-white','text-gray-700');
        document.querySelectorAll('#posts > a').forEach(function(c){{c.style.display=(f==='all'||c.dataset.cat===f)?'':'none';}});
      }});}});
    </script>
"""
    out += FOOTER.format(tel=PHONE_TEL, phone=PHONE, year=date.today().year)
    (ROOT / "blog" / "index.html").write_text(out, encoding="utf-8", newline="\n")


def update_home(posts):
    path = ROOT / "index.html"
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    start, end = "<!-- BLOG:START -->", "<!-- BLOG:END -->"
    if start not in raw:
        print("index.html: BLOG markers not found, skipped")
        return
    cards = "".join(card(p, root="") for p in posts[:3])
    block = f"""{start}
        <section id="blog" class="py-16 bg-gray-50">
            <div class="container mx-auto px-6">
                <div class="text-center mb-10">
                    <h2 class="section-title text-3xl md:text-4xl font-black text-gray-800 mb-3">Home Repair Tips <span class="text-orange">from the Blog</span></h2>
                    <p class="text-gray-600">Practical advice for Calgary-area homeowners.</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">{cards}
                </div>
                <div class="text-center mt-8"><a href="blog/" class="inline-block bg-orange text-white font-bold px-8 py-3 rounded-full hover:opacity-90">All articles</a></div>
            </div>
        </section>
        {end}"""
    new = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: block, raw, flags=re.S)
    new = re.sub(r"\r?\n", nl, new)
    path.write_bytes(new.encode("utf-8"))


def build_sitemap(posts):
    today = date.today().isoformat()
    urls = [(f"{SITE}/{p}", today) for p in STATIC_PAGES] + [(f"{SITE}/blog/", posts[0]["updated"])]
    urls += [(f"{SITE}/blog/{p['slug']}.html", p["updated"]) for p in posts]
    body = "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n',
        encoding="utf-8", newline="\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8", newline="\n")


def build_redirects(posts):
    slugs = {p["slug"] for p in posts}
    lines = ["# Generated by .claude/blog/build.py - old Soro blog URLs (/?post=slug) -> static posts"]
    if MERGED.exists():
        for line in MERGED.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                old, new = line.split()
                if new in slugs:
                    lines += [f"/ post={old} /blog/{new}.html 301!", f"/index.html post={old} /blog/{new}.html 301!"]
    lines += ["/ post=:post /blog/:post.html 301!", "/index.html post=:post /blog/:post.html 301!",
              "/.claude/* /404.html 404!"]
    (ROOT / "_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main():
    posts = []
    errors = []
    for f in sorted(POSTS.glob("*.html")):
        try:
            posts.append(parse(f))
        except ValueError as e:
            errors.append(str(e))
    if errors:
        sys.exit("Build failed:\n  " + "\n  ".join(errors))
    today = date.today().isoformat()
    future = [p["slug"] for p in posts if p["date"] > today]
    posts = [p for p in posts if p["date"] <= today]  # scheduled posts stay hidden until their date
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    (ROOT / "blog").mkdir(exist_ok=True)
    for old in (ROOT / "blog").glob("*.html"):
        old.unlink()
    for p in posts:
        build_post(p, posts)
    build_index(posts)
    update_home(posts)
    build_sitemap(posts)
    build_redirects(posts)
    print(f"Built {len(posts)} posts" + (f", {len(future)} scheduled: {future}" if future else ""))


if __name__ == "__main__":
    main()
