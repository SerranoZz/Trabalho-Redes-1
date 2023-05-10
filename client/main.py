import socket
import select
import subprocess
import platform
import time

host = "127.0.0.1"
port = int(input("Digite a porta: "))

#construimos a interface grafica com base neste codigo
#nao ira rodar por aqui porque modificamos a função que manda o tabuleiro, o placar, etc para o cliente


def clean_terminal():
    if platform.system() == "Windows":
        subprocess.Popen("cls", shell=True).communicate()
    else:
        print("\033c", end="")


def read_coords(msg, message):
    dim = int(msg.split("\n")[0][-2]) + 1
    try:
        i = int(message.split(" ")[0])
        j = int(message.split(" ")[1])
    except ValueError:
        print("Coordenadas invalidas! Use o formato \"i j\" (sem aspas),")
        print("onde i e j sao inteiros maiores ou iguais a 0 e menores que {0}".format(dim))
        input("Pressione <enter> para continuar...")
        return False

    if i < 0 or i >= dim or j < 0 or j >= dim:
        print("Coordenada i e j deve ser maior ou igual a zero e menor que {0}".format(dim))
        input("Pressione <enter> para continuar...")
        return False

    return True


def keepalive(connection):
    while True:
        ready_sockets, _, _ = select.select([connection], [], [], 1)
        if not ready_sockets:
            continue

        res = connection.recv(2024)
        res_message = res.decode("utf-8")
        res_msgs = res_message.split("::= ")

        print(res_message)

        status = res_msgs[0]
        msg = res_msgs[1]

        if status == "YOUR_TURN":
            clean_terminal()
            message = input(msg)
            while not read_coords(msg, message):
                message = input("Especifique uma peca: ")
            connection.send(str.encode(message))
        elif status == "RESPONSE" or status == "NOT_YOUR_TURN":
            clean_terminal()
            print(msg)
        elif status == "END_GAME" or status == "SERVER_CLOSED":
            clean_terminal()
            print(msg)
            print("Até mais!")
            break
        elif status == "WAITING_PLAYERS":
            clean_terminal()
            print(msg)


if __name__ == "__main__":
    client = socket.socket()
    client.connect((host, port))
    keepalive(client)
