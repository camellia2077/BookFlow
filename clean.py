import zipfile
import os
import re

def deep_clean_epub(file_path):
    # 定义要删除的关键词黑名单
    blacklist = ["公众号：古德猫宁李", "沉金书屋", "chenjin5.com", "书单分享", "学习资源分析"]
    
    temp_file = file_path + ".clean"
    
    with zipfile.ZipFile(file_path, 'r') as zin:
        with zipfile.ZipFile(temp_file, 'w') as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                
                # 只对 HTML 内容进行扫描
                if item.filename.endswith(('.html', '.xhtml', '.htm')):
                    try:
                        text = data.decode('utf-8')
                        # 逻辑：如果某一行（或标签内）包含黑名单词汇，则替换为空
                        for word in blacklist:
                            # 匹配包含黑名单词汇的整个 HTML 标签块
                            pattern = rf'<[^>]+>[^<]*{re.escape(word)}[^<]*</[^>]+>'
                            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
                        data = text.encode('utf-8')
                    except UnicodeDecodeError:
                        pass # 保持原始二进制数据
                
                zout.writestr(item, data)
    
    os.replace(temp_file, file_path)

# 调用示例
deep_clean_epub("朱可夫元帅战争回忆录.epub")