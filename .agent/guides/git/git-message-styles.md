---
description: Agent 专用 Git 提交消息模板（轻量版）
---

# Git Commit Message Template

本文件只定义 agent 生成或重写 Git commit message 时必须遵守的最小规则。

目标：

- 让日常提交足够轻
- 让大改动提交仍然可读
- 不把发布版本号强行塞进每一次提交

## Allowed Types

- `feat`
- `feat!`
- `fix`
- `refactor`
- `docs`
- `perf`
- `chore`

## Hard Rules

- 代码改动禁止使用 `docs`
- 纯文档改动才允许使用 `docs`
- `subject` 必须简短直接，不写表情，不写句号
- 日常提交不强制写版本号
- 只有存在 breaking changes 时，才使用 `feat!` 或添加 `[Breaking Changes]`
- 空 section 不要保留
- `squash` 或 `reword` 后，不要保留 `Squashed commits:` 或原 commit 列表
- 涉及中文 commit message 的生成、落盘、amend、reword 或 `--file` 提交时，优先使用 `pwsh` / `pwsh.exe`
- 需要将提交信息写入文件时，使用 `pwsh` 的 UTF-8 输出（如 `Set-Content -Encoding utf8`），避免中文乱码

## Preferred Format

日常提交默认使用短格式：

```text
<type>: <subject>
```

示例：

```text
feat: 新增纯PDF目录复制逻辑
fix: 修正批量报告中的跳过目录统计
refactor: 调整项目目录结构
docs: 拆分使用说明和结构说明
chore: 更新bat脚本入口
```

## Extended Format

当改动较大、涉及多个点、或需要说明验证方式时，可以使用扩展格式：

```text
<type>: <subject>

[Summary]
<1-3 行摘要>

[Breaking Changes]
- <breaking change>

[Added]
- <added item>

[Changed & Refactored]
- <changed item>

[Fixed]
- <fixed item>

[Verification]
- <verification step>
```

## Section Rules

- `[Summary]` 在扩展格式中推荐使用，但不是强制
- `[Verification]` 只在需要说明验证方式时出现
- `[Breaking Changes]` 仅在存在 breaking changes 时出现
- `[Added]`、`[Changed & Refactored]`、`[Fixed]` 按实际改动保留
- 列表项统一使用 `- `

## Version Note

- `Release-Version: vX.Y.Z` 不再是每次提交的必填项
- 只有在用户明确要求生成“发布提交”或“版本提交”时，才在提交正文最后一行添加：

```text
Release-Version: vX.Y.Z
```

## Generic Example

短格式：

```text
fix: 修正纯PDF目录归档统计
```

扩展格式：

```text
refactor: 重构项目目录并统一CLI入口

[Summary]
整理模块边界并统一默认入口，减少重复实现。

[Changed & Refactored]
- 调整 `src/` 分层结构
- 合并重复逻辑
- 同步更新相关脚本

[Verification]
- 运行 `python -m compileall src`
- 运行 `python -m src.app.main --help`
```
