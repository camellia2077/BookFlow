# 项目结构说明

这份文档只讲两件事：

- 代码放在哪里
- 想修改某类功能时，应该先看哪里

如果你想看“怎么运行”和“会生成什么文件”，请看 [USAGE.md](C:/code/format/docs/USAGE.md)。

## 一眼看懂

推荐第一次接手时按这个顺序看：

1. [main.py](C:/code/format/src/app/main.py)
2. [batch_service.py](C:/code/format/src/application/batch_service.py)
3. 你要修改的对应模块

原因：

- [main.py](C:/code/format/src/app/main.py) 是命令入口
- [batch_service.py](C:/code/format/src/application/batch_service.py) 是主流程总控
- 其余模块按职责分层，改动点比较集中

## 目录职责

```text
src/
  app/
  application/
  domain/
  infrastructure/
  presentation/
  settings.py
```

### `src/app`

入口层。

核心文件：

- [main.py](C:/code\format/src/app/main.py)

职责：

- 解析 CLI 参数
- 提供 `convert` / `scan` 子命令
- 调用应用层主流程

改这些内容先看这里：

- 命令名
- CLI 参数
- 运行入口

### `src/application`

流程编排层。

核心文件：

- [batch_service.py](C:/code/format/src/application/batch_service.py)
- [product_service.py](C:/code/format/src/application/product_service.py)

职责：

- 组织“扫描 -> 转换 -> 生成说明 -> 打包/复制 -> 汇总”整条流程
- 决定什么时候压缩，什么时候复制目录
- 决定什么时候生成汇总文件

改这些内容先看这里：

- 批处理流程
- 纯 PDF 目录处理方式
- 输出归档逻辑
- 汇总文件生成逻辑

### `src/domain`

业务规则层。

核心文件：

- [book_parser.py](C:/code/format/src/domain/book_parser.py)
- [file_metadata.py](C:/code/format/src/domain/file_metadata.py)
- [product_formatter.py](C:/code/format/src/domain/product_formatter.py)

职责：

- 文件名解析
- 书名和作者提取
- PDF 页数 / TXT 行数统计
- 商品介绍模板拼装

改这些内容先看这里：

- 文件名解析规则
- 商品标题生成规则
- 商品介绍模板文案
- 页数/行数统计规则

### `src/infrastructure`

底层适配层。

核心文件：

- [calibre_converter.py](C:/code/format/src/infrastructure/calibre_converter.py)
- [file_ops.py](C:/code/format/src/infrastructure/file_ops.py)
- [zip_archiver.py](C:/code/format/src/infrastructure/zip_archiver.py)

职责：

- 调 Calibre 转换格式
- 扫描敏感词
- 处理文件系统读写
- 生成目录清单
- 复制纯 PDF 目录
- 生成 ZIP 压缩包

改这些内容先看这里：

- Calibre 路径
- 转换参数
- 压缩包排除哪些文件
- 复制目录时排除哪些文件
- 文件读写细节

### `src/presentation`

表现层。

核心文件：

- [console.py](C:/code/format/src/presentation/console.py)

职责：

- 终端输出
- 进度条
- 批量报告

改这些内容先看这里：

- 控制台输出文案
- 进度条样式
- 批量报告格式

### `src/settings.py`

全局配置。

核心文件：

- [settings.py](C:/code/format/src/settings.py)

目前集中放：

- Calibre 路径
- 敏感词列表
- 打包/复制时排除的文件名

改这些内容先看这里：

- 全局常量
- 默认路径
- 排除规则

## 常见改动应该从哪开始

### 想改商品介绍模板

先看：

- [product_formatter.py](C:/code/format/src/domain/product_formatter.py)

### 想改文件名解析规则

先看：

- [book_parser.py](C:/code/format/src/domain/book_parser.py)

### 想改 PDF 页数或 TXT 行数统计

先看：

- [file_metadata.py](C:/code/format/src/domain/file_metadata.py)

### 想改纯 PDF 目录如何进入输出归档

先看：

- [batch_service.py](C:/code/format/src/application/batch_service.py)
- [file_ops.py](C:/code/format/src/infrastructure/file_ops.py)

### 想改压缩包排除哪些文件

先看：

- [settings.py](C:/code/format/src/settings.py)
- [zip_archiver.py](C:/code/format/src/infrastructure/zip_archiver.py)

### 想改命令和参数

先看：

- [main.py](C:/code/format/src/app/main.py)

## 当前主流程落点

主流程总控在：

- [run_batch_workflow](C:/code/format/src/application/batch_service.py)

目录批处理逻辑在：

- [process_directory_batch](C:/code/format/src/application/batch_service.py)

单文件转换逻辑在：

- [convert_single_file](C:/code/format/src/application/batch_service.py)

商品介绍生成在：

- [write_product_description](C:/code/format/src/application/product_service.py)
- [build_product_template](C:/code/format/src/domain/product_formatter.py)

## 当前项目特点

- `epub / mobi / azw3` 转 `pdf` 时，会额外生成 `txt` 和 `docx`
- 纯 PDF 目录会复制到 `输出归档`
- `商品介绍.txt` 和 `文件清单.txt` 不进入压缩包，也不进入纯 PDF 复制结果
- 商品介绍里的“文件页数”当前只统计：
  - `pdf` 的页数
  - `txt` 的行数

## 修改建议

- 改流程顺序，优先看 `application`
- 改业务规则，优先看 `domain`
- 改底层工具调用，优先看 `infrastructure`
- 改显示文案，优先看 `presentation`
- 改全局常量，优先看 `settings.py`

