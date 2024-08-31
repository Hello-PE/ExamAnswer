import requests
import json
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from Cryptodome.Cipher import DES3
from Cryptodome.Util.Padding import unpad
import base64
import pyperclip
import yaml
import time


# 读取配置
def read_config(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    file.close()
    return config


# 写入配置
def write_config(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        yaml.safe_dump(
            data,
            file,
            allow_unicode=True,
            encoding="utf-8",
            sort_keys=False
        )
    file.close()
    return None


# 解密数据
def decrypt_data(text, key):
    cipher = DES3.new(key=key, mode=DES3.MODE_ECB)
    return unpad(
        cipher.decrypt(base64.b64decode(text)), DES3.block_size
    ).decode("utf-8")


# 密钥检查
def check_key(test_txt, key):
    try:
        decrypt_data(test_txt, key)
        return True
    except ValueError:
        return False


# 获取密钥
def get_key():
    # 构建请求头
    headers = {
        "authority": "beta_api.jbea.cn",
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=1.0",
        "cache-control": "no-cache",
        "content-length": "0",
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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/122.0.0.0 Safari/537.36"
    }

    # 请求链接
    url = "https://beta_api.jbea.cn/api/Students/GetTokenKey"

    # 禁用SSL证书验证
    disable_warnings(InsecureRequestWarning)

    # 发送请求
    response = requests.post(url, headers=headers, verify=False)

    # 解析数据
    parsed_data = json.loads(response.text)

    # 处理返回参数
    key = parsed_data["Key"]
    offset = parsed_data["Offset"]
    time_value = int(parsed_data["Time"])

    # 根据参数提取密钥
    decrypted_code = "".join(key[int(offset[i] - time_value)] for i in range(len(offset)))
    start_index = offset[time_value]
    end_index = start_index + len(decrypted_code)
    final_result = key[start_index:end_index]
    return final_result


def is_json(text):
    try:
        json.loads(text)
        return True
    except ValueError:
        return False


def decrypt(debug_mode, config_file_path, encrypt_data):
    # 读取配置
    config_data = read_config(config_file_path)

    # 设定解密错误次数
    decrypt_error_limit = 3

    # 小程序/网页
    decrypt_key = config_data["Decrypt_Data_Key"]

    # 循环检查密钥
    while not check_key(encrypt_data, config_data["Decrypt_Data_Key"]):
        if check_key(encrypt_data, config_data["Decrypt_M_Key"]):
            print("看起来这是一个小程序上的加密, 已为您切换解密钥")
            decrypt_key = config_data["Decrypt_M_Key"]
            break

        if decrypt_error_limit == 0:
            print("解密错误次数过多, 请检查配置文件或联系作者")
            exit(1)
        print("密钥过期/出错, 开始为您重新获取...")

        config_data["Decrypt_Data_Key"] = get_key()
        print(f"已获取到最新密钥: {config_data["Decrypt_Data_Key"]}\n已将其写入到配置中\n")

        write_config(config_file_path, config_data)
        decrypt_error_limit -= 1

    # 解密和计时
    start_time = time.time()
    data = decrypt_data(encrypt_data, decrypt_key)
    end_time = time.time()

    # 输出解密完成
    print("解密完成, 开始处理数据...")

    # 根据调试模式返回数据
    if debug_mode:
        if is_json(data):
            # 格式化Json并复制到剪切板
            json_data = json.dumps(
                json.loads(data),
                indent=4,
                ensure_ascii=False
            )
            pyperclip.copy(json_data)
            print(f"解密后的原文: \r\n{json_data}\r\n处理后的Json已复制到剪切板")
            print(f"解密耗时: {end_time - start_time:.6f} 秒")
            return json.loads(data)
        else:
            print(f"解密后的原文: \r\n{data}")
            print(f"解密耗时: {end_time - start_time:.6f} 秒")
            return data
    else:
        if is_json(data):
            return json.loads(data)
        else:
            return decrypt_data


if __name__ == "__main__":
    decrypt(debug_mode=True,
            config_file_path="../config/main.yml",
            encrypt_data=input("请输入密文:").encode("utf-8"))
