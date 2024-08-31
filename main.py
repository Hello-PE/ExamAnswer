from module.answer import answer
from module.decrypt import decrypt
import asyncio
from module.websocket import start_server
import traceback


async def main():
    # 初始化 #
    # 运行模式 (1.手动输入/2.WebSocket请求)
    run_mode = 1

    # 答题模式 (1.静默/2.暴力/3.综合)
    answer_mode = 3

    # 是否跳过题库中未有的题目
    skip = True

    # 是否一直运行
    keep_run = True

    # 配置文件
    config_file_path = "config/main.yml"

    # 数据库文件
    database_path = "database/test.json"

    # 主程序 #
    try:
        while True:
            # 运行模式判断
            if run_mode == 1:
                # 获取密文并解密
                encrypt_data = input("请输入题目密文: ").encode('utf-8')

                # 调用答题函数
                answer(
                    debug_mode,
                    answer_mode,
                    skip,
                    decrypt(
                        debug_mode,
                        config_file_path,
                        encrypt_data
                    ),
                    database_path,
                    ws=False
                )
            elif run_mode == 2:
                await start_server()

            if not keep_run:
                break
    # 异常处理 #
    # 用户取消
    except KeyboardInterrupt:
        print("\r\n\r\n用户取消了程序运行")
    # 程序终止
    except SystemExit:
        print("\r\n\r\n已终止")
    # 其它错误
    except Exception as error:
        print(f"\r\n\r\n出错了: \r\n{error}\r\n堆栈信息等: \r\n{traceback.print_exc()}\r\n请将上述信息通知作者, 谢谢!")


if __name__ == "__main__":
    # 程序信息
    program_name = "Hello-PE"
    program_version = "1.0.0"
    program_author = "Libws"
    debug_mode = False

    # 骚话, 属于是每个程序必备了Lmao
    print("\r\n“人们常常仰视英雄的光芒与伟业，却鲜有人探寻他们背后的痛楚与泪痕”\r\n")
    print("  _   _          _   _                   ____    _____ ")
    print(" | | | |   ___  | | | |   ___           |  _ \\  | ____|")
    print(" | |_| |  / _ \\ | | | |  / _ \\   _____  | |_) | |  _|  ")
    print(" |  _  | |  __/ | | | | | (_) | |_____| |  __/  | |___ ")
    print(" |_| |_|  \\___| |_| |_|  \\___/          |_|     |_____|")
    print("                                                       ")
    print(f"欢迎使用: {program_name}, 当前版本: {program_version}, 作者: {program_author}\r\n")
    if debug_mode:
        print("注意: 调试模式已开启, 如果您不清楚您在干什么, 请立即关闭程序并通知作者!\r\n")

    asyncio.run(main())

    print("\r\n程序运行结束, Bye ~\r\n\r\n")
