# MuseGAN Hugging Face Space
# 基于 TensorFlow 2.10 官方镜像 (Python 3.9，支持 TF1.x 兼容模式)

FROM tensorflow/tensorflow:2.10.0

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# 启用 multiverse 仓库并安装系统依赖（包含 SoundFont）
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository -y multiverse && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libsndfile1 \
    fluidsynth \
    fluid-soundfont-gm \
    && rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/share/sounds/sf2/FluidR3_GM.sf2 /usr/share/sounds/sf2/default.sf2

# 复制依赖文件
COPY requirements.txt .

# 先升级基础依赖，避免版本冲突
RUN pip install --no-cache-dir --upgrade typing_extensions>=4.12.2 packaging>=23.1

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .
COPY model_utils.py .
COPY midi_utils.py .
COPY musicxml_utils.py .
COPY config.py .
COPY i18n.py .
COPY convert_checkpoint.py .

# 复制模型文件 - 直接使用 default/model/ 目录中的 checkpoint 文件
COPY default/ ./default/

# 转换模型: 从 checkpoint 生成 frozen_model.pb
RUN python convert_checkpoint.py

# 验证模型文件
RUN if [ ! -f frozen_model.pb ]; then \
        echo "ERROR: frozen_model.pb not generated!"; \
        exit 1; \
    fi && \
    SIZE=$(stat -c%s frozen_model.pb 2>/dev/null || stat -f%z frozen_model.pb); \
    echo "Model file size: $SIZE bytes (~$((SIZE/1024/1024))MB)"; \
    if [ "$SIZE" -lt 1000000 ]; then \
        echo "WARNING: Model file is very small (< 1MB), might be corrupted"; \
    fi

# 暴露端口（Hugging Face 要求）
EXPOSE 7860

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# 启动命令
CMD ["python", "app.py"]
