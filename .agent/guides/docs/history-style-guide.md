---
description: Agent 专用版本历史模板（轻量版）
---

# Release History Template

本文件只定义 agent 编写版本历史或发布说明时必须遵守的最小规则。

目标：

- 让版本历史保持清晰
- 只记录真正重要的变化
- 不要求像大型项目那样写得过重

## Hard Rules

- 最新条目必须写在最前面
- 版本标题格式必须为 `## [vX.Y.Z] - YYYY-MM-DD`
- 日期必须使用 ISO 8601：`YYYY-MM-DD`
- 分类只使用以下几类：
  - `### 新增功能 (Added)`
  - `### 技术改进/重构 (Changed/Refactor)`
  - `### 修复 (Fixed)`
  - `### 安全性 (Security)`
  - `### 弃用/删除 (Deprecated/Removed)`
- 列表统一使用 `* `
- 空分类不要保留
- 条目应以动词开头，简短直接
- 文件名、命令、路径、配置键统一使用反引号

## Template

```md
## [vX.Y.Z] - YYYY-MM-DD

### 新增功能 (Added)
* 新增 `<feature or file>`

### 技术改进/重构 (Changed/Refactor)
* 重构 `<module or workflow>`

### 修复 (Fixed)
* 修复 `<bug or regression>`
```

## Writing Rules

- 只写用户可感知或工程上重要的变化
- 不要求把每个小改动都写进版本历史
- 同类改动尽量合并表达
- 涉及目录迁移时，明确写出路径
- 若涉及版本号、配置格式、构建方式变化，应明确写出旧口径与新口径

## Generic Example

```md
## [v0.1.0] - 2026-04-16

### 新增功能 (Added)
* 新增 `商品介绍.txt` 自动生成。
* 新增纯 PDF 目录复制到 `输出归档` 的处理逻辑。

### 技术改进/重构 (Changed/Refactor)
* 重构 `src/` 目录结构，统一入口为 `python -m src.app.main`。

### 修复 (Fixed)
* 修复压缩包误包含 `商品介绍.txt` 和 `文件清单.txt` 的问题。
```
