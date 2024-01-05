import os,re
from datetime import datetime,timedelta

import openai
from markdownify import markdownify as md

import oracledb
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
    subject=datetime.now().strftime('%Y年%m月%d日')+subject
    sender = os.environ['MAIL'] #发送的邮箱
    receiver = receiver.split(';')  #要接受的邮箱（注:测试中发送其他邮箱会提示错误）
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

def sumTweets(twitter_user:str,mail:str,lang = '中文',length:int = 10000, model='openai/gpt-3.5-turbo-1106'):
    '''
    抓取目标推特AI总结并发邮件
    :param lang:
    :param length:
    :param model:
    :param mail:
    :param render:
    :return:
    '''
    nitter:str = os.environ['NITTER']
    rss_url = f'https://{nitter}/i/lists/{twitter_user}/rss'
    print(rss_url)
    feed = parse(rss_url)
    df = pd.json_normalize(feed.entries)
    for k, v in df.iterrows():
        pattern = r'<a\s+.*?href="([^"]*https://%s/[^/]+/status/[^"]*)"[^>]*>'%nitter.replace(".",r'\.')
        matches = re.findall(pattern, v['summary'])
        if len(matches) > 0:
            if matches[0] in df['id'].values:
                indices = df[df['id'] == matches[0]]
                df.at[k, 'summary'] = re.sub(pattern, "<blockquote>%s</blockquote>" % indices['summary'].values[0],
                                             v['summary'])
                if 'i/lists' in twitter_user:
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
    df['content'] ='[' + df['published'].str[len('Sun, '):-len(' GMT')] + df['author'] + ']' + '(' + df[
        'id'].str.replace(nitter, 'x.com') + '): ' + df['summary']
    # df.to_csv('test.csv', index=False)
    contents=[]
    for tweet in df['content'].values:
        if len(''.join(contents))<10000:
            contents.append(tweet)
        else:
            break
    tweets = '<br>'.join(contents).replace(nitter, 'x.com').replace('x.com/pic',nitter+'/pic')
    prompt =  "<tweets>{tweets}</tweets>\nThe above are some tweets. You are a senior writer of {lang} blog. Please compile the above tweets into a {lang} article formatted in markdown, including the time of tweeting, author (if any), and Twitter link (if any). Yes) and Twitter content as well as your interpretation and comments"
    prompt =  prompt.format(tweets=md(tweets).replace('\n\n','\n').replace('\_','_'),lang=lang)
    print('tweets:', prompt)
    result = completion(model=model, messages=[{"role": "user", "content": prompt}],
                        api_base=os.environ['API_BASE_URL'],
                        api_key=os.environ['OPENAI_API_KEY'],
    )["choices"][0]["message"][
        "content"]
    result=markdown(result.replace('```','').replace('markdown',''),extensions=['markdown.extensions.tables'])
    if '@' in mail:
        sendEmail(result,receiver=mail)
    return result

def run():
    cs = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-sanjose-1.oraclecloud.com))(connect_data=(service_name=g6587d1fcad5014_subxtwitter_medium.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"
    conn = oracledb.connect(user="ADMIN", password='Gnpw#0755#OC', dsn=cs)
    cursor = conn.cursor()
    # Define the SQL query
    checkTime = datetime.utcnow() - timedelta(minutes=5)
    pushTime = datetime.utcnow() + timedelta(minutes=5)
    sql_query = "SELECT * FROM users WHERE expire_date >= :curdate AND mail_time <= :pushTime AND mail_time >= :checkTime"
    cursor.execute(sql_query,curdate=datetime.now(),pushTime=pushTime,checkTime=checkTime)
    sql_query = "SELECT * FROM users WHERE expire_date >= :curdate"
    cursor.execute(sql_query,curdate=datetime.now())
    # Fetch all rows from the result set
    rows = cursor.fetchall()

    # Print the results
    for row in rows:
        # print(row)
        # print(checkTime, pushTime,row[3])
        sumTweets(twitter_user=row[1],mail=row[0],lang=row[2],render=True)
        sql_update = "UPDATE users SET mail_time = :new_mail_time WHERE email = :email"
        cursor.execute(sql_update, {"new_mail_time": row[3]+timedelta(days=1), "email": row[1]})
        conn.commit()

    cursor.close()
    conn.close()

if __name__=='__main__':
    run()

