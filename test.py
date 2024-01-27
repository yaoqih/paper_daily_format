import requests
import re

url = "https://kimi.moonshot.cn/api/chat"
headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "authorization": "Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTcwNjI3OTg3NCwiaWF0IjoxNzA2Mjc4OTc0LCJqdGkiOiJjbXBzMGZtY3A3ZmR2cjExbGx1ZyIsInR5cCI6ImFjY2VzcyIsInN1YiI6ImNtbDN2bmN1ZHU2NXZtNTFkb2NnIiwic3BhY2VfaWQiOiJjbWwzdm5jdWR1NjV2bTUxZG9jMCJ9.JZGSS-P7BMEI3WuPDnzP8_8Rd4Wwmxbx4dxSA0eAo0-d6SGYzw0GMjeq7LmiWAzVk3JIkkCjYvjZv_WcR5nqZg",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "pragma": "no-cache",
    "r-timezone": "Asia/Shanghai",
    "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Microsoft Edge\";v=\"120\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
}

payload = {
    "name": "未命名会话",
    "is_example": False
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
