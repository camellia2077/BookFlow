import subprocess
import os
import argparse
import sys

# --- 1. Bootstrap: 环境检测 ---
def check_environment():
    """检测转换引擎是否存在，返回路径或抛出异常"""
    calibre_path = r"C:\Program Files\Calibre2\ebook-convert.exe"
    if not os.path.exists(calibre_path):
        raise FileNotFoundError(f"未找到 Calibre 转换引擎于 {calibre_path}")
    return calibre_path

# --- 2. UI/Display: 负责显示层 ---
def display_progress(current, total, fmt, filename):
    """负责原地刷新进度显示"""
    status_text = f"\r任务进度: [{current}/{total}] | 正在处理: {fmt:<5} | 文件: {filename}"
    sys.stdout.write(status_text)
    sys.stdout.flush()

def display_error(fmt, message=""):
    """负责错误信息的输出格式"""
    sys.stdout.write(f"\n  [失败]: {fmt} 转换出错。{message}\n")

def display_final(filename):
    """任务完成后的最终输出"""
    sys.stdout.write(f"\n[完成]: '{filename}' 的所有转换任务已结束。\n")
    sys.stdout.flush()

# --- 3. Conversion Engine: 转换逻辑与 IO 解耦 ---
def run_conversion_task(engine_path, input_path, output_path, target_fmt):
    """
    纯粹的转换执行器，不含 print。
    返回 (bool, error_message)
    """
    command = [engine_path, input_path, output_path]
    if target_fmt.lower() == "pdf":
        command.extend(["--paper-size", "a4", "--pdf-default-font-size", "12"])
    
    try:
        subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )
        return True, ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr

# --- 4. Core Logic: 任务编排与格式策略 ---
def get_target_formats(input_ext, user_specified_format):
    """根据策略决定需要转换的格式列表"""
    input_ext = input_ext.lower().strip('.')
    # 逻辑解耦：如果是特定格式且用户未指定特殊要求，则触发全格式输出
    if input_ext in ['epub', 'mobi', 'azw3'] and user_specified_format == "pdf":
        return ["pdf", "txt", "docx"]
    return [user_specified_format]

def execute_conversion_flow(input_path, user_format):
    """主业务流编排"""
    # 环境自检
    try:
        engine_path = check_environment()
    except Exception as e:
        print(f"环境错误: {e}", file=sys.stderr)
        return

    # 路径解析
    base_name, input_ext = os.path.splitext(input_path)
    file_name = os.path.basename(input_path)
    
    # 策略决策
    formats_to_process = get_target_formats(input_ext, user_format)
    total = len(formats_to_process)

    # 流程控制
    for i, fmt in enumerate(formats_to_process, 1):
        fmt = fmt.lower().strip('.')
        output_path = f"{base_name}.{fmt}"
        
        # 调用显示层
        display_progress(i, total, fmt, file_name)
        
        # 调用转换引擎
        success, err = run_conversion_task(engine_path, input_path, output_path, fmt)
        
        if not success:
            display_error(fmt)

    display_final(file_name)

# --- 5. Main: 入口与参数解析 ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="分层架构的电子书转换工具")
    parser.add_argument("input", help="输入文件的路径")
    parser.add_argument("-f", "--format", default="pdf", help="目标格式")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 找不到文件 '{args.input}'", file=sys.stderr)
    else:
        execute_conversion_flow(args.input, args.format)