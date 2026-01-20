# macOS DMG 构建快速指南

## ✅ 已完成的改进

按照方案一对 `build_macos.py` 进行了以下增强：

### 1. 版本号自动同步 ✅
- 从 `installer.iss` 自动读取版本号和显示名称
- 确保 macOS 和 Windows 版本保持一致

### 2. 图标验证增强 ✅
- 添加 `iconutil` 工具可用性检查
- 提供清晰的错误提示和解决方案

### 3. DMG 创建优化 ✅
- 支持自定义背景（`dmg-background.png`）
- 使用最高压缩级别减小文件大小
- 显示详细的构建进度和最终文件大小
- 改进的异常处理和资源清理

### 4. Spec 文件增强 ✅
- 添加版权信息
- 使用动态显示名称
- 更完整的应用元数据

### 5. 构建输出改进 ✅
- 显示版本号和显示名称
- DMG 卷标使用应用显示名称

---

## 🚀 快速开始

### 前置要求

```bash
# 1. 安装 Xcode Command Line Tools（如果尚未安装）
xcode-select --install

# 2. 验证工具
which iconutil   # 应该返回路径
which hdiutil    # 应该返回路径
which codesign   # 应该返回路径
```

### 基本构建

```bash
cd build

# 标准 .app 构建
python build_macos.py

# 构建 .app + DMG 安装包
python build_macos.py --dmg

# 构建 .app + 便携 ZIP
python build_macos.py --portable

# 清理后重新构建
python build_macos.py --clean
```

### 高级选项

```bash
# 使用开发者证书签名（需要 Apple 开发者账号）
python build_macos.py --sign "Developer ID Application: Your Name"

# 使用 ad-hoc 签名（默认）
python build_macos.py --sign "-"

# 跳过前端构建（使用现有构建）
python build_macos.py --skip-frontend

# 跳过依赖安装
python build_macos.py --skip-deps
```

---

## 📦 输出文件

构建成功后，在 `build/dist/` 目录下会生成：

```
build/dist/
├── NormCodeCanvas.app/           # macOS 应用包
│   └── Contents/
│       ├── Info.plist
│       ├── MacOS/
│       ├── Resources/
│       └── Frameworks/
├── NormCodeCanvas-1.0.3-alpha.dmg   # DMG 安装包（如果使用 --dmg）
└── NormCodeCanvas-1.0.3-alpha-macos.zip  # 便携 ZIP（如果使用 --portable）
```

---

## 🎨 自定义资源

### 1. 添加 DMG 背景图片

```bash
# 创建背景图片（推荐尺寸：800x600 或 1024x768）
# 保存为: build/resources/dmg-background.png

# 构建时会自动使用
python build_macos.py --dmg
```

### 2. 使用自定义图标

```bash
# 选项 1：自动生成（推荐）
# 脚本会从 Psylensai_log_raw.png 自动生成 icon.icns

# 选项 2：手动创建
# 使用在线工具: https://cloudconvert.com/png-to-icns
# 或使用 iconutil:
mkdir build/resources/icon.iconset
sips -z 16 16 build/resources/Psylensai_log_raw.png --out build/resources/icon.iconset/icon_16x16.png
# ... 为所有尺寸重复 ...
iconutil -c icns build/resources/icon.iconset -o build/resources/icon.icns
```

---

## 🔢 更新版本号

只需在一个地方修改版本号：

```ini
# 编辑 build/installer.iss
#define MyAppVersion "1.0.4-beta"
#define MyAppName "NormCode Canvas"
```

然后运行构建脚本，版本会自动同步：

```bash
python build_macos.py
# 输出会显示: Version: 1.0.4-beta
```

---

## 🧪 测试构建

### 挂载 DMG 测试

```bash
# 挂载 DMG
open build/dist/NormCodeCanvas-1.0.3-alpha.dmg

# 验证应用签名
codesign -dv --verbose=4 build/dist/NormCodeCanvas.app

# 运行应用
open build/dist/NormCodeCanvas.app
```

### 验证应用包结构

```bash
# 查看应用包内容
ls -la build/dist/NormCodeCanvas.app/Contents/

# 查看资源
ls -la build/dist/NormCodeCanvas.app/Contents/Resources/
```

---

## ⚠️ 常见问题

### 问题 1: iconutil not found

```
[ERROR] iconutil not found
[INFO] iconutil is part of Xcode Command Line Tools
[INFO] Install with: xcode-select --install
```

**解决方案：**
```bash
xcode-select --install
```

### 问题 2: 版本号不匹配

确保 `installer.iss` 中定义了版本号：
```bash
grep "MyAppVersion" build/installer.iss
```

应该看到：
```ini
#define MyAppVersion "1.0.3-alpha"
```

### 问题 3: DMG 文件过大

- 脚本已使用最高压缩级别 (zlib-level=9)
- 可以检查是否包含不必要的依赖
- 考虑使用 UPX 压缩（在 spec 文件中）

---

## 📊 与 Windows 构建的对比

| 特性 | Windows | macOS |
|------|---------|-------|
| 版本管理 | installer.iss | 从 installer.iss 自动读取 ✅ |
| 图标格式 | .ico | .icns (从 PNG 自动生成) ✅ |
| 安装程序 | Inno Setup (.exe) | hdiutil (.dmg) ✅ |
| 背景支持 | banner.bmp, wizard.bmp | dmg-background.png ✅ |
| 代码签名 | 可选 | 必需 (ad-hoc 或开发者) |
| 桌面窗口 | EdgeChromium (WebView2) | Cocoa (WKWebView) |

---

## 📝 详细文档

更多详细信息请参阅：
- [macOS 构建改进详解](build/MACOS_BUILD_IMPROVEMENTS.md)
- [资源文件说明](build/resources/README.md)
- [通用构建指南](build/BUILD_README.md)

---

## 🎯 下一步建议

### 可选增强

1. **开发者签名和公证**
   ```bash
   # 如果有 Apple 开发者账号
   python build_macos.py --sign "Developer ID Application: Your Name"
   
   # 公证（需要 Apple 开发者账号）
   xcrun notarytool submit dist/NormCodeCanvas-1.0.3-alpha.dmg \
     --apple-id "your@email.com" \
     --password "app-specific-password" \
     --team-id "TEAM123456" \
     --wait
   
   # 装订公证凭证
   xcrun stapler staple dist/NormCodeCanvas-1.0.3-alpha.dmg
   ```

2. **Universal Binary 支持**
   - 支持 Intel (x86_64) 和 Apple Silicon (arm64)
   - 需要在两台 Mac 上分别构建或使用 cross-compile

3. **DMG 布局自定义**
   - 使用 AppleScript 调整窗口大小和位置
   - 自定义图标位置

---

## ✨ 总结

现在你已经拥有一个完善的 macOS 构建系统：

✅ 版本号自动同步
✅ 智能图标生成
✅ 优化的 DMG 创建
✅ 详细的构建日志
✅ 完善的错误处理
✅ 清晰的文档

开始构建你的第一个 macOS DMG 吧！

```bash
cd build
python build_macos.py --dmg
```

🎉 完成！
