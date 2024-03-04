import json
mechanism_check=open('mechanism_check.txt','r',encoding='utf-8').read().split('--------------------------------------------------------------------------------\n')

mecanism_dict={i.split(':')[0]:i.split(':')[1] for i in open('mechanism_list.txt','r',encoding='utf-8').read().split('\n') if i}
paper_mechnism={}
for paper in mechanism_check:
    if paper:
        mechanism_str=''
        for mechanism in paper.split('\n')[1:]:
            if mechanism:
                mechanism_str+=mechanism.split(':')[1]+','
                if mechanism.split(':')[0] not in mecanism_dict:
                    mecanism_dict[mechanism.split(':')[0]]=mechanism.split(':')[1]
        paper_mechnism[paper.split('\n')[0]]=mechanism_str[:-1]
res=json.load(open('result.json','r',encoding='utf-8'))
res=sorted(res.items(),key=lambda x:x[1]['title_datetime_url'][1])  
for i in res:
    print(i[1]['title_datetime_url'][0].split(":")[0],i[1]['title_datetime_url'][1].replace('.','/'),i[1]['title_datetime_url'][2],paper_mechnism[i[1]['title_datetime_url'][0]])