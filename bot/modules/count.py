from threading import Thread
from time import sleep

from telegram.ext import CommandHandler

from bot import *
from bot.helper.ext_utils.bot_utils import is_gdrive_link, is_gdtot_link, new_thread
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
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import (
    auto_delete_message,
    auto_delete_upload_message,
    deleteMessage,
    sendMessage,
)


@new_thread
def countNode(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    link = ""

    uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
    cnts = sendMessage("<b>Processing Your Link...</b>", bot, update)
    sleep(2)
    try:
        editMessage(
            f"{uname}<i> has sent the below Link for Counting</i> :-> \n <code>{link}</code>\n\n<b>User ID</b> : <code>{uid}</code>\n\n",
            cnts,
        )
    except BaseException:
        deleteMessage(context.bot, cnts)

    if reply_to is not None:
        reply_to.delete()
    if len(args) > 1:
        link = args[1]
        if update.message.from_user.username:
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
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴅʀɪᴠᴇAᴘᴘ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_appdrive:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Aᴘᴘᴅʀɪᴠᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_hubdrive:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇʜᴜʙ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ Hᴜʙᴅʀɪᴠᴇ Lɪɴᴋ:- \n<code>{link}</code>", context.bot, update
            )
            link = hubdrive_dl(link)
            deleteMessage(context.bot, msg)
            if not is_gdrive_link(link):
                return sendMessage("GDrive Link Not Found", context.bot, update)
            else:
                pass
        except DirectDownloadLinkException as e:
            return sendMessage(str(e), context.bot, update)
    if is_drivehub:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇʜᴜʙ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_kolop:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Kᴏʟᴏᴘ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n", bot, update
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_drivebuzz:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇʙᴜᴢᴢ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_gdflix:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Gᴅғʟɪx ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n", bot, update
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_drivesharer:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇsʜᴀʀᴇʀ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_drivebit:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇʙɪᴛ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_drivelink:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇʟɪɴᴋ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_driveace:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇᴀᴄᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_drivepro:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇᴘʀᴏ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_katdrive:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Kᴀᴛᴅʀɪᴠᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_drivefire:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Dʀɪᴠᴇғɪʀᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_gadrive:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Gᴀᴅʀɪᴠᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_jiodrive:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Jɪᴏᴅʀɪᴠᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_sharerpw:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ Sʜᴀʀᴇʀᴘᴡ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n",
                bot,
                update,
            )
            sleep(1)
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
            return sendMessage(str(e), context.bot, update)
    if is_gdtot:
        try:
            msg2 = sendMessage(
                f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ GᴅTᴏT ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n", bot, update
            )
            sleep(1)
            msg = sendMessage(
                f"Pʀᴏᴄᴇssɪɴɢ GᴅTᴏT Lɪɴᴋ:-\n<code>{link}</code>", context.bot, update
            )
            link = gdtot(link)
            deleteMessage(context.bot, msg)
        except DirectDownloadLinkException as e:
            return sendMessage(str(e), context.bot, update)
    if is_gdrive_link(link):
        msg2 = sendMessage(
            f"ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ɢᴅʀɪᴠᴇ ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ғᴏʀ ᴄᴏᴜɴᴛɪɴɢ\n", bot, update
        )
        sleep(1)
        msg = sendMessage(f"Counting: <code>{link}</code>", context.bot, update)
        gd = GoogleDriveHelper()
        result = gd.count(link)
        deleteMessage(context.bot, msg)
        cc = f"\n\n<b>Counted By: </b>{tag}"
        msg = sendMessage(result + cc, context.bot, update)
        Thread(
            target=auto_delete_upload_message, args=(context.bot, update.message, msg)
        ).start()
        if is_gdtot:
            gd.deletefile(link)
        if is_appdrive:
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
    else:
        msg = sendMessage(
            "Sᴇɴᴅ Gᴅʀɪᴠᴇ/Gᴅᴛᴏᴛ/Aᴘᴘᴅʀɪᴠᴇ/Dʀɪᴠᴇᴀᴘᴘ/Dʀɪᴠᴇʜᴜʙ/Hᴜʙᴅʀɪᴠᴇ/Kᴏʟᴏᴘ/Dʀɪᴠᴇʙᴜᴢᴢ/Gᴅғʟɪx/Dʀɪᴠᴇsʜᴀʀᴇʀ/Dʀɪᴠᴇʙɪᴛ/Kᴀᴛᴅʀɪᴠᴇ/Dʀɪᴠᴇғɪʀᴇ/Dʀɪᴠᴇʟɪɴᴋ/Sʜᴀʀᴇʀ.ᴘᴡ/Gᴀᴅʀɪᴠᴇ/Jɪᴏᴅʀɪᴠᴇ/Dʀɪᴠᴇᴘʀᴏ/Dʀɪᴠᴇᴀᴄᴇ Lɪɴᴋ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴘʀᴏᴘᴇʀ Cᴏᴍᴍᴀɴᴅ ᴏʀ ʙʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴛʜᴇ ʟɪɴᴋ ʙʏ Cᴏᴍᴍᴀɴᴅ",
            context.bot,
            update,
        )
        Thread(
            target=auto_delete_message, args=(context.bot, update.message, msg)
        ).start()

        Thread(target=auto_delete_message, args=(bot, update.message, msg2)).start()


count_handler = CommandHandler(
    BotCommands.CountCommand,
    countNode,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
    run_async=True,
)

dispatcher.add_handler(count_handler)
