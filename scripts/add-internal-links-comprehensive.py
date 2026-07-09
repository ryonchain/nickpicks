#!/usr/bin/env python3
"""
Comprehensive internal linking pass — adds Related Guides to all articles
that don't already have them. Covers all categories, not just the top 10.
"""

import os
import re
import sys

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


# Broad normalization — map everything to a canonical bucket
CAT_NORM = {
    # Home Office / Desk
    'home office': 'home-office',
    'home-office': 'home-office',
    '"home office"': 'home-office',
    'desk-productivity': 'home-office',
    'computers & accessories': 'home-office',
    '"computers & accessories"': 'home-office',
    'electronics': 'tech',
    '"electronics"': 'tech',
    'tech': 'tech',
    'tech-accessories': 'tech',
    'tech accessories': 'tech',
    'smart home & tech': 'smart-home',
    'smart home & security': 'smart-home',
    '"smart home security"': 'smart-home',
    'smart home security': 'smart-home',
    '"smart home & tech"': 'smart-home',
    '"smart home & security"': 'smart-home',
    '"smart home"': 'smart-home',
    'smart home': 'smart-home',
    'smart-home': 'smart-home',
    # Kitchen
    'kitchen': 'kitchen',
    '"kitchen"': 'kitchen',
    'kitchen & dining': 'kitchen',
    'kitchen & housewares': 'kitchen',
    '"kitchen & dining"': 'kitchen',
    '"kitchen & housewares"': 'kitchen',
    'kitchen & housewares': 'kitchen',
    'kitchen-appliances': 'kitchen',
    'kitchen-coffee': 'kitchen',
    'kitchen-entertainment': 'kitchen',
    'home & kitchen': 'kitchen',
    'coffee': 'kitchen',
    # Fitness / Health
    'fitness': 'fitness',
    '"fitness"': 'fitness',
    'fitness & outdoors': 'fitness',
    '"fitness & outdoors"': 'fitness',
    'fitness-home-gym': 'fitness',
    'health & wellness': 'fitness',
    '"health & wellness"': 'fitness',
    'health-wellness': 'fitness',
    'health & beauty': 'beauty',
    'health': 'fitness',
    '"health"': 'fitness',
    'health-home': 'fitness',
    'wellness': 'fitness',
    # Beauty / Grooming
    'luxury beauty': 'luxury-beauty',
    'luxury-beauty': 'luxury-beauty',
    '"luxury beauty"': 'luxury-beauty',
    'beauty': 'beauty',
    '"beauty"': 'beauty',
    'beauty-hair': 'beauty',
    'personal care': 'beauty',
    '"personal care"': 'beauty',
    'grooming': 'beauty',
    '"grooming"': 'beauty',
    'mens-grooming': 'beauty',
    # Outdoor / Sports
    'sports & outdoors': 'outdoor',
    '"sports & outdoors"': 'outdoor',
    'outdoor': 'outdoor',
    'outdoor-camping': 'outdoor',
    'outdoor-grilling': 'outdoor',
    'outdoor-recreation': 'outdoor',
    'outdoor-sports': 'outdoor',
    'outdoor-wellness': 'outdoor',
    'outdoor-cooking': 'outdoor',
    'outdoor-fishing': 'outdoor',
    'outdoor-footwear': 'outdoor',
    'outdoor-pool': 'outdoor',
    'outdoor-transportation': 'outdoor',
    'outdoor-emergency': 'outdoor',
    'garden-outdoor': 'outdoor',
    'garden': 'outdoor',
    # Home / Cleaning
    'home': 'home',
    '"home"': 'home',
    'home & garden': 'home',
    'home & health': 'home',
    'home-improvement': 'home',
    'home-organization': 'home',
    'home-cleaning': 'home',
    'home-security': 'home',
    'home-outdoor': 'home',
    'home-bedroom': 'home',
    '"home theater"': 'home',
    'home theater': 'home',
    'furniture-home': 'home',
    'bedroom': 'home',
    'bathroom': 'home',
    # Pets
    'pet-tech': 'pets',
    'pet supplies': 'pets',
    '"pet supplies"': 'pets',
    'pets': 'pets',
    # Audio
    'audio-tech': 'audio',
    'audio tech': 'audio',
    '"audio"': 'audio',
    'audio': 'audio',
    # Tools
    'tools-hardware': 'tools',
    'tools & home improvement': 'tools',
    '"tools & home improvement"': 'tools',
    'tools': 'tools',
    'business & industrial': 'tools',
    '"business & industrial"': 'tools',
    # Baby / Family
    'baby & parenting': 'baby',
    '"baby & parenting"': 'baby',
    'baby & kids': 'baby',
    '"baby & kids"': 'baby',
    'baby': 'baby',
    'kids & education': 'baby',
    '"kids & education"': 'baby',
    # Fashion / Accessories
    'fashion-accessories': 'fashion',
    'fashion': 'fashion',
    '"fashion"': 'fashion',
    'watches': 'fashion',
    '"watches"': 'fashion',
    # Gaming / Recreation
    'recreation-games': 'gaming',
    'gaming': 'gaming',
    # Travel
    'travel': 'travel',
    # Automotive
    'automotive': 'automotive',
    # Music
    'musical instruments': 'music',
    '"musical instruments"': 'music',
}

