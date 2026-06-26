# How to Add a New Article

## 1. Create the article file

Create a new `.md` file in `src/articles/` with this template:

```markdown
---
layout: article.njk
title: "Your Article Title Here"
description: "One-sentence meta description (150 chars max). Should include the target keyword."
category: home-office
date: 2026-07-01
readTime: 8
permalink: /articles/your-article-slug/index.html
---

Your article body in Markdown goes here.

Use ## for H2 headings, ### for H3, etc.

For Amazon affiliate links, use this format:
[Check price on Amazon →](YOUR_AMAZON_AFFILIATE_URL){rel="nofollow sponsored" target="_blank"}
```

### Available categories
- `home-office` — Standing desks, chairs, monitor arms, keyboards, webcams
- `luxury-beauty` — Skincare, serums, luxury cosmetics  
- `fitness` — Dumbbells, resistance equipment, fitness accessories
- `kitchen` — Air fryers, instant pots, kitchen gadgets
- `pet-tech` — GPS trackers, smart feeders, pet accessories

### Naming the file
Use lowercase kebab-case: `best-standing-desks-2026.md`

## 2. Get the real Amazon affiliate link

Replace `{{AMAZON_LINK_*}}` placeholders once your Associates account is confirmed active:

1. Log into Amazon Associates dashboard
2. Search for the product
3. Use the "Get Link" tool to generate your affiliate URL
4. Replace the placeholder in the article file

## 3. Build and preview locally

```bash
npm run serve
# Opens browser preview at http://localhost:8080
```

## 4. Deploy

**GitHub Pages (recommended):**
```bash
git add src/articles/your-new-article.md
git commit -m "Add article: Your Article Title"
git push origin main
# GitHub Actions builds and deploys automatically (~2 minutes)
```

**Netlify:**
- Drag the `_site/` folder to https://app.netlify.com/drop
- Or connect the GitHub repo for auto-deploy on push

## 5. Submit to Google Search Console

After deploying a new article:
1. Log into Google Search Console
2. Paste the article URL in the inspection tool
3. Click "Request Indexing"

## Article quality checklist

- [ ] Title includes the target keyword
- [ ] Meta description is 150 chars or less and includes the keyword
- [ ] Article starts with FTC affiliate disclosure (handled automatically by the template)
- [ ] Amazon links use `rel="nofollow sponsored"`
- [ ] Article has a clear H1 (the `title` frontmatter field)
- [ ] At least one H2 subheading every 300 words
- [ ] Article is 800+ words for SEO weight

## Site configuration

Edit `src/_data/site.json` to update the site name, domain URL, or category list.

**⚠️ When you change the domain:** Update `siteUrl` in `src/_data/site.json` to your actual domain. This updates canonical URLs, sitemap.xml, and robots.txt automatically.
