#!/usr/bin/env python3
"""Build separate square covers from GBA/ without altering the originals.

Known square original artwork is preferred. Remaining covers use SmartCrop.py,
an open-source content-aware crop scorer. Every output is a 512x512 PNG.
"""
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import sys

import smartcrop
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


def crop_square(image):
    """Use SmartCrop.py to pick a content-aware 1:1 window from a non-square cover."""
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if "transparency" in image.info else "RGB")
    width, height = image.size
    if width == height:
        return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)

    side = min(width, height)
    try:
        # SmartCrop.py scores candidate windows using visual detail, edges,
        # saturation, skin-colour likelihood, and composition heuristics.
        analysis = image.convert("RGB")
        result = smartcrop.SmartCrop().crop(analysis, side, side)
        best = result.get("top_crop") or {}
        x = max(0, min(int(best.get("x", (width - side) // 2)), width - 1))
        y = max(0, min(int(best.get("y", (height - side) // 2)), height - 1))
        crop_width = max(1, min(int(best.get("width", side)), width - x))
        crop_height = max(1, min(int(best.get("height", side)), height - y))

        # SmartCrop may choose a slightly smaller or rounded crop. Convert its
        # selected window to a true square around the chosen composition.
        square_side = min(crop_width, crop_height)
        x += max(0, (crop_width - square_side) // 2)
        y += max(0, (crop_height - square_side) // 2)
        cropped = image.crop((x, y, x + square_side, y + square_side))
        return cropped.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    except Exception as exc:
        # Keep batch processing resilient; mark fallback clearly in CI logs.
        print(f"WARNING: SmartCrop failed for one image; using centre crop: {exc}", file=sys.stderr)
        x = (width - side) // 2
        y = (height - side) // 2
        cropped = image.crop((x, y, x + side, y + side))
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
        "- ✂️ 从原图裁切：没有找到合适的方形原版封面，使用 SmartCrop.py 从 GBA/ 原图中选择方形区域。",
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
        "原版封面来源库：[Libretro Nintendo - Game Boy Advance Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts)。需要裁切的封面使用开源 [SmartCrop.py](https://github.com/smartcrop/smartcrop.py) 算法选择画面区域；该算法使用细节、边缘、颜色饱和度、肤色线索和构图启发式，不是完美的人物识别，结果仍可能需要人工检查。少数未裁切方图使用同一游戏的其他地区原版封面；原始比例图片始终保留在 GBA/。",
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
