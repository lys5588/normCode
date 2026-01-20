# Build Scripts - 辅助工具集

本目录包含用于应用程序打包的辅助脚本。

## 工具列表

### 1. ico_to_icns.py - ICO 转 ICNS

将 Windows ICO 文件转换为 macOS ICNS 格式。

**功能特性：**
- 自动提取 ICO 文件中的所有尺寸
- 生成 macOS 所需的所有标准尺寸（16-1024）
- 包含 Retina (@2x) 分辨率
- 智能尺寸映射（使用最接近的源尺寸）
- 高质量图像重采样（LANCZOS）
- 支持自定义输出路径

**依赖要求：**
- macOS 平台
- iconutil（Xcode Command Line Tools）
- Pillow (PIL)

**安装依赖：**
```bash
pip install Pillow
```

**基本用法：**
```bash
# 基本转换
python ico_to_icns.py icon.ico

# 指定输出路径
python ico_to_icns.py icon.ico icon.icns

# 使用相对路径
python ico_to_icns.py ../resources/icon.ico ./icon.icns

# 保留 iconset 目录（用于调试）
python ico_to_icns.py icon.ico --keep-iconset
```

**示例输出：**
```
============================================================
  ICO to ICNS Converter
============================================================

Input:  /Users/user/build/resources/icon.ico
Output: /Users/user/build/resources/icon.icns

-> Extracting sizes from ICO...
  Found sizes: [16, 32, 48, 64, 128, 256, 512]

-> Creating iconset at: /Users/user/build/resources/icon.iconset
  Using original size 16x16
  Using original size 32x32
  Resized 48x48 -> 64x64
  Using original size 128x128
  Using original size 256x256
  Using original size 512x512
  Resized 512x512 -> 1024x1024
  Generated retina 32x32 (@2x)
  Generated retina 64x64 (@2x)
  Generated retina 128x128 (@2x)
  Generated retina 256x256 (@2x)
  Generated retina 512x512 (@2x)
  [OK] Generated 7 sizes: [16, 32, 64, 128, 256, 512, 1024]

-> Running iconutil...
[OK] Created ICNS file: /Users/user/build/resources/icon.icns
     Size: 245.67 KB

============================================================
  Conversion successful!
============================================================
```

---

### 2. png_to_icns.py - PNG 转 ICNS

将 PNG 图像转换为 macOS ICNS 格式。

**功能特性：**
- 支持任意尺寸的 PNG 源图像
- 生成 macOS 所需的所有标准尺寸
- 包含 Retina (@2x) 分辨率
- 高质量图像重采样（LANCZOS）
- 可指定最大尺寸
- 自动处理 RGBA 转换

**依赖要求：**
- macOS 平台
- iconutil（Xcode Command Line Tools）
- Pillow (PIL)

**安装依赖：**
```bash
pip install Pillow
```

**基本用法：**
```bash
# 基本转换
python png_to_icns.py icon.png

# 指定输出路径
python png_to_icns.py icon.png icon.icns

# 指定最大尺寸
python png_to_icns.py icon.png --size 512

# 使用相对路径
python png_to_icns.py Psylensai_log_raw.png --output resources/icon.icns

# 保留 iconset 目录（用于调试）
python png_to_icns.py icon.png --keep-iconset
```

**支持的尺寸选项：**
- `16` - 最小尺寸（Dock 最小）
- `32` - 小尺寸
- `64` - 标准尺寸
- `128` - 常见尺寸
- `256` - 大尺寸
- `512` - 大尺寸（默认用于高质量）
- `1024` - 最大尺寸（默认）

**示例输出：**
```
============================================================
  PNG to ICNS Converter
============================================================

Input:  /Users/user/build/resources/Psylensai_log_raw.png
Output: /Users/user/build/resources/icon.icns
Max Size: 1024x1024

-> Creating iconset at: /Users/user/build/resources/icon.iconset
  Loading source image: /Users/user/build/resources/Psylensai_log_raw.png
  Source size: 2048x2048
  Converted to RGBA mode
  Generated 16x16 (resized from 2048x2048)
  Generated 32x32 (resized from 2048x2048)
  Generated 64x64 (resized from 2048x2048)
  Generated 128x128 (resized from 2048x2048)
  Generated 256x256 (resized from 2048x2048)
  Generated 512x512 (resized from 2048x2048)
  Generated 1024x1024 (resized from 2048x2048)
  Generated retina 32x32 (@2x)
  Generated retina 64x64 (@2x)
  Generated retina 128x128 (@2x)
  Generated retina 256x256 (@2x)
  Generated retina 512x512 (@2x)
  [OK] Generated 7 sizes

-> Running iconutil...
[OK] Created ICNS file: /Users/user/build/resources/icon.icns
     Size: 245.67 KB

============================================================
  Conversion successful!
============================================================
```

---

## 使用场景

### 场景 1：从 Windows 迁移图标到 macOS

如果你有现成的 Windows ICO 文件：

```bash
# 直接转换
python ico_to_icns.py ../resources/icon.ico

# 输出将在同一目录：icon.icns
```

### 场景 2：从 PNG 生成高质量图标

如果你有高分辨率 PNG（推荐至少 1024x1024）：

```bash
# 从 PNG 生成所有尺寸
python png_to_icns.py Psylensai_log_raw.png --output icon.icns
```

### 场景 3：生成较小尺寸的图标

如果你不需要 1024x1024 的大尺寸：

```bash
# 只生成到 512x512
python png_to_icns.py icon.png --size 512
```

### 场景 4：调试图标生成

保留中间文件以查看生成的各个尺寸：

