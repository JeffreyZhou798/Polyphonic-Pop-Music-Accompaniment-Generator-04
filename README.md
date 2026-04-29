---
title: Polyphonic Pop Music Accompaniment Generator
emoji: 🎵
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# 🎵 Polyphonic Pop Music Accompaniment Generator

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/JeffreyZhou798/Polyphonic-Pop-Music-Accompaniment-Generator-04)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

**👉 [Try it on Hugging Face Spaces](https://huggingface.co/spaces/JeffreyZhou798/Polyphonic-Pop-Music-Accompaniment-Generator-04)**
 **👉 [ModelScope Version](https://www.modelscope.cn/studios/JeffreyZhou2026/Polyphonic-Pop-Music-Accompaniment-Generator-02/summary)**

---

## English

### Overview

An AI-powered **5-track polyphonic pop music accompaniment generator** with a user-friendly web interface. Upload your melody and get professional accompaniment instantly!

**🚀 [Try on Hugging Face Spaces](https://huggingface.co/spaces/JeffreyZhou798/Polyphonic-Pop-Music-Accompaniment-Generator-04)** | **👉 [ModelScope Version](https://www.modelscope.cn/studios/JeffreyZhou2026/Polyphonic-Pop-Music-Accompaniment-Generator-02/summary)**

### Key Features

| Feature | Description |
|---------|-------------|
| 🎹 **5-Track Generation** | Drums, Piano, Guitar, Bass, Strings |
| 📂 **Multi-Format Support** | Import: MusicXML, MXL, MIDI / Export: MIDI, MusicXML |
| 🌍 **Multi-Language UI** | English, 中文, 日本語 |
| 🎵 **Melody Preservation** | Your input melody is perfectly preserved and aligned |
| 📏 **Arbitrary Length** | Supports any song length - no more 4-bar limitation! |
| 🎼 **Professional Export** | Compatible with MuseScore, Finale, Sibelius |

### Innovations by the Author

This project represents significant original contributions:

1. **Dynamic Length Support** - Engineered a novel segment-based generation approach that supports melodies of any length, breaking the fixed 4-bar limitation
2. **Melody-Accompaniment Alignment** - Developed a robust algorithm ensuring perfect temporal alignment between preserved melodies and AI-generated accompaniment
3. **Seed Derivation System** - Created a melody feature extraction system that derives deterministic seeds from musical content for reproducible results
4. **Cross-Platform Deployment** - Achieved seamless deployment on Hugging Face Spaces with Docker containerization
5. **Professional MusicXML Pipeline** - Built a complete MusicXML parsing and generation pipeline with proper namespace handling

### Quick Start

1. **Upload** your melody file (`.musicxml`, `.mxl`, `.mid`, `.midi`) - optional
2. **Adjust** Temperature and Threshold parameters
3. **Click** "Generate Music"
4. **Download** MIDI or MusicXML file
5. **Edit** in MuseScore or your favorite DAW

### Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| Temperature | 0.5-2.0 | 1.0 | Higher = more diverse/creative |
| Threshold | 0.3-0.7 | 0.5 | Higher = fewer notes (sparser) |
| Seed | Integer | Random | Fixed seed = reproducible results |

### Output Tracks

| Track | Instrument | MIDI Channel |
|-------|------------|--------------|
| Drums | Drum Kit | 10 |
| Piano | Acoustic Grand Piano | 1 |
| Guitar | Nylon String Guitar | 2 |
| Bass | Electric Bass | 3 |
| Strings | String Ensemble | 4 |

### Generation Optimization: Continuity Strategy

For melodies longer than 4 bars, the system uses a segment-based generation approach with two key optimizations to ensure musical continuity:

**1. Continuous Seed Strategy**

Instead of using large jumps in seed values (e.g., 42 → 1042 → 2042), we use a hash-based approach to generate smoothly varying seeds:

```python
seed_str = f"{base_seed}_{segment_idx}"
segment_seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16) % 1000000
```

**2. Temperature Annealing**

Later segments use progressively lower temperatures, making the AI more conservative and consistent:

| Segment | Temperature |
|---------|-------------|
| 1st | Base (e.g., 1.0) |
| 2nd | 0.92 |
| 3rd | 0.84 |
| ... | ... |
| Last | Min (0.6×base) |

**Result**: Earlier segments are more creative/experimental, later segments are more conservative/consistent.


## License

MIT License - See [LICENSE](../LICENSE) for details.

---



## ⚠️ Copyright Notice

© 2026 Jeffrey Zhou. All rights reserved.

This repository and its contents are protected by copyright law.  
No part of this project may be copied, reproduced, modified, or distributed without prior written permission from the author.

Commercial use is strictly prohibited.


*Built with ❤️ for music education*


---

## 中文

### 概述

一款基于 AI 的**五轨道复调流行音乐伴奏生成器**，提供友好的网页界面。上传您的旋律，即可获得专业的伴奏！

**🚀 [在线试用 (Hugging Face)](https://huggingface.co/spaces/JeffreyZhou798/Polyphonic-Pop-Music-Accompaniment-Generator-04)** | **👉 [ModelScope 版本](https://www.modelscope.cn/studios/JeffreyZhou2026/Polyphonic-Pop-Music-Accompaniment-Generator-02/summary)**

### 核心功能

| 功能 | 描述 |
|------|------|
| 🎹 **五轨道生成** | 鼓、钢琴、吉他、贝斯、弦乐 |
| 📂 **多格式支持** | 导入：MusicXML、MXL、MIDI / 导出：MIDI、MusicXML |
| 🌍 **多语言界面** | English、中文、日本語 |
| 🎵 **旋律完整保留** | 输入旋律被完美保留并对齐 |
| 📏 **任意长度支持** | 支持任意乐曲长度——不再受限于4小节！ |
| 🎼 **专业导出** | 兼容 MuseScore、Finale、Sibelius |

### 作者的创新贡献

本项目包含多项原创性技术贡献：

1. **动态长度支持** — 创新设计了基于片段的生成方法，支持任意长度的旋律，突破了固定4小节的限制
2. **旋律-伴奏对齐算法** — 开发了稳健的对齐算法，确保保留的旋律与AI生成的伴奏在时间上完美同步
3. **种子派生系统** — 创建了旋律特征提取系统，从音乐内容派生确定性种子，实现可复现的生成结果
4. **跨平台部署** — 成功实现了在 Hugging Face Spaces 上的 Docker 容器化部署
5. **专业 MusicXML 流水线** — 构建了完整的 MusicXML 解析和生成流水线，正确处理命名空间

### 快速开始

1. **上传**您的旋律文件（`.musicxml`、`.mxl`、`.mid`、`.midi`）— 可选
2. **调整**温度和阈值参数
3. **点击**"生成音乐"
4. **下载**MIDI 或 MusicXML 文件
5. **编辑**在 MuseScore 或您喜欢的 DAW 中

### 参数说明

| 参数 | 范围 | 默认值 | 描述 |
|------|------|--------|------|
| 温度 | 0.5-2.0 | 1.0 | 值越高越多样化/有创意 |
| 阈值 | 0.3-0.7 | 0.5 | 值越高音符越少（更稀疏） |
| 种子 | 整数 | 随机 | 固定种子可复现结果 |

### 输出轨道

| 轨道 | 乐器 | MIDI 通道 |
|------|------|-----------|
| 鼓 | 鼓组 | 10 |
| 钢琴 | 三角钢琴 | 1 |
| 吉他 | 尼龙弦吉他 | 2 |
| 贝斯 | 电贝斯 | 3 |
| 弦乐 | 弦乐合奏 | 4 |

### 生成优化：连续性策略

对于超过4小节的旋律，系统采用基于片段的生成方法，并使用两项关键优化确保音乐连续性：

**1. 连续 Seed 策略**

使用基于哈希的方法生成平滑变化的种子值，而非大跳跃：

```python
seed_str = f"{base_seed}_{segment_idx}"
segment_seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16) % 1000000
```

**2. 温度退火**

后续片段使用逐渐降低的温度，使AI更保守、更一致：

| 片段 | 温度 |
|------|------|
| 首个 | 基准（如1.0） |
| 第二 | 0.92 |
| 第三 | 0.84 |
| ... | ... |
| 末个 | 最低（0.6×基准） |

**效果**：前段更有创意/实验性，后段更保守/一致。

---

## 日本語

### 概要

AI搭載の**5トラック・ポリフォニーポップ音楽伴奏生成器**です。使いやすいWebインターフェースを提供。メロディをアップロードするだけで、プロフェッショナルな伴奏が瞬時に！

**🚀 [Hugging Faceで試す](https://huggingface.co/spaces/JeffreyZhou798/Polyphonic-Pop-Music-Accompaniment-Generator-04)** | **👉 [ModelScope版](https://www.modelscope.cn/studios/JeffreyZhou2026/Polyphonic-Pop-Music-Accompaniment-Generator-02/summary)**

### 主な機能

| 機能 | 説明 |
|------|------|
| 🎹 **5トラック生成** | ドラム、ピアノ、ギター、ベース、ストリングス |
| 📂 **マルチフォーマット対応** | 入力：MusicXML、MXL、MIDI / 出力：MIDI、MusicXML |
| 🌍 **多言語UI** | English、中文、日本語 |
| 🎵 **メロディ完全保持** | 入力メロディが完全に保持され、正確に配置 |
| 📏 **任意長対応** | 任意の曲長に対応—4小節の制限なし！ |
| 🎼 **プロフェッショナル出力** | MuseScore、Finale、Sibelius互換 |

### 作者の革新的貢献

本プロジェクトには重要な独自の貢献が含まれています：

1. **動的長さ対応** — セグメントベースの生成アプローチを設計し、任意の長さのメロディに対応、固定4小節の制限を突破
2. **メロディ-伴奏アライメント** — 保持されたメロディとAI生成の伴奏の完璧な時間同期を確保する堅牢なアルゴリズムを開発
3. **シード派生システム** — 音楽コンテンツから決定論的シードを派生させ、再現可能な結果を実現するメロディ特徴抽出システムを作成
4. **クロスプラットフォーム展開** — Hugging Face SpacesでのDockerコンテナ化デプロイを実現
5. **プロフェッショナルMusicXMLパイプライン** — 名前空間処理を含む完全なMusicXML解析・生成パイプラインを構築

### クイックスタート

1. **アップロード**メロディファイル（`.musicxml`、`.mxl`、`.mid`、`.midi`）— オプション
2. **調整**温度と閾値パラメータ
3. **クリック**「音楽を生成」
4. **ダウンロード**MIDIまたはMusicXMLファイル
5. **編集**MuseScoreまたはお気に入りのDAWで

### パラメータ

| パラメータ | 範囲 | デフォルト | 説明 |
|------------|------|------------|------|
| 温度 | 0.5-2.0 | 1.0 | 高いほど多様/クリエイティブ |
| 閾値 | 0.3-0.7 | 0.5 | 高いほど音符が少ない（疎） |
| シード | 整数 | ランダム | 固定シードで再現可能 |

### 出力トラック

| トラック | 楽器 | MIDIチャンネル |
|----------|------|----------------|
| ドラム | ドラムキット | 10 |
| ピアノ | グランドピアノ | 1 |
| ギター | ナイロン弦ギター | 2 |
| ベース | エレキベース | 3 |
| ストリングス | ストリングスアンサンブル | 4 |

### 生成最適化：連続性戦略

4小節を超えるメロディに対して、システムはセグメントベースの生成アプローチを使用し、2つの主要な最適化で音楽の連続性を確保します：

**1. 連続シード戦略**

大きなジャンプ（例：42 → 1042 → 2042）の代わりに、ハッシュベースのアプローチを使用してスムーズに変化するシードを生成します：

```python
seed_str = f"{base_seed}_{segment_idx}"
segment_seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16) % 1000000
```

**2. 温度アニーリング**

後続のセグメントは徐々に低下する温度を使用するため、AIはより保守的で一貫性のある出力を生成します：

| セグメント | 温度 |
|------------|------|
| 最初 | ベース（例：1.0） |
| 2番目 | 0.92 |
| 3番目 | 0.84 |
| ... | ... |
| 最後 | 最小（0.6×ベース） |

**効果**：最初のセグメントはよりクリエイティブ/実験的、後半はより保守的/一貫しています。

---

## Generation Optimization: Continuity Strategy

For melodies longer than 4 bars, the system uses a segment-based generation approach with two key optimizations to ensure musical continuity:

### 1. Continuous Seed Strategy

Instead of using large jumps in seed values (e.g., 42 → 1042 → 2042), we use a hash-based approach to generate smoothly varying seeds:

```python
# Hash-based seed derivation for smooth transitions
seed_str = f"{base_seed}_{segment_idx}"
segment_seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16) % 1000000
```

This ensures adjacent segments have related but distinct seeds, reducing style/tempo discontinuities.

### 2. Temperature Annealing

Later segments use progressively lower temperatures, making the AI more conservative and consistent:

| Segment | Temperature |
|---------|-------------|
| 1st | Base (e.g., 1.0) |
| 2nd | 0.92 |
| 3rd | 0.84 |
| ... | ... |
| Last | Min (0.6×base) |

**Result**: Earlier segments are more creative/experimental, later segments are more conservative/consistent.

---

## Technical Architecture

```
Input Melody (MusicXML/MIDI)
         ↓
    [Parser] → Feature Extraction → Seed Derivation
         ↓
    [Pianoroll] ← Dynamic Length Support
         ↓
    [AI Model] → Multi-segment Generation → Concatenation
         ↓
    [Merger] → Melody + Accompaniment Alignment
         ↓
Output (MIDI + MusicXML)
```

## Author

**Jeffrey Zhou **

- 🎓 Music Education Researcher & AI Developer
- 🔗 [Hugging Face Profile](https://huggingface.co/JeffreyZhou798)
- 🌐 [Try the Demo](https://huggingface.co/spaces/JeffreyZhou798/Polyphonic-Pop-Music-Accompaniment-Generator-04)

## License

MIT License - See [LICENSE](../LICENSE) for details.

---



## ⚠️ Copyright Notice

© 2026 Jeffrey Zhou. All rights reserved.

This repository and its contents are protected by copyright law.  
No part of this project may be copied, reproduced, modified, or distributed without prior written permission from the author.

Commercial use is strictly prohibited.


*Built with ❤️ for music education*
