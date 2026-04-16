FORBIDDEN_KEYWORDS = [
    "公众号",
    "书单分享",
    "电子书搜索下载",
    "电子书打包资源分享",
    "学习资源分享",
    "书友学习交流",
    "学习资源分析",
]

CALIBRE_PATH = r"C:\Program Files\Calibre2\ebook-convert.exe"

# These files are generated to help the seller review and publish a product,
# but they are not part of the ebook bundle delivered to the buyer.
ARCHIVE_EXCLUDED_FILE_PREFIXES = (
    "商品介绍_",
    "商品介绍汇总_",
    "文件清单_",
    "info_",
    "01_封面_",
    "02_目录_",
    "03_内页_",
    "04_内页_",
)
# Product preview screenshots are kept next to the source files for convenience,
# yet they should stay out of archives and copied delivery folders.
ARCHIVE_EXCLUDED_DIRNAMES = {"商品图片"}

# ZIP 压缩等级，范围为 0-9：
# 0 表示仅打包、几乎不压缩；9 表示最高压缩率但速度最慢。
# 电子书文件通常压缩收益有限，默认使用 3，优先兼顾速度与体积。
ZIP_COMPRESSION_LEVEL = 3

PRODUCT_IMAGE_DIRNAME = "商品图片"
# Only image folders carrying this marker are considered owned by the program.
# This protects manually curated folders with the same visible name from deletion.
PRODUCT_IMAGE_MARKER_FILENAME = ".bookflow-generated"
PRODUCT_IMAGE_SCALE = 2.0
# TOC detection is keyword-based on the PDF text layer only.
# If a scan has no text layer, TOC screenshots are intentionally skipped.
TOC_KEYWORDS = ("目录", "目次", "contents", "content")
TOC_CHAPTER_PATTERNS = (
    r"第[一二三四五六七八九十百零〇两0-9]+章",
    r"chapter\s+\d+",
    r"chapter\s+[ivxlcdm]+",
)
TOC_CHAPTER_MATCH_THRESHOLD = 3
