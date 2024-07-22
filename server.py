import socket,time,threading,sys
from colorama import init, Fore, just_fix_windows_console
Version="0.1.4-stable"
#初始化
def Init():
    global server,clientList,usernameList,running,argv,kicklist
    clientList=[]
    kicklist=[] #待被kick列表
    running=True
    usernameList=[]
    init()
    just_fix_windows_console()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("  ____ _           _   ____             __  __ ")
    print(" / ___| |__   __ _| |_|  _ \ ___   ___ |  \/  |")
    print("| |   | '_ \ / _` | __| |_) / _ \ / _ \| |\/| |")
    print("| |___| | | | (_| | |_|  _ < (_) | (_) | |  | |")
    print(" \____|_| |_|\__,_|\__|_| \_\___/ \___/|_|  |_|")
    print("ChatRooM v0.1.4-stable")
    print("Thanks for using ChatRooM!")
    print()
#绑定端口和IP
def bind():
    log("CONFIG","Set server host (normally 127.0.0.1): ")
    host=input()
    log("CONFIG","Set server port: ")
    port=int(input())
    server.bind((host, port))
    log("INFO","Server started on "+host)
    log("INFO","Listening on port "+str(port))
#日志输出
def log(status, msg):
    localTime=time.strftime('%H:%M:%S', time.localtime())
    if status=="INFO":
        print("["+Fore.LIGHTCYAN_EX+localTime+Fore.RESET+Fore.GREEN+" INFO"+Fore.RESET+"]: "+msg)
    elif status=="WARNING":
        print("["+Fore.LIGHTCYAN_EX+localTime+Fore.RESET+Fore.LIGHTYELLOW_EX+" WARNING"+Fore.RESET+"]: "+msg)
    elif status=="ERROR":
        print("["+Fore.LIGHTCYAN_EX+localTime+Fore.RESET+Fore.LIGHTRED_EX+" ERROR"+Fore.RESET+"]: "+Fore.LIGHTRED_EX+msg+Fore.RESET)
    elif status=="FATAL":
        print("["+Fore.LIGHTCYAN_EX+localTime+Fore.RESET+Fore.RED+" FATAL"+Fore.RESET+"]: "+Fore.RED+msg+Fore.RESET)
        sys.exit(1)
    elif status=="CONFIG":
        print("["+Fore.LIGHTCYAN_EX+localTime+Fore.RESET+Fore.LIGHTBLACK_EX+" CONFIG"+Fore.RESET+"]: "+msg)
#接收连接
def connectHandler(server):
    try:
        server.listen(5)
        while running:
            conn, address = server.accept()
            username=conn.recv(2048).decode('utf-8')
            usernameList.append(username)
            log("INFO",Fore.LIGHTYELLOW_EX+f"{username} {address} joined the chat room"+Fore.RESET)
            clientList.append(conn)
            threading.Thread(target=msgHandler, args=(conn,address,username,)).start()
    except OSError:#过滤由于关闭导致的崩溃信息
        return
#处理接收的信息并发送
def msgHandler(conn,address,mainUsername):
    try: #过滤崩溃信息
        while running and (mainUsername in usernameList): #检测
            username=conn.recv(2048).decode('utf-8')
            msg=conn.recv(2048).decode('utf-8')
            if mainUsername in kicklist:#是否被踢出
                break #防止消息更新
            if not msg:
                log("INFO",Fore.LIGHTYELLOW_EX+f"{username} {address} left the chat room"+Fore.RESET)
                usernameList.remove(mainUsername)
                clientList.remove(conn)
                return
            else:
                if msg is None:
                    break
                else:
                    log("INFO","<"+username+"> "+msg)
                    for client in clientList:
                        client.send(("<"+username+"> "+msg).encode('utf-8'))
    except OSError: #关闭服务器后过滤报错
        conn.close()
        log("INFO",Fore.LIGHTYELLOW_EX+f"{username} {address} left the chat room"+Fore.RESET) #关闭服务器的处理
        return
    if mainUsername in kicklist and conn in clientList: #被踢出处理
        log("INFO",Fore.LIGHTYELLOW_EX+f"{username} {address} kicked from the chat room"+Fore.RESET)
        conn.send('server_kick'.encode('utf-8'))
        conn.close()
        clientList.remove(conn)
        kicklist.remove(mainUsername)
    if conn in clientList: #删除客户端连接
        clientList.remove(conn)
    log("INFO",Fore.LIGHTYELLOW_EX+f"{username} {address} left the chat room"+Fore.RESET) #可能的正常退出
    return

def exit():
    global running,server
    running=False
    for client in clientList:
        client.send("server_closed".encode('utf-8'))
        client.close()
    server.__exit__()

class Command: #定义关于命令的类
    def __init__(self=None): #初始化
        pass
    def help():
        print("CommandList:")
        print("     help: Show this message")
        print("     stop: stop the server")
        print("     kick: Kick chatroom member")
        print("     ban: Ban chatroom member")
        print("     unban: Unban chatroom member")
        print(f"     version: {Version}") #todo
    def stop(): 
        exit() #发送server_closed信息,关闭线程
        sys.exit(0)
    def version():
        print(Version)
    def kick(): #踢出用户
        if len(argv)==0 or len(argv) > 1: 
            log("ERROR","Invalid parameter.")
        else:
            if not argv[0] in usernameList:
                log("ERROR","User not found")
            else: #删除此用户存在的状态
                usernameList.remove(argv[0])
                kicklist.append(argv[0]) #将用户添加到踢出列表，等待线程检测后踢出
    commandList={"help":help,"stop":stop,"kick":kick,"ban":None,"unban":None,"version":version}     #命令列表


def command():
    global running,server,argv
    commands=Command()
    while True:
        command=input().split(" ") #拆分空格参数
        command=list(filter(lambda x: x != '', command)) #过滤空字符串
        if not command:
            continue
        argv=command[1:] #拆分命令与参数
        commands.commandList[command[0]]() if command[0] in commands.commandList else log("ERROR",Fore.LIGHTRED_EX+"Invalid command"+Fore.RESET) #命令存在-> 执行命令,不存在- > 输出错误信息

def main():
    Init()
    bind()
    getConnect=threading.Thread(target=connectHandler, args=(server,)) #接受连接
    getConnect.start()
    command() #命令行

if __name__ == "__main__":
    main() 