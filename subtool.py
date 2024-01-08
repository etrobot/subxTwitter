import os

# 定义要替换的目标字符串和替换后的字符串
# target_str='subscribe by id in your language.<br><div class="title">Start for FREE</div>'
# replace_str='subscribe by id in your language.<br><div class="title font-bold">Start for FREE</div>'


# target_str= '''<div><button id="theme-toggle" class="px-2 rounded">🌒</button></div>'''
# replace_str = '''<div><button id="theme-toggle" class="px-2 rounded">🌒</button></div>
# <div class="sidebar w-full max-w-sm items-center"></div>'''

# target_str= '''img style="max-width: 20rem;margin:0.2rem auto;"'''
# replace_str = '''img style="max-width: 20rem;margin:1rem;"'''

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