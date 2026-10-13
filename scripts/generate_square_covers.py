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

# Exact 1:1 original artworks found in the public GBA box-art collection.
# Only the square set uses these regional alternatives; GBA/ remains untouched.
SQUARE_ORIGINALS = {
    "公主同盟[狼狼小酷+流星落月](v20100811+NO.56修复)(简)(JP)(256Mb).png":
        "Yggdra Union - We'll Never Fight Alone (USA).png",
    "塞尔达传说 - 缩小帽[天使汉化组](日汉最终版v2005SP4)(简)(JP)(128Mb).png":
        "Legend of Zelda, The - The Minish Cap (USA).png",
    "星之卡比 - 镜之大迷宫[CGP](简)(JP)(128Mb).png":
        "Kirby _ The Amazing Mirror (USA).png",
    "约束之地 - 利维艾拉[PromisedLand](v1.05)[简](JP)(256Mb).png":
        "Riviera - The Promised Land (USA).png",
}


def load_square_original(filename):
    source_name = SQUARE_ORIGINALS.get(filename.name)
    if not source_name:
        return None
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
            return image.copy(), source_name
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
    square_sources = []
    made = 0

    for path in files:
        try:
            override = load_square_original(path)
            if override:
                cover, source_name = override
                output = cover.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
                square_sources.append(f"- {path.stem}: square original artwork {source_name}")
            else:
                with Image.open(path) as original:
                    output = crop_square(original.copy())
                square_sources.append(f"- {path.stem}: square crop from GBA/{path.name}")
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
        "有确切 1:1 原版封面可用时，方形版本优先采用该原版封面；若没有合适方图，则从 GBA/ 中原图按视觉细节与中心位置选取方形区域。原始比例封面始终保留在 GBA/。",
        "",
        "## 本次生成记录",
        "",
        *square_sources,
        "",
        "来源库：Libretro Nintendo - Game Boy Advance Named Boxarts。少数方形原版图是同一游戏的其他地区版本；GBA/ 原图未修改。",
        "",
    ]
    (DEST / "README.md").write_text("\n".join(note), encoding="utf-8")
    print(f"Done: {made}/{len(files)} square covers in {DEST.relative_to(ROOT)}")
    return 0 if made == len(files) else 1


if __name__ == "__main__":
    raise SystemExit(main())
