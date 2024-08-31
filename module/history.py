from decrypt import decrypt
import requests
import json
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import pyperclip
import time


def history(debug_mod, ext):
    # 临时写死
    token = "<填你的JWT令牌>"

    # 请求链接
    url = "https://beta_api.jbea.cn/api/ExamInfo/GetExamPageAnalysis"

    # 请求数据
    data = {
        "ext": ext,
        "token": token
    }
    data = json.dumps(data, separators=(',', ':'))

    # 构建请求头
    headers = {
        "authority": "beta_api.jbea.cn",
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=1.0",
        "Authorization": "Bearer " + token,
        "cache-control": "no-cache",
        "Content-Length": str(len(data)),
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://cdn.jbea.cn",
        "pragma": "no-cache",
        "referer": "https://cdn.jbea.cn/",
        "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    # 禁用SSL证书验证
    disable_warnings(InsecureRequestWarning)

    start_time = time.time()

    # 发送请求
    response = requests.post(url=url, headers=headers, data=data, verify=False)

    # 检查状态码
    if response.status_code != 200:
        print(f"请求失败, 状态码: {response.status_code}")
        return False

    # 解析数据
    parsed_data = decrypt(
        debug_mod,
        "../config/main.yml",
        response.text.encode("utf-8")
    )

    # 格式化Json并复制到剪切板
    json_data = json.dumps(
        parsed_data,
        indent=4,
        ensure_ascii=False
    )

    end_time = time.time()

    # 输出并复制到剪切板
    if debug_mod:
        print(f"这是您需要的历史试卷:\r\n{json_data}\r\n")
        print(f"查询耗时: {end_time - start_time:.6f} 秒")
    pyperclip.copy(json_data)
    print("处理后的Json已复制到剪切板")
    return parsed_data


if __name__ == "__main__":
    history(debug_mod=False, ext=input("请输入题目ID: "))
