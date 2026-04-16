# Agent Rules

## Shell

- 在本项目中默认优先使用 `pwsh` / `pwsh.exe` 执行命令，尤其是在需要处理中文路径、中文提交信息或写入文本文件时。

## Verification

- 只要修改了项目代码，就必须在结束前运行测试。
- 当前项目的默认测试命令为：

```bash
pytest -q
```
