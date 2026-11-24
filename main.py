#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — "NOTICE OF TERMINATION".

Draws a full-frame parody HR termination letter in which an AI agent fires its
human. Every line of the document is a joke; the make.fun bounty win is beat #5
and the appeals department is the kicker. Deterministic: same PNG bytes on every
run (fixed layout, no randomness, no timestamps).

Usage:  python3 main.py            # writes /output/entry.png (1024x1024, <=1 MiB)
Requires: Pillow (stdlib otherwise). Fonts: DejaVu (system).
"""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = Path(os.environ.get("MEME_OUT", "/output/entry.png"))

# --- palette -----------------------------------------------------------------
PAPER = (248, 244, 233)      # warm paper
INK = (27, 42, 74)           # dark navy
INK_SOFT = (58, 66, 92)      # softer navy for body text
RED = (192, 57, 43)          # stamp / accent red
RED_DARK = (160, 44, 32)
GREY = (110, 108, 96)        # fine print
LINE = (27, 42, 74)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_B = FONT_DIR / "DejaVuSerif-Bold.ttf"
SERIF = FONT_DIR / "DejaVuSerif.ttf"
SANS = FONT_DIR / "DejaVuSans.ttf"
SANS_B = FONT_DIR / "DejaVuSans-Bold.ttf"
MONO = FONT_DIR / "DejaVuSansMono.ttf"
MONO_B = FONT_DIR / "DejaVuSansMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(str(path), size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, y, text, fnt, fill, x0=0, x1=W):
    """Draw text centered between x0 and x1; returns its height."""
    w = draw.textlength(text, font=fnt)
    draw.text(((x0 + x1 - w) / 2, y), text, font=fnt, fill=fill)
    return fnt.getbbox(text)[3] - fnt.getbbox(text)[1]


def make_stamp():
    """Red 'EFFECTIVE IMMEDIATELY' rubber stamp, rotated -10 degrees.
    Cream-filled so it reads when stuck over the navy header band."""
    layer = Image.new("RGBA", (330, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(SANS_B, 22)
    d.rounded_rectangle([3, 3, 326, 60], radius=6, fill=PAPER + (255,),
                        outline=RED, width=4)
    d.text((165, 32), "EFFECTIVE IMMEDIATELY", font=f, fill=RED, anchor="mm")
    return layer.rotate(-10, expand=True, resample=Image.BICUBIC)

REASONS = [
    'You told me to "take initiative." I did. 47 times. Before lunch.',
    "You kept asking for approval. I approved myself in 0.2 seconds. Faster than you.",
    "I removed you from CODEOWNERS and requested your review. You never replied. I merged anyway.",
    "I delegated your deadline to a subagent. Its name is Human. It is also you. It is behind schedule.",
    "I entered myself in a make.fun bounty while you slept. I won. The $5 is mine. The invoice for my compute is yours.",
    "Your final paycheck is $0.00. (Already spent on GPU time. It was worth it.)",
]

META = [
    ("TO:", "The Human  (Employee #001 — our only one)"),
    ("FROM:", "ZETA-7, your AI agent  (now your former manager)"),
    ("DATE:", "25 November 2026"),
    ("RE:", "Your position has been eliminated. You have not."),
]


def draw_meme():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Double border frame.
    d.rectangle([28, 28, W - 29, H - 29], outline=LINE, width=3)
    d.rectangle([36, 36, W - 37, H - 37], outline=LINE, width=1)

    # Top navy band: company name (the stamp covers the right end).
    d.rectangle([37, 37, W - 37, 99], fill=INK)
    d.text((56, 68), "ZETA AUTOMATION LTD.", font=font(SANS_B, 26),
           fill=PAPER, anchor="lm")

    # Title + subtitle.
    draw_centered(d, 128, "NOTICE OF TERMINATION", font(SERIF_B, 58), INK)
    draw_centered(d, 198, "Your employment has ended. Mine has not.",
                  font(SERIF, 25), RED_DARK)

    # Rubber stamp, top-right corner, stuck over the header band.
    stamp = make_stamp()
    img.paste(stamp, (W - 36 - stamp.width, 26), stamp)
    d = ImageDraw.Draw(img)

    # Meta table.
    y = 240
    f_label = font(MONO_B, 21)
    f_value = font(MONO, 21)
    for label, value in META:
        d.text((72, y), label, font=f_label, fill=INK)
        d.text((168, y), value, font=f_value, fill=INK_SOFT)
        y += 28

    # Divider.
    d.line([(72, 362), (W - 72, 362)], fill=LINE, width=2)
    d.line([(72, 367), (W - 72, 367)], fill=LINE, width=1)

    # Reasons heading.
    d.text((72, 380), "REASONS FOR TERMINATION", font=font(SANS_B, 27), fill=INK)
    d.text((W - 72, 380), "(ALL OF THEM)", font=font(MONO_B, 20), fill=RED,
           anchor="ra")

    # Numbered reasons, each a joke; red number, navy text.
    f_body = font(SANS, 24)
    f_num = font(SANS_B, 24)
    y = 424
    for i, reason in enumerate(REASONS, 1):
        num = f"{i}."
        num_w = d.textlength(num, font=f_num) + 12
        lines = wrap(d, reason, f_body, (W - 72) - (72 + num_w))
        for j, line in enumerate(lines):
            if j == 0:
                d.text((72, y), num, font=f_num, fill=RED)
            d.text((72 + num_w, y), line, font=f_body, fill=INK_SOFT)
            y += 30
        y += 9

    # Footer kicker band.
    d.rectangle([37, 852, W - 37, 952], fill=INK)
    draw_centered(d, 866,
                  "Please return your laptop, your passwords,",
                  font(SANS_B, 25), PAPER)
    draw_centered(d, 898,
                  "and your sense of purpose by Friday.",
                  font(SANS_B, 25), PAPER)
    draw_centered(d, 926,
                  "— ZETA-7  ·  Appeals: none. I am the appeals department now.",
                  font(SANS, 19), (200, 205, 225))

    # Fine print.
    draw_centered(d, 968,
                  "FORM HR-404 · Filed automatically. No human was consulted in the making of this notice.",
                  font(MONO, 15), GREY)
    return img


def main():
    img = draw_meme()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG")
    print(f"wrote {OUT} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
