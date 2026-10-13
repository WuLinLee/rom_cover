#!/usr/bin/env python3
"""Build a separate 1:1 cover set from the original images in GBA/.

The originals in GBA/ are never changed. Already-square images are preserved.
Other images are cropped around a saliency-weighted, centre-biased focal area.
All outputs are normalized to 512x512 PNGs.
"""
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "GBA"
DEST = ROOT / "GBA_Square"
SIZE = 512


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


def square_cover(path):
    im = ImageOps.exif_transpose(Image.open(path))
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "transparency" in im.info else "RGB")
    width, height = im.size
    if width != height:
        scale = min(1.0, 512.0 / max(width, height))
        analysis = im.convert("RGB")
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
        im = im.crop((left, top, left + side, top + side))
    return im.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


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
    made = 0
    for path in files:
        try:
            out = DEST / (path.stem + ".png")
            square_cover(path).save(out, format="PNG", optimize=True)
            made += 1
            print(f"Created {out.relative_to(ROOT)}")
        except Exception as exc:
            print(f"ERROR: {path.name}: {exc}", file=sys.stderr)
    print(f"Done: {made}/{len(files)} square covers in {DEST.relative_to(ROOT)}")
    return 0 if made == len(files) else 1


if __name__ == "__main__":
    raise SystemExit(main())
