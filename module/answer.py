import re
import json
import pyperclip
from sklearn.feature_extraction.text import CountVectorizer
from scipy.linalg import norm
import numpy as np
import time
import base64


# TF计算文本相似度
class TextSimilarity:
    # 初始化CountVectorized, 并设置为不去除停用词
    def __init__(self):
        self.cv = CountVectorizer(tokenizer=lambda s: s.split(), token_pattern=None)

    # 将文本转换成向量
    @staticmethod
    def add_space(s):
        return ' '.join(list(s))

    # 计算两个文本的相似度
    def tf_similarity(self, s1, s2):
        s1, s2 = self.add_space(s1), self.add_space(s2)
        vectors = self.cv.fit_transform([s1, s2]).toarray()
        return np.dot(vectors[0], vectors[1]) / (norm(vectors[0]) * norm(vectors[1]))


# 导入题目
def import_exam(path):
    # 打开JSON文件
    with open(path, "r", encoding="utf-8") as file:
        # 从文件中加载JSON数据
        data = json.load(file)

    # 现在，变量"data"包含了从JSON文件中读取的数据，然后返回
    return data


# 导入数据库
def import_database(path):
    # 打开JSON文件
    with open(path, "r", encoding="utf-8") as file:
        # 从文件中加载JSON数据
        data = json.load(file)

    # 现在，变量"data"包含了从JSON文件中读取的数据，然后返回
    return data


# 比对(核心)
def compare(debug_mode, exam, database):
    # 获取题目答案
    exam_option_values = set(
        re.sub(r'[\s\\]+', '', option["OptionValue"]) for option in exam["ChoseOption"]
    )
    # 遍历数据库
    for item in database:
        # 遍历数据库中的每个题目
        for database in item.get("data", []):
            # 检查数据库中的题干是否为空
            if database["Title"] is not None:
                # 题目与数据库中题目的答案是否一致
                if exam_option_values == set(
                        re.sub(r'[\s\\]+', '', option["OptionValue"]) for option in database["ChoseOption"]
                ):
                    # 题目与数据库中题目的代码段是否一致
                    if exam["Code"] is None:
                        exam["Code"] = ''
                    else:
                        exam["Code"] = re.sub(r'[^a-zA-Z]', '', exam["Code"])
                    if database["Code"] is None:
                        database["Code"] = ''
                    else:
                        database["Code"] = re.sub(r'[^a-zA-Z]', '', database["Code"])
                    if exam["Code"] == database["Code"]:
                        # 题目与数据库中题目的题干否一致
                        if exam["Title"] == database["Title"]:
                            # 验证其它参数是否一致
                            if exam["isMulti"] == database["isMulti"] and exam["Multi"] == database["Multi"]:
                                result = []
                                for ans in database["Answer"]:
                                    for option in database["ChoseOption"]:
                                        if option["OptionKey"].strip(',') == ans:
                                            option_value = option["OptionValue"]
                                            for option2 in exam["ChoseOption"]:
                                                if option2["OptionValue"] == option_value:
                                                    # 条件断点打法：exam["Title"] == "题目"
                                                    result.append(option2["OptionKey"].strip(','))
                                return ','.join(result)
                        # 不一致时, 计算相似度
                        elif TextSimilarity().tf_similarity(exam["Title"], database["Title"]) > 0.9900000000000000:
                            # 调试信息
                            if debug_mode and TextSimilarity().tf_similarity(exam["Title"], database["Title"]) < 1.0000000000000000:
                                print(
                                    "发现可疑题干, 正在进行验证...\r\n" +
                                    f"题干: {exam["Title"].replace('\\"', "").replace("\r", "").replace("\n", "")}\r\n" +
                                    f"数据库: {database["Title"].replace('\\"', "").replace("\r", "").replace("\n", "")}\r\n" +
                                    f"相似度: {TextSimilarity().tf_similarity(exam["Title"], database["Title"])}"
                                )
                            # 验证其它参数是否一致
                            if exam["isMulti"] == database["isMulti"] and exam["Multi"] == database["Multi"]:
                                if debug_mode and TextSimilarity().tf_similarity(exam["Title"], database["Title"]) < 1.0000000000000000:
                                    print("验证通过√")
                                result = []
                                for ans in database["Answer"]:
                                    for option in database["ChoseOption"]:
                                        if ans == option["OptionKey"].strip(','):
                                            option_value = option["OptionValue"]
                                            for option2 in exam["ChoseOption"]:
                                                if option2["OptionValue"] == option_value:
                                                    result.append(option2["OptionKey"].strip(','))
                                return ','.join(result)
    return None


# 小程序专用对比
def compare_m(debug_mode, exam):
    if debug_mode:
        print(
            f"QSID: {exam["QSID"]}\r\n" +
            f"题目: {exam["title"].replace('\\"', "").replace("\r", "").replace("\n", "")}\r\n" +
            f"答案: {exam["answer"]}\r\n\r\n"
        )
    return exam["answer"]


# 手动答题
def manual_answer(exam):
    print(
        f"未找到题干为《{exam["Title"].replace('\\"', "").replace("\r", "").replace("\n", "")}》的答案, 请手动回答:\r\n" +
        f"QSID: {exam["QSID"]}\r\n" +
        f"题目: {exam["Title"].replace('\\"', "").replace("\r", "").replace("\n", "")}\r\n" +
        f"选项: {str(exam["ChoseOption"][0]["OptionKey"]).strip(",")}." +
        f"{exam["ChoseOption"][0]["OptionValue"]} | " +
        f"{str(exam["ChoseOption"][1]["OptionKey"]).strip(",")}." +
        f"{exam["ChoseOption"][1]["OptionValue"]} | " +
        f"{str(exam["ChoseOption"][2]["OptionKey"]).strip(",")}." +
        f"{exam["ChoseOption"][2]["OptionValue"]} | " +
        f"{str(exam["ChoseOption"][3]["OptionKey"]).strip(",")}." +
        f"{exam["ChoseOption"][3]["OptionValue"]}\r\n" +
        f"图片: {exam["Pic"]}\r\n" +
        f"代码: {exam["Code"]}\r\n" +
        f"是否多选: {exam["isMulti"]}\r\n" +
        f"选几个: {exam["Multi"]}"
    )
    return input("请输入您选择的答案: ").upper()


