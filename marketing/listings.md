# CaliDoorCheck listing and outreach targets

Prepared: Monday, November 23, 2026 (America/Los_Angeles).  
Site: https://calidoorcheck.com  
Owner: Yaro Celis / YCO Productions  

Nothing in this file has been submitted, posted, or sent. Each item is a draft plan for approval. Do not invent traffic, reviews, or rankings in any form.

**Suggested listing copy (reuse everywhere, do not embellish):**

> CaliDoorCheck is a free directory of currently renewed California CSLB D-28 (Doors, Gates and Activating Devices) licensed garage door contractors in Los Angeles, Orange, Ventura, Riverside, San Bernardino, and San Diego counties. Every listing comes from the Contractors State License Board's public List by Classification and County. The site also publishes sourced guides on how to check a license, common garage door repair scams, and published spring-replacement price ranges.

Facts you can cite (from the Nov 22, 2026 CSLB download and the live site): 1,608 clear licenses; six counties; 114 live pages as of this writing (home, about, 3 guides, 2 county hubs, 107 city pages). Price figures on the site are national published ranges, not a CaliDoorCheck survey. Do not call the site "the official CSLB directory."

---

## Priority 1 — do these first (indexing and identity)

These do the most for discoverability and trust. They need your Google, Microsoft, and/or GoDaddy login. An agent can add DNS TXT records or verification files after you share the exact values, but should not create the accounts for you.

### 1. Google Search Console (highest priority)

- **Submission page:** https://search.google.com/search-console  
  Help: https://support.google.com/webmasters/answer/34592  
  Verification help: https://support.google.com/webmasters/answer/9008080
- **Account needed:** Yes (a Google account you control).
- **What to enter:**
  1. Click the property selector → **Add property**.
  2. Choose a **Domain** property and enter `calidoorcheck.com` (no `https://`). This covers http/https and www/non-www. Domain properties require a DNS TXT record in GoDaddy.
  3. Copy the TXT record Google gives you into GoDaddy DNS for `@`, wait for it to resolve, then click Verify.
  4. After verification, open **Sitemaps** and submit `https://calidoorcheck.com/sitemap.xml`.
  5. Use **URL Inspection** on the homepage and the three live guides, then request indexing if they are not already in the index.
- **Why first:** This is how Google Search (and later AI answers that cite the open web) discover and monitor the site. It also unlocks the fastest path into Bing (import).

### 2. Bing Webmaster Tools

- **Submission page:** https://www.bing.com/webmasters  
  Add/verify help: https://www2.bing.com/webmasters/help/add-and-verify-site-12184f8b
- **Account needed:** Yes (Microsoft, Google, or Facebook login).
- **What to enter:**
  1. Fastest path: use **Import from Google Search Console** after step 1 is verified.
  2. Or add `https://calidoorcheck.com` manually and verify by DNS, `BingSiteAuth.xml` at the site root, or a meta tag.
  3. Submit the same sitemap: `https://calidoorcheck.com/sitemap.xml`.
- **Note:** DuckDuckGo does not have a separate webmaster tool; it relies heavily on Bing's index, so Bing coverage helps there too.

### 3. IndexNow (notify Bing and other participating engines of new pages)

- **Get started:** https://www.bing.com/indexnow/getstarted  
  Protocol docs: https://www.indexnow.org/documentation  
  Shared API endpoint: `https://api.indexnow.org/indexnow`
- **Account needed:** A Bing Webmaster Tools property is the practical way to generate the key and later check that submissions were received. The protocol itself is a hosted key file plus an HTTP request.
- **What to enter / do:**
  1. Generate an IndexNow API key (8–128 letters, digits, or hyphens) on Bing's get-started page.
  2. Host a UTF-8 text file at `https://calidoorcheck.com/{key}.txt` whose contents are exactly that key. This requires a small site change (approval first).
  3. After each nightly new page (and after rebuilds), POST the new or updated URLs as JSON to `https://api.indexnow.org/indexnow` with `host`, `key`, `keyLocation`, and `urlList`.
  4. Monitor submissions under the IndexNow tab in Bing Webmaster Tools.
