from requests import post
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler

from bot import LOGGER, dispatcher
from bot.helper.telegram_helper import button_build
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMarkup, sendMessage


def shorten_link(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    message = update.message

    if message.from_user.username:
        tag = f"@{message.from_user.username}"
    else:
        tag = message.from_user.mention_html(message.from_user.first_name)

    if len(args) > 1:
        link = args[1]
    elif reply_to is not None:
        link = reply_to.text
    else:
        link = None

    if link is not None:
        LOGGER.info(f"shorten link: {link}")
        data = {
            "url": link,
        }
        res = post("https://cleanuri.com/api/v1/shorten", data=data)
        result = res.json()

        try:
            if result["error"]:
                return sendMessage(result["error"], context.bot, update.message)
        except KeyError:
            pass

        result_url = result["result_url"]
        buttons = button_build.ButtonMaker()
        buttons.buildbutton("Shortened URL", result_url)
        button = InlineKeyboardMarkup(buttons.build_menu(1))
        msg = "URL shortened!"
        msg += f"\nOriginal: {link}"
        msg += f"\n\n<b>cc: </b> {tag}"

        sendMarkup(msg, context.bot, update.message, button)

    else:
        msg = "Send a link along with command or by replying to the link by command"

        sendMessage(msg, context.bot, update.message)


shorten_link_handler = CommandHandler(
    BotCommands.ShortenerCommand,
    shorten_link,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
    run_async=True,
)

dispatcher.add_handler(shorten_link_handler)
