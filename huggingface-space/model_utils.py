"""
模型加载和推理工具
支持 TensorFlow 1.x 和 2.x 兼容模式
"""

import os
import numpy as np
import logging
from typing import Optional, Tuple

# TensorFlow 兼容性处理
TF_MODE = "unknown"
try:
    import tensorflow as tf
    if int(tf.__version__.split('.')[0]) >= 2:
        import tensorflow.compat.v1 as tf1
        tf1.disable_v2_behavior()
        TF_MODE = "tf2_compat"
    else:
        tf1 = tf
        TF_MODE = "tf1"
except ImportError:
    raise ImportError("TensorFlow not found. Please install tensorflow>=2.10")

from config import (
    MODEL_PATH, INPUT_NODE, OUTPUT_NODE,
    INPUT_NODE_FALLBACKS, OUTPUT_NODE_FALLBACKS,
    LATENT_DIM, N_BARS, N_STEPS, N_PITCHES, N_TRACKS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MuseGANModel:
    """MuseGAN 模型封装类"""
    
    def __init__(self):
        self.graph = None
        self.session = None
        self.input_tensor = None
        self.output_tensor = None
        self.is_loaded = False
        
    def load(self) -> bool:
        """加载冻结模型"""
        try:
            logger.info(f"Loading frozen model from {MODEL_PATH}...")
            
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
            
            # 统一使用 tf1 (compat.v1) 的 API
            self.graph = tf1.Graph()
            
            with self.graph.as_default():
                graph_def = tf1.GraphDef()
                with tf1.gfile.GFile(MODEL_PATH, 'rb') as f:
                    graph_def.ParseFromString(f.read())
                
                tf1.import_graph_def(graph_def, name='')
                
                # 尝试查找输入张量
                self.input_tensor = self._find_tensor(INPUT_NODE, INPUT_NODE_FALLBACKS, "input")
                if self.input_tensor is None:
                    self._print_available_tensors()
                    raise ValueError(f"Input tensor not found. Tried: {[INPUT_NODE] + INPUT_NODE_FALLBACKS}")
                
                # 尝试查找输出张量
                self.output_tensor = self._find_tensor(OUTPUT_NODE, OUTPUT_NODE_FALLBACKS, "output")
                if self.output_tensor is None:
                    self._print_available_tensors()
                    raise ValueError(f"Output tensor not found. Tried: {[OUTPUT_NODE] + OUTPUT_NODE_FALLBACKS}")
                
                config = tf1.ConfigProto()
                config.gpu_options.allow_growth = True
                self.session = tf1.Session(graph=self.graph, config=config)
                
            self.is_loaded = True
            logger.info(f"Model loaded successfully! Input: {self.input_tensor.name}, Output: {self.output_tensor.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.is_loaded = False
            return False
    
    def _find_tensor(self, primary_name: str, fallback_names: list, tensor_type: str):
        """尝试查找张量，支持备选名称"""
        # 首先尝试主名称
        try:
            tensor = self.graph.get_tensor_by_name(primary_name)
            logger.info(f"Found {tensor_type} tensor: {primary_name}")
            return tensor
        except (KeyError, ValueError):
            pass
        
        # 尝试备选名称
        for name in fallback_names:
            if name == primary_name:
                continue
            try:
                tensor = self.graph.get_tensor_by_name(name)
                logger.info(f"Found {tensor_type} tensor (fallback): {name}")
                return tensor
            except (KeyError, ValueError):
                continue
        
        return None
    
    def _print_available_tensors(self):
        """打印图中所有可用的张量名称（用于调试）"""
        logger.error("=== Available tensors in the graph ===")
        all_tensors = []
        for op in self.graph.get_operations():
            for output in op.outputs:
                all_tensors.append(output.name)
        
        # 分类打印
        placeholder_tensors = [t for t in all_tensors if 'Placeholder' in t and 'shape' not in t.lower()]
        concat_tensors = [t for t in all_tensors if 'concat' in t]
        generator_tensors = [t for t in all_tensors if 'Generator' in t or 'generator' in t]
        
        logger.error(f"\n=== Placeholder-like tensors ({len(placeholder_tensors)}) ===")
        for name in placeholder_tensors[:20]:
            logger.error(f"  {name}")
        
        logger.error(f"\n=== Concat tensors ({len(concat_tensors)}) ===")
        for name in concat_tensors[:20]:
            logger.error(f"  {name}")
        
        logger.error(f"\n=== Generator tensors ({len(generator_tensors)}) ===")
        for name in generator_tensors[:20]:
            logger.error(f"  {name}")
        
        # 打印前100个张量
        logger.error(f"\n=== First 100 tensors ===")
        for i, name in enumerate(all_tensors[:100]):
            logger.error(f"  {name}")
        
        if len(all_tensors) > 100:
            logger.error(f"  ... and {len(all_tensors) - 100} more tensors")
        logger.error(f"Total: {len(all_tensors)} tensors")
    
    def generate(self, seed: Optional[int] = None, temperature: float = 1.0) -> np.ndarray:
        """生成音乐"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        if seed is not None:
            np.random.seed(seed)
        
        # 模型期望 batch size = 64，生成64个样本后取第一个
        z = np.random.normal(0, 1, (64, LATENT_DIM)) * temperature
        
        with self.graph.as_default():
            output = self.session.run(self.output_tensor, feed_dict={self.input_tensor: z})
        
        # 返回第一个样本的结果
        return output[0]
    
    def close(self):
        """释放资源"""
        if self.session:
            self.session.close()
        self.is_loaded = False


_model: Optional[MuseGANModel] = None


def get_model() -> MuseGANModel:
    """获取全局模型实例"""
    global _model
    if _model is None:
        _model = MuseGANModel()
    return _model


def load_model() -> bool:
    """加载模型"""
    model = get_model()
    if not model.is_loaded:
        return model.load()
    return True


def generate_music(seed: Optional[int] = None, temperature: float = 1.0, threshold: float = 0.5, n_bars: int = None) -> Tuple[np.ndarray, np.ndarray]:
    """生成音乐（带后处理）
    
    Args:
        seed: 随机种子
        temperature: 温度参数
        threshold: 二值化阈值
        n_bars: 目标小节数，如果为 None 或 <= N_BARS 则生成 N_BARS 小节
    
    Returns:
        (raw_output, binary_output): shape (n_bars, N_STEPS, N_PITCHES, N_TRACKS)
    """
    model = get_model()
    
    # 如果不需要扩展，直接生成
    if n_bars is None or n_bars <= N_BARS:
        raw_output = model.generate(seed=seed, temperature=temperature)
        binary_output = (raw_output > threshold).astype(np.float32)
        return raw_output, binary_output
    
    # 需要生成超过 N_BARS 小节：循环生成多个片段并拼接
    n_segments = (n_bars + N_BARS - 1) // N_BARS  # 向上取整
    logger.info(f"Generating {n_bars} bars in {n_segments} segments...")
    
    raw_segments = []
    for i in range(n_segments):
        # 每个片段使用不同的种子（基于基础种子递增）
        segment_seed = (seed + i * 1000) if seed is not None else None
        segment = model.generate(seed=segment_seed, temperature=temperature)
        raw_segments.append(segment)
        logger.info(f"Generated segment {i+1}/{n_segments}")
    
    # 拼接所有片段
    raw_output = np.concatenate(raw_segments, axis=0)[:n_bars]
    binary_output = (raw_output > threshold).astype(np.float32)
    
    logger.info(f"Final output shape: {binary_output.shape}")
    return raw_output, binary_output
