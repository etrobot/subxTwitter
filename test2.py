import os

# 定义要替换的目标字符串和替换后的字符串
target_str = '''<a href="/zh-CN" class="border-b-2 mr-2">简体中文</a>
        <a href="/zh-TW" class="border-b-2 mr-2">繁體中文</a>
        <a href="/en" class="border-b-2 mr-2">English</a>
        <a href="/ja" class="border-b-2 mr-2">日本語</a>
        <a href="/ko" class="border-b-2 mr-2">한국어</a>
        <a href="/es" class="border-b-2 mr-2">Español</a>
        <a href="/pt" class="border-b-2 mr-2">Português</a>
        <a href="/de" class="border-b-2 mr-2">Deutsch</a>
        <a href="/fr" class="border-b-2 mr-2">Français</a>
        <a href="/ar" class="border-b-2 mr-2">العربية</a>
        <a href="/id" class="border-b-2 mr-2">Bahasa Indonesia</a>
        <a href="/ms" class="border-b-2 mr-2">Bahasa Melayu</a>
        <a href="/tl" class="border-b-2 mr-2">Filipino</a>
        <a href="/vi" class="border-b-2 mr-2">Tiếng Việt</a>
        <a href="/pl" class="border-b-2 mr-2">Polski</a>
        <a href="/nl" class="border-b-2 mr-2">Nederlands</a>'''
replace_str = '''<a href="/lang/zh-CN" class="border-b-2 mr-2">简体中文</a>
        <a href="/lang/zh-TW" class="border-b-2 mr-2">繁體中文</a>
        <a href="/lang/en" class="border-b-2 mr-2">English</a>
        <a href="/lang/ja" class="border-b-2 mr-2">日本語</a>
        <a href="/lang/ko" class="border-b-2 mr-2">한국어</a>
        <a href="/lang/es" class="border-b-2 mr-2">Español</a>
        <a href="/lang/pt" class="border-b-2 mr-2">Português</a>
        <a href="/lang/de" class="border-b-2 mr-2">Deutsch</a>
        <a href="/lang/fr" class="border-b-2 mr-2">Français</a>
        <a href="/lang/ar" class="border-b-2 mr-2">العربية</a>
        <a href="/lang/id" class="border-b-2 mr-2">Bahasa Indonesia</a>
        <a href="/lang/ms" class="border-b-2 mr-2">Bahasa Melayu</a>
        <a href="/lang/tl" class="border-b-2 mr-2">Filipino</a>
        <a href="/lang/vi" class="border-b-2 mr-2">Tiếng Việt</a>
        <a href="/lang/pl" class="border-b-2 mr-2">Polski</a>
        <a href="/lang/nl" class="border-b-2 mr-2">Nederlands</a>
'''

target_str= '''<img alt="'''

replace_str = '''<img class="max-w-xs m-2" alt="'''

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