def answer(debug_mode, answer_mode, skip, exam_data, database_path, ws):
    # 初始化 #
    # 题目信息
    # exam_title = None
    # exam_option_key = []
    # exam_option_value = []
    # exam_code = None
    # exam_is_multi = None
    # exam_multi = None

    # 数据库信息
    database_data = import_database(database_path)

    # 答案和结果
    answer_data = []
    # answer_temp = ""
    result_data = ""
    # result_temp = []

    # 做题所在客户端
    device = "WEB"

    # 其它
    num = 0
    # schedule = 0

    # 记录程序开始时间
    start_time = time.time()

    # 判断是小程序还是网页
    if len(exam_data) < 6:
        device = "APP"

    # 防止弱智操作
    if device == "APP" and answer_mode == 3:
        print("小程序答题暂不支持综合模式, 已自动切换到静默模式!")
        answer_mode = 1

    # 循环取题目的所有信息并进行比对
    for item in exam_data["data"]:
        # 比对
        if device == "WEB":
            answer_temp = compare(debug_mode, item, database_data)
        elif device == "APP":
            answer_temp = compare_m(debug_mode, item)
        else:
            print("程序出错了-a1!")
            exit(0)

        # 如果题库没有就手动答题
        if answer_temp is None:
            if skip is False:
                answer_temp = manual_answer(item)
            elif skip is True:
                answer_temp = 'NF'

        # 处理多选和拼接
        if answer_mode == 2:
            # 暴力模式处理
            answer_temp = answer_temp + ","
        elif answer_mode == 1 or answer_mode == 3:
            if device == "WEB":
                if item["isMulti"] and answer_temp != "NF":
                    # 对于多选题，将新元素中的每个选项与ChoseOption中的OptionKey比较
                    multi_options = answer_temp.split(",")
                    multi_result = []
                    for option in multi_options:
                        for chose_option in item["ChoseOption"]:
                            if option == chose_option["OptionKey"].strip(","):
                                multi_result.append(chose_option["ShowOption"])
                                break
                    answer_temp = ",".join(multi_result)
                else:
                    # 对于单选题，与之前的逻辑相同
                    for option in item["ChoseOption"]:
                        if option["OptionKey"].strip(",") == answer_temp:
                            answer_temp = option["ShowOption"]
                            break
            elif device == "APP":
                pass
            else:
                print("程序出错了-a2!")
                exit(0)

        # 添加到数组
        if answer_mode == 1 or answer_mode == 2:
            answer_data.append(answer_temp)
        elif answer_mode == 3:
            if answer_temp != "NF":
                answer_temp = answer_temp + ","
            answer_data.append({"qsid": item['QSID'], "answer": answer_temp})

        # 周期完成
        num += 1

        # 计算进度
        if num == round((len(exam_data["data"])) / 4):  # 12.5
            print("25%")
        elif num == round(len(exam_data["data"]) / 4 * 2):  # 25
            print("50%")
        elif num == round(len(exam_data["data"]) / 4 * 3):  # 37.5
            print("75%")
        elif num == len(exam_data["data"]):  # 50
            print("100%")

    # 记录结束时间
    end_time = time.time()

    # 提示信息
    print("\r\n寻找完成√\r\n")

    if answer_mode == 2:
        # 调试信息
        if debug_mode:
            print(f"您选择是暴力模式, 已为您输出提交给接口所需的答案:\r\n{str(answer_data)}")

        # 复制到剪切板
        pyperclip.copy(str(answer_data))

        # 最后信息
        print(
            f"寻找耗时: {end_time - start_time:.6f} 秒\r\n" +
            f"已为您复制到剪切板, Bye ~"
        )
        return True

    if answer_mode == 3:

        answer_data = base64.b64encode(json.dumps(answer_data, ensure_ascii=True).encode('utf-8')).decode('utf-8')

        # 调试信息
        if debug_mode:
            print(f"您选择是综合模式, 已为您输出给器灵的神秘代码:\r\n{answer_data}")

        # 最后信息
        print(
            f"寻找耗时: {end_time - start_time:.6f} 秒\r\n" +
            f"已为您复制到剪切板, Bye ~"
        )

        if ws:
            return answer_data
        else:
            # 复制到剪切板
            pyperclip.copy(answer_data)
            return True

    # 按格式排序
    for i, options in enumerate(answer_data):
        result_data = result_data + f"{i + 1}. {" ".join(options)}\n"

    # 调试信息
    if debug_mode:
        print(f"您选择是静默模式, 已为您输出正常做题时所需的答案: \r\n{result_data}\r\n")

    # 复制到剪切板
    pyperclip.copy(result_data)

    # 最后信息
    print(
        f"寻找耗时: {end_time - start_time:.6f} 秒 \r\n" +
        f"已为您复制到剪切板"
    )

    return True


# 主函数入口
if __name__ == "__main__":
    answer(debug_mode=True,
           answer_mode=1,
           skip=False,
           exam_data=import_exam("exam.json"),
           database_path="../database/test.json",
           ws=False)
