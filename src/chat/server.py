import socket
import threading

HOST = "127.0.0.1"
PORT = 8888

clients = []


def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode("utf-8"))
            except Exception:
                remove_client(client)


def remove_client(client_socket):
    if client_socket in clients:
        clients.remove(client_socket)
        client_socket.close()


def handle_client(client_socket, address):
    print(f"新使用者连接：{address}")

    try:
        client_socket.send("欢迎进入餐厅评价平台即时客服聊天室！\n".encode("utf-8"))

        while True:
            message = client_socket.recv(1024).decode("utf-8")

            if not message:
                break

            print(f"{address}: {message}")
            broadcast(f"{address}: {message}", client_socket)

    except ConnectionResetError:
        print(f"使用者异常断线：{address}")

    except Exception as e:
        print(f"处理使用者时发生错误：{e}")

    finally:
        remove_client(client_socket)
        print(f"使用者离开：{address}")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((HOST, PORT))
        server.listen()

        print(f"聊天室服务器启动成功：{HOST}:{PORT}")
        print("等待使用者连接...")

        while True:
            client_socket, address = server.accept()
            clients.append(client_socket)

            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address)
            )
            thread.start()

    except Exception as e:
        print(f"服务器发生错误：{e}")

    finally:
        server.close()


if __name__ == "__main__":
    start_server()