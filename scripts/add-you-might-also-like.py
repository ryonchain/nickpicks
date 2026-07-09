#!/usr/bin/env python3
"""
Add "You Might Also Like" cross-category internal linking sections
to specific articles for NIC-631.
"""

import os
import sys

ARTICLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'articles')

# Mapping: article filename -> list of (title, url) pairs to link to
ARTICLE_LINKS = {
    # Cluster 1: Home Office / WFH — Webcam articles → Headphones + Desk Lamp
    "best-webcams-video-calls-streaming-2026.md": [
        ("Best Noise-Canceling Headphones for Work", "/articles/best-noise-canceling-headphones-work-2026/"),
        ("Best Noise-Canceling Headphones Under $100 for WFH", "/articles/best-noise-canceling-headphones-under-100-wfh-2026/"),
        ("Best LED Desk Lamps for Home Office", "/articles/best-led-desk-lamps-home-office-2026/"),
    ],
    "best-4k-webcams-remote-meetings-2026.md": [
        ("Best Noise-Canceling Headphones for Work", "/articles/best-noise-canceling-headphones-work-2026/"),
        ("Best LED Desk Lamps for Eye Strain", "/articles/best-led-desk-lamps-eye-strain-2026/"),
        ("Best Ring Lights for Home Office & Content Creation", "/articles/best-ring-lights-home-office-content-creation-2026/"),
    ],
    "best-webcams-home-office-under-100-2026.md": [
        ("Best Noise-Canceling Headphones Under $100 for WFH", "/articles/best-noise-canceling-headphones-under-100-wfh-2026/"),
        ("Best LED Desk Lamps for Home Office", "/articles/best-led-desk-lamps-home-office-2026/"),
        ("Best Budget Home Office Accessories Under $50", "/articles/best-budget-home-office-accessories-under-50/"),
    ],

    # Cluster 1: Home Office / WFH — Monitor Stand articles → USB Hub + Ergonomic Keyboard
    "best-monitor-stands-dual-setup-2026.md": [
        ("Best USB Hubs for Laptop", "/articles/best-usb-hubs-for-laptop-2026/"),
        ("Best USB Hubs for Remote Work", "/articles/best-usb-hubs-remote-work-2026/"),
        ("Best Ergonomic Keyboards for Home Office", "/articles/best-ergonomic-keyboards-home-office-2026/"),
    ],
    "best-monitor-stands-with-storage-2026.md": [
        ("Best USB Hubs for Laptop", "/articles/best-usb-hubs-for-laptop-2026/"),
        ("Best Ergonomic Keyboards for Home Office", "/articles/best-ergonomic-keyboards-home-office-2026/"),
        ("Best Desk Organizers", "/articles/best-desk-organizers-2026/"),
    ],
    "best-laptop-stands-home-office-2026.md": [
        ("Best USB Hubs for Remote Work", "/articles/best-usb-hubs-remote-work-2026/"),
        ("Best Ergonomic Keyboards", "/articles/best-ergonomic-keyboards-2026/"),
        ("Best Ergonomic Mouse for Home Office", "/articles/best-ergonomic-mouse-home-office-2026/"),
    ],

    # Cluster 1: Home Office / WFH — Desk Organizer articles → Cable Management + LED Lamp
    "best-mesh-desk-organizers-2026.md": [
        ("Best Cable Management Solutions for Desk Setup", "/articles/best-cable-management-solutions-desk-setup-2026/"),
        ("Best Cable Management Kits for Desks", "/articles/best-cable-management-kits-desks-2026/"),
        ("Best LED Desk Lamps for Home Office", "/articles/best-led-desk-lamps-home-office-2026/"),
    ],
    "best-desk-organizers-with-wireless-charging-2026.md": [
        ("Best Cable Management Boxes", "/articles/best-cable-management-boxes-2026/"),
        ("Best Smart LED Desk Lamps", "/articles/best-smart-led-desk-lamps-2026/"),
        ("Best USB Hubs for Laptop", "/articles/best-usb-hubs-for-laptop-2026/"),
    ],
    "best-under-desk-storage-home-office.md": [
        ("Best Cable Management for Desk", "/articles/best-cable-management-desk-2026/"),
        ("Best LED Desk Lamps", "/articles/best-led-desk-lamps-2026/"),
        ("Best Desk Organizers", "/articles/best-desk-organizers-2026/"),
    ],

    # Cluster 2: Kitchen + Coffee — Espresso Machine articles → Coffee Grinder + Pour-Over
    "best-espresso-machine-home-2026.md": [
        ("Best Burr Coffee Grinders for Pour-Over", "/articles/best-burr-coffee-grinders-for-pour-over-2026/"),
        ("Best Coffee Grinders for Home Baristas", "/articles/best-coffee-grinders-home-barista-2026/"),
        ("Best Electric Kettles for Pour-Over", "/articles/best-electric-kettles-pour-over-2026/"),
    ],
    "best-home-espresso-machines-2026.md": [
        ("Best Coffee Grinders", "/articles/best-coffee-grinders-2026/"),
        ("Best Burr Coffee Grinders", "/articles/best-burr-coffee-grinders-2026/"),
        ("Best Electric Kettles for Pour-Over with Gooseneck & Temperature Control", "/articles/best-electric-kettles-pour-over-gooseneck-temperature-2026/"),
    ],
    "best-espresso-machines-home-2026.md": [
        ("Best Coffee Grinders Under $100", "/articles/best-coffee-grinders-under-100-2026/"),
        ("Best Espresso Grinders for Home", "/articles/best-espresso-grinders-home-2026/"),
        ("Best Electric Kettles for Pour-Over", "/articles/best-electric-kettles-pour-over-2026/"),
    ],

    # Cluster 2: Kitchen + Coffee — Air Fryer articles → Instant Pot + Kitchen Gadgets
    "best-air-fryers-healthy-cooking-2026.md": [
        ("Best Instant Pot Pressure Cookers", "/articles/best-instant-pot-pressure-cookers-2026/"),
        ("Best Instant Pots & Multi-Cookers", "/articles/best-instant-pots-multicookers-2026/"),
        ("Best Air Fryer Toaster Ovens", "/articles/best-air-fryer-toaster-ovens-2026/"),
    ],
    "best-air-fryers-family-2026.md": [
        ("Best Instant Pot Electric Pressure Cookers", "/articles/best-instant-pot-electric-pressure-cookers-2026/"),
        ("Best Instant Pot Multi-Cookers", "/articles/best-instant-pot-multi-cookers-2026/"),
        ("Best Air Fryer Ovens", "/articles/best-air-fryer-ovens-2026/"),
    ],

    # Cluster 2: Kitchen + Coffee — Cold Brew articles → Coffee Grinder + related
    "cold-brew-coffee-makers.md": [
        ("Best Coffee Grinders for Fresh Grounds", "/articles/best-coffee-grinders-fresh-grounds-2026/"),
        ("Best Burr Coffee Grinders", "/articles/best-burr-coffee-grinders-2026/"),
        ("Best Electric Kettles for Pour-Over", "/articles/best-electric-kettles-pour-over-2026/"),
    ],
    "best-cold-brew-coffee-makers-2026.md": [
        ("Best Coffee Grinders", "/articles/best-coffee-grinders-2026/"),
        ("Best Coffee Grinders for Beginners", "/articles/best-coffee-grinders-for-beginners/"),
        ("Best Espresso Machines for Home", "/articles/best-espresso-machines-home-2026/"),
    ],

    # Cluster 3: Smart Home — Smart Doorbell articles → Security Camera + Smart Lock
    "best-smart-doorbells-motion-detection-2026.md": [
        ("Best Home Security Cameras", "/articles/best-home-security-cameras-2026/"),
        ("Best Indoor Security Cameras", "/articles/best-indoor-security-cameras-2026/"),
        ("Best Smart Locks", "/articles/best-smart-locks-2026/"),
    ],
    "best-smart-doorbells-ring-vs-eufy-vs-nest-2026.md": [
        ("Best Home Security Cameras Outdoor", "/articles/best-home-security-cameras-outdoor-2026/"),
        ("Best Smart Home Security Cameras", "/articles/best-smart-home-security-cameras-2026/"),
        ("Best Smart Locks for Apartments", "/articles/best-smart-locks-apartments-2026/"),
    ],
    "best-smart-doorbells-under-100-2026.md": [
        ("Best Home Security Cameras Under $100", "/articles/best-home-security-cameras-under-100/"),
        ("Best Smart Security Cameras", "/articles/best-smart-security-cameras-2026/"),
        ("Best Smart Locks", "/articles/best-smart-locks-2026/"),
    ],

    # Cluster 3: Smart Home — Smart Plug articles → Smart Doorbells + Security
    "best-smart-plugs-alexa-google-home-scheduling-2026.md": [
        ("Best Smart Doorbells", "/articles/best-smart-doorbells-2026/"),
        ("Best Smart Home Security Cameras", "/articles/best-smart-home-security-cameras-2026/"),
        ("Best Smart Plugs for Power Strips", "/articles/best-smart-plugs-power-strips-2026/"),
    ],
    "best-smart-plugs-energy-monitoring-2026.md": [
        ("Best Smart Home Security Camera Systems", "/articles/best-smart-home-security-camera-systems-2026/"),
        ("Best Smart Locks", "/articles/best-smart-locks-2026/"),
        ("Best Smart Doorbells with Motion Detection", "/articles/best-smart-doorbells-motion-detection-2026/"),
    ],
    "best-smart-plugs-home-automation-2026.md": [
        ("Best Smart Doorbells", "/articles/best-smart-doorbells-2026/"),
        ("Best Smart Security Cameras Indoor & Outdoor", "/articles/best-smart-security-cameras-indoor-outdoor-2026/"),
        ("Best Smart Plugs Under $20", "/articles/best-smart-plugs-under-20-2026/"),
    ],

    # Cluster 4: Tech Gifts / Holiday — Gift guides → Product categories
    "gift-guide-christmas-under-50-2026.md": [
        ("Best Noise-Canceling Headphones Under $200", "/articles/best-noise-canceling-headphones-under-200-2026/"),
        ("Best Smart Plugs Under $20", "/articles/best-smart-plugs-under-20-2026/"),
        ("Best Tech Gifts Under $50", "/articles/best-tech-gifts-under-50-2026/"),
    ],
    "gift-guide-for-dad-2026.md": [
        ("Best Ergonomic Keyboards for Home Office", "/articles/best-ergonomic-keyboards-home-office-2026/"),
        ("Best Smart Doorbells", "/articles/best-smart-doorbells-2026/"),
        ("Best Coffee Grinders", "/articles/best-coffee-grinders-2026/"),
    ],
    "gift-guide-for-her-2026.md": [
        ("Best Coffee Grinders", "/articles/best-coffee-grinders-2026/"),
        ("Best Cold Brew Coffee Makers", "/articles/best-cold-brew-coffee-makers-2026/"),
        ("Best Smart Plugs", "/articles/best-smart-plugs-2026/"),
    ],
    "gift-guide-for-him-2026.md": [
        ("Best Ergonomic Keyboards", "/articles/best-ergonomic-keyboards-2026/"),
        ("Best Espresso Machines for Home", "/articles/best-espresso-machines-home-2026/"),
        ("Best Webcams for Home Office", "/articles/best-webcams-home-office-2026/"),
    ],
    "best-tech-gifts-under-50-2026.md": [
        ("Best Smart Plugs Under $20", "/articles/best-smart-plugs-under-20-2026/"),
        ("Best Webcams for Home Office Under $100", "/articles/best-webcams-home-office-under-100-2026/"),
        ("Best Noise-Canceling Headphones Under $100 for WFH", "/articles/best-noise-canceling-headphones-under-100-wfh-2026/"),
    ],
}


