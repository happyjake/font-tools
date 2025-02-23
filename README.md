# Font Tools

工具集用于处理TTF字体文件，包括预览生成、信息修改、字体合并等功能。

## 系统要求

- Python 3.9+

## 安装

1. 克隆仓库:
```bash
git clone https://github.com/happyjake/font-tools.git
cd font-tools
```

2. 创建虚拟环境:
```bash
python -m venv venv
source ./venv/bin/activate
```

3. 安装依赖::
```bash
pip install -r requirements.txt
```

### For Termux

If you encounter an error while installing dependencies with pip, try installing libjpeg-turbo:

```bash
pkg in libjpeg-turbo
```

## 使用方法

```bash
./脚本选择.sh
```

## 常见问题 / Troubleshooting

### Pillow _imagingft Import Error

如果遇到以下错误 / If you encounter this error:

```
ImportError: cannot import name '_imagingft' from 'PIL' (/data/data/com.termux/files/home/font-tools/venv/lib/python3.12/site-packages/PIL/__init__.py)
```

解决方法 / Solution:

1. 安装系统依赖 / Install system dependencies:
```bash
pkg install libjpeg-turbo freetype python-pillow
```

2. 重置虚拟环境 / Reset virtual environment:
```bash
deactivate
source venv/bin/activate
```

3. 重新安装Pillow / Reinstall Pillow:
```bash
pip uninstall Pillow
pip install --no-cache-dir Pillow
```
