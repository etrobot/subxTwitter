from main import sumTweets

lists=[
    {'id':'1733652180576686386','name':'AGI Thoughts','headPicId':'https://pbs.twimg.com/list_banner_img/1733654690490200064/ig-cUZfi?format=jpg&name=360x360'},
    {'id': '1365676237558059010', 'name': 'Never Boring', 'headPicId': 'https://pbs.twimg.com/media/EXZ1_hkUYAA56JA?format=png&name=360x360'},
    {'id': '967467772341923840', 'name': 'BitCoin', 'headPicId': 'https://pbs.twimg.com/list_banner_img/1274429237349552129/shZgINIk?format=jpg&name=360x360'},
    {'id': '1283027505297985536', 'name': 'Building In Public', 'headPicId': 'https://pbs.twimg.com/list_banner_img/1283027805253533698/B7VpTOsQ?format=jpg&name=360x360'},
    {'id': '1432003348744470530', 'name': 'Design Teams', 'headPicId': 'https://pbs.twimg.com/list_banner_img/1432005358386483206/8bsQ-_Po?format=jpg&name=360x360'},
    {'id': '810352678735781888', 'name': 'Reading', 'headPicId': 'https://pbs.twimg.com/media/EXZ2w_qUcAMwN3x?format=png&name=360x360'}
]
langs = {
    'zh-CN': '简体中文',
    'zh-TW': '繁體中文',
    'en': 'English',
    'ja': '日本語',
    'ko': '한국어',
    'es': 'Español',
    'pt': 'Português',
    'de': 'Deutsch',
    'fr': 'Français',
    'ar': 'العربية',
    'id': 'Bahasa Indonesia',
    'ms': 'Bahasa Melayu',
    'tl': 'Filipino',
    'vi': 'Tiếng Việt',
    'pl': 'Polski',
    'nl': 'Nederlands',
}


domTemplate='''
    <div class="flex flex-col rounded-xl mx-1 my-1 p-4 max-w-md bg-gray-500 bg-opacity-5">
        <div class="flex w-full items-center space-x-2 ">
            <div class="w-16 h-10 rounded overflow-hidden">
                <img src="{{headPicId}}" class="object-none w-full h-full"/>
            </div>

            <a class="text-sm w-full" href="https://twitter.com/i/lists/{{listId}}">
                <div class="font-bold">{{name}}</div>
                <div class="text-gray-500">{{listId}}</div>
            </a>
            <button class="subx bg-blue-400 text-white px-3 py-1  rounded-full" value="{{listId}}">🔔</button>
        </div>
        <div class="mt-2 text-sm overflow-hidden h-60">
            {{sumTweets}}
        </div><br>{{path}}
    </div>
'''

htmlHead='''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/html">

<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>GPT Subscripton for Twitter List</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
   <link rel="stylesheet" href="/static/style.css">
</head>
<body class="bg-gray-100">
<div><button id="theme-toggle" class="px-2 rounded">🌒</button></div>
'''

htmlTail='''<script src="/static/index.js"></script></body>
'''

def output():
    for l in langs.keys():
        lang=langs[l]
        doms = []
        for li in lists:
            htmlstr = sumTweets(li['id'],'',lang)
            atriclePath='<a href="/lang/{p}">more</a>'.format(p=l + '_' + li['id'])
            dom = domTemplate.replace('{{sumTweets}}',htmlstr).replace("{{listId}}",li['id']).replace("{{name}}",li['name']).replace("{{headPicId}}",li['headPicId']).replace("{{path}}",atriclePath).replace('<a href','<a class="text-blue-400" href').replace('<img alt="','<img class="max-w-xs m-2" alt="')
            with open('static/%s.html' % (l + '_' + li['id']), 'w') as f:
               f.write(htmlHead+dom.replace('max-w-md ','').replace(' overflow-hidden h-60','').replace(atriclePath,'<a href="/lang/{p}">{p}</a>'.format(p=l))+htmlTail)
            doms.append(dom)
        fulldom='\n'.join(doms)
        with open('templates/template.html', 'r') as f:
            template = f.read()
        rendered_template = template.replace('{{gptDoms}}',fulldom)
        with open('static/%s.html'%l, 'w') as f:
            f.write(rendered_template)
        if l=='en':
            with open('static/index.html', 'w') as f:
                f.write(rendered_template)

output()

