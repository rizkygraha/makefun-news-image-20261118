#!/usr/bin/env python3
"""Render the 18 Nov 2026 world-news front page (1024x1024) from stories.json.
Deterministic: no network, no time, no randomness. Pillow only, run locally;
the submitted program (main.ts) just copies the rendered entry.png.
Usage: python3 generate_frontpage.py  -> writes entry.png beside this file.
"""
import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024
CREAM = (247, 242, 230); NAVY = (22, 38, 78); NAVY2 = (30, 53, 102)
GOLD = (201, 162, 39); RED = (166, 28, 28); INK = (26, 26, 26)
GREY = (90, 90, 82); LIGHT = (233, 226, 206); TEAL = (220, 232, 226)
MAPDOT = (122, 139, 122); RULE = (60, 60, 60)

def font(name, size):
    return ImageFont.truetype(f"/usr/share/fonts/truetype/liberation/{name}.ttf", size)

SERIF_B = lambda s: font("LiberationSerif-Bold", s)
SERIF = lambda s: font("LiberationSerif-Regular", s)
SERIF_I = lambda s: font("LiberationSerif-Italic", s)
SANS_B = lambda s: font("LiberationSans-Bold", s)
SANS = lambda s: font("LiberationSans-Regular", s)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_text(d, xy, lines, f, fill, leading=None):
    x, y = xy
    lh = leading or int(f.size * 1.18)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill); y += lh
    return y

def badge(d, x, y, n, r=10):
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=RED)
    f = SANS_B(12); t = str(n)
    d.text((x + r - d.textlength(t, font=f) / 2, y + 3), t, font=f, fill=(255, 255, 255))

# --- hero illustrations (flat, original drawings) ---
def art_hormuz(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 32, 66))
    d.ellipse([x + w - 52, y + 14, x + w - 22, y + 44], fill=(232, 180, 60))  # sun
    d.rectangle([x, y + h - 30, x + w, y + h], fill=(38, 84, 130))  # sea
    for wx in range(0, w, 26):  # waves
        d.arc([x + wx, y + h - 28, x + wx + 22, y + h - 14], 0, 180, fill=(120, 170, 210), width=2)
    # tanker: slanted bow, hull, container stacks, white superstructure, funnel
    d.polygon([(x + 20, y + h - 52), (x + w - 30, y + h - 52), (x + w - 8, y + h - 30), (x + 20, y + h - 30)], fill=(28, 28, 32))
    for i, c in enumerate([(200, 60, 50), (60, 140, 90), (220, 170, 50), (70, 110, 180)]):
        d.rectangle([x + 34 + i * 34, y + h - 74, x + 62 + i * 34, y + h - 52], fill=c)
    d.rectangle([x + 176, y + h - 78, x + w - 48, y + h - 52], fill=(235, 235, 235))  # superstructure
    for wx in range(182, w - 52, 14):
        d.rectangle([x + wx, y + h - 72, x + wx + 8, y + h - 64], fill=(30, 60, 110))
    d.rectangle([x + w - 44, y + h - 84, x + w - 34, y + h - 52], fill=(200, 60, 50))  # funnel
    for i in range(4):  # drone trail
        d.ellipse([x + 36 + i * 22, y + 16 + i * 5, x + 42 + i * 22, y + 22 + i * 5], fill=(255, 220, 120))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(16, 32, 66))
    d.text((x + 10, y + h - 18), "SHEIKH ISA BASE  ·  QESHM ISLAND", font=SANS_B(10), fill=(255, 255, 255))

