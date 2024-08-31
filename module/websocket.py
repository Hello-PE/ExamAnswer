import asyncio
import json
import websockets
import base64
from module.decrypt import decrypt
from module.answer import answer

# 全局事件来通知主程序何时退出
stop_event = asyncio.Event()


# 处理连接的协程函数
async def handle_connection(websocket, path):
    if path == "/test":
        try:
            async for message in websocket:
                if message == "stop":
                    print("停止服务")
                    await websocket.close()
                    stop_event.set()  # 设置停止事件
                    break  # 退出循环，停止服务器

                # print(dec)  # 打印解码后的数据
                await websocket.send(
                    answer(
                        debug_mode=False,
                        answer_mode=3,
                        skip=True,
                        exam_data=decrypt(
                            debug_mode=False,
                            config_file_path='./config/main.yml',
                            encrypt_data=base64.b64decode(message).decode('utf-8')
                        ),
                        database_path='./database/test.json',
                        ws=True
                    )
                )
        except websockets.ConnectionClosed:
            pass
    else:
        # 如果路径不是/test，不处理
        pass


# 启动WebSocket服务器的协程函数
async def start_server():
    server = await websockets.serve(handle_connection, "localhost", 54188)
    print("已开始监听")
    await stop_event.wait()  # 等待停止事件触发
    server.close()
    await server.wait_closed()
    print("已结束监听")


# 如果直接运行本模块，启动服务器
if __name__ == "__main__":
    asyncio.run(start_server())
