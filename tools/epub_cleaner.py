import os
import zipfile
from bs4 import BeautifulSoup

def clean_epub_with_bs4(input_path, output_path=None, keywords=None):
    """
    使用 BS4 重构 EPUB 清洗逻辑，避免正则误伤与编码崩溃。
    """
    if not keywords:
        return

    is_overwrite = False
    if not output_path or os.path.abspath(output_path) == os.path.abspath(input_path):
        is_overwrite = True
        work_path = input_path + ".tmp"
    else:
        work_path = output_path

    try:
        with zipfile.ZipFile(input_path, 'r') as zin, \
             zipfile.ZipFile(work_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            
            if 'mimetype' in zin.namelist():
                zout.writestr('mimetype', zin.read('mimetype'), compress_type=zipfile.ZIP_STORED)
                
            for item in zin.infolist():
                if item.filename == 'mimetype':
                    continue
                    
                content = zin.read(item.filename)
                
                # 仅针对文档结构层进行介入
                if item.filename.lower().endswith(('.html', '.xhtml', '.htm')):
                    # 补充盲点 1: 多重编码降级重试机制
                    try:
                        html_text = content.decode('utf-8')
                    except UnicodeDecodeError:
                        html_text = content.decode('gbk', errors='ignore')
                    
                    # 使用 HTML 解析器构建 DOM 树
                    soup = BeautifulSoup(html_text, 'html.parser')
                    
                    # 补充盲点 2: 仅操作纯文本节点 (NavigableString)，不破坏标签结构
                    for text_node in soup.find_all(string=True):
                        node_text = str(text_node)
                        has_mod = False
                        
                        for kw in keywords:
                            if kw in node_text:
                                node_text = node_text.replace(kw, '')
                                has_mod = True
                                
                        if has_mod:
                            # 顺带清理常见的 HTML 实体空白残留
                            node_text = node_text.replace('&nbsp;', '').replace('\xa0', '').strip()
                            text_node.replace_with(node_text)
                            
                    # 清理无内容的死节点 (跳过自闭合空标签如 img, br, hr, meta)
                    for tag in soup.find_all():
                        if tag.name not in ['img', 'br', 'hr', 'meta', 'link']:
                            # 如果标签内既没有文本，也没有需要保留的子标签
                            if not tag.get_text(strip=True) and not tag.find_all(['img', 'br']):
                                tag.decompose()
                                
                    content = str(soup).encode('utf-8', errors='ignore')
                    
                zout.writestr(item, content)
                
    except Exception as e:
        # 异常阻断：捕获导致 1KB 的底层崩溃，安全撤销临时文件
        if is_overwrite and os.path.exists(work_path):
            os.remove(work_path)
        raise RuntimeError(f"流控异常，已终止并保护源文件: {str(e)}")

    if is_overwrite:
        os.replace(work_path, input_path)

if __name__ == "__main__":
    TARGET_KEYWORDS = [
        "读累了记得休息一会哦~",
        "电子书搜索下载",
        "书友学习交流",
        "网站：",
        "电子书打包资源分享",
        "学习资源分享"
    ]
    
    test_input = "帝国的背影：土耳其简史+哈布斯堡王朝 by 彼得·贾德森, 诺曼·斯通.epub"
    
    if os.path.exists(test_input):
        clean_epub_with_bs4(test_input, keywords=TARGET_KEYWORDS)
        print(f"处理完成，DOM 已净化：{test_input}")
    else:
        print(f"找不到输入文件")