# NDS 方形封面来源说明

所有方形封面统一输出为 512 × 512 PNG，文件名与 ROM 对应。原始比例封面保存在 NDS/，不会被覆盖。

本目录分为两个子文件夹：Original/ 存放画面未裁切的原图方图/近方图（特殊替代图会单独注明）；Cropped/ 存放从原比例封面中选择方形区域的版本。来源网址集中记录在 Sources/cover_sources.csv。

自动裁切使用开源 SmartCrop.py，根据画面细节和构图线索选择窗口，并不保证每张人物构图都完美，建议重点检查人物脸部和边缘文字。

**统计：0 张原图本身为正方形；1 张为近方形（保留完整画面并轻微统一尺寸）；17 张从原版比例封面裁切。**

## Original/：原图未裁切

- `Original/塞尔达传说四支剑 25周年纪念版(简)(Monado汉化组)(108Mb).png` — 662×640；保留近方形，轻微统一比例社区替代封面。未找到原版零售盒绘；使用社区制作的封面图，不属于官方原版实体盒绘。

## Cropped/：内容感知裁切

- `Cropped/万能先生的泡妞生活 夜晚把妹实战篇 6.18修正版(JP)(星组)(256Mb).png` — 原图 512×453；从对应原版比例封面裁切。来源：Dekiru Otoko no Mote Life - Yoru no Mote Jissen Hen (Japan).png
- `Cropped/为你而生 完整汉化版(EU)(兔友汉化组)(1024Mb).png` — 原图 512×465；从对应原版比例封面裁切。来源：Project Rub (Europe) (En,Ja,Fr,De,Es,It).png
- `Cropped/侠盗车手 血战唐人街 1.8(EU)(远离汉化组)(1024Mb).png` — 原图 512×460；从对应原版比例封面裁切。来源：Grand Theft Auto - Chinatown Wars (Europe) (En,Fr,De,Es,It).png
- `Cropped/刺客信条2 英文字幕+中文配音最终版(fciq配音小组)(512Mb).png` — 原图 512×450；从对应原版比例封面裁切。来源：Assassin's Creed II - Discovery (USA) (En,Fr,Es) (NDSi Enhanced).png
- `Cropped/北欧女神 负罪者 V2(JP)(ACG汉化组)(1024Mb).png` — 原图 512×456；从对应原版比例封面裁切。来源：Valkyrie Profile - Toga o Seou Mono (Japan).png
- `Cropped/塞尔达传说 大地的汽笛(简)1.1(US)(FCU汉化组和兔友汉化组)(1024Mb).png` — 原图 512×458；从对应原版比例封面裁切。来源：Legend of Zelda, The - Spirit Tracks (USA) (En,Fr,Es).png
- `Cropped/塞尔达传说 幻影沙漏 修正版(简)(JP)(巴士汉化组)(512Mb).png` — 原图 512×462；从对应原版比例封面裁切。来源：Zelda no Densetsu - Mugen no Sunadokei (Japan).png
- `Cropped/大剑 银眼的魔女(JP)(CG汉化组)(1024Mb).png` — 原图 512×457；从对应原版比例封面裁切。来源：Claymore - Gingan no Majo (Japan).png
- `Cropped/守护甜心！兴高采烈！甜心旋律(JP)(兔友汉化组)(1024Mb).png` — 原图 500×450；从对应原版比例封面裁切。来源：Shugo Chara! - Nori Nori! CharanaRhythm (Japan).png
- `Cropped/恋爱布丁 恋爱大冒险！(JP)(SOMA汉化组)(256Mb).png` — 原图 512×460；从对应原版比例封面裁切。来源：Koisuru Purin! - Koi wa Daibouken! Dr. Kanmi no Yabou! (Japan).png
- `Cropped/欢迎回来！小机器人！开心富裕大扫除！ 1.1(JP)(兔友汉化组)(512Mb).png` — 原图 512×458；从对应原版比例封面裁切。来源：Okaeri! Chibi-Robo! - Happy Rich Oosouji! (Japan).png
- `Cropped/爱丽丝梦游仙境(US)(兔友汉化组)(512Mb).png` — 原图 512×459；从对应原版比例封面裁切。来源：Alice in Wonderland (USA) (En,Fr,Es) (NDSi Enhanced).png
- `Cropped/盗贼皇女(JP)(ACG汉化组)(512Mb).png` — 原图 500×450；从对应原版比例封面裁切。来源：Steal Princess - Touzoku Koujo (Japan) [b].png
- `Cropped/绿野仙踪奇遇记 大字体完全汉化v1.1(JP)(OREZERO)(1024Mb).png` — 原图 500×450；从对应原版比例封面裁切。来源：Riz-Zoawd (Japan).png
- `Cropped/美少女梦工场4DS 特别版 (繁)全文本汉化版 1.1(JP)(joyful)(1024Mb).png` — 原图 500×450；从对应原版比例封面裁切。来源：Princess Maker 4 - Special Edition (Japan).png
- `Cropped/集合！卡比 v20200227(R4TT补丁版)(简)(JP)(那个汉化组)(512Mb).png` — 原图 512×450；从对应原版比例封面裁切。来源：Atsumete! Kirby (Japan).png
- `Cropped/鬼太郎 妖怪大激战(JP)(CG汉化组)(256Mb).png` — 原图 512×462；从对应原版比例封面裁切。来源：Gegege no Kitarou - Youkai Daigekisen (Japan).png

算法来源：[SmartCrop.py](https://github.com/smartcrop/smartcrop.py)。画面自动裁切可能舍弃边缘文字、标志或人物的一部分；如有单张构图不理想，建议针对该图手动调整。
