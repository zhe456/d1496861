import socket
import threading
import getpass

from src.database.db import init_database, check_login

HOST = "127.0.0.1"
PORT = 8888


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")

            if not message:
                print("服务器已关闭连接。")
                break

            print(message)

        except Exception:
            print("接收讯息时发生错误，已离开聊天室。")
            break


def start_client():
    init_database()

    print("=== 餐厅评价平台 即时客服登入 ===")

    username = input("帐号：")
    password = getpass.getpass("密码：")

    if not check_login(username, password):
        print("登入失败：帐号或密码错误。")
        return

    print("登入成功，进入聊天室。输入 exit 可以离开。")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))

        receive_thread = threading.Thread(
            target=receive_messages,
            args=(client,),
            daemon=True
        )
        receive_thread.start()

        while True:
            message = input("")

            if message.lower() == "exit":
                print("已离开聊天室。")
                break

            full_message = f"{username}：{message}"
            client.send(full_message.encode("utf-8"))

    except ConnectionRefusedError:
        print("无法连接服务器，请先执行 chat_server.py。")

    except Exception as e:
        print(f"聊天室发生错误：{e}")

    finally:
        client.close()


if __name__ == "__main__":
    start_client()