def build_section(links):
    lines = ["", "## You Might Also Like", ""]
    for title, url in links:
        lines.append(f"- [{title}]({url})")
    lines.append("")
    return "\n".join(lines)


def add_section_to_article(filepath, links):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if "## You Might Also Like" in content:
        print(f"  SKIP (already has section): {os.path.basename(filepath)}")
        return False

    section = build_section(links)

    # Insert before "**Related Guides:**" line if present, otherwise append
    if "**Related Guides:**" in content:
        idx = content.rfind("**Related Guides:**")
        # Walk back to start of the line
        line_start = content.rfind("\n", 0, idx) + 1
        content = content[:line_start] + section + "\n" + content[line_start:]
    else:
        content = content.rstrip() + "\n" + section

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True


def main():
    processed = []
    skipped = []
    missing = []

    for filename, links in ARTICLE_LINKS.items():
        filepath = os.path.join(ARTICLES_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  MISSING: {filename}")
            missing.append(filename)
            continue

        print(f"Processing: {filename}")
        changed = add_section_to_article(filepath, links)
        if changed:
            processed.append(filename)
        else:
            skipped.append(filename)

    print(f"\n{'='*60}")
    print(f"Added 'You Might Also Like' sections: {len(processed)}")
    print(f"Already had sections (skipped): {len(skipped)}")
    print(f"Missing files: {len(missing)}")

    total_links = sum(len(links) for fname, links in ARTICLE_LINKS.items() if fname in processed)
    print(f"Total internal links added: {total_links}")

    if missing:
        print(f"\nMissing files:")
        for f in missing:
            print(f"  - {f}")

    return len(processed), total_links


if __name__ == "__main__":
    count, links = main()
    sys.exit(0 if count > 0 else 1)
