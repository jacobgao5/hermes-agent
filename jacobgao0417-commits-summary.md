# jacobgao0417 代码提交总结

**仓库：** `https://github.com/jacobgao5/hermes-agent.git`  
**作者：** `jacobgao0417 <jacobgao0417@gmail.com>`  
**涉及模块：** `skills/productivity/ocr-and-documents`

---

## 提交列表

| Commit | 日期 | 主题 |
|--------|------|------|
| `e044ce7d` | 2026-04-24 | 新增页面渲染与一键提取，修复兼容性 |
| `4191a10e` | 2026-04-24 | 为 `--all` 增加缓存机制 |

---

## Commit 1：`e044ce7d`

### 改动文件
- `skills/productivity/ocr-and-documents/SKILL.md`
- `skills/productivity/ocr-and-documents/scripts/extract_pymupdf.py`

### 主要内容

#### 1. 新增 `--render` 参数
将 PDF 页面渲染为 **2x PNG** 图片，适用于视觉模型分析。

```bash
python extract_pymupdf.py document.pdf --render out/
```

#### 2. 新增 `--all` 参数
一键执行完整提取，输出到指定目录：
- `out/full_text.txt` — 全文文本
- `out/metadata.json` — 元数据
- `out/renders/` — 页面渲染图

```bash
python extract_pymupdf.py document.pdf --all out/
```

#### 3. 修复 PyMuPDF 导入兼容性
- 老版本（≤1.23.x）`import pymupdf` 成功但返回的是没有 `open` 属性的 namespace package
- 现在会正确 fallback 到 `import fitz`

```python
try:
    import pymupdf
    if not hasattr(pymupdf, 'open'):
        raise AttributeError
except (ImportError, AttributeError):
    import fitz as pymupdf
```

#### 4. 修复图片提取问题
- 增加 **SMask（透明度遮罩）合并**
- 增加 **CMYK → RGB** 颜色空间转换
- 避免提取出黑图或残缺图

#### 5. 优化 SKILL.md 文档
- 版本号：`2.3.0` → `2.4.0`
- 删除内联代码示例，防止 agent 直接复制粘贴而不使用 helper script
- 新增 **IMPORTANT** 警告：始终使用 helper script，禁止手写自定义提取脚本
- 新增 **Pitfalls** 章节，列出常见陷阱：
  - `doc.extract_image()` 会产生黑图/不完整图像
  - `pymupdf4llm` 版本不匹配问题
  - NixOS 的 `libstdc++.so.6` 路径问题
  - 必须先激活 venv
  - 旧版 PyMuPDF 的 `import fitz` 兼容性问题

---

## Commit 2：`4191a10e`

### 改动文件
- `skills/productivity/ocr-and-documents/SKILL.md`
- `skills/productivity/ocr-and-documents/scripts/extract_pymupdf.py`

### 主要内容

#### 1. `--all` 参数增加缓存机制
在执行解析前，检查 `output_dir/.cache_key` 文件，内容包含 PDF 的**绝对路径 + 文件大小 + 修改时间**。

- **缓存命中**：若文件未变动且结果已存在，直接跳过解析，返回 JSON 结果并标记 `cached: true`
- **缓存未命中**：正常解析，并在完成后写入新的 cache key

#### 2. 新增 `--no-cache` 参数
强制重新解析，忽略已有缓存：

```bash
python extract_pymupdf.py document.pdf --all out/ --no-cache
```

#### 3. 缓存数据结构
缓存命中时返回的 JSON：

```json
{
  "output_dir": "out/",
  "metadata": "out/metadata.json",
  "text": "out/full_text.txt",
  "renders": "out/renders",
  "cached": true
}
```

正常解析完成后返回的 JSON（新增 `cached: false` 字段）：

```json
{
  "output_dir": "out/",
  "metadata": "out/metadata.json",
  "text": "out/full_text.txt",
  "renders": "out/renders",
  "pages_rendered": 10,
  "text_chars": 15230,
  "cached": false
}
```

---

## 总体评价

这两次提交将 `ocr-and-documents` skill 的 helper script 从单一的文本提取工具，升级为一个支持**页面渲染、一键全量提取、智能缓存**的完整方案。同时通过文档规范、兼容性修复和常见陷阱提示，显著提升了该 skill 在不同 Python/PyMuPDF 环境下的稳定性和易用性。
