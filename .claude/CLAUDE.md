# nestorshomehelp.ca: site repo rules for Claude

This repo is the live website of **Nestor's Home Help**, a solo, part-time, licensed and insured handyman business in Calgary, Alberta. The owner is Vitalii Nestorenko (always this spelling). **Netlify publishes `main` automatically within ~30 seconds of a push.**

## What may be published without the owner's approval
- **Blog posts only**, via the `blog-post` skill (`.claude/skills/blog-post/SKILL.md`). The owner explicitly approved fully automatic blog publishing on 2026-11-03.
- **Everything else** (index.html content, city pages, prices, design, redirects beyond what build.py generates) goes to a separate branch and waits for the owner's "так" (yes). Don't push anything else to `main`.

## Business facts (use exactly these, never invent others)
- Phone/text/WhatsApp: (403) 461-4332. Email: nestorshomehelp@gmail.com.
- Service area: **Calgary, Airdrie, Okotoks, Cochrane** (Chestermere is not confirmed, so don't claim it).
- Hours: Mon-Fri 2-10 PM, Sat-Sun 8 AM-8 PM. Same-day service when available.
- Pricing: **C$60/hour, minimum call-out C$85 including the first hour, materials extra**, free estimates. The final price is agreed after inspection. Don't quote other hourly rates. Fixed ranges are on index.html (Pricing) and can be cited as "from $X".
- Electrical and plumbing: replacements on **existing** connections only, no new wiring or permit work. Say clearly when a licensed electrician or plumber is needed.
- Owner background (true, usable): Master's degree in mechanical engineering; professional brewer with 8+ years (Certified Cicerone, IBD General Certificate in Brewing, award-winning lagers in Alberta), which is why the **home bar and kegerator** service is special. Don't name his brewery employer.
- Taxes and rules: Canadian and Alberta only. The business is not GST-registered.

## Privacy
Never commit client names, addresses, phone numbers (other than the business number), CSV or XLSX files, or estimates. Never mention a client's street or house number in content.

## Structure
- `index.html`, `airdrie-handyman.html`, `okotoks-handyman.html`, `home-bar-installation.html`: hand-edited pages. `index.html` uses CRLF line endings.
- Blog: source in `.claude/blog/posts/*.html`, built by `python .claude/blog/build.py` into `blog/`, `sitemap.xml`, `robots.txt`, `_redirects` and the homepage "BLOG" block. Don't edit generated files by hand.
- `.claude/` is never served (blocked in `_redirects`).
