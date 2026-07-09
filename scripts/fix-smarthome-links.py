#!/usr/bin/env python3
"""Fix smart-home articles that got baby monitor / car phone mount links."""

import os, re

ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "articles")
all_slugs = {f[:-3] for f in os.listdir(ARTICLES_DIR) if f.endswith('.md')}

def make_related_line(links):
    parts = [f'[{title}](/articles/{slug}/)' for slug, title in links]
    return '**Related Guides:** ' + ' · '.join(parts)

# Smart-home articles with targeted relevant links
LINK_PLAN = {
    'best-smart-light-bulbs-2026': [
        ('best-smart-led-bulbs-2026', 'Best Smart LED Bulbs'),
        ('best-smart-plugs-2026', 'Best Smart Plugs'),
        ('best-smart-home-devices-2026', 'Best Smart Home Devices'),
    ],
    'best-smart-light-switches-no-neutral-wire-2026': [
        ('best-smart-led-bulbs-2026', 'Best Smart LED Bulbs'),
        ('best-smart-plugs-2026', 'Best Smart Plugs'),
        ('best-smart-home-hubs-2026', 'Best Smart Home Hubs'),
    ],
    'best-smart-locks-apartments-2026': [
        ('best-smart-door-locks-2026', 'Best Smart Door Locks'),
        ('best-smart-door-locks-keypad-2026', 'Best Smart Door Locks with Keypad'),
        ('best-smart-home-security-cameras-2026', 'Best Smart Home Security Cameras'),
    ],
    'best-smart-plugs-2026': [
        ('best-smart-power-strips-2026', 'Best Smart Power Strips'),
        ('best-smart-led-bulbs-2026', 'Best Smart LED Bulbs'),
        ('best-smart-home-devices-2026', 'Best Smart Home Devices'),
    ],
    'best-smart-power-strips-2026': [
        ('best-smart-plugs-2026', 'Best Smart Plugs'),
        ('best-smart-led-bulbs-2026', 'Best Smart LED Bulbs'),
        ('best-smart-home-hubs-2026', 'Best Smart Home Hubs'),
    ],
    'best-smart-smoke-co-detectors-2026': [
        ('best-smart-home-security-cameras-2026', 'Best Smart Home Security Cameras'),
        ('best-smart-doorbells-motion-detection-2026', 'Best Smart Doorbells with Motion Detection'),
        ('best-smart-door-locks-2026', 'Best Smart Door Locks'),
    ],
    'best-smart-speakers-2026': [
        ('best-smart-home-hubs-2026', 'Best Smart Home Hubs'),
        ('best-smart-home-devices-2026', 'Best Smart Home Devices'),
        ('best-smart-plugs-2026', 'Best Smart Plugs'),
    ],
    'best-smart-thermostats-alexa-compatible-2026': [
        ('best-smart-thermostats-2026', 'Best Smart Thermostats'),
        ('best-smart-thermostats-for-renters-2026', 'Best Smart Thermostats for Renters'),
        ('best-smart-home-devices-2026', 'Best Smart Home Devices'),
    ],
    'best-smart-thermostats-energy-savings-2026': [
        ('best-smart-thermostats-2026', 'Best Smart Thermostats'),
        ('best-smart-thermostats-for-renters-2026', 'Best Smart Thermostats for Renters'),
        ('best-smart-home-devices-2026', 'Best Smart Home Devices'),
    ],
    'best-smart-thermostats-renters-2026': [
        ('best-smart-thermostats-2026', 'Best Smart Thermostats'),
        ('best-smart-thermostats-for-renters-2026', 'Best Smart Thermostats for Renters'),
        ('best-smart-home-devices-2026', 'Best Smart Home Devices'),
    ],
    'best-smart-video-doorbells-2026': [
        ('best-smart-doorbells-2026', 'Best Smart Doorbells'),
        ('best-smart-doorbells-motion-detection-2026', 'Best Smart Doorbells with Motion Detection'),
        ('best-smart-doorbells-under-100-2026', 'Best Smart Doorbells Under $100'),
    ],
}

print("Fixing smart-home article links...")
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

    content = re.sub(r'\n\*\*Related Guides:\*\*[^\n]*\n?', '', content)
    new_line = '\n' + make_related_line(valid_targets) + '\n'
    new_content = content.rstrip('\n') + '\n' + new_line

    with open(filepath, 'w') as f:
        f.write(new_content)

    print(f"  ✓ {source_slug}")
    for s, t in valid_targets:
        print(f"      → {s}")
    updated += 1

print(f"\nFixed {updated} smart-home articles.")
