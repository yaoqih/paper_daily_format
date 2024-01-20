import requests
import json
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
import re
import os
authorization="Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJlY2hvbWluZC1hcGktYXBpIiwiZXhwIjoxNzA1NjgyNTg0LCJpYXQiOjE3MDU2ODE2ODQsImp0aSI6ImNtbGE2NTR1ZHU2Y24zN2RjaW0wIiwidHlwIjoiYWNjZXNzIiwic3BhY2VfaWQiOiJjbWwzdm5jdWR1NjV2bTUxZG9jMCIsInN1YiI6ImNtbDN2bmN1ZHU2NXZtNTFkb2NnIn0.cWlsHaub09vRmMbwYEgAklssLsvrkFr3pWU6uXKJZaszeLi7PI2-__U8VrzU17fJfAlUL6h2FuPJ1lwVNHJb0g"
url = "https://kimi.moonshot.cn/api/chat/cmla6503r07bppj064k0/completion/stream"
paper_save_path='./paper_download/'
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
    response = requests.post(url, headers=headers, json=data, cookies={"credentials": "include"})
    if response.status_code != 200:
        print(response.text)
        exit()
    response_json = [json.loads("{"+i+"}") for i in response.content.decode("utf-8").replace("data",'"data"').split('\n\n')[6:-1]]
    response_text = ''.join([i["data"]["text"] for i in response_json if 'data'in i and 'text' in i["data"]])
    return response_text
def get_title_datetime(arxiv_abs_url):
    response=requests.get(arxiv_abs_url)
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
    response=requests.get(url+'.pdf')
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
for file in os.lisdir(paper_save_path):
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
                f.write(f'[{Project_Page}]({Project_Page})')
            paper_summary=get_summary(Paper.replace('abs','pdf'))
            f.write(paper_summary)