- **Limits:** A 200 response means "received," not "indexed." Google is not an IndexNow participant (as of November 2026 documentation). Do not resubmit unchanged URLs in a tight loop. Only submit URLs that changed after you start using the protocol.

### 4. Claim social handles (same day, before someone else does)

Create the accounts. Do not publish posts until the draft calendar in `x_posts.md` and `plan.md` is approved.

| Platform | Handle / URL to check | Status as of Nov 23, 2026 | Where to create | What to enter |
|---|---|---|---|---|
| X | [@calidoorcheck](https://x.com/calidoorcheck) | **Available** (X user lookup returned not found) | https://x.com/i/flow/signup (or convert a new account) | Name: CaliDoorCheck. Bio: "Verify before you call. Free directory of CSLB D-28 licensed garage door contractors in SoCal. Built from public license data." Website: https://calidoorcheck.com Location: Southern California |
| X (reserve) | @fairdoorla, @socaldoorcheck, @cadoorcheck, @calidoor, @caligaragedoor, @garagedoorcheck | **Available** (same lookup) | Same | Optional redirects/reserves. Not required. |
| X (taken, do not squat) | @DoorCheck | Taken — DoorCheck Ltd, Essex, UK fire-door inspectors | — | Unrelated business. Do not impersonate. |
| X (taken) | @calidoors | Taken — Cali Doors & Windows, San Diego | — | Unrelated local business. Leave it alone. |
| X (yours) | [@yaro360](https://x.com/yaro360) | Taken — your existing account | Already connected to Buffer | Fine to mention CaliDoorCheck occasionally; better to post daily tips from @calidoorcheck once it exists. |
| YouTube | https://www.youtube.com/@calidoorcheck | **Appears available** (public URL returned 404) | https://www.youtube.com/create_channel | Channel name CaliDoorCheck; same bio and site URL. No need to upload a video on day one. |
| LinkedIn Company | https://www.linkedin.com/company/calidoorcheck | **Appears available** (public company URL returned 404) | https://www.linkedin.com/company/setup/new | Company: CaliDoorCheck. Website: https://calidoorcheck.com. Industry: Internet / Consumer services or Information services. Company size: self / 1. HQ: Los Angeles, California. About: use the listing copy above. |
| Bluesky | https://bsky.app/profile/calidoorcheck.bsky.social | **Appears available** (public profile returned 404) | https://bsky.app | Handle `calidoorcheck.bsky.social`; same bio and site URL. Optional, lower priority than X. |
| Instagram | instagram.com/calidoorcheck | **Unconfirmed** (login wall; no public search hit for an exact @calidoorcheck, but that is not proof it is free) | Instagram app or https://www.instagram.com/accounts/emailsignup/ | Check the handle in the app before creating. Same bio and site URL. Business or Creator account once it exists. |
| Facebook Page | facebook.com/calidoorcheck | **Unconfirmed** (redirected to login) | https://www.facebook.com/pages/create | Page name: CaliDoorCheck. Category: Website or Community. About and website as above. Do not create this as a "garage door contractor" page. |
| Pinterest | pinterest.com/calidoorcheck | **Unconfirmed** (the site returns a generic 200) | https://www.pinterest.com/business/create/ | Business account; website https://calidoorcheck.com; pin the three live guides and city pages with sourced captions, not stock "hire us" ads. |
| TikTok | tiktok.com/@calidoorcheck | **Unconfirmed** | TikTok app | Check the handle in the app. Optional. Short license-check tips only, if you later want video. |
| Threads | threads.net/@calidoorcheck | **Unconfirmed** (tied to Instagram) | After Instagram exists | Same handle if available. |
| Nextdoor Business | Nextdoor business signup | **Unconfirmed** (pages are not reliably public) | https://business.nextdoor.com/ or https://nextdoor.com/for_business/ | Claim a business page for CaliDoorCheck as an online resource, not as a garage-door contractor. Use a real business mailing address. Do not mass-post the same promo in every neighborhood. |
| YouTube / LinkedIn / Bluesky caveats | — | 404s are a strong signal the exact slug is free, not a legal guarantee. Recheck at create time. | — | If a handle is taken, add a word (e.g. calidoorcheckca) rather than impersonating the other account. |

**Profile photo and tab icon:** use the same logo and favicon once those assets are approved. Until then, do not publish half-branded profiles.

---

## Priority 2 — legitimate directories and profiles

### 5. Crunchbase organization profile

- **Add form:** https://www.crunchbase.com/add-new  
  Official help: https://support.crunchbase.com/hc/en-us/articles/115011823988-How-do-I-create-a-Crunchbase-profile
- **Account needed:** Yes. Crunchbase requires a registered, socially authenticated user. Search first to confirm no CaliDoorCheck profile already exists.
- **What to enter:** Organization name CaliDoorCheck; website https://calidoorcheck.com; description = listing copy above; categories such as Information Services / Internet / Consumer; headquarters Los Angeles, California; founded 2026; operating status Active. Do not invent funding, employee counts, or traction metrics. Submit and wait for review.

### 6. Curlie (human-edited successor to DMOZ)

- **How to suggest:** https://curlie.org/docs/en/help/submit.html  
  You suggest a URL from inside a relevant category page, not from a generic dump form. Start by finding the closest category, for example under Regional / North America / United States / California, or a consumer / home-improvement category that actually fits.
- **Account needed:** A Curlie account is typically required to suggest. Editorial review is slow and may decline the site. That is expected.
- **What to enter:** Title: CaliDoorCheck. URL: https://calidoorcheck.com. Short objective description (the listing copy, trimmed). No superlatives.

### 7. Better Business Bureau business profile (optional, trust not SEO)

- **Start:** https://www.bbb.org/get-listed or the BBB of Los Angeles & Silicon Valley site.
- **Account needed:** Yes. You will need a real legal business name (YCO Productions or the entity that owns the domain) and a real business mailing address.
- **What to enter:** This is a website/consumer-information service, not a garage door contractor. Do not pick a contractor category. Do not claim BBB accreditation until it is granted. The BBB of LA was quoted in ABC7's September 21, 2026 garage-door story, so a truthful profile can help later press and company outreach, but it is not required to launch.

### 8. Google Business Profile and Bing Places — use caution, or skip

- **Google:** https://business.google.com/create (or https://www.google.com/business/)  
- **Bing Places:** https://www.bing.com/forbusiness  
- **Apple Business Connect:** https://businessconnect.apple.com/
- **Account needed:** Yes.
- **Why this is not Priority 1:** CaliDoorCheck is an online information directory, not a storefront and not a garage door company. Creating a Maps pin or a "Garage Door Supplier" category would be misleading and can get the profile suspended. If you later want a profile, use an accurate category such as Website or Internet service, do not invent a public office, and do not collect reviews as if you perform repairs. Search Console is the correct Google property for this site.

### 9. Yandex Webmaster (optional, low SoCal traffic)

- **Docs:** https://yandex.com/support/webmaster/en/service/quick-start  
  Tool: https://webmaster.yandex.com/
- **Account needed:** Yes (Yandex ID).
- **What to enter:** Add `https://calidoorcheck.com`, verify, submit the sitemap. Useful completeness, not a SoCal growth lever.

---

## Priority 3 — startup and product directories (only where a consumer directory fits)

These are optional. A consumer-protection license directory is not a typical "SaaS launch," so be honest in the tagline and do not force a fit.

### 10. Product Hunt

- **How to post (official):** https://help.producthunt.com/en/articles/479557-how-to-post-a-product  
  Build-your-page guide: https://help.producthunt.com/en/articles/17834537-4-build-your-product-page  
  Common editor URL after login: https://www.producthunt.com/posts/new
- **Account needed:** Yes, a personal "maker" account. Launches are scheduled and reviewed.
- **Fit:** Borderline but defensible if positioned as a free public-data consumer tool, not as "AI for contractors."
- **What to enter:** Name CaliDoorCheck. Tagline: "Verify a SoCal garage door company's California license before you call." Link: https://calidoorcheck.com. Description = listing copy. Topics such as Home, Productivity, or Civic tech if those are offered — pick only what is accurate. Screenshots of the homepage, a city page, and the license-check guide (no fake reviews). First comment should explain the CSLB data source and what the site does not do (no paid ranking today; future paid spots will be labeled Sponsored). Do not run a fake-upvote campaign.

### 11. BetaList

- **Submission page:** https://betalist.com/submissions/new
- **Account needed:** The form says they create an account on the spot (or email a login code).
- **Fit:** Early-stage consumer site; weak compared with a typical startup launch.
- **Cost warning:** Confirm the fee on the form before submitting. A November 2026 secondary source said BetaList now charges for submissions (refunded if not selected). Treat it as possibly paid until you see the current form. Do not pay without approval.

### 12. Indie Hackers product page

- **Site:** https://www.indiehackers.com/  
  Add a product or milestone after creating an account.
- **Account needed:** Yes.
- **What to enter:** Same honest description. This is a community profile, not a major referral source. Do not spam the forums.

### 13. Uneed (optional)

- **Help:** https://help.uneed.best/getting-started/how-to-submit-your-first-product  
  Product site: https://uneed.best/
- **Account needed:** You can start a submission without an account, per their help center; confirm on the form.
- **Fit:** Weak. Uneed skews product/SaaS/AI tools. Only submit if the categories clearly include a public-data or consumer directory. Skip if you would have to stretch the pitch.

### 14. AlternativeTo (optional, weak fit)

- **Site:** https://alternativeto.net/
- **Account needed:** Yes, to suggest software.
- **Fit:** Poor. CaliDoorCheck is not really an "alternative" to Angi or Yelp in their software taxonomy. Low priority.

---

## Link-earning targets (pitch, do not spray)

These can produce the kind of links and mentions that actually help SEO and AEO. Drafts only; no emails have been sent. Use official tip/contact channels. I did **not** verify personal reporter emails, so none are listed here.

### Consumer and investigative desks

| Outlet | Why they fit | Public contact to use | Do not claim |
|---|---|---|---|
| ABC7 Los Angeles, 7 On Your Side (Leanne Suter reported the Sept 21, 2026 garage-door overcharging story) | Direct follow-up to a story they already aired | News tip form: https://abc7.com/post/submit-los-angeles-southern-california-news-tips-abc7-abc7eyewitness/27721/ — Press/story email listed on the station contact page: pr@abc7.com — Station contact page: https://abc7.com/post/contact-abc7-los-angeles/50737/ | A personal email or cell for Leanne Suter (not published on the official contact page) |
| NBC4 Los Angeles I-Team / consumer | SoCal consumer investigations | Consumer complaint/tip form: https://www.nbclosangeles.com/consumer-form/ — Tip page: https://www.nbclosangeles.com/investigations/submit-tip/ | A personal producer email unless they publish one on that form |
| CBS News Los Angeles (Kristine Lazar is listed as a consumer investigative reporter on the CBS team page) | Consumer investigations | Use the official CBS News Los Angeles contact/tips path from https://www.cbsnews.com/losangeles/ — Lazar's public bio: https://www.cbsnews.com/team/kristine-lazar/ | A personal email I have not verified |
| KTLA (David Lazarus covers business and consumer news; public author page: https://ktla.com/author/david-lazarus/) | Consumer columnist now at KTLA | Use KTLA's official newsroom contact/tips page; do not scrape personal addresses | A personal Lazarus email |

Full pitch text is in `press_pitch.md`.

### CSLB consumer outreach

CSLB is the data source and the consumer-protection agency. A partnership or "here's a public tool built on your official list" note is appropriate. Do not imply CSLB endorses the site.

- Public Affairs Office (media inquiries only), published at https://www.cslb.ca.gov/About_us/Public_Affairs_Office.aspx:
  - Katherine White, Chief of Public Affairs, (916) 255-4143, Katherine.White@cslb.ca.gov
  - David Gower, Public Affairs Supervisor, (916) 255-4717, David.Gower@cslb.ca.gov
  - Natalie Watmore, Public Information Officer, (916) 255-3915, Natalie.Watmore@cslb.ca.gov
- General public questions: Public Information Center, (800) 321-CSLB (2752), via https://www.cslb.ca.gov/About_us/Contact_CSLB.aspx
- Complaints are a different channel and are not for pitching a website.
- Consumer education / Senior Scam Stopper programming is listed from the Media Room: https://www.cslb.ca.gov/Media_Room/ — a factual "you may want to know this free directory exists for D-28 in six SoCal counties" note could be relevant to outreach staff, sent only through the published contacts and clearly not a complaint.

### Neighborhood and local news (story ideas, not directory spam)

Use each site's public contact, tip, or "submit a story" form. I did not verify personal reporter inboxes, so pitch through those official channels. Angle: "after the ABC7 garage-door scam story, here's a free way neighbors can check a D-28 license in [this city]."

| Outlet | Coverage | Start here |
|---|---|---|
| LAist | LA public radio / local news | Official contact or tip path on laist.com (use the site's published contact page; do not invent an address) |
| The Eastsider | Eastside LA neighborhoods | https://www.theeastsiderla.com/ — the site invites readers to submit a tip, story idea, or suggestion via its published contact/support links |
| Long Beach Post | Long Beach | https://lbpost.com/ |
| Pasadena Now / local Pasadena press | Pasadena, Altadena, nearby | Publisher contact pages on pasadenanow.com or similar local titles |
| Westside Current | Westside LA | Publisher contact page |
| Larchmont Buzz | Larchmont / mid-Wilshire | Publisher contact page |
| Santa Monica local press (Lookout / Next, as available) | Santa Monica | Publisher contact page |
| Daily Breeze | South Bay | Official tips/contact |
| OC Register | Orange County | Official tips/contact |
| San Diego Union-Tribune | San Diego County | Official tips/contact |
| Ventura County Star | Ventura County | Official tips/contact |
| BBB of Los Angeles & Silicon Valley | Already quoted in the ABC7 story | Use the BBB's official media/contact path; a "we built a free D-28 license check for the same problem you described" note is reasonable, not a demand for a link |

---

## Places and tactics to AVOID

These tend to be link farms, paid-link schemes, or low-quality directories that can hurt search quality and trust. Do not submit CaliDoorCheck there, and do not buy "we'll list you in 500 directories" gigs.

- Mass "SEO directory submission" packages (Fiverr, Upwork, or email blasts promising hundreds of listings).
- Classic link-farm / free-for-all directories such as Hotfrog, Brownbook, Cylex, Tupalo, Yasabe, and look-alikes that accept any URL for a reciprocal or paid dofollow link with no editorial standard.
- SubmitExpress, AddMe, ExactSeek-style "submit to 1,000 search engines" services.
- Private blog networks, guest-post marketplaces sold as "DA30 contextual links," and paid link inserts.
- Low-quality press-release mills whose only output is syndicated spam (examples of this pattern already show up in garage-door related X search). A real desk pitch is fine; a $99 "distribution" that lands on scraper sites is not.
- Wikipedia or wiki spam, blog-comment spam, forum-profile spam, and fake Q&A answers.
- Fake Google, Yelp, or BBB reviews, invented testimonials, or fabricated "as seen in" logos.
- Creating a Google Maps or Yelp listing that pretends CaliDoorCheck is a garage door contractor.
- Impersonating CSLB, ABC7, or the BBB, or using their logos in a way that implies endorsement.

---

## Suggested one-line descriptions by length

- **Tagline (already on the site):** Verify before you call.
- **Short (under 120 characters):** Free directory of CSLB D-28 licensed garage door contractors in six Southern California counties.
- **Medium:** CaliDoorCheck lists currently renewed California D-28 garage door licenses from official CSLB public data, plus sourced guides on license checks, scams, and spring-replacement prices.
