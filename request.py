import requests
import json
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
import re
import os
import time
import requests
from requests.adapters import HTTPAdapter

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


authorization="Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTcwNjE3Mzc5NywiaWF0IjoxNzA2MTcyODk3LCJqdGkiOiJjbXAyM29hbG5sOTllNmhnamhrMCIsInR5cCI6ImFjY2VzcyIsInN1YiI6ImNtbDN2bmN1ZHU2NXZtNTFkb2NnIiwic3BhY2VfaWQiOiJjbWwzdm5jdWR1NjV2bTUxZG9jMCJ9.ROz6TVpvT4Vz4xZIYdUKiYK63jQQvyfnd3i6c1yscfQh9cx1iuSjLyJBB-eG8XfUGueNJ7Y6UjLMrKbViDUCTg"

url = "https://kimi.moonshot.cn/api/chat/cmp24hkodhskd0tu4ebg/completion/stream"
paper_save_path='./paper_download/'
proxies = {
    'http': 'http://127.0.0.1:8466',
    'https': 'http://127.0.0.1:8466'
}
def get_summary(arxiv_pdf_url):
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

    data = {
        "messages": [
            {
                "role": "user",
                "content": "请用300字总结，分三段 <url id=\"\" type=\"url\" status=\"\" title=\"\" wc=\"\">"+arxiv_pdf_url+"</url>"
            }
        ],
        "refs": [],
        "use_search": False
    }
    try:
        response = requests.post(url, headers=headers, json=data, cookies={"credentials": "include"}, verify=False,proxies=proxies,timeout=120)
    except requests.exceptions.RequestException as e:
        # print(e)
        # print(response.text)
        exit()
    response_json = [json.loads("{"+i+"}") for i in response.content.decode("utf-8").replace("data",'"data"').split('\n\n')[6:-1]]
    response_text = ''.join([i["data"]["text"] for i in response_json if 'data'in i and 'text' in i["data"]])
    return response_text
def get_title_datetime(arxiv_abs_url):
    try:
        response = s.get(arxiv_abs_url, verify=False,proxies=proxies,timeout=5)
    except requests.exceptions.RequestException as e:
        print(e)
    soup=BeautifulSoup(response.content,'html.parser')
    title=soup.find('h1',class_='title mathjax').next.next.next.text
    datetime_submit=soup.find('div',class_='dateline').text.split('on')[1][1:-1]
    # 将日期字符串解析为日期对象
    date_object = datetime.strptime(datetime_submit, '%d %b %Y')
    # 将日期对象格式化为新的日期字符串
    formatted_date = date_object.strftime('%Y.%m.%d')
    Project_Page=soup.find('a',class_='link-external').get('href') if soup.find('a',class_='link-external') else ''
    return title,formatted_date,Project_Page
if not os.path.exists(paper_save_path):
    os.mkdir(paper_save_path)
def download_paper(url,title):
    f=open(paper_save_path+clean_filename(title)+'.pdf','wb')
    try:
        response = s.get(url+'.pdf', verify=False,proxies=proxies,timeout=5)
    except requests.exceptions.RequestException as e:
        print(e)
    f.write(response.content)
    f.close()
def clean_filename(title):
    # 定义非法字符的正则表达式
    illegal_chars = r'[\/:*?"<>|]'
    # 替换非法字符为空格
    clean_title = re.sub(illegal_chars, ' ', title)
    # 移除连续的空格并去除首尾空格
    clean_title = ' '.join(clean_title.split())
    return clean_title
for file in os.listdir(paper_save_path):
    os.remove(paper_save_path+file)
with open('paper.yaml', 'r', encoding='utf-8') as f:
    topics = yaml.load(f.read(), Loader=yaml.FullLoader)
with open('result.md','w',encoding='utf-8') as f:
    for topic in topics:
        f.write('# Topic: '+topic+'｜\n\n')
        for Paper in topics[topic]:
            title,publish_datetime,Project_Page=get_title_datetime(Paper)
            f.write('## '+title+'\n\n')
            f.write(f'{publish_datetime}｜'+'\n\n')
            download_paper(Paper.replace('abs','pdf'),title)
            if Project_Page:
                f.write(f'<u>{Project_Page}</u>'+'\n\n')
            # paper_summary=get_summary(Paper.replace('abs','pdf'))
            paper_summary=''
            f.write("&ensp;&ensp;&ensp;&ensp;"+paper_summary.replace('\n\n','\n\n&&ensp;&ensp;&ensp;&ensp;')+'\n\n')
    