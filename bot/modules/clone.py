import random
import string
import time
from threading import Thread

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler

from bot import (
    AUTO_DELETE_UPLOAD_MESSAGE_DURATION,
    BOT_PM,
    CHANNEL_USERNAME,
    CLONE_LIMIT,
    FSUB,
    FSUB_CHANNEL_ID,
    LOGGER,
    MIRROR_LOGS,
    STOP_DUPLICATE,
    Interval,
    bot,
    dispatcher,
    download_dict,
    download_dict_lock,
)
from bot.helper.ext_utils.bot_utils import (
    get_readable_file_size,
    is_gdrive_link,
    is_gdtot_link,
    new_thread,
)
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.mirror_utils.download_utils.direct_link_generator import (
    appdrive,
    drivebuzz_dl,
    drivefire_dl,
    gadrive_dl,
    gdtot,
    hubdrive_dl,
    jiodrive_dl,
    katdrive_dl,
    kolop_dl,
    sharerpw_dl,
)
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import *


@new_thread
def cloneNode(update, context, multi=0):
    if AUTO_DELETE_UPLOAD_MESSAGE_DURATION != -1:
        reply_to = update.message.reply_to_message
        if reply_to is not None:
            reply_to.delete()
    if FSUB:
        try:
            uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
            user = bot.get_chat_member(
                f"{FSUB_CHANNEL_ID}", update.message.from_user.id
            )
            LOGGER.error(user.status)
            if user.status not in ("member", "creator", "administrator"):
                buttons = ButtonMaker()
                buttons.buildbutton(
                    "Click Here To Join Updates Channel",
                    f"https://t.me/{CHANNEL_USERNAME}",
                )
                reply_markup = InlineKeyboardMarkup(buttons.build_menu(1))
                message = sendMarkup(
                    str(
                        f"️<b>Dear {uname}, You haven't join our Updates Channel yet.</b>\n\nKindly Join @{CHANNEL_USERNAME} To Use Bots. "
                    ),
                    bot,
                    update,
                    reply_markup,
                )
                Thread(
                    target=auto_delete_upload_message,
                    args=(bot, update.message, message),
                ).start()
                return
        except BaseException:
            pass
    if BOT_PM:
        try:
            msg1 = f"ᴀᴅᴅᴇᴅ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛᴇᴅ ʟɪɴᴋ ᴛᴏ ᴄʟᴏɴᴇ!\n"
            send = bot.sendMessage(
                update.message.from_user.id,
                text=msg1,
            )
            send.delete()
        except Exception as e:
            LOGGER.warning(e)
            bot_d = bot.get_me()
            b_uname = bot_d.username
            uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
            channel = CHANNEL_USERNAME
            botstart = f"http://t.me/{b_uname}"
            keyboard = [
                [InlineKeyboardButton("Click Here to Start Me", url=f"{botstart}")],
                [
                    InlineKeyboardButton(
                        "Join our Updates Channel", url=f"t.me/{channel}"
                    )
                ],
            ]
            message = sendMarkup(
                f"Dear {uname},\n\n<b>I found that you haven't started me in PM (Private Chat) yet.</b>\n\nFrom now on i will give link and leeched files in PM and log channel only.",
                bot,
                update,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            Thread(
                target=auto_delete_message, args=(bot, update.message, message)
            ).start()
            return
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    link = ""
    if len(args) > 1:
        link = args[1]
        if link.isdigit():
            multi = int(link)
            link = ""
        elif update.message.from_user.username:
            tag = f"@{update.message.from_user.username}"
        else:
            tag = update.message.from_user.mention_html(
                update.message.from_user.first_name
            )
    elif reply_to is not None:
        if len(link) == 0:
            link = reply_to.text
        if reply_to.from_user.username:
            tag = f"@{reply_to.from_user.username}"
        else:
            tag = reply_to.from_user.mention_html(reply_to.from_user.first_name)

    uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
    clns = sendMessage("<b>Processing Your Link...</b>", bot, update)
    time.sleep(2)
    try:
        editMessage(
            f"{uname}<i> has sent the below Link for Cloning</i> :-> \n <code>{link}</code>\n\n<b>User ID</b> : <code>{uid}</code>\n\n",
            clns,
        )
    except BaseException:
        deleteMessage(context.bot, clns)

    is_gdtot = is_gdtot_link(link)
    is_driveapp = True if "driveapp" in link else False
    is_appdrive = True if "appdrive" in link else False
    is_hubdrive = True if "hubdrive" in link else False
    is_drivehub = True if "drivehub" in link else False
    is_kolop = True if "kolop" in link else False
    is_drivebuzz = True if "drivebuzz" in link else False
    is_gdflix = True if "gdflix" in link else False
    is_drivesharer = True if "drivesharer" in link else False
    is_drivebit = True if "drivebit" in link else False
    is_drivelink = True if "drivelink" in link else False
    is_driveace = True if "driveace" in link else False
    is_drivepro = True if "drivepro" in link else False
    is_katdrive = True if "katdrive" in link else False
    is_gadrive = True if "gadrive" in link else False
    is_jiodrive = True if "jiodrive" in link else False
    is_drivefire = True if "drivefire" in link else False
    is_sharerpw = True if "sharer.pw" in link else False

    if is_driveapp:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴅʀɪᴠᴇAᴘᴘ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ ᴅʀɪᴠᴇAᴘᴘ Lɪɴᴋ:-\n<code>{link}</code>", context.bot, update
            )
            link = appdrive(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_appdrive:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Aᴘᴘᴅʀɪᴠᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Aᴘᴘᴅʀɪᴠᴇ Lɪɴᴋ:- \n<code>{link}</code>", context.bot, update
            )
            link = appdrive(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_hubdrive:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇʜᴜʙ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Dʀɪᴠᴇʜᴜʙ Lɪɴᴋ:- \n<code>{link}</code>", context.bot, update
            )
            link = hubdrive_dl(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_drivehub:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇʜᴜʙ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Dʀɪᴠᴇʜᴜʙ Lɪɴᴋ:- \n<code>{link}</code>", context.bot, update
            )
            link = appdrive(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_kolop:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Kᴏʟᴏᴘ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Kᴏʟᴏᴘ Lɪɴᴋ:- \n<code>{link}</code>", context.bot, update
            )
            link = kolop_dl(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_drivebuzz:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇʙᴜᴢᴢ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n",
                bot,
                update,
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Dʀɪᴠᴇʙᴜᴢᴢ Lɪɴᴋ:- \n<code>{link}</code>",
                context.bot,
                update,
            )
            link = drivebuzz_dl(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_gdflix:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Gᴅғʟɪx ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Gᴅғʟɪx Lɪɴᴋ:- \n<code>{link}</code>", context.bot, update
            )
            link = appdrive(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_drivesharer:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇsʜᴀʀᴇʀ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n",
                bot,
                update,
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Dʀɪᴠᴇsʜᴀʀᴇʀ Lɪɴᴋ:- \n<code>{link}</code>",
                context.bot,
                update,
            )
            link = appdrive(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_drivebit:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇʙɪᴛ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Dʀɪᴠᴇʙɪᴛ Lɪɴᴋ:- \n<code>{link}</code>", context.bot, update
            )
            link = appdrive(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_drivelink:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇʟɪɴᴋ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n",
                bot,
                update,
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Dʀɪᴠᴇʟɪɴᴋ Lɪɴᴋ:- \n<code>{link}</code>",
                context.bot,
                update,
            )
            link = appdrive(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_driveace:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇᴀᴄᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n",
                bot,
                update,
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Dʀɪᴠᴇᴀᴄᴇ Lɪɴᴋ:- \n<code>{link}</code>",
                context.bot,
                update,
            )
            link = appdrive(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_drivepro:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇᴘʀᴏ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n",
                bot,
                update,
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Dʀɪᴠᴇᴘʀᴏ Lɪɴᴋ:- \n<code>{link}</code>",
                context.bot,
                update,
            )
            link = appdrive(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_katdrive:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Kᴀᴛᴅʀɪᴠᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Kᴀᴛᴅʀɪᴠᴇ Lɪɴᴋ:- \n<code>{link}</code>", context.bot, update
            )
            link = katdrive_dl(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_gadrive:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Gᴀᴅʀɪᴠᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n",
                bot,
                update,
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Gᴀᴅʀɪᴠᴇ Lɪɴᴋ:- \n<code>{link}</code>",
                context.bot,
                update,
            )
            link = gadrive_dl(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_jiodrive:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Jɪᴏᴅʀɪᴠᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n",
                bot,
                update,
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Jɪᴏᴅʀɪᴠᴇ Lɪɴᴋ:- \n<code>{link}</code>",
                context.bot,
                update,
            )
            link = jiodrive_dl(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_drivefire:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇғɪʀᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n",
                bot,
                update,
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Dʀɪᴠᴇғɪʀᴇ Lɪɴᴋ:- \n<code>{link}</code>",
                context.bot,
                update,
            )
            link = drivefire_dl(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_sharerpw:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Sʜᴀʀᴇʀᴘᴡ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Sʜᴀʀᴇʀᴘᴡ Lɪɴᴋ:- \n<code>{link}</code>", context.bot, update
            )
            link = sharerpw_dl(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_gdtot:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ GᴅTᴏT ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
            )
            time.sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ GᴅTᴏT Lɪɴᴋ:-\n<code>{link}</code>", context.bot, update
            )
            link = gdtot(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:

            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    if is_gdrive_link(link):
        msg2 = sendMessage(
            f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ɢᴅʀɪᴠᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄʟᴏɴɪɴɢ\n", bot, update
        )
        time.sleep(1)
        msg = sendMessage(
            f"Pʀᴏᴄᴇssɪɴɢ Gᴅʀɪᴠᴇ Lɪɴᴋ:-\n<code>{link}</code>", context.bot, update
        )
        gd = GoogleDriveHelper()
        res, size, name, files = gd.helper(link)
        if res != "":
            return sendMessage(res, context.bot, update)
        if STOP_DUPLICATE:
            LOGGER.info("Checking File/Folder if already in Drive...")
            smsg, button = gd.drive_list(name, True, True)
            if smsg:
                msg3 = "File/Folder is already available in Drive.\nHere are the search results:"
                return sendMarkup(msg3, context.bot, update, button)
        if CLONE_LIMIT is not None:
            LOGGER.info("Checking File/Folder Size...")
            if size > CLONE_LIMIT * 1024**3:
                msg2 = f"Failed, Clone limit is {CLONE_LIMIT}GB.\nYour File/Folder size is {get_readable_file_size(size)}."
                return sendMessage(msg2, context.bot, update)

        if multi > 1:
            time.sleep(1)
            nextmsg = type(
                "nextmsg",
                (object,),
                {
                    "chat_id": message.chat_id,
                    "message_id": message.reply_to_message.message_id + 1,
                },
            )
            nextmsg = sendMessage(args[0], context.bot, nextmsg)
            nextmsg.from_user.id = message.from_user.id
            multi -= 1
            time.sleep(1)
            Thread(target=_clone, args=(nextmsg, context.bot, multi)).start()

        if files <= 5:
            msg = sendMessage(f"Cloning: <code>{link}</code>", context.bot, update)
            result, button = gd.clone(link)
            deleteMessage(context.bot, msg)
        else:
            drive = GoogleDriveHelper(name)
            gid = "".join(
                random.SystemRandom().choices(
                    string.ascii_letters + string.digits, k=12
                )
            )
            clone_status = CloneStatus(drive, size, update, gid)
            LOGGER.info(f"Cloning Done: {name}")
            with download_dict_lock:
                download_dict[update.message.message_id] = clone_status
            sendStatusMessage(update, context.bot)
            result, button = drive.clone(link)
            with download_dict_lock:
                del download_dict[update.message.message_id]
                count = len(download_dict)
            try:
                if count == 0:
                    Interval[0].cancel()
                    del Interval[0]
                    delete_all_messages()
                else:
                    update_all_messages()
            except IndexError:
                pass
        cc = f"\n\n<b>#Cloned By: </b>{tag}"
        if button in ["cancelled", ""]:
            sendMessage(f"{tag} {result}", context.bot, update)
        else:
            if AUTO_DELETE_UPLOAD_MESSAGE_DURATION != -1:
                auto_delete_message2 = int(AUTO_DELETE_UPLOAD_MESSAGE_DURATION / 60)
                if update.message.chat.type == "private":
                    warnmsg = ""
                else:
                    warnmsg = f"\n<b>This message will be deleted in <i>{auto_delete_message2} minutes</i> from this group.</b>\n"
        if BOT_PM and update.message.chat.type != "private":
            pmwarn = f"\n<b>I have sent links in PM.</b>\n"
        elif update.message.chat.type == "private":
            pmwarn = ""
        else:
            pmwarn = ""
        uploadmsg = sendMarkup(
            result + cc + pmwarn + warnmsg, context.bot, update, button
        )
        Thread(
            target=auto_delete_upload_message, args=(bot, update.message, uploadmsg)
        ).start()
        if is_gdtot:
            gd.deletefile(link)
        elif is_appdrive:
            if link.get("link_type") == "login":
                LOGGER.info(f"Deleting: {link}")
                gd.deleteFile(link)
        if is_driveapp:
            if link.get("link_type") == "login":
                LOGGER.info(f"Deleting: {link}")
                gd.deleteFile(link)
        if is_hubdrive:
            gd.deletefile(link)
        if is_drivehub:
            if link.get("link_type") == "login":
                LOGGER.info(f"Deleting: {link}")
                gd.deleteFile(link)
        if is_kolop:
            gd.deletefile(link)
        if is_drivebuzz:
            gd.deletefile(link)
        if is_gdflix:
            if link.get("link_type") == "login":
                LOGGER.info(f"Deleting: {link}")
                gd.deleteFile(link)
        if is_drivesharer:
            if link.get("link_type") == "login":
                LOGGER.info(f"Deleting: {link}")
                gd.deleteFile(link)
        if is_drivebit:
            if link.get("link_type") == "login":
                LOGGER.info(f"Deleting: {link}")
                gd.deleteFile(link)
        if is_katdrive:
            gd.deletefile(link)
        if is_drivefire:
            gd.deletefile(link)
        if is_gadrive:
            gd.deletefile(link)
        if is_jiodrive:
            gd.deletefile(link)
        if is_drivelink:
            if link.get("link_type") == "login":
                LOGGER.info(f"Deleting: {link}")
                gd.deleteFile(link)
        if is_drivepro:
            if link.get("link_type") == "login":
                LOGGER.info(f"Deleting: {link}")
                gd.deleteFile(link)
        if is_driveace:
            if link.get("link_type") == "login":
                LOGGER.info(f"Deleting: {link}")
                gd.deleteFile(link)
        if is_sharerpw:
            gd.deletefile(link)
        if MIRROR_LOGS:
            try:
                for i in MIRROR_LOGS:
                    bot.sendMessage(
                        chat_id=i,
                        text=result + cc,
                        reply_markup=button,
                        parse_mode=ParseMode.HTML,
                    )
            except Exception as e:
                LOGGER.warning(e)
            if BOT_PM and update.message.chat.type != "private":
                try:
                    bot.sendMessage(
                        update.message.from_user.id,
                        text=result,
                        reply_markup=button,
                        parse_mode=ParseMode.HTML,
                    )
                except Exception as e:
                    LOGGER.warning(e)
                    return
    else:
        mesg = sendMessage(
            "Sᴇɴᴅ Gᴅʀɪᴠᴇ/Gᴅᴛᴏᴛ/Aᴘᴘᴅʀɪᴠᴇ/Dʀɪᴠᴇᴀᴘᴘ/Dʀɪᴠᴇʜᴜʙ/Hᴜʙᴅʀɪᴠᴇ/Kᴏʟᴏᴘ/Dʀɪᴠᴇʙᴜᴢᴢ/Gᴅғʟɪx/Dʀɪᴠᴇsʜᴀʀᴇʀ/Dʀɪᴠᴇʙɪᴛ/Kᴀᴛᴅʀɪᴠᴇ/Dʀɪᴠᴇғɪʀᴇ/Dʀɪᴠᴇʟɪɴᴋ/Sʜᴀʀᴇʀ.ᴘᴡ/Gᴀᴅʀɪᴠᴇ/Jɪᴏᴅʀɪᴠᴇ/Dʀɪᴠᴇᴀᴄᴇ/Dʀɪᴠᴇᴘʀᴏ Lɪɴᴋ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴘʀᴏᴘᴇʀ Cᴏᴍᴍᴀɴᴅ ᴏʀ ʙʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴛʜᴇ ʟɪɴᴋ ʙʏ Cᴏᴍᴍᴀɴᴅ",
            bot,
            update,
        )

        Thread(target=auto_delete_message, args=(bot, update.message, mesg)).start()
        Thread(target=auto_delete_message, args=(bot, update.message, msg2)).start()


clone_handler = CommandHandler(
    BotCommands.CloneCommand,
    cloneNode,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
    run_async=True,
)
dispatcher.add_handler(clone_handler)
