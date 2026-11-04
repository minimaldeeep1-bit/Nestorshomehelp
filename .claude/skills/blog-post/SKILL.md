---
name: blog-post
description: >
  Writes and publishes one new SEO blog post on nestorshomehelp.ca (Nestor's Home Help, Calgary
  handyman): picks a topic that isn't covered yet, researches facts with sources, writes the
  article, makes the cover, builds the static blog and pushes to main (Netlify auto-publishes).
  Use for the scheduled blog run, and whenever asked to "write a blog post", "new article",
  "напиши статтю", "пост у блог", or to replace the old Soro auto-blog.
---

# Write and publish one blog post

The goal is to bring Calgary-area homeowners to the site from Google and turn them into calls. That only happens when a post answers a real question better than the competition and points the reader to a service page. Generic filler ("In today's fast-paced world…") hurts the site, because Google demotes thin AI content, so write like a practical tradesperson who explains *why*.

Read `.claude/CLAUDE.md` first. The business facts, service area, prices and what may be published live there. Blog posts are the only thing you may push to `main` without the owner.

## 1. Pick the topic

1. List what exists: `ls .claude/blog/posts/` and skim the titles (`grep -h '^title:' .claude/blog/posts/*.html`).
2. **Don't duplicate.** If a post on the same search intent exists (for example there is already a "TV wall mounting Calgary" post), pick something else, or a clearly different angle ("TV mounting above a fireplace"). Duplicates compete with each other in Google. Old merged Soro topics are listed in `.claude/blog/merged.txt`, so treat them as covered too.
3. Choose, in this priority order:
   - **Home bar / kegerator** topics (the owner is a professional brewer, it's a rare niche with little competition, and there are almost no posts yet). Examples: kegerator installation Calgary, choosing a kegerator, draft line cleaning schedule, why beer pours foamy at home, CO2 pressure for different beer styles, building a basement bar, keg sizes in Canada.
   - **Season and events right now** in Calgary: see `.claude/blog/calgary-seasons.md` (posts should go up 2–6 weeks before the season peaks).
   - **City and service gaps:** service + Airdrie / Okotoks / Cochrane, which help the city pages.
   - Common homeowner questions ("can a handyman…", "how much does … cost in Calgary", "repair or replace").
4. Write down the main keyword (what someone types into Google) and 3–5 related phrases.

## 2. Research (only true facts)

- Use web search for anything factual: Alberta and Calgary rules (permits, landlord/tenant law, fire code), product specs, safety guidance, typical costs. Prefer official sources (alberta.ca, calgary.ca, canada.ca, manufacturers, brewing associations).
- Important claims (law, safety, money) need **2 independent sources**. If you can't confirm something, leave it out or phrase it as general advice. Never invent statistics, studies, quotes or customer stories.
- Prices: only the business's own prices from `.claude/CLAUDE.md` / index.html Pricing. Market ranges only with a source ("HomeStars lists…").
- **No fabricated experience.** Don't write "last week I fixed a deck in Tuscany" unless it's true. You may describe how the business approaches the job ("I always check for…") because that reflects the owner's real method: engineering approach, studs not anchors, cleanup after work.
- Keep the source URLs. They go into an HTML comment at the end of the post (not shown to readers), so the owner can verify them later.

## 3. Write

File: `.claude/blog/posts/<slug>.html`. The slug is lowercase-hyphenated with the main keyword, 3–7 words, unique.

```
---
title: <55–65 chars, keyword near the start, no clickbait>
description: <140–160 chars, keyword + benefit + Calgary>
date: <today YYYY-MM-DD>
category: <plumbing|electrical|mounting|interior|outdoor|home-bar|guides>
image: <slug>.webp
---
<p>Opening: answer the question in the first 2–3 sentences.</p>
<h2>…</h2>
…
```

Rules for the body (HTML, no `<h1>`, because the template adds the title):
- **1,000–1,500 words.** Short paragraphs (2–4 sentences), H2 every 150–300 words, H3 where useful, at least one `<ul>` or `<ol>` checklist.
- Canadian English spelling (colour, metre, centre) and Calgary specifics where they really matter: chinook temperature swings, dry air, hail season, hard water, freeze-thaw, basements, older bungalows vs new builds.
- Mention the service area naturally once ("Calgary, Airdrie, Okotoks and Cochrane"). No phone number in the body (the template adds the call-to-action box).
- **2–4 internal links** with descriptive anchor text, relative paths from `/blog/`:
  - services: `../index.html#comprehensive-services`, pricing `../index.html#pricing`, quote `../index.html#request`
  - cities: `../airdrie-handyman.html`, `../okotoks-handyman.html`
  - home bar: `../home-bar-installation.html` (always link it from home-bar posts)
  - other posts: `<other-slug>.html` (same folder)
- Be honest about limits: when the job needs a licensed electrician or plumber, a permit, or is DIY-friendly, say so. That honesty builds trust.
- End with a short `<h2>FAQ</h2>` of 3 questions with `<h3>` question / `<p>` answer.
- Last line: `<!-- sources: url1 | url2 | … -->`

## 4. Cover image

```bash
python .claude/blog/make_cover.py <slug> "<Title>" <category>
```
If a real work photo fits (in `assets/`), add `--photo assets/<file>`. Real photos are better than graphics.

## 5. Build, check, publish

```bash
python .claude/blog/build.py
```
It fails loudly on missing fields or images. Then check:
- `blog/<slug>.html` exists, the new post is first in `blog/index.html`, and it's in `sitemap.xml`;
- word count is in range, internal links point to files that exist, and no phone numbers or client details are in the body.

Then publish:
```bash
git checkout main && git pull --ff-only
git add .claude/blog/posts/<slug>.html assets/blog/<slug>.webp blog/ sitemap.xml index.html _redirects robots.txt
git commit -m "Blog: <title>"
git push origin main
```
About a minute later, confirm `https://nestorshomehelp.ca/blog/<slug>.html` returns 200.

If anything looks wrong (build error, unsure facts, a topic too close to an existing one), **don't push**. Leave the work on a branch `blog/draft-<slug>` and say what needs the owner's eye.

## 6. Report

Finish with a short summary: title, URL, main keyword, sources used, and the next 2 topic ideas (so the next run has a head start).
