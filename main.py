import os,re
from datetime import datetime,timedelta
import random
import openai
from markdownify import markdownify
from crud import *
import pandas as pd
import requests
from bs4 import BeautifulSoup
from litellm import completion
from feedparser import parse
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from markdown import markdown
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
# openai v1.0.0+
client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'],base_url=os.environ['API_BASE_URL'])

NITTER = os.environ['NITTER'].split(';')

def sendEmail(message:str,receiver:str='d361@qq.com',subject:str=''):
    '''
    发送邮件的方法
    :param message:
    :param receiver:
    :param subject:
    :return:
    '''
    if len(message)==0:
        return
    message=message.replace('<td','<td style="border:1px solid grey;"').replace('<table','<table style="border-collapse:collapse;"')
    subject='GPT Subscription for Twitter Lists'
    sender = os.environ['MAIL'] #发送的邮箱
    smtpserver = os.environ['SMTP']
    username = os.environ['MAIL'] #你的邮箱账号
    password = os.environ['MAILPWD'] #你的邮箱密码
    msg = MIMEText(message,'html','utf-8') #中文需参数‘utf-8'，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8') #邮件主题
    msg['from'] = sender    #自己的邮件地址
    smtp = smtplib.SMTP(smtpserver, 587)
    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string()) #发送
    smtp.quit() # 结束
    print(sender, receiver)

def getTwList(twitter_user:str):
    for nit in NITTER:
        try:
            rss_url = f'https://{nit}/i/lists/{twitter_user}/rss'
            print(rss_url)
            feed = parse(rss_url)
            df = pd.json_normalize(feed.entries)
            df['timestamp'] = df['published'].apply(lambda x: pd.Timestamp(x).timestamp())
            # df.to_csv('test.csv',index=False)
            disc=feed.feed.title.split('/')[0].strip()
            print(disc)
            return df,disc,nit
        except Exception as e:
            print(e)
            continue

def addSubInfo(disc:str,listId:str,html_fragment:str,mail:str,expired:str):
    listHref=f'<p><a href="https://twitter.com/i/lists/{listId}">twitter.com/i/lists/{disc}</a></p>'
    button = f'''<a style="display: inline-block;
               padding: 4px;
               background-color: #2a79ef;
               color: white;
               text-decoration: none;
               border-radius: 4px;
               border: none;
               cursor: pointer;
               text-align: center;
               font-size: 16px;"
       href="https://subx.fun/pay?email={mail}">$5 for 3 months</a>
            '''
    return listHref + html_fragment + '\n\n subscription expired on %s ' %expired  + button + f'<p><a href="https://subx.fun/unsubscribe?email={mail}">Unsubscribe</a></p>'

def sumTweets(df:pd.DataFrame,nitter:str,lang = '中文',length:int = 10000, model='openai/gpt-3.5-turbo-1106'):
    '''
    抓取目标推特AI总结并发邮件
    :param lang:
    :param length:
    :param model:
    :return:
    '''

    for k, v in df.iterrows():
        pattern = r'<a\s+.*?href="([^"]*https://%s/[^/]+/status/[^"]*)"[^>]*>'%nitter.replace(".",r'\.')
        matches = re.findall(pattern, v['summary'])
        if len(matches) > 0:
            if matches[0] in df['id'].values:
                indices = df[df['id'] == matches[0]]
                df.at[k, 'summary'] = re.sub(pattern, "<blockquote>%s</blockquote>" % indices['summary'].values[0],
                                             v['summary'])
                df = df.drop(indices.index)
            else:
                headers = {
                    'accept-language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6,ja;q=0.5',
                    'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36"
                }
                session = requests.Session()
                session.headers = headers
                oripost = session.get(matches[0]).text
                quote = BeautifulSoup(oripost, 'html.parser').title.string.replace(" | nitter", '')
                df.at[k, 'summary'] = re.sub(pattern, "<blockquote>%s</blockquote>" % quote, v['summary'])
    df['content'] ='[' + df['published'].str[len('Sun, '):-len(' GMT')] +' '+ df['author'] + ']' + '(' + df[
        'id'].str.replace(nitter, 'x.com') + '): ' + df['summary']
    df['content'] = df['content'].astype(str).apply(lambda x: markdownify(x))
    # df.to_csv('test.csv', index=False)
    contents=[]
    for tweet in df['content'].values:
        if len(''.join(contents))<length:
            contents.append(tweet)
        else:
            break
    tweets = '<hr>'.join(contents).replace(nitter, 'x.com').replace('x.com/pic',nitter+'/pic')
    prompt = "<tweets>{tweets}</tweets>\nThe above are some tweets. You are a senior editor of a {lang} blog focusing on edition of tweets. " \
              "Please compile the above tweets into a {lang} article formatted in markdown, keeping " \
              "the format that including  tweeting time, author,Twitter link, " \
              "and Twitter content, kindly comment after every tweet in language {lang}. " \
             "If you can tidy all the tweets well, you will get USD200 as extra bonus."
    prompt = prompt.format(tweets=tweets.replace('\n\n','\n').replace('\_','_'),lang=lang)
    print('tweets:', prompt)
    result = completion(model=model, messages=[{"role": "user", "content": prompt}],
                        api_base=os.environ['API_BASE_URL'],
                        api_key=os.environ['OPENAI_API_KEY'],
    )["choices"][0]["message"][
        "content"]
    result=markdown(result.replace('```','').replace('markdown',''),extensions=['markdown.extensions.tables']).replace('><a href','><a style="color:#5da2ff;" href').replace('<img alt="','<img style="max-height: 16rem;margin:1rem;" alt="').replace('http://','https://')
    return result

def run():
    pd.set_option('display.max_columns', None)
    # print(select_data_as_dataframe('users'))
    # sql_query = "SELECT * FROM users WHERE expire_date >= :curdate AND mail_time <= :pushTime AND mail_time >= :checkTime"
    curdate = datetime.utcnow()  # 替换为你需要的日期时间
    checkTime = curdate - timedelta(minutes=5)
    pushTime = curdate + timedelta(minutes=5)
    # print(checkTime,pushTime)
    df = select_data_as_dataframe('users', '*','expire_date >= :curdate AND mail_time <= :pushTime AND mail_time >= :checkTime', curdate=curdate, pushTime=pushTime, checkTime=checkTime)
    print(df)
    # Print the results
    for k,v in df.iterrows():
        mail=v['EMAIL']
        expired=v['EXPIRE_DATE'].strftime("%Y/%m/%d")
        print(v)
        print(checkTime, pushTime,v['MAIL_TIME'])
        tweetDf,disc,nit=getTwList(v['TARGET_ID'])
        sumhtml= sumTweets(tweetDf,nit,lang=v['LANG'])
        if '@' in mail:
            sendEmail(addSubInfo(sumhtml, mail, expired), receiver=mail)
        sql_update = "UPDATE users SET mail_time = :new_mail_time WHERE email = :email"
        cursor.execute(sql_update, {"new_mail_time": v['MAIL_TIME']+timedelta(days=1), "email": mail})
        cursor.connection.commit()

    cursor.connection.close()

if __name__=='__main__':
    run()