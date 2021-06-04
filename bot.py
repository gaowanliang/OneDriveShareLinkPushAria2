from telegram.ext import Updater
REQUEST_KWARGS = {
    # "USERNAME:PASSWORD@" is optional, if you need authentication:
    'proxy_url': 'http://127.0.0.1:2334',
}

updater = Updater('',
                  request_kwargs=REQUEST_KWARGS)
dispatcher = updater.dispatcher
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update, context):
    print(update.effective_chat.id)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="你可以输入一个 xxx-my.sharepoint.com 链接，程序会自动解析文件")


def stop(update, context):
    if update.effective_chat.id == 0:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="机器人已停止")
        updater.stop()
        exit()


from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

stop_handler = CommandHandler('stop', stop)
dispatcher.add_handler(stop_handler)

updater.start_polling()
