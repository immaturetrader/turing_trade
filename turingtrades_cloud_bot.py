import base64
import telepot
import telegram

chat_id='-1001491623564' # GCP group id

bot_token = '1810052736:AAF_8pAew3N6IlqHRSpWBRqWzRVtwxbQMdQ'
TelegramBot = telepot.Bot(bot_token)

def send_chat_message(text):
    TelegramBot.sendMessage(chat_id=chat_id, text=text)
    return "Success"


def telegram_alert(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    send_chat_message(pubsub_message)
    return "OK"