import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from utils import clean_filename
import os
import warnings
import re
from config import clash_port,opai_key
import httpx
warnings.filterwarnings("ignore")
import random
from hashlib import md5
from config import baidu_appid,baidu_appkey
from openai import OpenAI

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=opai_key,
    base_url="https://api.chatanywhere.cn",
    http_client=httpx.Client(
        proxies=f"http://127.0.0.1:{clash_port}",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    )
)


def chatgpt(system='你是一个经验丰富的科研工作者',content='',s=requests.Session()):
    headers={
        "accept": "*/*",
        "Authorization":"Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzc1NjI2MzcxIiwiaWF0IjoxNzA5NTQzNDk0LCJleHAiOjE3MTAxNDgyOTR9.HYHNTre6cLoi4USimnbLhRuFlqAe6V3DpdP5zj5fN-8kqVN3WVEfr8tzgrnVS0WkQdXP7fY_cAb03DsSErXhQQ",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Microsoft Edge\";v=\"116\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
    }
    body={
    "messages": [
        {
        "role": "system",
        "content": system
        },
        {
        "role": "user",
        "content": content
        }
    ],
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    "presence_penalty": 0.5,
    }
    proxies = {"http": None, "https": None}
    res=s.post('https://hubtalk1.top/api/openai/v1/chat/completions',headers=headers,data=json.dumps(body),timeout=60,proxies=proxies)
    # res=s.post('https://hubchat1.top/api/openai/v1/chat/completions',headers=headers,data=json.dumps(body),timeout=60)
    if len(res.content.decode('utf-8'))<200:
        print('gpt_error')
    return json.loads(res.content.decode('utf-8'))['choices'][0]['message']['content'].replace('\n','<br>').replace(' ','&nbsp;')

def chatgpt_openai(system='You are an experienced scientific researcher',content='',s=requests.Session()):
    messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": content},
        ]
    try:
        completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    except Exception as e:
        print(e)
    return completion.choices[0].message.content.replace('\n','<br>').replace(' ','&nbsp;')

def kimi(content,s=requests.Session(),authorization=None,url="https://kimi.moonshot.cn/api/chat",title=None):
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "authorization": authorization,
        "cache-control": "no-cache",
        "content-type": "application/json",
        "pragma": "no-cache",
        "r-timezone": "Asia/Shanghai",
        "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Microsoft Edge\";v=\"120\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }

    chat_data = {
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "refs": [],
        "use_search": False
    }
    increase_data = {
        'is_example':False,
        'name':'未命名会话' if not title else title,
    }
    response = s.post(url, headers=headers, json=increase_data, cookies={"credentials": "include"},timeout=120)
    if '授权已过期' in response.text:
        print('kimi授权已过期请重新设置authorization')
        exit()
    id=response.json()['id']
    # authorization=refresh_auth(authorization,s=s)
    response = s.post(f"https://kimi.moonshot.cn/api/chat/{id}/completion/stream", headers=headers, json=chat_data, cookies={"credentials": "include"},timeout=120)
    response_json = [json.loads("{"+i+"}") for i in response.content.decode("utf-8").replace("data",'"data"').split('\n\n')[6:-1] if 'cmpl' in i]
    response_text = ''.join([i["data"]["text"] for i in response_json if 'data'in i and 'text' in i["data"]])
    if "由于网络原因" in response_text or "由于网络问题" in response_text:
        print("Kimi network error,Please run again later! "+content)
        return ""
    return response_text.strip()

def refresh_auth(authorization,s=requests.Session()):
    url = "https://kimi.moonshot.cn/api/auth/token/refresh"

    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "authorization":authorization,
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Microsoft Edge\";v=\"120\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }

    response = s.get(url, headers=headers, cookies={'name': 'value'})
    if '授权已过期' in response.text:
        print('kimi授权已过期请重新设置authorization')
        exit()
    return response.json()['refresh_token']

def get_title_datetime_url(arxiv_abs_url,s=requests.Session(),proxies=None):
    try:
        response = s.get(arxiv_abs_url,proxies=proxies,timeout=5)
    except requests.exceptions.RequestException as e:
        print(e)
    soup=BeautifulSoup(response.content,'html.parser')
    title=soup.find('h1',class_='title mathjax').next.next.next.text
    submit_date=soup.find('div',class_='dateline').text
    date_pattern = r'(\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4})'

    # 使用正则表达式提取日期
    dates1 = re.findall(date_pattern, submit_date)
    # 将日期字符串解析为日期对象
    date_object = datetime.strptime(dates1[-1], '%d %b %Y')
    # 将日期对象格式化为新的日期字符串
    formatted_date = date_object.strftime('%Y.%m.%d')
    Project_Page=soup.find('a',class_='link-external').get('href') if soup.find('a',class_='link-external') else ''
    return title,formatted_date,Project_Page

def download_paper(url,title,paper_save_path='./paper_download/',s=requests.Session()):
    if not os.access(paper_save_path+clean_filename(title)+'.pdf', os.F_OK):
        f=open(paper_save_path+clean_filename(title)+'.pdf','wb')
        try:
            response = s.get(url+'.pdf',timeout=5)
            f.write(response.content)
            f.close()
        except requests.exceptions.RequestException as e:
            print(e)
            print('Error: download_paper_error,please check your network and proxy!')
            exit()
# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document


def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()
def translate_baidu(query,s=requests.Session()):
    # Set your own appid/appkey.
    appid = baidu_appid
    appkey = baidu_appkey

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'en'
    to_lang =  'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path
    # Generate salt and sign
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = s.post(url, params=payload, headers=headers)
    result = r.json()

    # Show response
    return result['trans_result'][0]['dst']
