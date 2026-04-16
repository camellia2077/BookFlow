import os
import json
import shutil

def apply_rename_from_json(target_dir, json_file):
    """
    根据 JSON 映射表，批量重命名并将成功处理的文件移动到 done 文件夹。
    修复：严格保留文件格式后缀，防止生成 0kb 损坏文件。
    """
    # 1. 加载映射表
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            rename_map = json.load(f)
    except Exception as e:
        print(f"[错误] 无法读取 JSON 文件: {e}")
        return

    # 2. 确保目标文件夹 done 存在
    done_dir = os.path.join(target_dir, "done")
    os.makedirs(done_dir, exist_ok=True)

    # 3. 遍历执行重命名与归档
    count = 0
    for old_name, new_name in rename_map.items():
        old_name = old_name.strip()
        new_name = new_name.strip()
        
        old_path = os.path.join(target_dir, old_name)
        
        # 获取原始文件的扩展名（如 .pdf, .epub）
        _, extension = os.path.splitext(old_name)
        
        # 确保新文件名带有正确的扩展名
        if not new_name.lower().endswith(extension.lower()):
            final_new_name = f"{new_name}{extension}"
        else:
            final_new_name = new_name
            
        new_path = os.path.join(done_dir, final_new_name)

        # 逻辑检查
        if os.path.exists(old_path):
            if os.path.exists(new_path):
                print(f"[跳过] 目标文件已存在: {final_new_name}")
                continue
            
            try:
                # 使用 shutil.move 确保文件内容完整移动
                shutil.move(old_path, new_path)
                print(f"[成功] {old_name} -> done/{final_new_name}")
                count += 1
            except Exception as e:
                print(f"[失败] 无法移动文件 {old_name}: {e}")
        else:
            print(f"[跳过] 未在源目录找到文件: {old_name}")

    print(f"\n--- 审计执行完毕，共处理 {count} 个文件 ---")

if __name__ == "__main__":
    # 配置你的实际路径
    MY_DIR = r"C:\Users\17596\Downloads\Navy - 副本" 
    MY_JSON = r"C:\code\format\temp\rename_list.json"
    
    apply_rename_from_json(MY_DIR, MY_JSON)