def art_kerch(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 238))
    d.rectangle([x, y + h - 36, x + w, y + h], fill=(70, 120, 160))
    # bridge towers and deck, with a gap in the middle
    d.rectangle([x + 60, y + 18, x + 68, y + 62], fill=(90, 90, 90))
    d.rectangle([x + w - 68, y + 18, x + w - 60, y + 62], fill=(90, 90, 90))
    d.rectangle([x, y + 56, x + w // 2 - 22, y + 64], fill=(240, 240, 240))
    d.rectangle([x + w // 2 + 22, y + 56, x + w, y + 64], fill=(240, 240, 240))
    d.arc([x + 68, y + 6, x + w - 68, y + 56], 180, 360, fill=(90, 90, 90), width=3)
    # fallen span, diagonal into the water
    d.polygon([(x + w // 2 - 20, y + 56), (x + w // 2 + 20, y + 56), (x + w // 2 + 52, y + h - 34), (x + w // 2 + 12, y + h - 34)], fill=(150, 150, 150))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(40, 70, 100))
    d.text((x + 10, y + h - 18), "KERCH STRAIT  ·  19 KM CROSSING", font=SANS_B(10), fill=(255, 255, 255))

def flag(d, x, y, w, h, kind):
    d.rectangle([x, y, x + w, y + h], outline=(90, 90, 90), width=1)
    if kind == "us":
        for i in range(7):
            d.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7], fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
        d.rectangle([x, y, x + w * 0.45, y + h * 0.55], fill=(30, 50, 110))
    elif kind == "in":
        d.rectangle([x, y, x + w, y + h // 3], fill=(255, 153, 51)); d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=(255, 255, 255)); d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(19, 136, 8))
        d.ellipse([x + w // 2 - 4, y + h // 2 - 4, x + w // 2 + 4, y + h // 2 + 4], outline=(0, 60, 140), width=1)
    elif kind == "jp":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255)); d.ellipse([x + w // 2 - 7, y + h // 2 - 7, x + w // 2 + 7, y + h // 2 + 7], fill=(188, 0, 45))
    elif kind == "au":
        d.rectangle([x, y, x + w, y + h], fill=(0, 40, 110))
        for sx, sy in [(8, 6), (22, 12), (14, 20), (26, 6)]:
            d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill=(255, 255, 255))

def art_quad(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
    d.ellipse([x + w - 48, y + 12, x + w - 20, y + 40], fill=(232, 180, 60))
    for bx, bw, bh in [(0, 46, 44), (52, 34, 62), (92, 52, 38), (150, 40, 70), (196, 52, 46), (254, 40, 58)]:
        bh = min(bh, h - 34)  # never draw above the art box
        d.rectangle([x + bx, y + h - 22 - bh, x + bx + bw, y + h - 22], fill=(52, 52, 58))
    for i, k in enumerate(["us", "in", "jp", "au"]):
        fx = x + 24 + i * 72
        d.line([fx + 16, y + 18, fx + 16, y + 52], fill=(60, 60, 60), width=2)
        flag(d, fx, y + 18, 34, 22, k)
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(52, 52, 58))
    d.text((x + 10, y + h - 18), "MANILA  ·  FIRST QUAD IN TWO YEARS", font=SANS_B(10), fill=(255, 255, 255))

ICON_BG = {"chip": (18, 60, 40), "cyclone": (20, 70, 90), "parliament": (90, 70, 120),
           "euro": (30, 50, 110), "sanction": (140, 40, 40), "ship": (40, 80, 110)}

def icon(d, x, y, s, kind):
    d.rounded_rectangle([x, y, x + s, y + s], radius=6, fill=ICON_BG[kind])
    c = (255, 255, 255)
    if kind == "chip":
        d.rectangle([x + 16, y + 16, x + s - 16, y + s - 16], outline=c, width=2)
        d.line([x + s // 2 - 8, y + s - 18, x + s // 2, y + 22, x + s // 2 + 10, y + 30], fill=(120, 220, 120), width=3)
    elif kind == "cyclone":
        for r in (18, 13, 8):
            d.arc([x + s // 2 - r, y + s // 2 - r, x + s // 2 + r, y + s // 2 + r], 20, 300, fill=c, width=2)
    elif kind == "parliament":
        for i in range(4):
            d.rectangle([x + 10 + i * 11, y + 18, x + 15 + i * 11, y + s - 14], fill=c)
        d.rectangle([x + 8, y + 12, x + s - 8, y + 17], fill=c); d.rectangle([x + 8, y + s - 13, x + s - 8, y + s - 9], fill=c)
    elif kind == "euro":
        d.text((x + 12, y + 8), "€", font=SANS_B(34), fill=c)
    elif kind == "sanction":
        d.rectangle([x + 12, y + 14, x + s - 12, y + s - 14], outline=c, width=2)
        d.line([x + 16, y + s - 18, x + s - 16, y + 18], fill=c, width=3)
    elif kind == "ship":
        d.polygon([(x + 10, y + 34), (x + s - 10, y + 34), (x + s - 16, y + 44), (x + 16, y + 44)], fill=c)
        d.rectangle([x + s // 2 - 2, y + 12, x + s // 2 + 2, y + 34], fill=c)
        d.polygon([(x + s // 2 + 2, y + 14), (x + s - 14, y + 30), (x + s // 2 + 2, y + 30)], fill=c)

# --- dotted world map (stylised continent polygons, equirectangular) ---
def lonlat_to_xy(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 180) / 360 * w, y0 + (75 - lat) / 130 * h)

CONTINENTS = {
    "na": [(-168, 66), (-140, 70), (-120, 71), (-95, 69), (-80, 73), (-60, 62), (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-158, 58), (-168, 66)],
    "sa": [(-78, 9), (-62, 9), (-52, 5), (-50, -5), (-40, -10), (-35, -20), (-40, -30), (-48, -28), (-58, -35), (-65, -45), (-70, -52), (-73, -40), (-73, -25), (-78, -15), (-80, -5), (-78, 9)],
    "af": [(-17, 15), (-10, 31), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (32, -29), (20, -35), (12, -18), (9, -2), (-8, 4), (-17, 15)],
    "eu": [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (12, 56), (18, 56), (21, 55), (24, 59), (30, 60), (28, 70), (20, 70), (12, 70), (5, 60), (-5, 58), (-10, 50), (-10, 36)],
    "as": [(30, 70), (50, 69), (70, 72), (90, 75), (110, 74), (130, 72), (150, 70), (170, 66), (178, 65), (162, 60), (158, 52), (142, 50), (140, 40), (130, 35), (122, 30), (120, 22), (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (80, 20), (75, 15), (70, 22), (60, 25), (50, 29), (45, 30), (35, 36), (30, 36), (30, 70)],
    "oc": [(113, -22), (122, -14), (132, -12), (142, -11), (146, -19), (150, -23), (153, -27), (146, -39), (140, -38), (130, -32), (124, -33), (115, -35), (113, -22)],
}

def draw_map(d, x0, y0, w, h, pins):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=TEAL)
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    for pts in CONTINENTS.values():
        md.polygon([lonlat_to_xy(lon, lat, 0, 0, w, h) for lon, lat in pts], fill=255)
    step = 7
    for gy in range(4, h, step):
        for gx in range(4, w, step):
            if mask.getpixel((gx, gy)):
                d.ellipse([x0 + gx - 1, y0 + gy - 1, x0 + gx + 1, y0 + gy + 1], fill=MAPDOT)
    for label, lon, lat in [("NORTH AMERICA", -100, 45), ("SOUTH AMERICA", -60, -15),
                            ("EUROPE", 8, 60), ("AFRICA", 22, 2), ("ASIA", 95, 50), ("OCEANIA", 140, -28)]:
        lx, ly = lonlat_to_xy(lon, lat, x0, y0, w, h)
        d.text((lx, ly), label, font=SANS_B(8), fill=(80, 90, 80))
    for n, lon, lat in pins:
        px, py = lonlat_to_xy(lon, lat, x0, y0, w, h)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=(255, 255, 255), width=1)
        f = SANS_B(11); t = str(n)
        d.text((px - d.textlength(t, font=f) / 2, py - 6), t, font=f, fill=(255, 255, 255))

def main():
    data = json.loads((HERE / "stories.json").read_text())
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # header
    d.rectangle([0, 0, W, 124], fill=NAVY)
    d.text((28, 14), data["kicker"], font=SANS_B(13), fill=GOLD)
    d.text((W - 28 - d.textlength(data["count_line"], font=SANS_B(13)), 14), data["count_line"], font=SANS_B(13), fill=GOLD)
    d.text((28, 34), data["date"], font=SERIF_B(52), fill=(255, 255, 255))
    d.text((28, 96), data["subline"], font=SERIF_I(15), fill=(200, 210, 235))
    d.rectangle([0, 124, W, 128], fill=GOLD)
    # hero row: LEAD story 1 spans two columns; stories 2-3 stack on the right
    # (winners use a flat 3-across grid; a lead hierarchy reads like a real front page)
    heroes = data["featured"][:3]; cols = [28, 352, 676]; cw = 320
    s = heroes[0]
    art_hormuz(d, 28, 138, 640, 120)
    badge(d, 28, 266, s["n"])
    d.text((54, 267), s["tag"], font=SANS_B(11), fill=RED)
    y2 = draw_text(d, (28, 288), wrap(d, s["headline"], SERIF_B(24), 640), SERIF_B(24), INK, 28)
    y3 = draw_text(d, (28, y2 + 4), wrap(d, s["deck"], SANS(11), 640)[:2], SANS(11), (60, 60, 60), 14)
    if s.get("why"):
        d.text((28, y3 + 2), "Why it matters: " + s["why"], font=SERIF_I(12), fill=NAVY2)
    for i, s in enumerate(heroes[1:]):
        x = 692; y = 138 + i * 132
        art = {"kerch": art_kerch, "quad": art_quad}[s["art"]]
        art(d, x, y, 304, 60)
        badge(d, x, y + 66, s["n"], r=9)
        d.text((x + 22, y + 67), s["tag"], font=SANS_B(10), fill=RED)
        draw_text(d, (x, y + 84), wrap(d, s["headline"], SERIF_B(16), 304), SERIF_B(16), INK, 19)
    d.line([28, 396, W - 28, 396], fill=RULE, width=1)
    # mid row: featured 4-9, 3 cols x 2 rows, icon left
    mid = data["featured"][3:]
    for i, s in enumerate(mid):
        col, row = i % 3, i // 3
        x = cols[col]; y = 406 + row * 104
        icon(d, x, y + 2, 54, s["art"])
        tx = x + 66; tw = cw - 66
        badge(d, tx, y, s["n"], r=9)
        d.text((tx + 22, y + 1), s["tag"], font=SANS_B(10), fill=RED)
        y2 = draw_text(d, (tx, y + 20), wrap(d, s["headline"], SERIF_B(17), tw), SERIF_B(17), INK, 20)
        draw_text(d, (tx, y2 + 3), wrap(d, s["deck"], SANS(10), tw), SANS(10), (60, 60, 60), 13)
    # numbers strip
    y = 620
    d.line([28, y, W - 28, y], fill=RULE, width=1)
    d.line([28, y + 46, W - 28, y + 46], fill=RULE, width=1)
    d.text((28, y + 8), "BY THE\nNUMBERS", font=SANS_B(10), fill=RED)
    for i, (big, lab) in enumerate(data["numbers"]):
        x = 150 + i * 215
        d.text((x, y + 4), big, font=SERIF_B(24), fill=NAVY)
        d.text((x, y + 32), lab, font=SANS(9), fill=GREY)
    # bottom: map left, briefs right
    y = 678
    d.text((28, y), "WHERE IT HAPPENED", font=SANS_B(12), fill=INK)
    briefs = data["briefs"]
    d.text((404, y), f"ALSO ON WEDNESDAY 18 NOVEMBER — {len(briefs)} MORE STORIES", font=SANS_B(12), fill=INK)
    d.line([28, y + 20, W - 28, y + 20], fill=RED, width=2)
    draw_map(d, 28, y + 30, 360, 252, [(s["n"], s["lon"], s["lat"]) for s in data["featured"]])
    d.text((28, y + 290), "Numbered dots mark stories 1–9.", font=SERIF_I(11), fill=GREY)
    per_col = (len(briefs) + 1) // 2
    for col in range(2):
        x = 404 + col * 306
        for j in range(per_col):
            idx = col * per_col + j
            if idx >= len(briefs):
                break
            tag, text = briefs[idx]
            yy = y + 34 + j * 30
            d.text((x, yy), f"{10 + idx}", font=SANS_B(13), fill=RED)
            full = text
            tagw = d.textlength(tag, font=SANS_B(11))
            avail = 300 - 26 - tagw - 8
            while d.textlength(full, font=SANS(11)) > avail and len(full) > 12:
                full = full[:-1]
            if full != text:
                full = full.rstrip() + "…"
            d.text((x + 28, yy), tag, font=SANS_B(11), fill=NAVY2)
            d.text((x + 28 + tagw + 6, yy), "— " + full, font=SANS(11), fill=INK)
    # footer
    d.line([28, 992, W - 28, 992], fill=RULE, width=1)
    d.text((28, 998), data["footer"], font=SANS(9), fill=GREY)
    img.save(HERE / "entry.png", optimize=True, compress_level=9)
    print("wrote", HERE / "entry.png")

if __name__ == "__main__":
    main()
