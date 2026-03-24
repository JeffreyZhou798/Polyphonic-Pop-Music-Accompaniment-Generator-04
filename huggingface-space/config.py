"""
MuseGAN 配置参数
"""

import os
import logging

logger = logging.getLogger(__name__)

# ==================== 版本信息 ====================
VERSION = "1.0.0"
BUILD_DATE = "2025-03-23"

# ==================== 模型配置 ====================
MODEL_PATH = "frozen_model.pb"
INPUT_NODE = "Placeholder:0"  # 潜在向量输入节点 (TF1.x checkpoint)
OUTPUT_NODE = "Model_2/Generator/merged_private/concat:0"  # 输出节点

# 备选输入节点（如果默认节点不存在）
INPUT_NODE_FALLBACKS = [
    "Placeholder:0",
    "Placeholder_1:0",
    "z:0",
    "z_latent:0",
    "latent:0",
    "input:0",
    "input_z:0",
    "noise:0",
    "random_input:0",
    "Generator/z:0",
]

# 备选输出节点（如果默认节点不存在）
OUTPUT_NODE_FALLBACKS = [
    "Model_2/Generator/merged_private/concat:0",
    "Model/Generator/merged_private/concat:0",
    "Generator/merged_private/concat:0",
    "generator/merged_private/concat_5:0",
    "concat_5:0",
    "concat:0",
    "output:0",
    "Generator/output:0",
]

# 模型输出维度
LATENT_DIM = 128      # 潜在向量维度
N_BARS = 4            # 小节数
N_STEPS = 48          # 每小节步数（12步/拍 × 4拍）
N_PITCHES = 84        # 音高范围 (MIDI 24-107)
N_TRACKS = 5          # 轨道数

# ==================== 轨道配置 ====================
TRACK_CONFIG = {
    0: {"name": "Drums", "program": 0, "is_drum": True, "channel": 9},
    1: {"name": "Piano", "program": 0, "is_drum": False, "channel": 0},
    2: {"name": "Guitar", "program": 25, "is_drum": False, "channel": 1},
    3: {"name": "Bass", "program": 33, "is_drum": False, "channel": 2},
    4: {"name": "Strings", "program": 48, "is_drum": False, "channel": 3},
}

# ==================== MIDI 配置 ====================
LOWEST_PITCH = 24     # 最低音高 (C1)
HIGHEST_PITCH = 107   # 最高音高 (B7)
DEFAULT_TEMPO = 120   # 默认速度 (BPM)
DEFAULT_VELOCITY = 80 # 默认力度

# ==================== 生成配置 ====================
DEFAULT_TEMPERATURE = 1.0
DEFAULT_THRESHOLD = 0.5
DEFAULT_SEED = None

# 温度范围
TEMPERATURE_MIN = 0.5
TEMPERATURE_MAX = 2.0
TEMPERATURE_STEP = 0.1

# 阈值范围
THRESHOLD_MIN = 0.3
THRESHOLD_MAX = 0.7
THRESHOLD_STEP = 0.05

# ==================== 文件上传配置 ====================
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = ['.musicxml', '.mxl', '.mid', '.midi']

# ==================== 语言配置 ====================
DEFAULT_LANGUAGE = 'en'
SUPPORTED_LANGUAGES = ['en', 'zh', 'ja']


# ==================== 模型验证 ====================
def validate_model_config() -> tuple:
    """
    验证模型配置是否正确
    返回: (is_valid, error_message)
    """
    # 检查模型文件是否存在
    if not os.path.exists(MODEL_PATH):
        return False, f"Model file not found: {MODEL_PATH}"
    
    # 检查模型文件大小
    model_size = os.path.getsize(MODEL_PATH)
    if model_size < 1024 * 1024:  # 小于 1MB
        return False, f"Model file too small: {model_size} bytes"
    
    logger.info(f"Model validation passed: {MODEL_PATH} ({model_size / 1024 / 1024:.1f} MB)")
    return True, ""


def get_model_info() -> dict:
    """获取模型信息"""
    info = {
        "model_path": MODEL_PATH,
        "input_node": INPUT_NODE,
        "output_node": OUTPUT_NODE,
        "latent_dim": LATENT_DIM,
        "n_bars": N_BARS,
        "n_steps": N_STEPS,
        "n_pitches": N_PITCHES,
        "n_tracks": N_TRACKS,
        "version": VERSION,
    }
    
    if os.path.exists(MODEL_PATH):
        info["model_size_mb"] = os.path.getsize(MODEL_PATH) / 1024 / 1024
    
    return info
