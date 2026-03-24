"""
MuseGAN Checkpoint to Frozen Model Converter
在 Docker 构建时运行，将 TF1.x checkpoint 转换为 frozen_model.pb

输入:
- pretrained_models.tar.gz (用户上传)
- 或 default/model/model.ckpt-* 文件

输出:
- frozen_model.pb (可用于推理)
"""

import os
import sys
import tarfile
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# TensorFlow 兼容模式
import tensorflow as tf
tf_compat = tf.compat.v1
tf_compat.disable_v2_behavior()

# 模型配置
LATENT_DIM = 128
N_BARS = 4
N_STEPS = 48
N_PITCHES = 84
N_TRACKS = 5

# 输入输出节点名称
INPUT_NAME = "Placeholder"
OUTPUT_NAME = "Generator/merged_private/concat"


def extract_tarball(tar_path: str, extract_to: str) -> str:
    """解压 tar.gz 文件"""
    logger.info(f"Extracting {tar_path} to {extract_to}...")
    
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=extract_to)
    
    # 查找 checkpoint 文件
    for root, dirs, files in os.walk(extract_to):
        for f in files:
            if f.endswith('.index'):
                checkpoint_path = os.path.join(root, f.replace('.index', ''))
                logger.info(f"Found checkpoint: {checkpoint_path}")
                return checkpoint_path
    
    return None


def find_checkpoint(base_path: str) -> str:
    """查找 checkpoint 文件"""
    # 尝试多种路径
    possible_paths = [
        os.path.join(base_path, "model.ckpt-300450"),
        os.path.join(base_path, "default/model/model.ckpt-300450"),
        os.path.join(base_path, "model.ckpt"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path + '.index'):
            logger.info(f"Found checkpoint: {path}")
            return path
    
    # 递归搜索
    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith('.index'):
                checkpoint_path = os.path.join(root, f.replace('.index', ''))
                logger.info(f"Found checkpoint (recursive): {checkpoint_path}")
                return checkpoint_path
    
    return None


def get_tensor_names(graph) -> tuple:
    """获取图中的输入输出张量名称"""
    all_tensors = []
    input_candidates = []
    output_candidates = []
    
    for op in graph.get_operations():
        for output in op.outputs:
            name = output.name
            all_tensors.append(name)
            
            # 检测输入张量
            if 'Placeholder' in name or 'input' in name.lower() or 'z' in name.lower():
                if ':' in name and 'shape' not in name.lower():
                    input_candidates.append(name)
            
            # 检测输出张量
            if 'concat' in name or 'output' in name.lower() or 'generated' in name.lower():
                if 'merged_private' in name or 'Generator' in name:
                    output_candidates.append(name)
    
    logger.info(f"Total tensors: {len(all_tensors)}")
    
    return input_candidates, output_candidates, all_tensors


def convert_to_frozen_model(checkpoint_path: str, output_path: str) -> bool:
    """将 checkpoint 转换为 frozen model"""
    logger.info(f"Converting checkpoint to frozen model...")
    logger.info(f"  Input: {checkpoint_path}")
    logger.info(f"  Output: {output_path}")
    
    try:
        with tf_compat.Session() as sess:
            # 导入 meta graph
            saver = tf_compat.train.import_meta_graph(
                checkpoint_path + '.meta', 
                clear_devices=True
            )
            saver.restore(sess, checkpoint_path)
            
            graph = tf_compat.get_default_graph()
            
            # 获取所有张量名称
            input_candidates, output_candidates, all_tensors = get_tensor_names(graph)
            
            logger.info(f"\n=== Input candidates ===")
            for name in input_candidates[:10]:
                logger.info(f"  {name}")
            
            logger.info(f"\n=== Output candidates ===")
            for name in output_candidates[:10]:
                logger.info(f"  {name}")
            
            # 查找输入张量
            input_tensor = None
            input_names_to_try = [
                "Placeholder:0",
                "z:0",
                "z_latent:0",
                "input:0",
            ] + input_candidates
            
            for name in input_names_to_try:
                try:
                    input_tensor = graph.get_tensor_by_name(name)
                    logger.info(f"\n✓ Found input tensor: {name}")
                    break
                except (KeyError, ValueError):
                    continue
            
            if input_tensor is None:
                logger.error("Could not find input tensor!")
                logger.error("First 30 tensors:")
                for name in all_tensors[:30]:
                    logger.error(f"  {name}")
                return False
            
            # 查找输出张量
            output_tensor = None
            output_names_to_try = [
                "Generator/merged_private/concat:0",
                "Model/Generator/merged_private/concat:0",
                "Model_2/Generator/merged_private/concat:0",
            ] + output_candidates
            
            for name in output_names_to_try:
                try:
                    output_tensor = graph.get_tensor_by_name(name)
                    logger.info(f"✓ Found output tensor: {name}")
                    break
                except (KeyError, ValueError):
                    continue
            
            if output_tensor is None:
                logger.error("Could not find output tensor!")
                return False
            
            # 冻结图
            logger.info(f"\nFreezing graph...")
            output_graph_def = tf_compat.graph_util.convert_variables_to_constants(
                sess,
                graph.as_graph_def(),
                [output_tensor.name.split(':')[0]]
            )
            
            # 保存 frozen model
            with tf_compat.gfile.GFile(output_path, 'wb') as f:
                f.write(output_graph_def.SerializeToString())
            
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(f"\n✓ Frozen model saved: {output_path} ({file_size:.2f} MB)")
            
            # 验证
            if file_size < 1:
                logger.error("Frozen model is too small! Might be corrupted.")
                return False
            
            return True
            
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    logger.info("=" * 60)
    logger.info("MuseGAN Checkpoint to Frozen Model Converter")
    logger.info("=" * 60)
    
    # 查找 checkpoint - 直接从 default/model 目录
    checkpoint_path = None
    default_path = "/app/default/model"
    
    if os.path.exists(default_path):
        logger.info(f"Looking for checkpoint in: {default_path}")
        checkpoint_path = find_checkpoint(default_path)
    else:
        logger.error(f"Model directory not found: {default_path}")
    
    # 备用: 从当前目录搜索
    if not checkpoint_path:
        checkpoint_path = find_checkpoint("/app")
    
    if not checkpoint_path:
        logger.error("No checkpoint found!")
        logger.error("Please ensure /app/default/model/ contains model.ckpt-* files")
        sys.exit(1)
    
    # 转换
    output_path = "/app/frozen_model.pb"
    success = convert_to_frozen_model(checkpoint_path, output_path)
    
    if success:
        logger.info("\n" + "=" * 60)
        logger.info("✅ Conversion successful!")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("\n" + "=" * 60)
        logger.error("❌ Conversion failed!")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
