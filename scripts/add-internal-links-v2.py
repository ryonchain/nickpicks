#!/usr/bin/env python3
"""
Add internal links (Related Guides) to all remaining NickPicks articles.
Handles all categories including niche ones: mens-grooming, travel, luxury-beauty,
smart-home variants, coffee, tools, baby, watches, fashion, musical instruments, etc.
"""

import os
import re

ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "articles")


def parse_frontmatter(content):
    if not content.startswith('---'):
        return {}, content
    end = content.find('---', 3)
    if end == -1:
        return {}, content
    fm_text = content[3:end].strip()
    result = {}
    for line in fm_text.split('\n'):
        if ':' in line and not line.startswith(' ') and not line.startswith('-'):
            key, _, val = line.partition(':')
            result[key.strip()] = val.strip().strip('"\'')
    return result, content[end+3:]


# Comprehensive category normalization — covers lowercase, title-case, and hyphenated variants
CAT_NORM = {
    # kitchen
    'kitchen': 'kitchen', 'kitchen & dining': 'kitchen', 'home & kitchen': 'kitchen',
    'kitchen & housewares': 'kitchen', 'kitchen-appliances': 'kitchen',
    'kitchen-coffee': 'kitchen', 'kitchen-entertainment': 'kitchen',
    # coffee (keep as own cluster with enough articles)
    'coffee': 'coffee',
    # fitness
    'fitness': 'fitness', 'fitness & outdoors': 'fitness', 'health & wellness': 'fitness',
    'health-wellness': 'fitness', 'health': 'fitness', 'fitness-home-gym': 'fitness',
    'home office fitness': 'fitness',
    # home-office
    'home office': 'home-office', 'home-office': 'home-office', 'desk-productivity': 'home-office',
    # smart-home (all spellings)
    'smart home': 'smart-home', 'smart-home': 'smart-home', 'smart home & tech': 'smart-home',
    'smart home & security': 'smart-home', 'smart home security': 'smart-home',
    'Smart Home': 'smart-home',
    # home
    'home': 'home', 'home & garden': 'home', 'home-improvement': 'home',
    'furniture-home': 'home', 'home-cleaning': 'home', 'home-organization': 'home',
    'home-outdoor': 'home', 'home-security': 'home', 'home & health': 'home',
    'bedroom': 'home', 'bathroom': 'home', 'home theater': 'home',
    # beauty & grooming (combined for cross-linking)
    'beauty': 'beauty', 'health & beauty': 'beauty', 'personal care': 'beauty',
    'beauty-hair': 'beauty', 'grooming': 'beauty',
    # mens-grooming (large enough cluster to stand alone)
    'mens-grooming': 'mens-grooming',
    # luxury-beauty
    'luxury beauty': 'luxury-beauty', 'luxury-beauty': 'luxury-beauty',
    'Luxury Beauty': 'luxury-beauty',
    # outdoor
    'sports & outdoors': 'outdoor', 'outdoor-camping': 'outdoor', 'outdoor-grilling': 'outdoor',
    'outdoor-recreation': 'outdoor', 'outdoor-sports': 'outdoor', 'outdoor-wellness': 'outdoor',
    'outdoor-cooking': 'outdoor', 'outdoor-fishing': 'outdoor', 'outdoor-footwear': 'outdoor',
    'outdoor-pool': 'outdoor', 'garden-outdoor': 'outdoor', 'garden': 'outdoor',
    'outdoor-garden': 'outdoor', 'outdoor-transportation': 'outdoor', 'outdoor-emergency': 'outdoor',
    # travel
    'travel': 'travel',
    # pets
    'pet-tech': 'pets', 'pet supplies': 'pets', 'pets': 'pets',
    # tech / electronics
    'computers & accessories': 'tech', 'electronics': 'tech', 'tech': 'tech',
    'audio-tech': 'audio', 'audio tech': 'audio', 'audio': 'audio',
    # tools
    'tools-hardware': 'tools', 'tools & home improvement': 'tools',
    'Tools & Home Improvement': 'tools', 'business & industrial': 'tools',
    'Business & Industrial': 'tools',
    # baby
    'baby & parenting': 'baby', 'baby & kids': 'baby', 'kids & education': 'baby',
    'baby-parenting': 'baby', 'Baby & Kids': 'baby',
    # fashion / watches
    'fashion': 'fashion', 'Fashion': 'fashion',
    'watches': 'watches', 'Watches': 'watches',
    # music
    'musical instruments': 'music', 'Musical Instruments': 'music',
    # gaming
    'recreation-games': 'gaming',
}


