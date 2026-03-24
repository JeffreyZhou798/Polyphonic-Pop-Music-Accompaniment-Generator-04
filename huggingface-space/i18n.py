"""
国际化配置
支持英语、中文、日语
"""

from typing import Dict

DEFAULT_LANGUAGE = 'en'

TRANSLATIONS = {
    'en': {
        # Header
        'title': 'Polyphonic Pop Music Accompaniment Generator',
        'subtitle': 'AI-Powered Multi-Track Music Generation',
        'description': 'Generate 5-track polyphonic music (Drums, Piano, Guitar, Bass, Strings)',
        
        # Upload section
        'upload_section': 'Upload Melody (Optional)',
        'upload_label': 'Upload Melody File',
        'upload_formats': '''**Supported formats:**
- `.musicxml` - MusicXML format
- `.mxl` - Compressed MusicXML
- `.mid` / `.midi` - MIDI format

**Compatible with:** MuseScore, Finale, Sibelius''',
        
        # Parameters section
        'params_section': 'Generation Parameters',
        'seed_label': 'Random Seed (Optional)',
        'seed_info': 'Fixed seed for reproducible results',
        'temperature_label': 'Temperature',
        'temperature_info': 'Controls diversity. Higher = more random',
        'threshold_label': 'Threshold',
        'threshold_info': 'Note activation threshold. Higher = sparser',
        
        # Buttons and status
        'generate_btn': 'Generate Music',
        'status_label': 'Status',
        'status_ready': 'Ready to generate',
        
        # Output section
        'download_section': 'Download Results',
        'midi_label': 'MIDI File',
        'musicxml_label': 'MusicXML File',
        'preview_section': 'Piano Roll Preview',
        'preview_label': 'Preview',
        
        # Quick start
        'quick_start_section': 'Quick Start Presets',
        'preset_label': 'Preset Parameters',
        
        # Usage guide
        'usage_section': 'Usage',
        'usage_text': '''1. **Upload a melody** (optional): Upload a single-track melody file
2. **Adjust parameters**: Temperature and Threshold control the output
3. **Click Generate**: Wait 5-10 seconds
4. **Download**: Get MIDI or MusicXML file
5. **Edit in MuseScore**: Open the MusicXML file in MuseScore''',
        
        # Parameters table
        'params_table': '''| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| Temperature | 0.5-2.0 | 1.0 | Higher = more diverse |
| Threshold | 0.3-0.7 | 0.5 | Higher = fewer notes |
| Seed | Integer | Random | Fixed seed = reproducible |''',
        
        # Output tracks
        'tracks_section': 'Output Tracks',
        'tracks_text': '''- **Drums**: Drum kit (Channel 10)
- **Piano**: Acoustic Grand Piano
- **Guitar**: Nylon String Guitar
- **Bass**: Electric Bass
- **Strings**: String Ensemble''',
        
        # Footer
        'footer': '''---
Powered by [MuseGAN](https://github.com/salu133445/musegan) | 
Deployed on [Hugging Face Spaces](https://huggingface.co/spaces)''',
        
        # Progress messages
        'progress_parsing': 'Parsing file...',
        'progress_loading': 'Loading AI model...',
        'progress_generating': 'AI generating...',
        'progress_converting': 'Converting to output format...',
        'success': 'Generation Complete!',
        'error': 'Generation Failed',
        'error_format': 'Unsupported file format. Please upload .musicxml, .mxl, or .mid',
        'error_size': 'File too large. Maximum size is 10 MB',
        'error_parse': 'Failed to parse file. Please check the file format',
        
        # Statistics
        'stats': 'Statistics',
        'num_notes': 'Total Notes',
        'duration': 'Duration',
        'tracks': 'Tracks',
        
        # Input melody info
        'melody_preserved': 'Input Melody (Preserved)',
        'notes': 'Notes',
        'derived_seed': 'Derived Seed',
        'track': 'Track',
        'ai_accompaniment': 'AI Accompaniment',
        
        # Language
        'language': 'Language',
    },
    'zh': {
        # Header
        'title': '复调流行音乐伴奏生成器',
        'subtitle': 'AI 驱动的多声部音乐生成',
        'description': '生成 5 轨道复调音乐（鼓、钢琴、吉他、贝斯、弦乐）',
        
        # Upload section
        'upload_section': '上传旋律（可选）',
        'upload_label': '上传旋律文件',
        'upload_formats': '''**支持的格式：**
- `.musicxml` - MusicXML 格式
- `.mxl` - 压缩 MusicXML
- `.mid` / `.midi` - MIDI 格式

**兼容软件：** MuseScore、Finale、Sibelius''',
        
        # Parameters section
        'params_section': '生成参数',
        'seed_label': '随机种子（可选）',
        'seed_info': '固定种子可复现相同结果',
        'temperature_label': '温度',
        'temperature_info': '控制多样性，值越高越随机',
        'threshold_label': '阈值',
        'threshold_info': '音符激活阈值，值越高音符越稀疏',
        
        # Buttons and status
        'generate_btn': '生成音乐',
        'status_label': '状态',
        'status_ready': '准备生成',
        
        # Output section
        'download_section': '下载结果',
        'midi_label': 'MIDI 文件',
        'musicxml_label': 'MusicXML 文件',
        'preview_section': '钢琴卷帘预览',
        'preview_label': '预览',
        
        # Quick start
        'quick_start_section': '快速开始预设',
        'preset_label': '预设参数',
        
        # Usage guide
        'usage_section': '使用说明',
        'usage_text': '''1. **上传旋律**（可选）：上传单声部旋律文件
2. **调整参数**：温度和阈值控制输出结果
3. **点击生成**：等待 5-10 秒
4. **下载**：获取 MIDI 或 MusicXML 文件
5. **在 MuseScore 中编辑**：用 MuseScore 打开 MusicXML 文件''',
        
        # Parameters table
        'params_table': '''| 参数 | 范围 | 默认值 | 说明 |
|------|------|--------|------|
| 温度 | 0.5-2.0 | 1.0 | 值越高越多样化 |
| 阈值 | 0.3-0.7 | 0.5 | 值越高音符越少 |
| 种子 | 整数 | 随机 | 固定种子可复现 |''',
        
        # Output tracks
        'tracks_section': '输出轨道',
        'tracks_text': '''- **鼓**：鼓组（通道 10）
- **钢琴**：三角钢琴
- **吉他**：尼龙弦吉他
- **贝斯**：电贝斯
- **弦乐**：弦乐合奏''',
        
        # Footer
        'footer': '''---
由 [MuseGAN](https://github.com/salu133445/musegan) 提供支持 | 
部署于 [Hugging Face Spaces](https://huggingface.co/spaces)''',
        
        # Progress messages
        'progress_parsing': '正在解析文件...',
        'progress_loading': '正在加载 AI 模型...',
        'progress_generating': 'AI 生成中...',
        'progress_converting': '转换输出格式...',
        'success': '生成成功！',
        'error': '生成失败',
        'error_format': '不支持的文件格式，请上传 .musicxml, .mxl 或 .mid 文件',
        'error_size': '文件过大，最大支持 10 MB',
        'error_parse': '文件解析失败，请检查文件格式',
        
        # Statistics
        'stats': '统计信息',
        'num_notes': '总音符数',
        'duration': '时长',
        'tracks': '轨道数',
        
        # Input melody info
        'melody_preserved': '输入旋律（已保留）',
        'notes': '音符数',
        'derived_seed': '派生种子',
        'track': '轨道',
        'ai_accompaniment': 'AI 伴奏',
        
        # Language
        'language': '语言',
    },
    'ja': {
        # Header
        'title': 'ポリフォニーポップ音楽伴奏生成器',
        'subtitle': 'AI搭載マルチトラック音楽生成',
        'description': '5トラックのポリフォニー音楽を生成（ドラム、ピアノ、ギター、ベース、ストリングス）',
        
        # Upload section
        'upload_section': 'メロディをアップロード（オプション）',
        'upload_label': 'メロディファイルをアップロード',
        'upload_formats': '''**対応形式：**
- `.musicxml` - MusicXML形式
- `.mxl` - 圧縮MusicXML
- `.mid` / `.midi` - MIDI形式

**互換ソフト：** MuseScore、Finale、Sibelius''',
        
        # Parameters section
        'params_section': '生成パラメータ',
        'seed_label': 'ランダムシード（オプション）',
        'seed_info': '固定シードで再現可能な結果',
        'temperature_label': '温度',
        'temperature_info': '多様性を制御。高いほどランダム',
        'threshold_label': '閾値',
        'threshold_info': '音符アクティブ閾値。高いほど疎',
        
        # Buttons and status
        'generate_btn': '音楽を生成',
        'status_label': 'ステータス',
        'status_ready': '生成準備完了',
        
        # Output section
        'download_section': '結果をダウンロード',
        'midi_label': 'MIDIファイル',
        'musicxml_label': 'MusicXMLファイル',
        'preview_section': 'ピアノロールプレビュー',
        'preview_label': 'プレビュー',
        
        # Quick start
        'quick_start_section': 'クイックスタートプリセット',
        'preset_label': 'プリセットパラメータ',
        
        # Usage guide
        'usage_section': '使い方',
        'usage_text': '''1. **メロディをアップロード**（オプション）：単一トラックのメロディファイルをアップロード
2. **パラメータを調整**：温度と閾値で出力を制御
3. **生成をクリック**：5-10秒お待ちください
4. **ダウンロード**：MIDIまたはMusicXMLファイルを取得
5. **MuseScoreで編集**：MusicXMLファイルをMuseScoreで開く''',
        
        # Parameters table
        'params_table': '''| パラメータ | 範囲 | デフォルト | 説明 |
|------------|------|------------|------|
| 温度 | 0.5-2.0 | 1.0 | 高いほど多様 |
| 閾値 | 0.3-0.7 | 0.5 | 高いほど音符が少ない |
| シード | 整数 | ランダム | 固定シードで再現可能 |''',
        
        # Output tracks
        'tracks_section': '出力トラック',
        'tracks_text': '''- **ドラム**：ドラムキット（チャンネル10）
- **ピアノ**：グランドピアノ
- **ギター**：ナイロン弦ギター
- **ベース**：エレキベース
- **ストリングス**：ストリングスアンサンブル''',
        
        # Footer
        'footer': '''---
[MuseGAN](https://github.com/salu133445/musegan) による | 
[Hugging Face Spaces](https://huggingface.co/spaces) でデプロイ''',
        
        # Progress messages
        'progress_parsing': 'ファイルを解析中...',
        'progress_loading': 'AIモデルを読み込み中...',
        'progress_generating': 'AI生成中...',
        'progress_converting': '出力形式に変換中...',
        'success': '生成完了！',
        'error': '生成失敗',
        'error_format': 'サポートされていない形式です。.musicxml, .mxl, .mid をアップロードしてください',
        'error_size': 'ファイルが大きすぎます。最大10MBまで',
        'error_parse': 'ファイルの解析に失敗しました。形式を確認してください',
        
        # Statistics
        'stats': '統計情報',
        'num_notes': '総音符数',
        'duration': '長さ',
        'tracks': 'トラック数',
        
        # Input melody info
        'melody_preserved': '入力メロディ（保持）',
        'notes': '音符数',
        'derived_seed': '派生シード',
        'track': 'トラック',
        'ai_accompaniment': 'AI伴奏',
        
        # Language
        'language': '言語',
    }
}


def get_text(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """获取翻译文本"""
    if lang not in TRANSLATIONS:
        lang = DEFAULT_LANGUAGE
    return TRANSLATIONS[lang].get(key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))


def get_all_texts(lang: str = DEFAULT_LANGUAGE) -> Dict[str, str]:
    """获取所有翻译文本"""
    if lang not in TRANSLATIONS:
        lang = DEFAULT_LANGUAGE
    return TRANSLATIONS[lang].copy()


def get_supported_languages() -> list:
    """获取支持的语言列表"""
    return list(TRANSLATIONS.keys())
