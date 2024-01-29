import requests
import json
import yaml
import os
import time
import requests
from requests.adapters import HTTPAdapter
import json
from spider import chatgpt,kimi,get_title_datetime_url,download_paper,refresh_auth
from utils import clean_filename
import pdfplumber
from tqdm import tqdm

paper_save_path='./paper_download/'
if not os.path.exists(paper_save_path):
    os.mkdir(paper_save_path)
authorization="Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTcwNjMzNjQ3NSwiaWF0IjoxNzA2MzM1NTc1LCJqdGkiOiJjbXE5cWx1Y3A3ZmR2cjE3N2FxZyIsInR5cCI6ImFjY2VzcyIsInN1YiI6ImNtbDN2bmN1ZHU2NXZtNTFkb2NnIiwic3BhY2VfaWQiOiJjbWwzdm5jdWR1NjV2bTUxZG9jMCJ9.CkjL9xgAndT7HJLGJDFoMR-SykTe8XO-37-sFQLbWjm0u5KU3GOXwv4MSnVX-U2fooSVP8BwpfpLuBC80z06QQ"
proxies = {
    'http': 'http://127.0.0.1:8466',
    'https': 'https://127.0.0.1:8466'
}
s = requests.Session()
s.proxies = proxies
s.verify = False
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))
task={'summary':1,'mechanism':1,'title_datetime_url':1,'download_paper':1}
assert not (not task['title_datetime_url'] and task['download_paper']),'必须获取论文title才能下载论文'
assert not (not task['download_paper'] and task['mechanism']),'必须下载论文后才能获取机构信息'

filemt = time.localtime(os.stat('result.json').st_mtime)
resume=time.strftime("%Y-%m-%d", filemt)==time.strftime("%Y-%m-%d", time.localtime())
task_content={}

def get_mechanism(file_name):
    with pdfplumber.open(file_name) as pdf:
        page01 = pdf.pages[0] #指定页码
        text = page01.extract_text()#提取文本
    return get_mechanism_chatgpt(text)

def get_mechanism_chatgpt(text):
    content=f"我接下来给你一页论文，请找出其中全部的作者的学校或者研究机构，并以缩写的形式回复我,中间用, 隔开。例如：MIT, ZJU, PKU。请仅回答作者的学校或者研究机构的缩写，不要回答其他的信息。论文：```{text}```"
    return chatgpt(content=content,s=s)

def get_summary(arxiv_pdf_url):
    return kimi(content=f"请用300字总结，分三段 <url id=\"\" type=\"url\" status=\"\" title=\"\" wc=\"\">{arxiv_pdf_url}</url>",s=s,authorization=authorization)
if not resume:
    for file in os.listdir(paper_save_path):
        os.remove(paper_save_path+file)
with open('paper.yaml', 'r', encoding='utf-8') as f:
    topics = yaml.load(f.read(), Loader=yaml.FullLoader)
    
if resume:
    task_content=json.loads(open('result.json','r',encoding='utf-8').read())
for topic in topics:
    for Paper in topics[topic]:
        if Paper not in task_content:
            task_content[Paper]={}
pbar = tqdm(task_content.keys())
for Paper in pbar:
    try:
        if task['title_datetime_url'] and 'title_datetime_url' not in task_content[Paper]:
            task_content[Paper]['title_datetime_url']=get_title_datetime_url(Paper,s=s)
        if task['download_paper'] and 'download_paper' not in task_content[Paper]:
            download_paper(Paper.replace('abs','pdf'),task_content[Paper]['title_datetime_url'][0],paper_save_path=paper_save_path,s=s)
        if task['mechanism'] and 'mechanism' not in task_content[Paper]:
            task_content[Paper]['mechanism']=get_mechanism(paper_save_path+clean_filename(task_content[Paper]['title_datetime_url'][0])+'.pdf')
        if task['summary'] and 'summary' not in task_content[Paper]:
            task_content[Paper]['summary']=get_summary(Paper.replace('abs','pdf'))
    except Exception as e:
        print(e) 
        json.dump(task_content,open('result.json','w',encoding='utf-8'),ensure_ascii=False)
    json.dump(task_content,open('result.json','w',encoding='utf-8'),ensure_ascii=False)
with open('result.md','w',encoding='utf-8') as f:
    for topic in topics:
        f.write('# Topic: '+topic+'｜\n\n')
        for Paper in topics[topic]:
            title,publish_datetime,Project_Page=task_content[Paper]['title_datetime_url']
            mechanism=task_content[Paper]['mechanism']
            f.write('## '+title+'\n\n')
            f.write(f'{publish_datetime}｜{mechanism}'+'\n\n')
            if Project_Page:
                f.write(f'<u>{Project_Page}</u>'+'\n\n')
            paper_summary=task_content[Paper]['summary']
            f.write("&ensp;&ensp;&ensp;&ensp;"+paper_summary.replace('\n\n','\n\n&&ensp;&ensp;&ensp;&ensp;')+'\n\n')
    