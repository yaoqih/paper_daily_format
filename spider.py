import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from utils import clean_filename
import os
import warnings
import re
warnings.filterwarnings("ignore")
def chatgpt(system='你是一个经验丰富的科研工作者',content='',s=requests.Session()):
    headers={
        "accept": "*/*",
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
    "model": "gpt-3.5-turbo-16k-0613",
    "temperature": 0,
    "presence_penalty": 0.5,
    }
    res=s.post('https://hubchat1.top/api/openai/v1/chat/completions',headers=headers,data=json.dumps(body),timeout=60)
    if len(res.content.decode('utf-8'))<200:
        print('gpt_error')
    return json.loads(res.content.decode('utf-8'))['choices'][0]['message']['content'].replace('\n','<br>').replace(' ','&nbsp;')

def kimi(content,s=requests.Session(),authorization=None,url="https://kimi.moonshot.cn/api/chat"):
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
        'name':'未命名会话',
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
    return response_text

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