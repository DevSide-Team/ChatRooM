import tkinter,ctypes,sys,socket,threading
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk
import ttkbootstrap as ttk

#初始化
root = ttk.Window(title='ChatRooM 客户端',size=(800,600),themename='darkly',resizable=(False,False),position=(100,100))
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverconfPath=Path(__file__).parent / "servers"
imagePath=Path(__file__).parent / "images"

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
root.tk.call('tk', 'scaling', ScaleFactor/75)

root.protocol("WM_DELETE_WINDOW", lambda:quitHandler(client))

#图片处理
image=Image.open(imagePath / 'exit.png')
exitImage=ImageTk.PhotoImage(image)
image=Image.open(imagePath / 'about.png')
aboutImage=ImageTk.PhotoImage(image)
image=Image.open(imagePath / 'icon.png')
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

serverBox=tkinter.Listbox(serverFrame,font=('Microsoft JhengHei UI',15),bg='#f5f5f5')

iconLable=ttk.Label(homeFrame,image=iconImage)

connectButton=ttk.Button(homeFrame,text='连接服务器',command=lambda:connectServer(client))
exitButton=ttk.Button(homeFrame,bootstyle='danger',image=exitImage,command=lambda:sys.exit(0))
aboutButton=ttk.Button(homeFrame,image=aboutImage,bootstyle='secondary',command=lambda:about())
addButton=ttk.Button(homeFrame,text='添加服务器',command=lambda:addServerFrameSwitch())
deleteButton=ttk.Button(homeFrame,text='删除',bootstyle='danger',command=lambda:deleteServer())
#添加服务器部分
addServerFrame = ttk.Frame(root,width=800,height=600)

connectLabel=ttk.Label(addServerFrame,text='添加服务器',font=('Microsoft JhengHei UI',30,'bold'))
serverNameLabel=ttk.Label(addServerFrame,text='服务器名称',font=('Microsoft JhengHei UI',15))
serverAddrLabel=ttk.Label(addServerFrame,text='服务器地址',font=('Microsoft JhengHei UI',15))
usernameLabel=ttk.Label(addServerFrame,text='用户名',font=('Microsoft JhengHei UI',15))

backButton=ttk.Button(addServerFrame,text='<--返回',command=lambda:back())
confirmButton=ttk.Button(addServerFrame,text='确定',bootstyle='success',command=lambda:addServer())

serverNameEntry=ttk.Entry(addServerFrame)
usernameEntry=ttk.Entry(addServerFrame)
serverAddrEntry=ttk.Entry(addServerFrame)
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
#添加服务器部分
backButton.place(x=15,y=22)
confirmButton.place(x=360,y=440)

connectLabel.place(x=250,y=10)
serverNameLabel.place(x=320,y=100)
serverAddrLabel.place(x=320,y=200)
usernameLabel.place(x=355,y=300)

serverNameEntry.place(x=285,y=145)
serverAddrEntry.place(x=285,y=245)
usernameEntry.place(x=285,y=345)
#聊天部分
msgBox.place(x=5,y=5,width=790,height=520)
msgEntry.place(x=5,y=540,width=660,height=50)
sendButton.place(x=675,y=540,width=120,height=50)

#关于
def about():
    messagebox.showinfo('关于','ChatRooM Client v0.2.0-UI_update_04\nMade by Explore Team')
#切换添加服务器页面
def addServerFrameSwitch():
    addServerFrame.pack()
    homeFrame.pack_forget()
#添加服务器
def addServer():
    sName=serverNameEntry.get()
    addServerFrame.pack_forget()
    homeFrame.pack()
    serverBox.insert(tkinter.END,sName)
    temp=open(str(serverconfPath / serverNameEntry.get())+'.conf','w')
    temp.write(serverAddrEntry.get()+'\n')
    temp.write(usernameEntry.get())
    temp.close()
#删除服务器
def deleteServer():
    try:
        temp=Path(str(serverconfPath / serverBox.get(serverBox.curselection()))+'.conf')
        temp.unlink()
        serverBox.delete(serverBox.curselection())
    except Exception as e:
        messagebox.showerror('错误','请选择项目后再删除')
#返回主页
def back():
    addServerFrame.pack_forget()
    homeFrame.pack()
#连接服务器
def connectServer(client):
    global homeFrame,msgFrame,usernameEntry
    try:
        temp=open(str(serverconfPath / serverBox.get(serverBox.curselection()))+'.conf','r')
        t=temp.readlines()
        t0=t[0].strip('\n')
        ip=t0.split(':')[0]
        port=t0.split(':')[1]
        usr=t[1]
        client.connect((ip,int(port)))
        client.send(usr.encode('utf-8'))
        temp.close()
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
    try:
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
    except Exception as e:
        pass

#main()
root.mainloop()