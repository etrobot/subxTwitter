import os

# 定义要替换的目标字符串和替换后的字符串

target_str= '''mt-2 text-sm overflow-hidden h-60'''

replace_str = '''mt-4 text-sm overflow-hidden h-60'''

# 遍历static目录下的所有文件
static_dir = 'static'
for root, dirs, files in os.walk(static_dir):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(root, file)
            # 逐行读取文件内容并替换目标字符串
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                file_content = file_content.replace(target_str, replace_str)
            # 将修改后的内容写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)