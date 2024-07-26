import socket,time,json,threading,sys,os
from fs import osfs
from colorama import init, Fore, just_fix_windows_console
Version="v0.1.9-command_update_03"

class user:
    info={}
    def __init__(self,username,ip,port,conn):
        self.info={'username':username,'ip':ip,'port':port,'conn':conn}
    

#初始化
def Init():
    global server,running,argv,kicklist,bannedList,Files,userList
    Files=osfs.OSFS(sys.path[0])
    if not Files.exists('banned.json'):
        Files.appendtext('banned.json','[]')    
    bannedList=json.loads(Files.readtext('banned.json',encoding='utf-8'))
    kicklist=[] #待被kick列表
    running=True
    userList={}
    init()
    just_fix_windows_console()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("  ____ _           _   ____             __  __ ")
    print(" / ___| |__   __ _| |_|  _ \ ___   ___ |  \/  |")
    print("| |   | '_ \ / _` | __| |_) / _ \ / _ \| |\/| |")
    print("| |___| | | | (_| | |_|  _ < (_) | (_) | |  | |")
    print(" \____|_| |_|\__,_|\__|_| \_\___/ \___/|_|  |_|")
    print(f"ChatRooM {Version}")
    print("Made by Explore Team")
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
        global running,userList,bannedList
        server.listen(5)
        while running:
            conn,address=server.accept()
            username=conn.recv(2048).decode('utf-8')
            if username in userList:
                conn.send("server_name_used".encode('utf-8'))
                conn.close()
                continue
            if address[0] in bannedList:
                conn.send("server_banned".encode('utf-8'))
                conn.close()
                log("INFO",f"{username} {address} was banned but try into char room"+Fore.RESET)
                continue
            userList|={username:user(username,address[0],address[1],conn)}
            log("INFO",Fore.LIGHTYELLOW_EX+f"{username} {address} joined the chat room"+Fore.RESET)
            threading.Thread(target=msgHandler, args=(username,)).start()
    except:
        log("WARNING",'connectHandler running falied')
        pass    
#处理接收的信息并发送
def msgHandler(mainUsername):
    try:
        global running,userList,bannedList
        conn=userList[mainUsername].info['conn']
        address=(userList[mainUsername].info['ip'],userList[mainUsername].info['port'])
        while running and (mainUsername in userList):
            username=conn.recv(2048).decode('utf-8')
            msg=conn.recv(2048).decode('utf-8')
            if (not msg) or (msg is None):
                log("INFO",Fore.LIGHTYELLOW_EX+f"{mainUsername} {address} left the chat room"+Fore.RESET)
                del userList[mainUsername]
                return
            else:
                log("INFO","<"+mainUsername+"> "+msg)
                for Useri in userList:
                    userList[Useri].info['conn'].send(("<"+mainUsername+"> "+msg).encode('utf-8'))
    except:
        if mainUsername in userList and running:
            del userList[mainUsername]
        log("INFO",Fore.LIGHTYELLOW_EX+f"{mainUsername} {address} left the chat room"+Fore.RESET) #可能的正常退出
    return

def exit():
    global running,server
    running=False
    for user in userList:
        try:
            userList[user].info['conn'].send("server_closed".encode('utf-8'))
            userList[user].info['conn'].close()
        except:
            pass
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
    def kick(self=None): #踢出用户
        if len(argv)==0 or len(argv) > 1: 
            log("ERROR",Fore.LIGHTRED_EX+"Invalid parameter."+Fore.RESET)
        else:
            if not argv[0] in userList:
                log("ERROR",Fore.LIGHTRED_EX+"User not found"+Fore.RESET)
            else: #删除此用户存在的状态
                address=(userList[argv[0]].info['ip'],userList[argv[0]].info['port'])
                userList[argv[0]].info['conn'].send('server_kick'.encode('utf-8'))
                userList[argv[0]].info['conn'].close()
                # del userList[argv[0]]
                log("INFO",Fore.LIGHTYELLOW_EX+f"{argv[0]} {address} kicked from the chat room"+Fore.RESET)

    def ban():
        if len(argv)==0 or len(argv) > 1: 
            log("ERROR",Fore.LIGHTRED_EX+"Invalid parameter."+Fore.RESET)
        else:
            if not argv[0] in userList:
                log("ERROR",Fore.LIGHTRED_EX+"User not found"+Fore.RESET)
            else:
                bannedList.append(userList[argv[0]].info['ip'])
                Files.settext('banned.json',json.dumps(bannedList)) #保存到文件
                Command().kick()
    def unban():
        if len(argv)==0 or len(argv) > 1: 
            log("ERROR",Fore.LIGHTRED_EX+"Invalid parameter."+Fore.RESET)
        else:
            if not argv[0] in bannedList:
                log("ERROR",Fore.LIGHTRED_EX+"Address not found"+Fore.RESET)
            else:
                bannedList.remove(argv[0])
                Files.settext('banned.json',json.dumps(bannedList)) #保存到文件
    commandList={"help":help,"stop":stop,"kick":kick,"ban":ban,"unban":unban,"version":version}     #命令列表


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
    get_connect=threading.Thread(target=connectHandler, args=(server,)) #接受连接
    get_connect.start()
    command() #命令行

if __name__ == "__main__":
    main() 