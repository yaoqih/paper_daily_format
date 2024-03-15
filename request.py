import requests
import json
import yaml
import os
import time
import requests
from requests.adapters import HTTPAdapter
import json
import re
from spider import chatgpt,kimi,get_title_datetime_url,download_paper,refresh_auth,chatgpt_openai,translate_baidu
from utils import clean_filename
import pdfplumber
from tqdm import tqdm
from config import clash_port,clash_address
# setting
authorization="Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTcxMDQ3NjQ3NCwiaWF0IjoxNzEwNDc1NTc0LCJqdGkiOiJjbnBzaWRtY3A3ZjFodXFuMzQ2ZyIsInR5cCI6ImFjY2VzcyIsInN1YiI6ImNtbDN2bmN1ZHU2NXZtNTFkb2NnIiwic3BhY2VfaWQiOiJjbWwzdm5jdWR1NjV2bTUxZG9jMCIsImFic3RyYWN0X3VzZXJfaWQiOiJjbWwzdm5jdWR1NjV2bTUxZG9jZyJ9.7ylsrGD82BJ-KmPUyf7Mr7SVaFCCPTBQK8iX2nxIU-guWDZnwnDCrdM1miGFUi3eegQDF2Yd4LGkoBMP09kRjw"
task={'summary':1,'mechanism':1,'title_datetime_url':1,'download_paper':1,'translate_title':1}
assert not (not task['title_datetime_url'] and task['download_paper']),'必须获取论文title才能下载论文'
assert not (not task['download_paper'] and task['mechanism']),'必须下载论文后才能获取机构信息'
paper_save_path='./paper_download/'
if not os.path.exists(paper_save_path):
    os.mkdir(paper_save_path)
    
# proxy
proxies = {
    'http': f'http://{clash_address}:{clash_port}',
    'https': f'https://{clash_address}:{clash_port}'
}
s = requests.Session()
s.proxies = proxies
s.verify = False
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))
# resume
if  os.path.exists('result.json'):
    filemt = time.localtime(os.stat('result.json').st_mtime)
    resume=time.strftime("%Y-%m-%d", filemt)==time.strftime("%Y-%m-%d", time.localtime())
else:
    resume=False
task_content={}

def get_mechanism(file_name):
    try:
        with pdfplumber.open(file_name) as pdf:
            page01 = pdf.pages[0] #指定页码
            text = page01.extract_text()#提取文本
    except:
        print('Error:PDF解析失败，请检查文件是否损坏或者网络是否正常！'+file_name)
        os.remove(file_name)
        return ''
    return get_mechanism_chatgpt(text)

def get_mechanism_chatgpt(text):
    content=f"I will give you a page of paper next. Please find out the names of all the authors’ schools or research institutions, and reply to me in the form of name:name abbreviation, separated by '||' For example:“Massachusetts Institute of Technology:MIT||Peking University:PKU||Tencent AI Lab:Tencent AI Lab||Deemos Technology:Deemos”。If there are multiple identical schools or research institutions. Only answer the research school, institution and its abbreviation according to the prescribed format. Do not answer other information.paper：```{text}```"
    return chatgpt_openai(content=content,s=s)

def get_summary(arxiv_pdf_url,title=None):
    return kimi(content=f"请用300字总结，分三段: <url id=\"\" type=\"url\" status=\"\" title=\"\" wc=\"\">{arxiv_pdf_url}</url>",s=s,authorization=authorization,title=title)
if not resume:
    for file in os.listdir(paper_save_path):
        if file.endswith('.pdf'):
            os.remove(paper_save_path+file)
with open('paper.yaml', 'r', encoding='utf-8') as f:
    topics = yaml.load(f.read(), Loader=yaml.FullLoader)
if resume:
    task_content=json.loads(open('result.json','r',encoding='utf-8').read())
for topic in topics:
    for Paper in topics[topic]:
        if Paper not in task_content:
            task_content[Paper]={"title_datetime_url":None,"mechanism":None,"summary":None,"translate_title":None}
