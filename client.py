import tkinter,ctypes,sys,socket,threading
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk
import ttkbootstrap as ttk

#初始化
root = ttk.Window(title='ChatRooM 客户端',size=(800,600),themename='darkly',resizable=(False,False),position=(100,100))
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
path=Path(__file__).parent / "images"

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
root.tk.call('tk', 'scaling', ScaleFactor/75)

root.protocol("WM_DELETE_WINDOW", lambda:quitHandler(client))

#图片处理
image=Image.open(path / 'exit.png')
exitImage=ImageTk.PhotoImage(image)
image=Image.open(path / 'about.png')
aboutImage=ImageTk.PhotoImage(image)
image=Image.open(path / 'icon.png')
iconImage=ImageTk.PhotoImage(image)


#退出窗口时触发
def quitHandler(client):
    sys.exit(0)

#样式配置
LS=ttk.Style()
LS.configure("TButton",font=('Microsoft JhengHei UI',14))

#组件创建
#主页部分
homeFrame = ttk.Frame(root,width=800,height=600)
serverFrame= ttk.Frame(homeFrame,width=600,height=500,bootstyle='secondary')

serverBox=tkinter.Text(serverFrame,state=tkinter.DISABLED,wrap='word',font=('Microsoft JhengHei UI',12),bg='#f5f5f5')

iconLable=ttk.Label(homeFrame,image=iconImage)

connectButton=ttk.Button(homeFrame,text='连接服务器',command=lambda:frameSwitchHandler(client))
exitButton=ttk.Button(homeFrame,bootstyle='danger',image=exitImage,command=lambda:sys.exit(0))
aboutButton=ttk.Button(homeFrame,image=aboutImage,bootstyle='secondary',command=lambda:about())
addButton=ttk.Button(homeFrame,text='添加服务器')
deleteButton=ttk.Button(homeFrame,text='删除',bootstyle='danger')

IPEntry=ttk.Entry(homeFrame)
portEntry=ttk.Entry(homeFrame)
usernameEntry=ttk.Entry(homeFrame)
#聊天部分
msgFrame = ttk.Frame(root,width=800,height=600)
msgBox=tkinter.Text(msgFrame,state=tkinter.DISABLED,wrap='word',font=('Microsoft JhengHei UI',12),bg='#f5f5f5')
msgEntry=ttk.Entry(msgFrame,font=('Microsoft JhengHei UI',12))
sendButton=ttk.Button(msgFrame,text='发送',style='connectButton.TButton',command=lambda:sendMsg(client))

#组件放置
#主页部分
homeFrame.pack()
serverFrame.place(x=25,y=75)

serverBox.place(x=0,y=0,width=600,height=500)

exitButton.place(x=720,y=10)
aboutButton.place(x=640,y=10)
connectButton.place(x=632,y=150,width=162,height=50)
addButton.place(x=632,y=210,width=162,height=50)
deleteButton.place(x=632,y=300,width=162,height=50)

iconLable.place(x=15,y=0)
#聊天部分
msgBox.place(x=5,y=5,width=790,height=520)
msgEntry.place(x=5,y=540,width=660,height=50)
sendButton.place(x=675,y=540,width=120,height=50)

#关于
def about():
    messagebox.showinfo('关于','ChatRooM Client v0.1.9\nMade by Explore Team')
#添加服务器
def addServer():
    pass
#界面切换
def frameSwitchHandler(client):
    global homeFrame,msgFrame,IPEntry,portEntry,usernameEntry
    try:
        client.connect((IPEntry.get(),int(portEntry.get())))
        client.send(usernameEntry.get().encode('utf-8'))
        homeFrame.pack_forget()  
        msgFrame.pack()
        threading.Thread(target=recvMsg,args=(client,)).start()
    except Exception as e:
        messagebox.showerror('连接失败','请检查输入的IP地址和端口是否正确')
#信息发送
def sendMsg(client):
    global msgEntry,usernameEntry
    if msgEntry.get().strip:
        client.send(usernameEntry.get().encode('utf-8'))
        client.send(msgEntry.get().encode('utf-8'))
#信息接收
def recvMsg(client):
    global msgBox
    while True:
        msg=client.recv(2048).decode('utf-8')
        if msg=='server_closed':
            messagebox.showerror('连接失败','Server Closed')
            client.close()
            msgFrame.pack_forget()
            homeFrame.pack()
        if msg=='server_kick':
            messagebox.showerror('连接失败','You have been kicked by an operator.')
            client.close()
            msgFrame.pack_forget()
            homeFrame.pack()
        if msg=='server_banned':
            messagebox.showerror('连接失败','You have been banned from the server.')
            client.close()
            msgFrame.pack_forget()
            homeFrame.pack()
        msgBox.config(state=tkinter.NORMAL)
        msgBox.insert(tkinter.END,msg+'\n')
        msgBox.config(state=tkinter.DISABLED)

#main()
root.mainloop()