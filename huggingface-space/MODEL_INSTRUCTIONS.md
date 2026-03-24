# 模型文件说明

## ⚠️ 重要：模型文件需要单独上传

`frozen_model.pb` 文件（约 43 MB）需要从项目根目录复制到此目录。

### 步骤：

1. 找到项目根目录下的 `frozen_model.pb` 文件
2. 复制到 `huggingface-space/` 目录
3. 与其他文件一起上传到 Hugging Face

### 源文件路径：

```
Polyphony-MuseGan-Web-04/
├── frozen_model.pb          ← 从这里复制
└── huggingface-space/
    ├── Dockerfile
    ├── requirements.txt
    ├── app.py
    ├── ...
    └── frozen_model.pb      ← 复制到这里
```

### 验证：

上传后，确保文件结构如下：

```
huggingface-space/
├── Dockerfile
├── requirements.txt
├── app.py
├── model_utils.py
├── midi_utils.py
├── musicxml_utils.py
├── config.py
├── i18n.py
├── frozen_model.pb    ← 必须存在！
└── README.md
```

如果没有这个文件，Space 将无法启动。