pbar = tqdm(task_content.keys())
for Paper in pbar:
    try:
        if task['title_datetime_url'] and not task_content[Paper]['title_datetime_url']:
            task_content[Paper]['title_datetime_url']=get_title_datetime_url(Paper,s=s)
        if task['download_paper']:
            download_paper(Paper.replace('abs','pdf'),task_content[Paper]['title_datetime_url'][0],paper_save_path=paper_save_path,s=s)
        if task['mechanism'] and not task_content[Paper]['mechanism']:
            task_content[Paper]['mechanism']=get_mechanism(paper_save_path+clean_filename(task_content[Paper]['title_datetime_url'][0])+'.pdf')
        if task['summary'] and not task_content[Paper]['summary']:
            task_content[Paper]['summary']=get_summary(Paper.replace('abs','pdf'),task_content[Paper]['title_datetime_url'][0][:20])
            task_content[Paper]['summary']=re.sub(r'\*\*.*?\*\*\n', "",task_content[Paper]['summary'])
            task_content[Paper]['summary']=re.sub(r'\n\n\n', "\n\n",task_content[Paper]['summary'])
            task_content[Paper]['summary']=re.sub(r'\n\n\n', "\n\n",task_content[Paper]['summary'])
        if task['translate_title'] and not task_content[Paper]['translate_title']:
            task_content[Paper]['translate_title']=translate_baidu(task_content[Paper]['title_datetime_url'][0])
    except Exception as e:
        print(e) 
        print(f'Error in {Paper}')
        json.dump(task_content,open('result.json','w',encoding='utf-8'),ensure_ascii=False)
    json.dump(task_content,open('result.json','w',encoding='utf-8'),ensure_ascii=False)
with open('result.md','w',encoding='utf-8') as f:
    if task['translate_title']:
        title_summary=''
        for topic in topics:
            for Paper in topics[topic]:
                if not task_content[Paper]['title_datetime_url']:
                    title,publish_datetime,Project_Page='','',''
                else:
                    title,publish_datetime,Project_Page=task_content[Paper]['title_datetime_url']
                title_summary+=title+'\n'
                title_summary+=task_content[Paper]['translate_title']+'\n'
        f.write(title_summary)
    for topic in topics:
        f.write('# Topic: '+topic+'\n\n')
        for Paper in topics[topic]:
            if not task_content[Paper]['title_datetime_url']:
                title,publish_datetime,Project_Page='','',''
            else:
                title,publish_datetime,Project_Page=task_content[Paper]['title_datetime_url']
            # mechanism=task_content[Paper]['mechanism'] if task_content[Paper]['mechanism'] else ''
            mechanism=''
            f.write('## '+title+'\n\n')
            f.write(f'{publish_datetime}｜{mechanism}'+'\n\n')
            if Project_Page:
                f.write(f'<u>{Project_Page}</u>'+'\n\n')
            else:
                f.write(f'<u>{Paper}</u>'+'\n\n')
            paper_summary=task_content[Paper]['summary'] if task_content[Paper]['summary'] else ''
            f.write(paper_summary+'\n\n')
mecanism_dict={i.split(':')[0]:i.split(':')[1] for i in open('mechanism_list.txt','r',encoding='utf-8').read().split('\n') if i}
with open('mechanism_check.txt','w',encoding='utf-8') as f:
    for paper in task_content:
        if task_content[paper]['mechanism']:
            f.write(task_content[paper]['title_datetime_url'][0]+'\n')
            for mecanism in task_content[paper]['mechanism'].replace('&nbsp;',' ').split('||'):
                mecanism_split=mecanism.split(':')
                mecanism_long=mecanism_split[0].strip()
                if len(mecanism_split)==1:
                    mecanism_short=''
                else:
                    mecanism_short=mecanism_dict.get(mecanism_long) if mecanism_dict.get(mecanism_long) else mecanism_split[1].strip()
                f.write(f'{mecanism_long}:{mecanism_short}\n')
            f.write('--------------------------------------------------------------------------------\n')