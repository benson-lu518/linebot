# linebot 圖文設定 Benson QA
#line developer: https://developers.line.biz/console/channel/1655609443/basics
#圖片網址: https://bensonlu518.imgur.com/all
#dgnrock: https://ngrok.com/download (跟py檔放在同個路徑)
#路徑: C:\Users\do860\OneDrive\桌面\Python 工研院\linebot\heroku2
#步驟: cmd開啟>heroku login>heroku create appname>git init>heroku git:remote -a appname
#>git add .>git commit -am"make it better">git push heroku master

from flask import Flask
app=Flask(__name__)

from flask import request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import( MessageEvent,TextMessage,TextSendMessage)
                           
#使用者channel access token
line_bot_api=LineBotApi('7WRO8/o9RBzHKWfgSv8XM8ddCPw71awDkA2rlJBwwo+sGkUTbyVDWpJkfH65wunqJBcWvAqSAqKrzTFBgmVW3Di0Oju1pRw1OG61UyiXw6BpYSPQc4fA1zQ0foWVyChyjtgZzY7xtjLfebkAiuArMgdB04t89/1O/w1cDnyilFU=') 
#使用者 channel secret
handler=WebhookHandler('66aa668472152c2a039ef469fd812348') 


#建立callback路由
@app.route("/callback",methods=['POST'])
def callback():
    signature=request.headers['X-Line-Signature']
    body=request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


#爬網頁
import requests 
#xml 解析模組
try:
    import xml.etree.eElementTree as et
except ImportError:
    import xml.etree.ElementTree as et


#建立函數 參數為期別
def monoNum(n):
        
    content=requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
    tree=et.fromstring(content.text)#解析xml
    items=list(tree.iter(tag='item'))
    title=items[n][0].text
    ptext=items[n][2].text
    ptext=ptext.replace('<p>','').replace('</p>','\n')
    return title +'月\n'+ptext[:-1] #[-1]移除最後一個\n



#將接受到的訊息回傳
@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    mtext=event.message.text
    if mtext=='@本期對獎號碼':
        try:
            message=TextSendMessage(
                text=monoNum(0)
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
    elif mtext=='@前期對獎號碼':
        try:
            message=TextSendMessage(
                text=monoNum(1)+'\n\n'+monoNum(2)
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
    elif len(mtext)==3 and mtext.isdigit():
        try:
            content=requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
            tree=et.fromstring(content.text)#解析xml
            #取本期獎號
            items=list(tree.iter(tag='item'))
            ptext=items[0][2].text
            ptext=ptext.replace('<p>','').replace('</p>','')
            ptext=ptext.split('：')
            
            #特別獎或特獎後三碼
            prizelist=[]
            prizelist.append(ptext[1][5:8])
            prizelist.append(ptext[2][5:8])
            
            #頭獎
            firstlist=ptext[3].split('、')
            for i in range(0,len(firstlist)):
                prizelist.append(firstlist[i][5:8])
            
            #增開六獎
            sixlist=ptext[4].split('、')
            for i in range(0,len(sixlist)):
                prizelist.append(sixlist[i])
              
            if mtext in prizelist:
                message=('前三碼有中呦,後面五碼自己對')
                message+=monoNum(0)
            else:
                message=('很可惜，沒對中，請輸入下一張發票後三碼')
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='請輸入發票後三碼!'))
   
if __name__=='__main__':
    app.run()