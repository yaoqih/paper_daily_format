# import json
# mechanism_check=open('mechanism_check.txt','r',encoding='utf-8').read().split('--------------------------------------------------------------------------------\n')

# mecanism_dict={i.split(':')[0]:i.split(':')[1] for i in open('mechanism_list.txt','r',encoding='utf-8').read().split('\n') if i}
# paper_mechnism={}
# for paper in mechanism_check:
#     if paper:
#         mechanism_str=''
#         for mechanism in paper.split('\n')[1:]:
#             if mechanism:
#                 mechanism_str+=mechanism.split(':')[1]+','
#                 if mechanism.split(':')[0] not in mecanism_dict:
#                     mecanism_dict[mechanism.split(':')[0]]=mechanism.split(':')[1]
#         paper_mechnism[paper.split('\n')[0]]=mechanism_str[:-1]
# res=json.load(open('result.json','r',encoding='utf-8'))
# res=sorted(res.items(),key=lambda x:x[1]['title_datetime_url'][1])  
# for i in res:
#     print(i[1]['title_datetime_url'][0].split(":")[0],i[1]['title_datetime_url'][1].replace('.','/'),i[1]['title_datetime_url'][2],paper_mechnism[i[1]['title_datetime_url'][0]])
from openai import OpenAI
import os
import httpx
clash_port = 8466

os.environ['http_proxy'] = 'None'
os.environ['https_proxy'] = 'None'
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="sk-T4p4PNbNOBuVBxXpwt2Hr67YtPbMVH0xCFDDZ5ieDSbtfr7i",
    base_url="https://api.chatanywhere.tech/v1",
    http_client=httpx.Client(
        proxies="http://127.0.0.1:8466",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    )
)



# 非流式响应
def gpt_35_api(messages: list):
    """为提供的对话消息创建新的回答

    Args:
        messages (list): 完整的对话消息
    """
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    print(completion.choices[0].message.content)

def gpt_35_api_stream(messages: list):
    """为提供的对话消息创建新的回答 (流式传输)

    Args:
        messages (list): 完整的对话消息
    """
    stream = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

if __name__ == '__main__':
    messages = [{'role': 'user','content': '鲁迅和周树人的关系'},]
    # 非流式调用
    gpt_35_api(messages)
    # 流式调用
    # gpt_35_api_stream(messages)