# Related-category fallback: if a category has too few articles, fall back to these broader groups
CATEGORY_GROUPS = {
    'luxury-beauty': ['luxury-beauty', 'beauty'],
    'beauty': ['beauty', 'luxury-beauty'],
    'fitness': ['fitness', 'outdoor'],
    'outdoor': ['outdoor', 'fitness'],
    'home': ['home', 'home-office', 'kitchen'],
    'home-office': ['home-office', 'tech', 'home'],
    'tech': ['tech', 'home-office', 'smart-home'],
    'smart-home': ['smart-home', 'tech', 'home'],
    'tools': ['tools', 'home', 'outdoor'],
    'gaming': ['gaming', 'tech'],
    'travel': ['travel', 'outdoor'],
    'music': ['music', 'tech'],
    'automotive': ['automotive', 'outdoor'],
    'fashion': ['fashion'],
    'baby': ['baby'],
    'pets': ['pets'],
    'audio': ['audio', 'tech'],
    'kitchen': ['kitchen', 'home'],
}


def normalize_category(cat):
    cat_lower = cat.lower().strip()
    return CAT_NORM.get(cat_lower, cat_lower)


def load_articles():
    articles = []
    for f in sorted(os.listdir(ARTICLES_DIR)):
        if not f.endswith('.md'):
            continue
        slug = f[:-3]
        filepath = os.path.join(ARTICLES_DIR, f)
        with open(filepath) as fh:
            content = fh.read()
        fm, _ = parse_frontmatter(content)
        has_related = 'Related Guides:' in content or 'Related guides:' in content or '## Related Guides' in content or '## Related guides' in content
        articles.append({
            'slug': slug,
            'title': fm.get('title', slug),
            'category': normalize_category(fm.get('category', 'unknown')),
            'has_related': has_related,
            'filepath': filepath,
            'content': content,
        })
    return articles


def get_display_title(title):
    return title.strip('"\'')


def pick_related(article, cat_index, count=3):
    """Pick related articles from the same or related categories, randomizing position."""
    groups = CATEGORY_GROUPS.get(article['category'], [article['category']])
    candidates = []
    for grp in groups:
        for a in cat_index.get(grp, []):
            if a['slug'] != article['slug']:
                candidates.append(a)

    if not candidates:
        return []

    # De-duplicate by slug
    seen = set()
    unique = []
    for c in candidates:
        if c['slug'] not in seen:
            seen.add(c['slug'])
            unique.append(c)

    # Prefer articles that already have related guides (higher-quality articles)
    with_related = [a for a in unique if a['has_related']]
    without_related = [a for a in unique if not a['has_related']]

    # Use a deterministic but spread-out selection: pick from different positions
    slug_hash = sum(ord(c) for c in article['slug'])

    selected = []
    pool = with_related if len(with_related) >= count else with_related + without_related
    if len(pool) >= count:
        # Use slug hash to offset selection, giving variety
        offset = slug_hash % max(1, len(pool) - count)
        selected = pool[offset:offset + count]
        if len(selected) < count:
            selected = pool[:count]
    else:
        selected = pool[:count]

    return selected[:count]


def format_related_guides(related):
    parts = []
    for a in related:
        title = get_display_title(a['title'])
        parts.append(f'[{title}](/articles/{a["slug"]}/)')
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
    articles = load_articles()
    print(f"Loaded {len(articles)} articles")

    without = [a for a in articles if not a['has_related']]
    print(f"Articles without related guides: {len(without)}")

    # Build category index (all articles, not just those without)
    cat_index = {}
    for a in articles:
        c = a['category']
        if c not in cat_index:
            cat_index[c] = []
        cat_index[c].append(a)

    # Print category distribution for articles needing updates
    cats = {}
    for a in without:
        cats[a['category']] = cats.get(a['category'], 0) + 1
    print("\nCategories needing updates:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    updated = []
    skipped = []

    for article in without:
        related = pick_related(article, cat_index, count=3)
        if len(related) < 2:
            print(f"  SKIP {article['slug']} ({article['category']}) — only {len(related)} related articles found")
            skipped.append(article['slug'])
            continue
        add_related_to_article(article, related)
        print(f"  ✓ {article['slug']} [{article['category']}]")
        for r in related:
            print(f"      → {r['slug']}")
        updated.append(article['slug'])

    print(f"\nUpdated: {len(updated)}")
    print(f"Skipped: {len(skipped)}")
    return updated


if __name__ == '__main__':
    updated = main()
    print(f"\nTotal articles updated: {len(updated)}")
    if len(updated) == 0:
        print("WARNING: No articles updated")
        sys.exit(1)
    sys.exit(0)
