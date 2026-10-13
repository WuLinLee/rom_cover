#!/usr/bin/env python3
"""Build separate square covers from GBA/ without altering the originals.

Known square original artwork is preferred where the Libretro collection has a
genuine 1:1 image for the same game. Remaining covers use a centre-biased crop.
Every output is a 512x512 PNG named after the matching ROM file.
"""
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import sys

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "GBA"
DEST = ROOT / "GBA_Square"
SIZE = 512
LIBRETRO_BASE = (
    "https://raw.githubusercontent.com/libretro-thumbnails/"
    "Nintendo_-_Game_Boy_Advance/master/Named_Boxarts/"
)

# Exact square and near-square original artworks found in the public GBA box-art set.
# Only GBA_Square/ uses these regional alternatives; GBA/ remains untouched.
# The True flag permits tiny ratio normalization for one naturally near-square original.
SQUARE_ORIGINALS = {
    "公主同盟[狼狼小酷+流星落月](v20100811+NO.56修复)(简)(JP)(256Mb).png":
        ("Yggdra Union - We'll Never Fight Alone (USA).png", False),
    "哈利波特 - 阿兹卡班的逃犯[施珂昱](简)(JP)(128Mb).png":
        ("Harry Potter to Azkaban no Shuujin (Japan).png", False),
    "哈利波特 - 魔法石[shikeyu](v0.1)(简)(64Mb).png":
        ("Harry Potter to Kenja no Ishi (Japan).png", False),
    "海绵宝宝 亚特兰蒂斯[3爻3](简)(45Mb).png":
        ("SpongeBob's Atlantis SquarePantis (USA).png", True),
    "塞尔达传说 - 过去的林克&四支剑[漫游](简)(US)(64Mb).png":
        ("Legend of Zelda, The - A Link to the Past _ Four Swords (USA).png", False),
    "塞尔达传说 - 缩小帽[天使汉化组](日汉最终版v2005SP4)(简)(JP)(128Mb).png":
        ("Legend of Zelda, The - The Minish Cap (USA).png", False),
    "星之卡比 - 梦之泉[伤雪&Sody](简)(JP)(64Mb).png":
        ("Kirby - Nightmare in Dream Land (USA).png", False),
    "星之卡比 - 镜之大迷宫[CGP](简)(JP)(128Mb).png":
        ("Kirby _ The Amazing Mirror (USA).png", False),
    "约束之地 - 利维艾拉[PromisedLand](v1.05)[简](JP)(256Mb).png":
        ("Riviera - The Promised Land (USA).png", False),
}


def load_square_original(filename):
    entry = SQUARE_ORIGINALS.get(filename.name)
    if not entry:
        return None
    source_name, near_square = entry
    url = LIBRETRO_BASE + quote(source_name, safe="")
    try:
        request = Request(url, headers={"User-Agent": "rom-cover-square-generator"})
        with urlopen(request, timeout=30) as response:
            data = response.read()
        with Image.open(BytesIO(data)) as source_image:
            image = ImageOps.exif_transpose(source_image).convert("RGB")
            width, height = image.size
            ratio = width / height
            if abs(ratio - 1.0) > 0.035:
                print(f"NOTE: {source_name} is not square; saliency crop will be used.")
                return None
            if not near_square and width != height:
                print(f"NOTE: {source_name} is not exactly square; saliency crop will be used.")
                return None
            return image.copy(), source_name, near_square
    except Exception as exc:
        print(f"WARNING: could not fetch square original {source_name}: {exc}", file=sys.stderr)
        return None


