import time
from datetime import datetime,timedelta
from main import sumTweets,sendEmail,getTwList,select_data_as_dataframe,addSubInfo,cursor
import pandas as pd
from bs4 import BeautifulSoup
import os,sys

lists=[
    {'id':'1733652180576686386','name':'AGI Thoughts','headPicId':'https://pbs.twimg.com/list_banner_img/1733654690490200064/ig-cUZfi?format=jpg&name=360x360'},
    {'id': '1365676237558059010', 'name': 'Never Boring', 'headPicId': 'https://pbs.twimg.com/media/EXZ1_hkUYAA56JA?format=png&name=360x360'},
    {'id': '967467772341923840', 'name': 'BitCoin', 'headPicId': 'https://pbs.twimg.com/list_banner_img/1274429237349552129/shZgINIk?format=jpg&name=360x360'},
    {'id': '1283027505297985536', 'name': 'Building In Public', 'headPicId': 'https://pbs.twimg.com/list_banner_img/1283027805253533698/B7VpTOsQ?format=jpg&name=360x360'},
    {'id': '1432003348744470530', 'name': 'Design Teams', 'headPicId': 'https://pbs.twimg.com/list_banner_img/1432005358386483206/8bsQ-_Po?format=jpg&name=360x360'},
]

langs = {
    # 'zh-CN': '简体中文',
    # 'zh-TW': '繁體中文',
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
    'th':'ไทย',
    'en': 'English'
}


domTemplate='''
    <div class="card flex flex-col rounded-xl my-1 p-4 bg-gray-500 bg-opacity-5 max-w-screen-md mx-auto">
        <div class="flex w-full items-center space-x-2 max-w-screen-lg">
            <div class="w-16 h-10 rounded overflow-hidden">
                <img src="{{headPicId}}" class="object-none w-full h-full"/>
            </div>

            <a class="text-sm w-full" href="https://twitter.com/i/lists/{{listId}}">
                <div class="font-bold">{{name}}</div>
                <div class="text-gray-500">{{listId}}</div>
            </a>
            <button class="subx bg-blue-400 text-white px-3 py-1  rounded-full" value="{{listId}}">🔔</button>
        </div>
        <div class="mt-2 text-sm overflow-hidden h-80">
            {{sumTweets}}
        </div><br><br><br><br><br><br>
    </div>
'''


def output(lang:str,doms=None):
    domFinal = '''
        <div class="card flex flex-col rounded-xl mx-1 my-1 p-4 bg-gray-500 bg-opacity-5">
            <div class="mt-2 text-sm overflow-hidden h-80">
                <p>You can <a style="color:#5da2ff;" href="https://business.twitter.com/en/blog/twitter-101-lists.html">edit your own Twitter List</a> and subscribe by id in your language.</p>
                <p class="title font-bold">Start for FREE</p>
            </div><br><br><br><br><br>
        </div>
        '''
    if doms is None:
        doms = {}
        for li in lists:
            doms[li["id"]] = localTweets(f'static/{lang}_{li["id"]}.html')
    for li in lists:
        atriclePath='<a class="ml-auto mt-1 text-xs"  style="color:#5da2ff;" href="/lang/{p}">show more</a>'.format(p=lang + '_' + li['id'])
        dom = domTemplate.replace('{{sumTweets}}',doms[li["id"]]).replace("{{listId}}",li['id']).replace("{{name}}",li['name']).replace("{{headPicId}}",li['headPicId'])
        doms[li["id"]]=dom.replace("<br><br><br><br><br><br>",atriclePath).replace('max-w-screen-md mx-auto','mx-1')
    domstr=list(doms.values())
    domstr.append(domFinal)
    fulldom='\n'.join(domstr)
    with open('templates/template.html', 'r') as f:
        template = f.read()
    rendered_template = template.replace('{{gptDoms}}',fulldom)
    with open('static/%s.html'%lang, 'w') as f:
        f.write(rendered_template)
    if lang=='en':
        with open('static/index.html', 'w') as f:
            f.write(rendered_template)

