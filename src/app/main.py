import argparse
import os
import sys

from src.application.batch_service import run_batch_workflow


def build_parser():
    parser = argparse.ArgumentParser(description="电子书处理工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="转换电子书并生成统计信息")
    convert_parser.add_argument("input", help="输入文件或文件夹路径")
    convert_parser.add_argument("-f", "--format", default="pdf", metavar="FMT", help="目标格式")

    scan_parser = subparsers.add_parser("scan", help="仅扫描敏感词，不执行转换")
    scan_parser.add_argument("input", help="输入文件或文件夹路径")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not os.path.exists(args.input):
        sys.stdout.write(f"❌ 找不到输入目标: {args.input}\n")
        return 1

    if args.command == "scan":
        run_batch_workflow(args.input, user_format="pdf", scan_only=True)
        return 0

    if args.command == "convert":
        run_batch_workflow(args.input, user_format=args.format, scan_only=False)
        return 0

    parser.error(f"未知命令: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
