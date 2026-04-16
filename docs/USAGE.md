# 使用说明

这份文档只讲：

- 怎么运行
- 会生成什么文件
- `bat` 脚本怎么用

如果你想了解代码目录和修改入口，请看 [PROJECT_STRUCTURE.md](C:/code/format/docs/PROJECT_STRUCTURE.md)。

## 运行环境

当前项目基于 Python 运行。

主要依赖：

- `tqdm`
- `pypdf`
- 本机安装的 Calibre

当前代码默认使用的 Calibre 路径定义在：

- [settings.py](C:/code/format/src/settings.py)

## 命令行入口

当前统一入口：

```bash
python -m src.app.main <command> ...
```

支持两个子命令：

- `convert`
- `scan`

## 1. 转换并生成说明

```bash
python -m src.app.main convert <输入路径> -f pdf
```

示例：

```bash
python -m src.app.main convert "C:\闲鱼书" -f pdf
python -m src.app.main convert "C:\books\test.epub" -f pdf
python -m src.app.main convert "C:\books\test.epub" -f txt
python -m src.app.main convert "C:\books\test.epub" -f docx
python -m src.app.main convert "C:\闲鱼书" -f pdf --no-archive
```

说明：

- `<输入路径>` 可以是单文件，也可以是目录
- `-f / --format` 是目标格式，默认 `pdf`
- `--format` 当前只允许：`pdf`、`txt`、`docx`
- `--no-archive` 表示只转换和生成说明文件，不压缩，也不复制到 `输出归档`

### `convert` 参数说明

- `-f pdf`
  - 对 `epub / mobi / azw3`，当前会额外生成 `pdf + txt + docx`
- `-f txt`
  - 只生成 `txt`
- `-f docx`
  - 只生成 `docx`
- `--no-archive`
  - 只转换、生成 `文件清单.txt`、`商品介绍.txt` 和汇总文件
  - 不生成压缩包
  - 不复制到 `输出归档`

## 2. 仅扫描敏感词

```bash
python -m src.app.main scan <输入路径>
```

示例：

```bash
python -m src.app.main scan "C:\闲鱼书"
```

说明：

- 只做扫描
- 不做转换
- 不生成压缩包

## BAT 脚本

项目里准备了两个便捷脚本：

- [single.bat](C:/code/format/temp/single.bat)
- [files.bat](C:/code/format/temp/files.bat)

### `temp/single.bat`

适合处理单个文件。

当前脚本会：

- 切回项目根目录
- 执行单文件 `convert`
- 停留窗口方便看结果

### `temp/files.bat`

适合处理一个批量目录。

当前脚本会：

- 切回项目根目录
- 执行目录 `convert`
- 停留窗口方便看结果

如果你换了常用输入路径，可以直接修改这两个 bat 里的路径。

## 转换时会发生什么

`convert` 模式大致流程：

1. 判断输入是文件还是目录
2. 扫描敏感词
3. 调 Calibre 做格式转换
4. 生成 `文件清单.txt`
5. 生成 `商品介绍.txt`
6. 如果未传 `--no-archive`：
   - 对转换目录打包到 `输出归档`
   - 对纯 PDF 目录复制到 `输出归档`
7. 在 `output/` 下写汇总文件

## 输出结果说明

### 目录内生成

处理过程中，目录内可能生成：

- `文件清单.txt`
- `商品介绍.txt`

用途：

- `文件清单.txt` 方便检查目录内容和文件大小
- `商品介绍.txt` 方便复制到闲鱼等平台

### `输出归档`

如果输入是目录，会在输入目录旁边生成：

```text
<原目录>_输出归档
```

里面的规则是：

- 转换过的目录：进入 zip
- 纯 PDF 目录：直接复制文件夹

如果使用了 `--no-archive`：

- 不会生成 `输出归档`

注意：

- `商品介绍.txt` 和 `文件清单.txt` 不进入压缩包
- `商品介绍.txt` 和 `文件清单.txt` 也不会出现在纯 PDF 复制结果里

### `output/`

项目根目录下会额外生成汇总输出：

- [info.txt](C:/code/format/output/info.txt)
- [商品介绍汇总.txt](C:/code/format/output/商品介绍汇总.txt)

用途：

- `info.txt`：批量文件清单汇总
- `商品介绍汇总.txt`：批量商品介绍汇总

## 当前业务规则

### 格式转换

当输入是：

- `epub`
- `mobi`
- `azw3`

并且目标格式是 `pdf` 时，当前程序会额外生成：

- `pdf`
- `txt`
- `docx`

如果目标格式是：

- `txt`：只生成 `txt`
- `docx`：只生成 `docx`

### 页数统计规则

商品介绍里的“文件页数”当前只统计：

- `pdf`：页数
- `txt`：行数

其他格式暂时不统计。

### 纯 PDF 目录规则

如果某个目录里没有待转换源文件，但已经有目标格式文件，比如纯 PDF 目录：

- 会生成 `文件清单.txt`
- 会生成 `商品介绍.txt`
- 会复制到 `输出归档`
- 复制结果里不包含这两个说明 txt

## 常见问题

### 1. 为什么没有开始转换？

先检查：

- 输入路径是否存在
- Calibre 是否安装
- Calibre 路径是否和 [settings.py](C:/code/format/src/settings.py) 一致

### 2. 为什么 `--help` 之前报编码问题？

Windows 控制台默认可能是 `gbk`，项目入口里的帮助文案已经去掉 emoji，以避免这个问题。

### 3. 想修改默认路径或者排除规则在哪里改？

看这里：

- [settings.py](C:/code/format/src/settings.py)