def localTweets(filename:str):
    print('open ',filename)
    with open(filename, 'r') as file:
        content = file.read()
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(content, 'html.parser')
    # 提取目标HTML片段
    div_element = soup.find('div', class_='mt-2 text-sm')
    return div_element.prettify()

def prepare():
        for lang in langs.keys():
            doms=dict()
            for li in lists:
                tweetDf, disc, nit = getTwList(li['id'])
                # retry=5
                # while retry>0:
                #     try:
                filename = f'static/{lang}_{li["id"]}.html'
                sumhtml = sumTweets(df=tweetDf, nitter=nit, lang=langs[lang])
                doms[li['id']] = sumhtml
                dom = domTemplate.replace('{{sumTweets}}', sumhtml).replace("{{listId}}", li["id"]).replace("{{name}}",li['name']).replace("{{headPicId}}",li['headPicId'])
                with open('templates/template.html', 'r') as f:
                    template = f.read()
                idleDom = dom.replace('card ', '').replace(' overflow-hidden h-80', '')
                rendered_template = template.replace('{{gptDoms}}', idleDom)
                with open(filename, 'w') as f:
                    f.write(rendered_template)
                    # except Exception as e:
                    #     print(e)
                    #     time.sleep(30)
                    #     retry-=1
                    #     continue
            output(lang,doms)

def mission():
    pd.set_option('display.max_columns', None)
    # print(select_data_as_dataframe('users'))
    # sql_query = "SELECT * FROM users WHERE expire_date >= :curdate AND mail_time <= :pushTime AND mail_time >= :checkTime"
    curdate = datetime.utcnow()  # 替换为你需要的日期时间
    checkTime = curdate - timedelta(minutes=5)
    pushTime = curdate + timedelta(minutes=5)
    print(checkTime,pushTime)
    df = select_data_as_dataframe('users', '*',
                                  'expire_date >= :curdate AND mail_time <= :pushTime AND mail_time >= :checkTime',
                                  curdate=curdate, pushTime=pushTime, checkTime=checkTime)
    # print(df)
    for k, v in df.iterrows():
        mail=v['EMAIL']
        expired=v['EXPIRE_DATE'].strftime("%Y/%m/%d")
        print(mail, v['MAIL_TIME'])
        tweetDf,disc,nit=getTwList(v['TARGET_ID'])
        filename=f'static/{v["LANG"]}_{v["TARGET_ID"]}.html'
        if os.path.isfile(filename) and tweetDf['published'].values[0]<os.path.getmtime(filename):
            html_fragment = localTweets(filename)
            sendEmail(addSubInfo(disc,html_fragment, mail, expired), receiver=mail)
        else:
            sumhtml = sumTweets(df=tweetDf,nitter=nit, lang=v['LANG'])
            sendEmail(addSubInfo(disc,v["TARGET_ID"],sumhtml, mail, expired), receiver=mail)
            dom = domTemplate.replace('{{sumTweets}}', sumhtml).replace("{{listId}}", v["TARGET_ID"]).replace("{{name}}",disc)
            with open('templates/template.html', 'r') as f:
                template = f.read()
            idleDom = dom.replace('card ', '').replace(' overflow-hidden h-80', '')
            rendered_template = template.replace('{{gptDoms}}', idleDom)
            with open(filename, 'w') as f:
                f.write(rendered_template)
            output(v['LANG'])
        sql_update = "UPDATE users SET mail_time = :new_mail_time WHERE email = :email"
        cursor.execute(sql_update, {"new_mail_time": v['MAIL_TIME'] + timedelta(days=1), "email": mail})
        cursor.connection.commit()

if __name__=='__main__':
    if sys.argv[-1]=='-p':
        prepare()
        # output('zh-TW')
    else:
        mission()
