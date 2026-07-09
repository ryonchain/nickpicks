#!/usr/bin/env python3
"""Fix related guides for 'unknown' category articles that got wrong cross-cluster links."""

import os, re

ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "articles")
all_slugs = {f[:-3] for f in os.listdir(ARTICLES_DIR) if f.endswith('.md')}

def read_title(slug):
    path = os.path.join(ARTICLES_DIR, slug + '.md')
    try:
        with open(path) as f:
            for line in f:
                if line.startswith('title:'):
                    return line.split(':', 1)[1].strip().strip('"\'')
    except FileNotFoundError:
        return slug
    return slug

def make_related_line(links):
    parts = [f'[{title}](/articles/{slug}/)' for slug, title in links]
    return '**Related Guides:** ' + ' · '.join(parts)

# Targeted link plan: source_slug -> [(target_slug, display_title)]
LINK_PLAN = {
    # Baby articles — link to other baby articles
    'best-baby-carrier-newborn-2026': [
        ('best-baby-monitors-new-parents-2026', 'Best Baby Monitors for New Parents'),
        ('best-baby-strollers-2026', 'Best Baby Strollers'),
        ('best-baby-swing-bouncer-2026', 'Best Baby Swings & Bouncers'),
    ],
    'best-baby-monitor-with-camera-2026': [
        ('best-baby-monitors-2026', 'Best Baby Monitors'),
        ('best-baby-monitors-with-video-2026', 'Best Baby Monitors with Video'),
        ('best-baby-monitors-new-parents-2026', 'Best Baby Monitors for New Parents'),
    ],
    'best-baby-swing-bouncer-2026': [
        ('best-baby-carrier-newborn-2026', 'Best Baby Carriers for Newborns'),
        ('best-baby-monitors-new-parents-2026', 'Best Baby Monitors for New Parents'),
        ('best-baby-strollers-2026', 'Best Baby Strollers'),
    ],
    'best-baby-white-noise-machine-2026': [
        ('best-baby-monitors-new-parents-2026', 'Best Baby Monitors for New Parents'),
        ('best-baby-carrier-newborn-2026', 'Best Baby Carriers for Newborns'),
        ('best-air-purifiers-bedroom-2026', 'Best Air Purifiers for Bedrooms'),
    ],
    'best-diaper-bag-backpack-2026': [
        ('best-baby-carrier-newborn-2026', 'Best Baby Carriers for Newborns'),
        ('best-baby-monitors-new-parents-2026', 'Best Baby Monitors for New Parents'),
        ('best-baby-strollers-2026', 'Best Baby Strollers'),
    ],
    # Kitchen articles
    'best-espresso-machine-home-2026': [
        ('best-espresso-machines-2026', 'Best Espresso Machines'),
        ('best-espresso-machines-home-2026', 'Best Espresso Machines for Home'),
        ('best-coffee-makers-home-brewers-2026', 'Best Coffee Makers & Home Brewers'),
    ],
    'best-stand-mixer-home-baking-2026': [
        ('best-stand-mixers-2026', 'Best Stand Mixers'),
        ('best-air-fryers-2026', 'Best Air Fryers'),
        ('best-instant-pot-electric-pressure-cookers-2026', 'Best Instant Pots & Electric Pressure Cookers'),
    ],
    # Luxury beauty / skincare articles
    'best-luxury-face-cream-anti-aging-2026': [
        ('best-anti-aging-face-creams-2026', 'Best Anti-Aging Face Creams'),
        ('best-luxury-face-serums-2026', 'Best Luxury Face Serums'),
        ('best-anti-aging-night-creams-2026', 'Best Anti-Aging Night Creams'),
    ],
    'best-luxury-perfume-women-2026': [
        ('best-luxury-perfumes-women-2026', 'Best Luxury Perfumes for Women'),
        ('best-womens-perfume-gift-sets-2026', "Best Women's Perfume Gift Sets"),
        ('best-luxury-body-lotions-2026', 'Best Luxury Body Lotions'),
    ],
    'best-luxury-skincare-serum-vitamin-c-2026': [
        ('best-luxury-face-serums-2026', 'Best Luxury Face Serums'),
        ('best-anti-aging-face-creams-2026', 'Best Anti-Aging Face Creams'),
        ('best-luxury-bath-gift-sets-2026', 'Best Luxury Bath Gift Sets'),
    ],
    # Watches / fashion
    'best-luxury-watches-men-under-1000-2026': [
        ('best-mens-dress-watches-under-500-2026', "Best Men's Dress Watches Under $500"),
        ('best-minimalist-watches-men-2026', 'Best Minimalist Watches for Men'),
        ('best-leather-wallets-men-2026', "Best Leather Wallets for Men"),
    ],
    'best-luxury-handbag-under-500-2026': [
        ('best-premium-sunglasses-2026', 'Best Premium Sunglasses'),
        ('best-leather-wallets-men-2026', 'Best Leather Wallets for Men'),
        ('best-luxury-perfumes-women-2026', 'Best Luxury Perfumes for Women'),
    ],
}

print("Fixing 'unknown' category article links...")
updated = 0
for source_slug, targets in LINK_PLAN.items():
    valid_targets = [(s, t) for s, t in targets if s in all_slugs]
    if len(valid_targets) < 2:
        print(f"  SKIP {source_slug}: only {len(valid_targets)} valid targets")
        continue

    filepath = os.path.join(ARTICLES_DIR, source_slug + '.md')
    if not os.path.exists(filepath):
        print(f"  MISSING: {source_slug}")
        continue

    with open(filepath) as f:
        content = f.read()

    # Remove existing Related Guides line
    content = re.sub(r'\n\*\*Related Guides:\*\*[^\n]*\n?', '', content)

    new_line = '\n' + make_related_line(valid_targets) + '\n'
    new_content = content.rstrip('\n') + '\n' + new_line

    with open(filepath, 'w') as f:
        f.write(new_content)

    print(f"  ✓ {source_slug}")
    for s, t in valid_targets:
        print(f"      → {s}")
    updated += 1

print(f"\nFixed {updated} articles with targeted links.")
