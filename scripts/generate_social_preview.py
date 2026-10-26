#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate high-resolution (1280x640) GitHub Social Preview Card."""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1280
HEIGHT = 640

OUTPUT_PATH = Path(".github/assets/social-preview.png")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# 1. Base Image
img = Image.new("RGBA", (WIDTH, HEIGHT), (9, 11, 20, 255))
draw = ImageDraw.Draw(img)

# 2. Draw sophisticated gradient & ambient radial glow
for y in range(HEIGHT):
    # subtle vertical gradient
    factor = y / HEIGHT
    r = int(10 + factor * 8)
    g = int(12 + factor * 10)
    b = int(24 + factor * 14)
    draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

# Radial ambient glows (Violet on top-left, Cyan on bottom-right)
glow_img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow_img)

# Top center-left violet glow
cx1, cy1 = 380, 220
max_r1 = 380
for rad in range(max_r1, 0, -6):
    alpha = int((1 - rad / max_r1) ** 2 * 45)
    glow_draw.ellipse([cx1 - rad, cy1 - rad, cx1 + rad, cy1 + rad], fill=(138, 43, 226, alpha))

# Bottom right cyan glow
cx2, cy2 = 980, 460
max_r2 = 320
for rad in range(max_r2, 0, -6):
    alpha = int((1 - rad / max_r2) ** 2 * 35)
    glow_draw.ellipse([cx2 - rad, cy2 - rad, cx2 + rad, cy2 + rad], fill=(6, 182, 212, alpha))

img = Image.alpha_composite(img, glow_img)
draw = ImageDraw.Draw(img)

# Outer delicate frame
draw.rounded_rectangle([20, 20, WIDTH - 20, HEIGHT - 20], radius=24, outline=(40, 48, 80, 200), width=1)

# Fonts
font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 52)
font_subtitle = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
font_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 14)
font_card_num = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 32)
font_card_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
font_card_desc = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
font_code = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 21)
font_footer = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)

# 3. Top Pill Badge: "OPEN-SOURCE AI CODING ENGINE • v1.11.7"
pill_x1, pill_y1 = 80, 52
pill_w, pill_h = 360, 32
draw.rounded_rectangle([pill_x1, pill_y1, pill_x1 + pill_w, pill_y1 + pill_h], radius=16, fill=(24, 28, 52, 220), outline=(99, 102, 241, 160), width=1)
# Green indicator dot
draw.ellipse([pill_x1 + 14, pill_y1 + 11, pill_x1 + 24, pill_y1 + 21], fill=(16, 185, 129, 255))
draw.text((pill_x1 + 34, pill_y1 + 6), "PRODUCTION AI AGENT OS  •  v1.11.7", fill=(224, 231, 255, 255), font=font_badge)

# 4. Main Hero Title
title_text = "⚡ GOKU DEV SKILLS"
draw.text((80, 104), title_text, fill=(255, 255, 255, 255), font=font_title)

# 5. Subtitle & Supported Agents
sub_text = "Engineering & Quality Verification Operating System for AI Coding Assistants"
draw.text((80, 172), sub_text, fill=(203, 213, 225, 255), font=font_subtitle)

agents_text = "Google Antigravity  ·  Cursor  ·  Claude Code  ·  Windsurf  ·  OpenCode"
draw.text((80, 206), agents_text, fill=(129, 140, 248, 255), font=font_subtitle)

# 6. Three Feature Cards
cards_data = [
    {
        "num": "30",
        "num_color": (168, 85, 247), # Purple
        "title": "PRODUCTION SKILLS",
        "desc": "Architecture, Pre-Launch, TDD,\nSecurity Audit, SEO & Themes"
    },
    {
        "num": "11",
        "num_color": (56, 189, 248), # Cyan
        "title": "DETERMINISTIC GATES",
        "desc": "Bundle Budgets, Anti-Slop, WCAG,\nDB Migrations & Unused Imports"
    },
    {
        "num": "5",
        "num_color": (52, 211, 153), # Emerald
        "title": "LAYER VERTICAL SLICE",
        "desc": "Zero Phantom Done: DB, View,\nAPI, UX & Admin Loop Closed"
    }
]

card_y = 260
card_w = 345
card_h = 175
card_gap = 42
start_x = 80

for i, c in enumerate(cards_data):
    cx = start_x + i * (card_w + card_gap)
    # Card background with border
    draw.rounded_rectangle([cx, card_y, cx + card_w, card_y + card_h], radius=16, fill=(17, 21, 38, 200), outline=(45, 55, 90, 180), width=1)
    
    # Accent top-left marker
    draw.rounded_rectangle([cx + 18, card_y + 18, cx + 24, card_y + 48], radius=3, fill=c["num_color"])
    
    # Large Number & Title
    draw.text((cx + 34, card_y + 14), c["num"], fill=c["num_color"], font=font_card_num)
    draw.text((cx + 80, card_y + 24), c["title"], fill=(241, 245, 249), font=font_card_title)
    
    # Description lines
    draw.text((cx + 18, card_y + 80), c["desc"], fill=(148, 163, 184), font=font_card_desc, spacing=8)

# 7. Bottom Quickstart Terminal Bar
bar_x = 80
bar_y = 475
bar_w = WIDTH - 160
bar_h = 76

# Terminal container
draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], radius=16, fill=(12, 15, 28, 240), outline=(79, 70, 229, 140), width=1)

# Mac-like window control dots
draw.ellipse([bar_x + 22, bar_y + 32, bar_x + 32, bar_y + 42], fill=(239, 68, 68, 200))
draw.ellipse([bar_x + 38, bar_y + 32, bar_x + 48, bar_y + 42], fill=(245, 158, 11, 200))
draw.ellipse([bar_x + 54, bar_y + 32, bar_x + 64, bar_y + 42], fill=(16, 185, 129, 200))

# Prompt symbol and code
draw.text((bar_x + 92, bar_y + 26), "$", fill=(148, 163, 184), font=font_code)
draw.text((bar_x + 115, bar_y + 26), "npx goku-dev-skills init --detect", fill=(56, 189, 248), font=font_code)

# Right badge: "Instant Zero-Config Setup"
right_tag = "🚀 ZERO-CONFIG AUTO-DETECT"
draw.text((bar_x + bar_w - 275, bar_y + 28), right_tag, fill=(129, 140, 248), font=font_badge)

# 8. Footer Metadata
draw.text((80, 580), "MIT Licensed  ·  Open Source  ·  100% Deterministic Verification  ·  Zero AI-Slop", fill=(100, 116, 139), font=font_footer)
draw.text((WIDTH - 380, 580), "github.com/mustafa-omeri/goku-dev-skills", fill=(129, 140, 248), font=font_footer)

# Save
img.save(str(OUTPUT_PATH), "PNG", optimize=True)
print(f"Generated social preview at: {OUTPUT_PATH} ({WIDTH}x{HEIGHT})")
