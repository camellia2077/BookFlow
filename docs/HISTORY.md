# HISTORY

## [v0.1.1] - 2026-04-16

### 新增功能 (Added)
* 新增 `images` 子命令，仅基于现有 PDF 生成 `商品图片` 预览图。
* 新增商品图片自动生成流程，支持封面、目录、内页截图，并支持按页码百分比抽样正文页。
* 新增商品介绍中的 `资料语言` 与 `文本状态` 字段，可标注 `英文原版`、`可复制可搜索` 与 `纯图片版`。
* 新增 `src/infrastructure/pdf_preview_generator.py`、`src/utils/timestamps.py` 以及 `tools/pdf_page_capture.py` 等辅助工具。
* 新增 `tests/` 自动化测试体系，并按 `app / application / domain / infrastructure` 轻量分层组织。

### 技术改进/重构 (Changed/Refactor)
* 调整生成文件命名规则，为商品介绍、文件清单、汇总文件和截图统一加入北京时间 ISO 风格时间戳。
* 调整批处理清理逻辑，在重新生成前清理旧的说明文件、截图和汇总文件，并通过 `.bookflow-generated` 标记保护手工维护的 `商品图片` 目录。
* 调整归档逻辑，每次批量任务开始前整块重建 `xxx_输出归档`，不再做增量覆盖。
* 调整测试目录结构，将 `tests/` 下的测试按职责拆分到子目录中，并改用 `pytest.toml` 作为配置入口。
* 调整批量报告输出，除统计数量外，同时打印命名不符合预期的具体文件路径。

### 修复 (Fixed)
* 修复 `tools/pdf_page_capture.py` 直接执行时无法导入 `src` 包的问题。
* 修复商品图片目录清理可能误删手工目录的问题，仅清理带程序标记的目录。
* 修复压缩包与复制目录中误带入生成说明文件和商品图片的问题。

## [v0.1.0] - 2026-04-16

### 新增功能 (Added)
* 新增 `python -m src.app.main` 命令入口，并提供 `convert` 与 `scan` 子命令。
* 新增 `商品介绍.txt` 自动生成能力，用于输出闲鱼商品介绍模板。
* 新增商品介绍中的 PDF 页数与 TXT 行数统计。
* 新增纯 PDF 目录复制到 `输出归档` 的处理逻辑。
* 新增 `VERSION` 文件，并设置当前版本为 `0.1.0`。

### 技术改进/重构 (Changed/Refactor)
* 重构 `src/` 目录结构为 `app / application / domain / infrastructure / presentation` 分层。
* 调整批处理主流程，统一扫描、转换、商品介绍生成、压缩与汇总输出的组织方式。
* 拆分文档为 `docs/PROJECT_STRUCTURE.md` 与 `docs/USAGE.md`，并补充 `docs/HISTORY.md`。
* 新增 `.agent/guides/` 下的轻量版 Git 提交、Tag 与历史文档规范。

### 修复 (Fixed)
* 修复压缩包误包含 `商品介绍.txt` 与 `文件清单.txt` 的问题。
* 修复纯 PDF 目录复制结果中包含说明文件的问题。
* 修复批量报告中纯 PDF 目录被计入“跳过目录数”的统计口径问题。