```bash
# 转换并保留 iconset
python ico_to_icns.py icon.ico --keep-iconset

# 查看生成的文件
ls -la icon.iconset/
```

---

## 常见问题

### Q1: iconutil not found

**问题：**
```
[ERROR] iconutil not found
[INFO] iconutil is part of Xcode Command Line Tools
[INFO] Install with: xcode-select --install
```

**解决方案：**
```bash
# 安装 Xcode Command Line Tools
xcode-select --install
```

---

### Q2: Pillow not installed

**问题：**
```
[ERROR] Pillow (PIL) is required
        Install with: pip install Pillow
```

**解决方案：**
```bash
# 安装 Pillow
pip install Pillow

# 或使用 pip3
pip3 install Pillow
```

---

### Q3: ICO 文件不包含所需的尺寸

**问题：**
```
[WARN] Source size too small: {source_size}x{source_size}
```

**解决方案：**
- 使用 `png_to_icns.py` 从高分辨率 PNG 生成
- 或编辑 ICO 文件添加更大尺寸
- 脚本会使用最接近的可用尺寸

---

### Q4: 输出的 ICNS 文件太大

**原因：**
- 包含了所有尺寸（包括 1024x1024 和 Retina 版本）
- PNG 源图像未优化

**解决方案：**
```bash
# 限制最大尺寸
python png_to_icns.py icon.png --size 512

# 或在图像编辑器中优化 PNG 源文件
```

---

## 技术细节

### macOS 图标尺寸要求

| 尺寸 | 用途 | Retina |
|------|------|--------|
| 16x16 | 最小显示 | 32x32 (@2x) |
| 32x32 | 小尺寸 | 64x64 (@2x) |
| 64x64 | 标准尺寸 | 128x128 (@2x) |
| 128x128 | 常见尺寸 | 256x256 (@2x) |
| 256x256 | 大尺寸 | 512x512 (@2x) |
| 512x512 | 大尺寸 | 1024x1024 (@2x) |
| 1024x1024 | 最大尺寸 | - |

### 图像重采样

脚本使用 PIL 的 `Image.Resampling.LANCZOS` 进行高质量图像缩放：

- LANCZOS 提供最佳的视觉质量
- 适合图标和 UI 元素
- 保持边缘清晰和细节

### 文件格式转换流程

```
ICO/PNG (输入)
  ↓
提取/加载所有尺寸
  ↓
生成标准尺寸 (16, 32, 64, 128, 256, 512, 1024)
  ↓
生成 Retina 尺寸 (@2x for ≤512)
  ↓
保存到 iconset 目录
  ↓
iconutil → ICNS (输出)
```

---

## 与构建脚本的集成

这些辅助脚本与主构建脚本协同工作：

### build_macos.py

`build_macos.py` 已经集成了 `ensure_icon()` 函数，会：
1. 检查 `icon.icns` 是否存在
2. 如果不存在，从 `Psylensai_log_raw.png` 自动生成
3. 使用与这些脚本相同的尺寸要求

**使用建议：**
- 对于标准构建：让 `build_macos.py` 自动处理
- 对于自定义转换：使用这些辅助脚本
- 对于调试：使用 `--keep-iconset` 选项

---

## 最佳实践

### 1. 源图像准备

```bash
# 推荐：使用至少 1024x1024 的 PNG
# 确保是正方形
# 使用 RGBA 模式以支持透明度
# 保存为 PNG 格式（无损压缩）
```

### 2. 批量转换

```bash
# 转换多个文件
for f in *.ico; do
    python ico_to_icns.py "$f"
done

# 或从多个 PNG 生成
for f in *.png; do
    python png_to_icns.py "$f" --size 512
done
```

### 3. 质量验证

```bash
# 使用 qlstephen 或 qlmanage 预览
qlmanage -p icon.icns

# 或使用 sips 验证
sips -g all icon.icns
```

### 4. 版本控制

```bash
# 将生成的 ICNS 添加到 .gitignore
echo "*.icns" >> .gitignore
echo "*.iconset" >> .gitignore

# 源文件（PNG/ICO）保留在版本控制中
git add Psylensai_log_raw.png
git add icon.ico
```

---

## 扩展和自定义

### 添加自定义尺寸

编辑脚本中的 `ICON_SIZES`：

```python
# 添加更多尺寸
ICON_SIZES = [16, 32, 64, 128, 256, 512, 1024, 2048]
```

### 修改重采样方法

```python
# 更快的缩放（质量略低）
resized = source.resize((size, size), Image.Resampling.BILINEAR)

# 最佳质量（较慢）
resized = source.resize((size, size), Image.Resampling.LANCZOS)
```

### 添加水印或徽章

```python
# 在生成每个尺寸后叠加徽章
from PIL import ImageDraw
draw = ImageDraw.Draw(resized)
draw.text((0, 0), "v1.0", fill="white")
```

---

## 许可证

这些脚本是 NormCode Canvas 项目的一部分。

## 贡献

欢迎提交改进和错误修复！

---

## 快速参考

```bash
# 安装依赖
pip install Pillow

# ICO 转 ICNS
python ico_to_icns.py input.ico [output.icns] [--keep-iconset]

# PNG 转 ICNS
python png_to_icns.py input.png [output.icns] [--size MAX_SIZE] [--keep-iconset]

# 检查 iconutil
which iconutil

# 预览 ICNS
qlmanage -p icon.icns

# 验证 ICNS
sips -g all icon.icns
```

---

**提示：** 这些脚本仅在 macOS 上可用，因为它们依赖于 Apple 的 `iconutil` 工具。
