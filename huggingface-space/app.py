"""
MuseGAN 复调音乐生成器 - Hugging Face Space 主应用
支持文件上传、多语言界面、进度条显示
"""

import os
import sys
import time

# 强制刷新输出的诊断函数
def log(msg):
    """带时间戳的日志输出，强制刷新"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

# 启动诊断
log("=" * 60)
log("MUSEGAN APP STARTING...")
log(f"Python: {sys.version}")
log(f"Working dir: {os.getcwd()}")
log(f"Environment: {list(os.environ.keys())[:3]}...")
log("=" * 60)

# 逐步导入并记录
log("Importing os... [OK]")

log("Importing gradio...")
import gradio as gr
log("Gradio imported [OK]")

log("Importing numpy...")
import numpy as np
log("NumPy imported [OK]")

log("Importing tempfile...")
import tempfile
log("tempfile imported [OK]")

log("Importing typing...")
from typing import Optional, Tuple
log("typing imported [OK]")

log("Importing config...")
from config import (
    N_TRACKS, N_BARS, DEFAULT_TEMPERATURE, DEFAULT_THRESHOLD,
    TEMPERATURE_MIN, TEMPERATURE_MAX, TEMPERATURE_STEP,
    THRESHOLD_MIN, THRESHOLD_MAX, THRESHOLD_STEP,
    MAX_FILE_SIZE, ALLOWED_EXTENSIONS, TRACK_CONFIG, DEFAULT_TEMPO
)
log("config imported [OK]")

log("Importing model_utils...")
from model_utils import load_model, generate_music
log("model_utils imported [OK]")

log("Importing midi_utils...")
from midi_utils import pianoroll_to_midi, create_multi_track_preview, get_midi_info
log("midi_utils imported [OK]")

log("Importing musicxml_utils...")
from musicxml_utils import (
    parse_musicxml_file, pianoroll_to_musicxml, 
    validate_musicxml
)
log("musicxml_utils imported [OK]")

log("Importing i18n...")
from i18n import get_text, get_all_texts, get_supported_languages
log("i18n imported [OK]")

log("All imports complete!")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProgressTracker:
    """进度跟踪器"""
    def __init__(self):
        self.progress = 0
        self.message = ""
    
    def update(self, progress: int, message: str):
        self.progress = progress
        self.message = message
        logger.info(f"Progress: {progress}% - {message}")


progress_tracker = ProgressTracker()


def validate_file(file) -> Tuple[bool, str]:
    """验证上传的文件"""
    if file is None:
        return True, ""
    
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        return False, get_text('error_size')
    
    filename = file.name if hasattr(file, 'name') else str(file)
    ext = os.path.splitext(filename.lower())[1]
    
    if ext not in ALLOWED_EXTENSIONS:
        return False, get_text('error_format')
    
    if ext in ['.musicxml', '.mxl']:
        with open(file if isinstance(file, str) else file.name, 'rb') as f:
            is_valid, msg = validate_musicxml(f.read(), filename)
        if not is_valid:
            return False, msg
    
    return True, ""


def extract_melody_seed(file_bytes: bytes, filename: str) -> Tuple[Optional[int], dict, Optional[np.ndarray]]:
    """
    从旋律文件提取特征并生成种子
    使用旋律的统计特征派生确定性种子
    
    Returns:
        seed: 派生的随机种子
        melody_info: 旋律信息字典
        melody_pianoroll: 解析后的旋律 pianoroll (N_BARS, N_STEPS, N_PITCHES) 或 None
    """
    import hashlib
    
    ext = os.path.splitext(filename.lower())[1]
    melody_info = {}
    melody_pianoroll = None
    
    print(f"[DEBUG] extract_melody_seed: filename={filename}, ext={ext}, file_size={len(file_bytes)} bytes")
    
    try:
        if ext in ['.musicxml', '.mxl']:
            print(f"[DEBUG] Calling parse_musicxml_file...")
            pianoroll, info = parse_musicxml_file(file_bytes, filename)
            print(f"[DEBUG] parse_musicxml_file returned: pianoroll.shape={pianoroll.shape if pianoroll is not None else None}, info={info}")
            melody_info = info
            melody_pianoroll = pianoroll
            # 使用音符数量和平均音高计算种子
            if pianoroll is not None and pianoroll.size > 0:
                note_count = int(np.sum(pianoroll > 0))
                active_pitches = np.where(np.sum(pianoroll, axis=(0, 1)) > 0)[0]
                avg_pitch = float(np.mean(active_pitches)) if len(active_pitches) > 0 else 60
                seed_str = f"{filename}_{note_count}_{avg_pitch:.1f}"
                seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
                print(f"[DEBUG] Generated seed: {seed}, note_count: {note_count}, avg_pitch: {avg_pitch:.1f}")
                return seed, melody_info, melody_pianoroll
        else:
            # MIDI 文件
            from midi_utils import midi_to_pianoroll
            midi_info = get_midi_info(file_bytes)
            melody_info = midi_info
            melody_pianoroll = midi_to_pianoroll(file_bytes, track_idx=0)
            if midi_info and 'num_notes' in midi_info:
                seed_str = f"{filename}_{midi_info['num_notes']}_{midi_info.get('duration', 0):.1f}"
                seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
                return seed, melody_info, melody_pianoroll
    except Exception as e:
        logger.warning(f"Failed to extract melody seed: {e}")
        import traceback
        traceback.print_exc()
    
    return None, melody_info, melody_pianoroll


def merge_melody_to_accompaniment(
    generated_pianoroll: np.ndarray,
    melody_pianoroll: np.ndarray,
    melody_track_idx: int = 1
) -> np.ndarray:
    """
    将输入旋律合并到生成的伴奏中
    原始旋律完整保留，直接覆盖到指定轨道
    
    Args:
        generated_pianoroll: 生成的 pianoroll (N_BARS, N_STEPS, N_PITCHES, N_TRACKS)
        melody_pianoroll: 输入旋律 pianoroll (N_BARS, N_STEPS, N_PITCHES)
        melody_track_idx: 旋律要放置的轨道索引 (默认 1 = Piano)
    
    Returns:
        合并后的 pianoroll，旋律完整保留，伴奏在时间上对齐
    """
    result = generated_pianoroll.copy()
    
    if melody_pianoroll is None or melody_pianoroll.size == 0:
        logger.warning("No melody to merge")
        return result
    
    # 直接用原始旋律覆盖 Piano 轨道
    # 这样保证原始旋律完全不变，时间完全对齐
    result[..., melody_track_idx] = melody_pianoroll
    
    # 统计信息
    melody_notes = int(np.sum(melody_pianoroll > 0))
    logger.info(f"✅ Merged {melody_notes} melody notes to track {melody_track_idx} ({TRACK_CONFIG[melody_track_idx]['name']})")
    
    return result


def generate_music_callback(
    file,
    seed: Optional[int],
    temperature: float,
    threshold: float,
    lang: str
) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
    """生成音乐回调函数
    
    方案B实现：
    1. 解析输入旋律 → 保留原始 pianoroll
    2. AI 生成 5 轨道伴奏
    3. 用原始旋律覆盖 Piano 轨道
    4. 输出：原旋律(不变) + AI伴奏(对齐)
    """
    texts = get_all_texts(lang)
    melody_seed = None
    melody_info = {}
    melody_pianoroll = None
    
    try:
        progress_tracker.update(10, texts['progress_parsing'])
        
        if file is not None:
            try:
                filename = file.name if hasattr(file, 'name') else str(file)
                with open(file if isinstance(file, str) else file.name, 'rb') as f:
                    file_bytes = f.read()
                
                # 从旋律文件提取种子、信息和 pianoroll（保留原始旋律）
                melody_seed, melody_info, melody_pianoroll = extract_melody_seed(file_bytes, filename)
                logger.info(f"Parsed melody: {melody_info}, derived seed: {melody_seed}")
                if melody_pianoroll is not None:
                    logger.info(f"Melody pianoroll shape: {melody_pianoroll.shape}, notes: {int(np.sum(melody_pianoroll > 0))}")
                
                # 如果用户没有指定种子，使用旋律派生的种子
                if seed is None or seed <= 0:
                    seed = melody_seed
                    
            except Exception as e:
                logger.warning(f"Failed to parse file: {e}")
        
        progress_tracker.update(30, texts['progress_loading'])
        
        load_model()
        
        progress_tracker.update(60, texts['progress_generating'])
        
        # 确定目标小节数：从输入旋律获取，或使用默认值
        target_n_bars = N_BARS
        if melody_pianoroll is not None and melody_pianoroll.size > 0:
            target_n_bars = melody_pianoroll.shape[0]
            logger.info(f"Target bars from melody: {target_n_bars}")
        
        raw_output, binary_output = generate_music(
            seed=seed if seed and seed > 0 else None,
            temperature=temperature,
            threshold=threshold,
            n_bars=target_n_bars
        )
        
        # 方案B：将输入旋律合并到 Piano 轨道
        # 原始旋律完整保留，与伴奏在时间和乐谱上对齐
        if melody_pianoroll is not None and melody_pianoroll.size > 0:
            progress_tracker.update(75, "Merging melody with accompaniment...")
            binary_output = merge_melody_to_accompaniment(binary_output, melody_pianoroll, melody_track_idx=1)
            logger.info("✅ Melody merged with AI accompaniment (time-aligned)")
        
        progress_tracker.update(90, texts['progress_converting'])
        
        midi_bytes = pianoroll_to_midi(binary_output, DEFAULT_TEMPO, n_bars=target_n_bars)
        midi_file = tempfile.NamedTemporaryFile(suffix='.mid', delete=False)
        midi_file.write(midi_bytes)
        midi_file.close()
        
        musicxml_bytes = pianoroll_to_musicxml(binary_output, DEFAULT_TEMPO, n_bars=target_n_bars)
        musicxml_file = tempfile.NamedTemporaryFile(suffix='.musicxml', delete=False)
        musicxml_file.write(musicxml_bytes)
        musicxml_file.close()
        
        preview_file = create_multi_track_preview(binary_output)
        
        progress_tracker.update(100, texts['success'])
        
        num_notes = int(np.sum(binary_output))
        actual_n_bars = binary_output.shape[0]
        
        # 构建信息文本
        info_parts = [f"### {texts['stats']}"]
        info_parts.append(f"- **{texts['num_notes']}**: {num_notes}")
        info_parts.append(f"- **{texts['duration']}**: {actual_n_bars * 4} beats ({actual_n_bars} bars)")
        info_parts.append(f"- **{texts['tracks']}**: {N_TRACKS}")
        
        # 显示种子信息
        if seed:
            info_parts.append(f"- **Seed**: {seed}")
        
        # 显示旋律信息
        if melody_info:
            info_parts.append(f"\n### 🎵 Input Melody (Preserved)")
            if 'num_notes' in melody_info:
                info_parts.append(f"- **Notes**: {melody_info['num_notes']}")
            if 'duration' in melody_info:
                info_parts.append(f"- **Duration**: {melody_info['duration']:.1f} beats")
            if melody_seed:
                info_parts.append(f"- **Derived Seed**: {melody_seed}")
            info_parts.append(f"- **Track**: Piano (Track 2)")
        
        # 显示伴奏信息
        if melody_pianoroll is not None:
            accompaniment_notes = num_notes - int(np.sum(melody_pianoroll > 0))
            info_parts.append(f"\n### 🎹 AI Accompaniment")
            info_parts.append(f"- **Tracks**: Drums, Guitar, Bass, Strings")
            info_parts.append(f"- **Accompaniment Notes**: {accompaniment_notes}")
        
        info_text = "\n".join(info_parts)
        
        return (
            midi_file.name,
            musicxml_file.name,
            preview_file,
            info_text
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return None, None, None, f"❌ {texts['error']}: {str(e)}"


def create_interface() -> gr.Blocks:
    """创建 Gradio 界面"""
    log("Creating interface...")
    
    # 获取默认语言的文本
    default_texts = get_all_texts('en')
    
    # 使用默认主题，避免网络加载自定义字体
    with gr.Blocks(
        title=default_texts['title'],
        theme=gr.themes.Default()
    ) as demo:
        
        # Header
        header_md = gr.Markdown(
            f"# 🎵 {default_texts['title']}\n\n### {default_texts['subtitle']}\n\n{default_texts['description']}"
        )
        
        with gr.Row():
            lang_selector = gr.Dropdown(
                choices=[('English', 'en'), ('中文', 'zh'), ('日本語', 'ja')],
                value='en',
                label="Language / 语言 / 言語",
                interactive=True
            )
        
        with gr.Row():
            with gr.Column(scale=1):
                upload_section = gr.Markdown(f"### 📁 {default_texts['upload_section']}")
                
                file_input = gr.File(
                    label=default_texts['upload_label'],
                    file_types=['.musicxml', '.mxl', '.mid', '.midi'],
                    type="filepath"
                )
                
                upload_formats_md = gr.Markdown(default_texts['upload_formats'])
                
                params_section = gr.Markdown(f"### ⚙️ {default_texts['params_section']}")
                
                seed_input = gr.Number(
                    label=f"🎲 {default_texts['seed_label']}",
                    value=None,
                    precision=0,
                    info=default_texts['seed_info']
                )
                
                temperature_slider = gr.Slider(
                    label=f"🌡️ {default_texts['temperature_label']}",
                    minimum=TEMPERATURE_MIN,
                    maximum=TEMPERATURE_MAX,
                    value=DEFAULT_TEMPERATURE,
                    step=TEMPERATURE_STEP,
                    info=default_texts['temperature_info']
                )
                
                threshold_slider = gr.Slider(
                    label=f"📊 {default_texts['threshold_label']}",
                    minimum=THRESHOLD_MIN,
                    maximum=THRESHOLD_MAX,
                    value=DEFAULT_THRESHOLD,
                    step=THRESHOLD_STEP,
                    info=default_texts['threshold_info']
                )
                
                generate_btn = gr.Button(
                    f"🎹 {default_texts['generate_btn']}",
                    variant="primary",
                    size="lg"
                )
                
                status_output = gr.Textbox(
                    label=default_texts['status_label'],
                    value=default_texts['status_ready'],
                    interactive=False
                )
            
            with gr.Column(scale=1):
                download_section = gr.Markdown(f"### 📥 {default_texts['download_section']}")
                
                midi_output = gr.File(
                    label=default_texts['midi_label'],
                    file_types=['.mid']
                )
                
                musicxml_output = gr.File(
                    label=default_texts['musicxml_label'],
                    file_types=['.musicxml']
                )
                
                preview_section = gr.Markdown(f"### 🎹 {default_texts['preview_section']}")
                
                preview_output = gr.Image(
                    label=default_texts['preview_label'],
                    type="filepath"
                )
                
                info_output = gr.Markdown()
        
        quick_start_section = gr.Markdown(f"### 🎯 {default_texts['quick_start_section']}")
        gr.Examples(
            examples=[
                [None, 42, 1.0, 0.5],
                [None, 123, 0.8, 0.45],
                [None, None, 1.2, 0.5],
                [None, 999, 1.5, 0.55],
            ],
            inputs=[file_input, seed_input, temperature_slider, threshold_slider],
            label=default_texts['preset_label']
        )
        
        # Usage section
        usage_section = gr.Markdown(f"---\n\n### 📖 {default_texts['usage_section']}\n\n{default_texts['usage_text']}\n\n### 🔧 {default_texts['params_section']}\n\n{default_texts['params_table']}\n\n### 🎹 {default_texts['tracks_section']}\n\n{default_texts['tracks_text']}\n\n{default_texts['footer']}")
        
        # 语言切换回调函数 - 使用 gr.update() 更新组件属性
        def update_language(lang):
            texts = get_all_texts(lang)
            return [
                # header_md
                gr.update(value=f"# 🎵 {texts['title']}\n\n### {texts['subtitle']}\n\n{texts['description']}"),
                # upload_section
                gr.update(value=f"### 📁 {texts['upload_section']}"),
                # file_input
                gr.update(label=texts['upload_label']),
                # upload_formats_md
                gr.update(value=texts['upload_formats']),
                # params_section
                gr.update(value=f"### ⚙️ {texts['params_section']}"),
                # seed_input (label)
                gr.update(label=f"🎲 {texts['seed_label']}", info=texts['seed_info']),
                # temperature_slider (label)
                gr.update(label=f"🌡️ {texts['temperature_label']}", info=texts['temperature_info']),
                # threshold_slider (label)
                gr.update(label=f"📊 {texts['threshold_label']}", info=texts['threshold_info']),
                # generate_btn
                gr.update(value=f"🎹 {texts['generate_btn']}"),
                # status_output
                gr.update(label=texts['status_label'], value=texts['status_ready']),
                # download_section
                gr.update(value=f"### 📥 {texts['download_section']}"),
                # midi_output
                gr.update(label=texts['midi_label']),
                # musicxml_output
                gr.update(label=texts['musicxml_label']),
                # preview_section
                gr.update(value=f"### 🎹 {texts['preview_section']}"),
                # preview_output
                gr.update(label=texts['preview_label']),
                # quick_start_section
                gr.update(value=f"### 🎯 {texts['quick_start_section']}"),
                # usage_section
                gr.update(value=f"---\n\n### 📖 {texts['usage_section']}\n\n{texts['usage_text']}\n\n### 🔧 {texts['params_section']}\n\n{texts['params_table']}\n\n### 🎹 {texts['tracks_section']}\n\n{texts['tracks_text']}\n\n{texts['footer']}"),
            ]
        
        # 绑定语言切换事件
        lang_selector.change(
            fn=update_language,
            inputs=[lang_selector],
            outputs=[
                header_md,
                upload_section,
                file_input,
                upload_formats_md,
                params_section,
                seed_input,
                temperature_slider,
                threshold_slider,
                generate_btn,
                status_output,
                download_section,
                midi_output,
                musicxml_output,
                preview_section,
                preview_output,
                quick_start_section,
                usage_section,
            ]
        )
        
        generate_btn.click(
            fn=generate_music_callback,
            inputs=[file_input, seed_input, temperature_slider, threshold_slider, lang_selector],
            outputs=[midi_output, musicxml_output, preview_output, info_output]
        )
    
    log("Interface created successfully")
    return demo


if __name__ == "__main__":
    log("=" * 60)
    log("MAIN: Creating Gradio interface...")
    try:
        demo = create_interface()
        log("MAIN: Interface created successfully")
        log("MAIN: Launching server on 0.0.0.0:7860...")
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True
        )
    except Exception as e:
        log(f"MAIN: FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
