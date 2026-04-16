import os
import re

# 配置目标目录
TARGET_DIR = r'C:\Users\17596\Downloads\新建文件夹 (2)' # 请修改为你的电子书实际路径

def clean_filename(filename):
    """
    针对 Anna's Archive 文件名的保守清理函数
    目标：剔除 ISBN、MD5、Anna 标签，保留书名、副标题与版本信息。
    """
    # 1. 分离扩展名
    base, ext = os.path.splitext(filename)
    if ext.lower() not in ['.pdf', '.epub', '.mobi', '.azw3']:
        return None

    # 2. 根据 Anna 站典型的 " -- " 分隔符切分
    # 结构通常为: [书名] -- [作者] -- [出版年/出版社] -- [ISBN] -- [哈希值] -- [来源标签]
    parts = base.split(' -- ')
    
    if len(parts) >= 2:
        # 核心信息提取
        title = parts[0].strip()
        author = parts[1].strip()
        
        # 处理作者名倒置 (Lastname, Firstname -> Firstname Lastname)
        if ',' in author and ';' not in author: # 避免误伤多作者分号
            name_parts = author.split(',')
            if len(name_parts) == 2:
                author = f"{name_parts[1].strip()} {name_parts[0].strip()}"
        
        # 处理书名中的特殊下划线（Anna 常将冒号标为 _ ）
        # 使用保守替换：只处理带空格的下划线，保留单词内部的下划线（若有）
        title = title.replace('_ ', ': ').replace(' _', ': ')
        
        # 3. 构造新文件名 (作者 - 书名)
        # 这种结构保证了即便 title 包含多余版本信息，也不会丢失数据
        new_name = f"{author} - {title}"
        
        # 4. 极致保守的字符清洗
        # a. 将非法字符替换为空格，而不是直接删除，防止单词粘连
        new_name = re.sub(r'[\\/*?:"<>|]', " ", new_name)
        # b. 将连续的空格合并为一个
        new_name = re.sub(r'\s+', " ", new_name)
        # c. 修正结尾可能出现的点或空格（Windows 不允许文件名以点结尾）
        new_name = new_name.strip().strip('.')
        
        return f"{new_name}{ext}"
    
    return None

def batch_rename(path):
    """
    批量执行重命名，并打印日志
    """
    for filename in os.listdir(path):
        new_name = clean_filename(filename)
        if new_name and new_name != filename:
            old_file = os.path.join(path, filename)
            new_file = os.path.join(path, new_name)
            
            # 冲突检查
            if os.path.exists(new_file):
                print(f"[跳过] 目标已存在: {new_name}")
                continue
                
            try:
                os.rename(old_file, new_file)
                print(f"[成功] {filename} -> {new_name}")
            except Exception as e:
                print(f"[错误] 重命名失败 {filename}: {e}")

if __name__ == "__main__":
    batch_rename(TARGET_DIR)