def normalize_category(cat, niche=None):
    """Normalize category, falling back to niche if category is unknown."""
    c = cat.strip()
    if c in CAT_NORM:
        return CAT_NORM[c]
    cl = c.lower()
    if cl in CAT_NORM:
        return CAT_NORM[cl]
    # Fall back to niche
    if niche:
        n = niche.strip()
        if n in CAT_NORM:
            return CAT_NORM[n]
        nl = n.lower()
        if nl in CAT_NORM:
            return CAT_NORM[nl]
    return cl if cl else 'unknown'


def load_articles():
    articles = []
    all_slugs = set()
    for f in sorted(os.listdir(ARTICLES_DIR)):
        if not f.endswith('.md'):
            continue
        slug = f[:-3]
        all_slugs.add(slug)
        filepath = os.path.join(ARTICLES_DIR, f)
        with open(filepath) as fh:
            content = fh.read()
        fm, _ = parse_frontmatter(content)
        has_related = 'Related Guides:' in content or 'Related guides:' in content
        cat_raw = fm.get('category', '')
        niche_raw = fm.get('niche', '')
        cat = normalize_category(cat_raw, niche_raw)
        articles.append({
            'slug': slug,
            'title': fm.get('title', slug).strip('"\''),
            'category': cat,
            'has_related': has_related,
            'filepath': filepath,
            'content': content,
        })
    return articles, all_slugs


# Cross-category fallback groups — when a category has < 3 peers, expand to these
CROSS_CATEGORY_GROUPS = {
    'watches': ['watches', 'fashion'],
    'fashion': ['fashion', 'watches', 'luxury-beauty'],
    'music': ['music', 'gaming', 'tech'],
    'gaming': ['gaming', 'tech', 'music'],
    'tools': ['tools', 'home', 'outdoor'],
    'coffee': ['coffee', 'kitchen'],
    'audio': ['audio', 'tech', 'home-office'],
}


def pick_related(article, category_index, all_slugs, count=3):
    """Pick 3 related articles from the same or cross-linked category."""
    cat = article['category']
    # Get peers in same category
    candidates = [a for a in category_index.get(cat, [])
                  if a['slug'] != article['slug'] and a['slug'] in all_slugs]

    # If not enough, expand to cross-category group
    if len(candidates) < count and cat in CROSS_CATEGORY_GROUPS:
        for fallback_cat in CROSS_CATEGORY_GROUPS[cat]:
            if fallback_cat == cat:
                continue
            candidates += [a for a in category_index.get(fallback_cat, [])
                           if a['slug'] != article['slug']
                           and a['slug'] in all_slugs
                           and a not in candidates]
            if len(candidates) >= count:
                break

    # Prefer articles that already have related guides
    with_related = [a for a in candidates if a['has_related']]
    without_related = [a for a in candidates if not a['has_related']]
    selected = with_related[:count]
    if len(selected) < count:
        selected += without_related[:count - len(selected)]
    return selected[:count]


def format_related_guides(related):
    parts = [f'[{a["title"]}](/articles/{a["slug"]}/)' for a in related]
    return '**Related Guides:** ' + ' · '.join(parts)


def add_related_to_article(article, related):
    content = article['content']
    line = format_related_guides(related)
    if content.endswith('\n'):
        new_content = content + '\n' + line + '\n'
    else:
        new_content = content + '\n\n' + line + '\n'
    with open(article['filepath'], 'w') as fh:
        fh.write(new_content)
    return line


def main():
    articles, all_slugs = load_articles()
    print(f"Loaded {len(articles)} articles")

    # Build category index
    cat_index = {}
    for a in articles:
        c = a['category']
        cat_index.setdefault(c, []).append(a)

    # Print category sizes
    print("\nCategory sizes (articles with related guides / total):")
    for cat in sorted(cat_index.keys()):
        total = len(cat_index[cat])
        with_r = sum(1 for a in cat_index[cat] if a['has_related'])
        print(f"  {cat}: {with_r}/{total}")

    # Find all articles without related guides
    missing = [a for a in articles if not a['has_related']]
    print(f"\n{len(missing)} articles without Related Guides")

    updated = []
    skipped = []
    for article in missing:
        related = pick_related(article, cat_index, all_slugs, count=3)
        if len(related) < 2:
            print(f"  SKIP {article['slug']} (category={article['category']}, only {len(related)} peers)")
            skipped.append(article['slug'])
            continue
        add_related_to_article(article, related)
        print(f"  ✓ {article['slug']} [{article['category']}]")
        for r in related:
            print(f"      → {r['slug']}")
        updated.append(article['slug'])

    print(f"\nUpdated: {len(updated)}, Skipped: {len(skipped)}")
    if skipped:
        print("\nSkipped articles (need manual attention):")
        for s in skipped:
            print(f"  {s}")
    return updated, skipped


if __name__ == '__main__':
    updated, skipped = main()