def saliency_map(image):
    """Approximate visual focus from edges and color intensity."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    gx = np.zeros_like(gray)
    gy = np.zeros_like(gray)
    gx[:, 1:-1] = np.abs(gray[:, 2:] - gray[:, :-2]) * 0.5
    gy[1:-1, :] = np.abs(gray[2:, :] - gray[:-2, :]) * 0.5
    edge = gx + gy
    saturation = np.maximum.reduce([r, g, b]) - np.minimum.reduce([r, g, b])
    colour_span = np.max(rgb, axis=2) - np.min(rgb, axis=2)
    score = 0.58 * edge + 0.27 * saturation + 0.15 * colour_span
    scale = float(np.percentile(score, 98))
    if scale > 1e-8:
        score = np.clip(score / scale, 0.0, 1.0)
    return score


def best_offset(score, axis_len, side, axis):
    """Choose a high-detail square crop without straying far from center."""
    excess = axis_len - side
    if excess <= 0:
        return 0
    center_left = excess / 2.0
    max_shift = min(excess // 2, max(1, int(side * 0.16)))
    lo = max(0, int(round(center_left - max_shift)))
    hi = min(excess, int(round(center_left + max_shift)))
    projection = score.sum(axis=0 if axis == 1 else 1)
    prefix = np.concatenate(([0.0], np.cumsum(projection, dtype=np.float64)))
    offsets = np.arange(lo, hi + 1)
    sums = prefix[offsets + side] - prefix[offsets]
    norm = max(float(sums.max() - sums.min()), 1e-8)
    penalty = 0.10 * norm * ((offsets - center_left) / max(max_shift, 1)) ** 2
    return int(offsets[np.argmax(sums - penalty)])


def crop_square(image):
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if "transparency" in image.info else "RGB")
    width, height = image.size
    if width == height:
        return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)

    scale = min(1.0, 512.0 / max(width, height))
    analysis = image.convert("RGB")
    if scale < 1:
        analysis = analysis.resize(
            (max(1, round(width * scale)), max(1, round(height * scale))),
            Image.Resampling.LANCZOS,
        )
    score = saliency_map(analysis)
    aw, ah = analysis.size

    if width > height:
        side = height
        left_a = best_offset(score, aw, min(ah, aw), axis=1)
        left = min(max(0, round(left_a / scale)), width - side)
        top = 0
    else:
        side = width
        top_a = best_offset(score, ah, min(aw, ah), axis=0)
        top = min(max(0, round(top_a / scale)), height - side)
        left = 0

    cropped = image.crop((left, top, left + side, top + side))
    return cropped.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main():
    if not SOURCE.is_dir():
        print(f"Missing source folder: {SOURCE}", file=sys.stderr)
        return 2
    files = sorted(p for p in SOURCE.iterdir()
                   if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
    if not files:
        print(f"No cover images found in {SOURCE}", file=sys.stderr)
        return 2

    DEST.mkdir(parents=True, exist_ok=True)
    no_crop_entries = []
    cropped_entries = []
    made = 0

    for path in files:
        try:
            override = load_square_original(path)
            if override:
                cover, source_name, near_square = override
                output = cover.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
                if near_square:
                    label = "✅ 原版近方图，未裁切（原图 256×257，仅轻微统一比例）"
                else:
                    label = "✅ 原版方图，未裁切（只统一输出尺寸）"
                no_crop_entries.append((path.name, source_name, label, near_square))
            else:
                with Image.open(path) as original:
                    output = crop_square(original.copy())
                cropped_entries.append((path.name, f"GBA/{path.name}"))
            output.save(DEST / (path.stem + ".png"), format="PNG", optimize=True)
            made += 1
            print(f"Created {path.stem}.png")
        except Exception as exc:
            print(f"ERROR: {path.name}: {exc}", file=sys.stderr)

    note = [
        "# 方形封面来源说明",
        "",
        "本目录图片均为 512 × 512 PNG，文件名与 ROM 对应。",
        "",
        "## 标记说明",
        "",
        "- ✅ 原版方图，未裁切：使用对应游戏的原版 1:1 封面，仅统一输出尺寸。",
        "- ✅ 原版近方图，未裁切：原图近似 1:1，只轻微统一比例，没有裁切画面。",
        "- ✂️ 从原图裁切：没有找到合适的方形原版封面，从 GBA/ 原图中选择方形区域。",
        "",
        f"**统计：{len(no_crop_entries)} 张使用原版方图/近方图（未裁切）；{len(cropped_entries)} 张由原图裁切。**",
        "",
        "## ✅ 原版方图 / 近方图：未裁切",
        "",
    ]
    for rom_name, source_name, label, near_square in no_crop_entries:
        note.append(f"- **{rom_name}** — {label}。源图：{source_name}")
    note.extend(["", "## ✂️ 从原始封面裁切", ""])
    for rom_name, source_name in cropped_entries:
        note.append(f"- **{rom_name}** — 从 {source_name} 裁切成正方形")
    note.extend([
        "",
        "来源库：[Libretro Nintendo - Game Boy Advance Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts)。少数未裁切方图使用同一游戏的其他地区原版封面；地区可能和本地汉化 ROM 不同。原始比例图片始终保留在 GBA/。",
        "",
    ])
    (DEST / "README.md").write_text("\n".join(note), encoding="utf-8")

    manifest = [
        "# ✅ 原版方图未裁切名单",
        "",
        "下列方形封面直接使用对应游戏的原版方形封面，没有裁切画面。输出统一调整到 512 × 512，仅作尺寸归一化。",
        "",
    ]
    for rom_name, source_name, label, near_square in no_crop_entries:
        if near_square:
            manifest.append(f"- ✅ **{rom_name}** — 原版近方图，未裁切，仅轻微统一比例。源图：{source_name}")
        else:
            manifest.append(f"- ✅ **{rom_name}** — 原版方图，未裁切。源图：{source_name}")
    manifest.extend([
        "",
        f"**合计：{len(no_crop_entries)} 张。** 其他 {len(cropped_entries)} 张来自原始比例封面的方形裁切，完整分类请查看 [README.md](README.md)。",
        "",
    ])
    (DEST / "原版方图未裁切名单.md").write_text("\n".join(manifest), encoding="utf-8")

    print(f"Done: {made}/{len(files)} square covers; {len(no_crop_entries)} original square/near-square, {len(cropped_entries)} cropped.")
    return 0 if made == len(files) else 1

if __name__ == "__main__":
    raise SystemExit(main())
