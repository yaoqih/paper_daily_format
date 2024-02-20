import re
def clean_filename(title):
    # 定义非法字符的正则表达式
    illegal_chars = r'[\/:*?"<>|]'
    # 替换非法字符为空格
    clean_title = re.sub(illegal_chars, ' ', title)
    # 移除连续的空格并去除首尾空格
    clean_title = ' '.join(clean_title.split())
    clean_title = re.sub(r'\$.*?\$', ' ', clean_title)

    return clean_title