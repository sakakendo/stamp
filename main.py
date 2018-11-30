import dotenv
import linebot
import os
from flask import Flask,request,abort
from linebot.exceptions import (
        InvalidSignatureError
    )
from linebot.models import (
        MessageEvent,TextMessage,TextSendMessage,
    )

# env
#print(dotenv.find_dotenv())
dotenv.load_dotenv(dotenv.find_dotenv())
CHANNEL_ACCESS_TOKEN=os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET=os.environ.get("CHANNEL_SECRET")
print(CHANNEL_ACCESS_TOKEN,CHANNEL_SECRET)
if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("env not loaded")
else:
    print("env file load successed")

app=Flask(__name__)

linebot_api=linebot.LineBotApi(CHANNEL_ACCESS_TOKEN)
handler=linebot.WebhookHandler(CHANNEL_SECRET)

@app.route("/")
def index():
    return """
    <!doctype html>
    <html>
        <head></head>
        <body>
            <h1> hello world</h1>
        </body>
    </html>
    """

@app.route("/callback",methods=["POST"])
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

if __name__ =="__main__":
    app.run(host="0.0.0.0",port=8080,debug=True)



