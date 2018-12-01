import dotenv
import linebot
import os
import requests
from flask import Flask,request,session,abort
#from flask.ext.session import Session
from linebot.exceptions import (
        InvalidSignatureError
    )
from linebot.models import (
        BeaconEvent,MessageEvent,TextMessage,TextSendMessage,
    )
from icecream import ic

HOST="https://sakak.ml"
REDIRECT_URL=HOST+"/line/login/callback"

# env
#print(dotenv.find_dotenv())
dotenv.load_dotenv(dotenv.find_dotenv())

#LINE MESSAGING API
CHANNEL_ACCESS_TOKEN=os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET=os.environ.get("CHANNEL_SECRET")
print(CHANNEL_ACCESS_TOKEN,CHANNEL_SECRET)
if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("env not loaded")
else:
    print("env file load successed")

# LINE LOGIN API
LINE_LOGIN_CHANNEL_ID=os.environ.get("LINE_LOGIN_CHANNEL_ID")
LINE_LOGIN_CHANNEL_SECRET=os.environ.get("LINE_LOGIN_CHANNEL_SECRET")
if not LINE_LOGIN_CHANNEL_ID or not LINE_LOGIN_CHANNEL_SECRET :
    print("line login channel_id or channle_secret is not loaded")
else:
    print("line login channel_id and channel_secret is loaded successfully")
LINE_OAUTH_STATE="QWERTY"

app=Flask(__name__)
app.secret_key="secret_key"

linebot_api=linebot.LineBotApi(CHANNEL_ACCESS_TOKEN)
handler=linebot.WebhookHandler(CHANNEL_SECRET)
access_tokens={}

def get_user_state():
    displayName=session.get('user')
    print(displayName)
    if displayName : return "<p>your name : {0}</p>".format(displayName)
    else :           return "<p>you are not logined yet </p>"

@app.route("/line/index")
def index():
    return """
    <!doctype html>
    <html>
        <head></head>
        <body>
            <h1> hello world</h1>
            {0}
            <p>
                this is a stamp rally with line api and google 360 media.
                <a src="/"> top page</a>
                <a src="#"> curreent page</a>
                <a src="/line/login">start page</a>
                <a src="/line/logout">logout</a>
            </p>
            <p>developer:<a href="https://github.com/sakakendo0321/>sakakendo0321</a></p>
        </body>
    </html>
    """.format(get_user_state())

@app.route("/line/login")
def login():
    url="https://access.line.me/oauth2/v2.1/authorize"
    response_type="code"
    client_id=LINE_LOGIN_CHANNEL_ID
    redirect_uri=REDIRECT_URL   # HOST+"/line/login/callback"
    state=LINE_OAUTH_STATE
    scope="profile"
    html="""
    <!doctype html>
    <html>
        <body>
            <p>{6}</p>
            <a href="{0}?response_type={1}&client_id={2}&redirect_uri={3}&state={4}&scope={5}">line login</a>
        </body>
    </html>
    """.format(url,response_type,client_id,redirect_uri,state,scope,get_user_state())
    print("login html",html)
    return html

def get_profile(access_token):
    if access_token is not None:
        bearer="Bearer {0}".format(access_token)
        print("bearer type",type(bearer))
        headers={"Authorization":bearer}
        print("get_profile headers",headers)
        url="https://api.line.me/v2/profile"
        res=requests.get(url,headers=headers)
        if res.status_code is 200:
            body=res.json()
#            print("get profile successed",body,type(body))
            return body
        else:
            print("get_profile failed",res.status_code)
    return None

def get_line_access_token(code):
    headers={"Content-Type":"application/x-www-form-urlencoded"}
    data={
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":REDIRECT_URL,
        "client_id":LINE_LOGIN_CHANNEL_ID,
        "client_secret":LINE_LOGIN_CHANNEL_SECRET
    }
    print(headers,data)
    res=requests.post("https://api.line.me/oauth2/v2.1/token",headers=headers,data=data)
    print("get access_token",res.status_code,res.headers)
    data=res.json()
    print("data:",data)
    access_token=data.get("access_token")
    if access_token is None:
        return None
    else:
        print("get access token successfully : ",access_token)
        return access_token

@app.route("/line/login/callback")
def login_callback():
    print("login callback args:",request.args)
    if request.args.get('error'):
        print('login failed. error:',request.args.get('error_description'))
        return """
        <!doctype html>
        <html>
            <body>
                <h1> login failure</h1>
                <p>error : {0}</p>
            </body>
        </html>
        """.format(request.args.get('error_description'))
 
#    elif request.args.get("friendship_status_changed") is "true":
    code=request.args.get("code")
    state=request.args.get("state")
    print("code",code,"state",state,type(state),type(LINE_OAUTH_STATE))
    if state != LINE_OAUTH_STATE:
        print("state doesn't matched",state," : ",LINE_OAUTH_STATE)
        return """
        <!doctype html>
        <html>
            <body>
                <h1> login failure</h1>
            </body>
        </html>
        """
    else:
        access_token=get_line_access_token(code)
        print("success to get access_token : ",access_token)
        profile=get_profile(access_token)
        print("get_profile",profile)
        displayName=profile.get("displayName")
        print("displayName",displayName)
        session['user']=displayName
        access_tokens[session['user']]=access_token
        ic(access_tokens)
        return """
        <!doctype html>
        <html>
            <body>
                <h1> login successed</h1>
                <p>user name:{0}</p>
            </body>
        </html>
        """.format(displayName)
#    return """ <!doctype html> <html> <body> <h1> login failure</h1> </body> </html> """

@app.route("/line/logout")
def logout():
    headers={"Content-Type":"application/x-www-form-urlencoded"}
    url="https://api.line.me/oauth2/v2.1/revoke"
    data={
        "access_token":access_tokens[session['user']],
        "client_id":LINE_LOGIN_CHANNEL_ID,
        "client_secret":LINE_LOGIN_CHANNEL_SECRET
    }
    res=requests.get(url,headers=headers,json=data)
    if res.status_code is not 200:
        print("logout failure",res.status_code)
        return """ <!doctype html> <html> <body> <h1> logout failed</h1> </body> </html> """
    return """ <!doctype html> <html> <body> <h1> logout failed</h1> </body> </html> """

@app.route("/callback",methods=["POST"])
@app.route("/line/message/callback",methods=["POST"])
def callback():
    print("callback url called")
    signature=request.headers['X-Line-Signature']
    body=request.get_data(as_text=True)
    app.logger.info("Request body"+body)
    try:
        print("signature : ",signature,"body :",body)
        handler.handle(body,signature)
    except InvalidSignatureError:
        print("invalidSignatureError")
        abort(400)
    except Exception as e:
        print("error : ",e)
    return 'OK'

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    ret=linebot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
    print("handle_message ret",ret)

@handler.add(BeaconEvent)
def handler_beacon(event):
    print(event)
    if event.beacon.type is "":
        pass


if __name__ =="__main__":
#    app.secret_key="super secret key"
#    app.config["SESSION_TYPE"]="filesystem"
#    sess=Session()
#    sess.init_app(app)

    app.run(host="0.0.0.0",port=8080,debug=True)



