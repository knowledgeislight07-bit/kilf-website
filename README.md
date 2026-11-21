# Knowledge Is Light Foundation — website

Static site for **knowledgeislight.us**. No Wix, no Squarespace, no monthly fee.

## Editing

| To change… | Edit |
|---|---|
| Email, phone, academic year, PayPal link, Google Form links | `site.json` |
| Page text | `src/pages/*.html` (plain HTML; the `<!--meta {...} -->` block at the top sets the Google title and description) |
| Header, menu, footer | `src/_layout.html` |
| Colors and fonts | `src/assets/css/site.css` (the variables at the top) |
| Images | `src/assets/img/` |

Build and preview locally:

```bash
python3 build.py --serve
```

Then open http://localhost:8000. The output goes to `dist/`. Python 3 is the only requirement.

### Two settings to fill in (`site.json`)
- **`paypal_url`**: her PayPal payment link. Easiest option: log into PayPal → *Get Paid* → create a **PayPal.me** link or a **Pay Link / Donate button** and paste the URL. Until it's set, the Tuition page asks families to email for a link.
- **`web3forms_key`** (optional): a free key from https://web3forms.com (enter `knowledgeislight07@gmail.com` and the key is emailed to you). With a key, the contact form sends messages straight to that inbox. Without one, the form opens the visitor's email app with the message pre-filled.

## Hosting for free: Cloudflare Pages (recommended)

Cloudflare Pages is free and supports the `_redirects` file. That file is what keeps the Google rankings (see below). GitHub Pages does **not** support it.

1. Push this folder to a GitHub repo.
2. Go to Cloudflare dashboard → *Workers & Pages* → *Create* → *Pages* → *Connect to Git* and pick the repo.
   - Build command: `python3 build.py`
   - Build output directory: `dist`
3. Deploy, then check the preview URL (`*.pages.dev`).
4. **Domain:** `knowledgeislight.us` currently uses Wix's DNS (`ns10/ns11.wixdns.net`).
   - If the domain was **bought through Wix**: in Wix go to *Domains* → *Transfer away from Wix*, get the transfer code, and transfer it to Cloudflare Registrar (at-cost, about $10/yr). Wait to cancel the Wix plan until the transfer completes.
   - If it was bought elsewhere: add the site to Cloudflare (free plan), then change the nameservers at the registrar to the two Cloudflare gives you.
   - Then in the Pages project → *Custom domains*, add both `www.knowledgeislight.us` and `knowledgeislight.us`. Add a redirect rule from the bare domain to `www.`, because Google has the `www.` version indexed.

## Keeping the #1 Google ranking

Her ranking comes mainly from the **domain name**, its age, and the links pointing to it, not from Wix. Keeping the same domain carries all of that over. The steps below cover the rest:

1. **Same domain, same `www.` host**: every canonical URL in the build uses `https://www.knowledgeislight.us`.
2. **301 redirects for every old Wix URL** (`src/_redirects`). For example, `/copy-of-about-us` goes to `/about/` and `/general-7` goes to `/islamic-foundations-program/`. Google moves each old page's ranking to its new address, and old links and QR-code flyers keep working.
3. **Same core title**: the homepage title still leads with "Online Islamic Education … Knowledge Is Light Foundation".
4. **Better on-page SEO than the Wix site:** each page has its own title and description, plus Open Graph tags for link previews. The build also adds structured data (`EducationalOrganization`/`NGO`, `Course` for each year, and breadcrumbs), an auto-generated `sitemap.xml` and `robots.txt`, and descriptive alt text. The pages are small and load fast, which Google rewards.
5. **After switching DNS (important):**
   - Set up **Google Search Console** for `knowledgeislight.us` (verify with a DNS TXT record in Cloudflare) and submit `https://www.knowledgeislight.us/sitemap.xml`.
   - Use *URL Inspection* → *Request indexing* on the homepage.
   - Check the *Pages* report over the next 2–4 weeks for 404s. A brief ranking wobble during that time is normal.
   - Keep `_redirects` in place permanently.
6. **Google Business Profile** (free) for "Knowledge Is Light Foundation" strongly helps branded and local searches.

## Image licensing note
The Wix site's geometric backgrounds and illustrations are **Adobe Stock images licensed through Wix**. That license generally covers use only on a Wix site, so they were deliberately **not** reused here. This site uses the foundation's own logo and flyers, Unsplash photos (free license), and an original geometric pattern (`src/assets/img/pattern.svg`).
