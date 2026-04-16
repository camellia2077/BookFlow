import argparse
import os
import sys

from src.application.batch_service import run_batch_workflow, run_image_generation_workflow


def build_parser():
    parser = argparse.ArgumentParser(description="电子书处理工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="转换电子书并生成统计信息")
    convert_parser.add_argument("input", help="输入文件或文件夹路径")
    convert_parser.add_argument(
        "-f",
        "--format",
        default="pdf",
        choices=["pdf", "txt", "docx"],
        metavar="FMT",
        help="目标格式",
    )
    convert_parser.add_argument(
        "--no-archive",
        action="store_true",
        help="只转换和生成说明文件，不压缩也不复制到输出归档",
    )

    scan_parser = subparsers.add_parser("scan", help="仅扫描敏感词，不执行转换")
    scan_parser.add_argument("input", help="输入文件或文件夹路径")

    image_parser = subparsers.add_parser("images", help="仅根据现有PDF生成商品图片")
    image_parser.add_argument("input", help="输入PDF文件或目录路径")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not os.path.exists(args.input):
        sys.stdout.write(f"❌ 找不到输入目标: {args.input}\n")
        return 1

    if args.command == "scan":
        run_batch_workflow(args.input, user_format="pdf", scan_only=True, no_archive=False)
        return 0

    if args.command == "convert":
        run_batch_workflow(args.input, user_format=args.format, scan_only=False, no_archive=args.no_archive)
        return 0

    if args.command == "images":
        run_image_generation_workflow(args.input)
        return 0

    parser.error(f"未知命令: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
