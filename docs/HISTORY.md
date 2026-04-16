# HISTORY

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
