import os
import time
import json
import yaml

if  os.path.exists('result.json'):
    filemt = time.localtime(os.stat('result.json').st_mtime)
    resume=time.strftime("%Y-%m-%d", filemt)==time.strftime("%Y-%m-%d", time.localtime())
else:
    resume=False

task_content=json.loads(open('result.json','r',encoding='utf-8').read())
with open('paper.yaml', 'r', encoding='utf-8') as f:
    topics = yaml.load(f.read(), Loader=yaml.FullLoader)
mechanism_check=open('mechanism_check.txt','r',encoding='utf-8').read().split('--------------------------------------------------------------------------------\n')
mecanism_dict={i.split(':')[0]:i.split(':')[1] for i in open('mechanism_list.txt','r',encoding='utf-8').read().split('\n') if i}

paper_mechnism={}
for paper in mechanism_check:
    if paper:
        mechanism_str=''
        for mechanism in paper.split('\n')[1:]:
            if mechanism:
                mechanism_str+=mechanism.split(':')[1]+', '
                if mechanism.split(':')[0] not in mecanism_dict:
                    mecanism_dict[mechanism.split(':')[0]]=mechanism.split(':')[1]
        paper_mechnism[paper.split('\n')[0]]=mechanism_str[:-2]
    
with open('result.md','w',encoding='utf-8') as f:
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
        f.write('# Topic: '+topic+'｜\n\n')
        for Paper in topics[topic]:
            if not task_content[Paper]['title_datetime_url']:
                title,publish_datetime,Project_Page='','',''
            else:
                title,publish_datetime,Project_Page=task_content[Paper]['title_datetime_url']
            # mechanism=task_content[Paper]['mechanism'] if task_content[Paper]['mechanism'] else ''
            mechanism=paper_mechnism[title]
            f.write('## '+title+'\n\n')
            f.write(f'{publish_datetime}｜{mechanism}'+'\n\n')
            if Project_Page:
                f.write(f'<u>{Project_Page}</u>'+'\n\n')
            else:
                f.write(f'<u>{Paper}</u>'+'\n\n')
            paper_summary=task_content[Paper]['summary'] if task_content[Paper]['summary'] else ''
            f.write(paper_summary+'\n\n')
mecanism_list=[f'{i}:{mecanism_dict[i]}' for i in mecanism_dict]
open('mechanism_list.txt','w',encoding='utf-8').write('\n'.join(mecanism_list))