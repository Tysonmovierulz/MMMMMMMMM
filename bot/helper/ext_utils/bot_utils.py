import shutil
import time
from math import ceil
from re import findall, match
from threading import Event, Thread
from urllib.request import urlopen

import psutil
from psutil import cpu_percent, disk_usage, virtual_memory
from requests import head as rhead
from telegram import InlineKeyboardMarkup
from telegram.error import RetryAfter
from telegram.ext import CallbackQueryHandler
from telegram.message import Message
from telegram.update import Update

from bot import *
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker

MAGNET_REGEX = r"magnet:\?xt=urn:btih:[a-zA-Z0-9]*"

URL_REGEX = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+"

COUNT = 0
PAGE_NO = 1

FINISHED_PROGRESS_STR = "█"
UNFINISHED_PROGRESS_STR = "░"


class MirrorStatus:
    STATUS_UPLOADING = "Uploading...📤"
    STATUS_DOWNLOADING = "Downloading...📥"
    STATUS_CLONING = "Cloning...♻️"
    STATUS_WAITING = "Queued...💤"
    STATUS_FAILED = "Failed 🚫. Cleaning Download..."
    STATUS_PAUSE = "Paused...⛔️"
    STATUS_ARCHIVING = "Archiving...🔐"
    STATUS_EXTRACTING = "Extracting...📂"
    STATUS_SPLITTING = "Splitting...✂️"
    STATUS_CHECKING = "CheckingUp...📝"
    STATUS_SEEDING = "Seeding...🌧"


SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]
PROGRESS_MAX_SIZE = 100 // 8


class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = Event()
        thread = Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime = time() + self.interval
        while not self.stopEvent.wait(nextTime - time()):
            nextTime += self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()


def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return "0B"
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f"{round(size_in_bytes, 2)}{SIZE_UNITS[index]}"
    except IndexError:
        return "File too large"


def getDownloadByGid(gid):
    with download_dict_lock:
        for dl in list(download_dict.values()):
            status = dl.status()
            if (
                status
                not in [
                    MirrorStatus.STATUS_ARCHIVING,
                    MirrorStatus.STATUS_EXTRACTING,
                    MirrorStatus.STATUS_SPLITTING,
                ]
                and dl.gid() == gid
            ):
                return dl
    return None


def getAllDownload():
    with download_dict_lock:
        for dl in list(download_dict.values()):
            status = dl.status()
            if (
                status
                not in [
                    MirrorStatus.STATUS_ARCHIVING,
                    MirrorStatus.STATUS_EXTRACTING,
                    MirrorStatus.STATUS_SPLITTING,
                ]
                and dl
            ):
                if req_status == "down" and (
                    status
                    not in [
                        MirrorStatus.STATUS_SEEDING,
                        MirrorStatus.STATUS_UPLOADING,
                        MirrorStatus.STATUS_CLONING,
                    ]
                ):
                    return dl
                elif req_status == "up" and status == MirrorStatus.STATUS_UPLOADING:
                    return dl
                elif req_status == "clone" and status == MirrorStatus.STATUS_CLONING:
                    return dl
                elif req_status == "seed" and status == MirrorStatus.STATUS_SEEDING:
                    return dl
                elif req_status == "all":
                    return dl
    return None


def get_progress_bar_string(status):
    completed = status.processed_bytes() / 8
    total = status.size_raw() / 8
    if total == 0:
        p = 0
    else:
        p = round(completed * 100 / total)
    p = min(max(p, 0), 100)
    cFull = p // 8
    cPart = p % 8 - 1
    p_str = FINISHED_PROGRESS_STR * cFull
    if cPart >= 0:
        p_str += FINISHED_PROGRESS_STR
    p_str += UNFINISHED_PROGRESS_STR * (PROGRESS_MAX_SIZE - cFull)
    p_str = f"[{p_str}]"
    return p_str


def progress_bar(percentage):
    """Returns a progress bar for download"""
    # percentage is on the scale of 0-1
    comp = FINISHED_PROGRESS_STR
    ncomp = UNFINISHED_PROGRESS_STR
    pr = ""

    if isinstance(percentage, str):
        return "NaN"

    try:
        percentage = int(percentage)
    except BaseException:
        percentage = 0

    for i in range(1, 11):
        if i <= int(percentage / 10):
            pr += comp
        else:
            pr += ncomp
    return pr


def sendMessage(text: str, bot, update: Update):
    try:
        return bot.send_message(
            update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            text=text,
            allow_sending_without_reply=True,
            parse_mode="HTMl",
            disable_web_page_preview=True,
        )
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return sendMessage(text, bot, update)
    except Exception as e:
        LOGGER.error(str(e))
        return


def sendMarkup(text: str, bot, update: Update, reply_markup: InlineKeyboardMarkup):
    try:
        return bot.send_message(
            update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            text=text,
            reply_markup=reply_markup,
            allow_sending_without_reply=True,
            parse_mode="HTMl",
            disable_web_page_preview=True,
        )
    except RetryAfter as r:
        LOGGER.error(str(r))
        sleep(r.retry_after)
        return sendMarkup(text, bot, update, reply_markup)
    except Exception as e:
        LOGGER.error(str(e))


def editMessage(text: str, message: Message, reply_markup=None):
    try:
        bot.edit_message_text(
            text=text,
            message_id=message.message_id,
            chat_id=message.chat.id,
            reply_markup=reply_markup,
            parse_mode="HTMl",
            disable_web_page_preview=True,
        )
    except RetryAfter as r:
        LOGGER.warning(str(r))
        sleep(r.retry_after * 1.5)
        return editMessage(text, message, reply_markup)
    except Exception as e:
        LOGGER.error(str(e))
        return


def deleteMessage(bot, message: Message):
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        LOGGER.error(str(e))


def auto_delete_message(bot, cmd_message: Message, bot_message: Message):
    if AUTO_DELETE_MESSAGE_DURATION != -1:
        sleep(AUTO_DELETE_MESSAGE_DURATION)
        try:
            # Skip if None is passed meaning we don't want to delete bot xor
            # cmd message
            deleteMessage(bot, cmd_message)
            deleteMessage(bot, bot_message)
        except AttributeError:
            pass


def delete_all_messages():
    with status_reply_dict_lock:
        for message in list(status_reply_dict.values()):
            try:
                deleteMessage(bot, message)
                del status_reply_dict[message.chat.id]
            except Exception as e:
                LOGGER.error(str(e))


def update_all_messages():
    msg, buttons = get_readable_message()
    with status_reply_dict_lock:
        for chat_id in list(status_reply_dict.keys()):
            if status_reply_dict[chat_id] and msg != status_reply_dict[chat_id].text:
                if buttons == "":
                    editMessage(msg, status_reply_dict[chat_id])
                else:
                    editMessage(msg, status_reply_dict[chat_id], buttons)
                status_reply_dict[chat_id].text = msg


def sendStatusMessage(msg, bot):
    if len(Interval) == 0:
        Interval.append(
            setInterval(DOWNLOAD_STATUS_UPDATE_INTERVAL, update_all_messages)
        )
    progress, buttons = get_readable_message()
    with status_reply_dict_lock:
        if msg.message.chat.id in list(status_reply_dict):
            try:
                message = status_reply_dict[msg.message.chat.id]
                deleteMessage(bot, message)
                del status_reply_dict[msg.message.chat.id]
            except Exception as e:
                LOGGER.error(str(e))
                del status_reply_dict[msg.message.chat.id]
        if buttons == "":
            message = sendMessage(progress, bot, msg)
        else:
            message = sendMarkup(progress, bot, msg, buttons)
        status_reply_dict[msg.message.chat.id] = message


def get_readable_message():
    with download_dict_lock:
        msg = ""
        dlspeed_bytes = 0
        num_active = 0
        num_upload = 0
        num_seeding = 0
        tasks = 0
        if STATUS_LIMIT is not None:
            tasks = len(download_dict)
            global pages
            pages = ceil(tasks / STATUS_LIMIT)
            if PAGE_NO > pages and pages != 0:
                globals()["COUNT"] -= STATUS_LIMIT
                globals()["PAGE_NO"] -= 1
        for stats in list(download_dict.values()):
            if stats.status() == MirrorStatus.STATUS_DOWNLOADING:
                num_active += 1
            if stats.status() == MirrorStatus.STATUS_UPLOADING:
                num_upload += 1
            if stats.status() == MirrorStatus.STATUS_SEEDING:
                num_seeding += 1
        msg = f"<b>Total Tasks : {tasks}</b>\n\n<b>DLs :{num_active} || ULs :{num_upload} || Seeding :{num_seeding}</b>\n"
        for index, download in enumerate(list(download_dict.values())[COUNT:], start=1):
            msg += f"\n\n<b>Name:</b> <code>{download.name()}</code>"
            msg += f"\n<b>Status:</b> <i>{download.status()}</i>"
            if download.status() not in [
                MirrorStatus.STATUS_ARCHIVING,
                MirrorStatus.STATUS_EXTRACTING,
                MirrorStatus.STATUS_SPLITTING,
                MirrorStatus.STATUS_SEEDING,
            ]:
                msg += f"\n<code>{get_progress_bar_string(download)}</code> {download.progress()}"
                if download.status() == MirrorStatus.STATUS_CLONING:
                    msg += f"\n<b> Cloned:</b> <code>{get_readable_file_size(download.processed_bytes())}</code> of <code>{download.size()}</code> \n"
                elif download.status() == MirrorStatus.STATUS_UPLOADING:
                    msg += f"\n<b>Uploaded:</b> <code>{get_readable_file_size(download.processed_bytes())}</code> of <code>{download.size()}</code> \n"
                else:
                    msg += f"\n<b>Downloaded:</b> <code>{get_readable_file_size(download.processed_bytes())}</code> of <code>{download.size()}</code> \n"
                # msg += f"<b>Elapsed:</b>{time() - self.message.date.timestamp()}"
                msg += f"<b>Speed:</b> <code>{download.speed()}</code> | <b>ETA:</b> <code>{download.eta()}</code>"
                try:
                    msg += (
                        f"\n<b>Engine:</b> Aria2 | <b> 🌱 Seeders :</b> {download.aria_download().num_seeders}"
                        f"<b>🍀 Peers :</b> {download.aria_download().connections}"
                    )
                except BaseException:
                    pass
                try:
                    msg += f"\n<b>Engine:</b> qBittorrent | <b>🌍:</b> {download.torrent_info().num_leechs} | <b>🌱:</b> {download.torrent_info().num_seeds}"
                except BaseException:
                    pass
                try:
                    if download.status() == MirrorStatus.STATUS_CLONING:
                        msg += f"\n<b>Engine:</b> AutoRClone"
                except BaseException:
                    pass
                reply_to = download.message.reply_to_message
                if reply_to:
                    msg += f"\n<b>Source Message:</b> <a href='https://t.me/c/{str(download.message.chat.id)[4:]}/{reply_to.message_id}'>Link</a>"
                else:
                    msg += f"\n<b>Source Message:</b> <a href='https://t.me/c/{str(download.message.chat.id)[4:]}/{download.message.message_id}'>Link</a>"
                msg += f"\n<b>User:</b> <b>{download.message.from_user.first_name}</b> (<code>{download.message.from_user.id}</code>)"
                msg += f"\n<b>To Stop:</b> <code>/{BotCommands.CancelMirror} {download.gid()}</code>\n"
                msg += "▬ ▬ ▬ ▬ ▬ ▬ ▬\n"
            elif download.status() == MirrorStatus.STATUS_SEEDING:
                msg += f"\n<b>Size: </b>{download.size()}"
                msg += f"\n<b>Speed: </b>{get_readable_file_size(download.torrent_info().upspeed)}/s"
                msg += f" | <b>Uploaded: </b>{get_readable_file_size(download.torrent_info().uploaded)}"
                msg += f"\n<b>Ratio: </b>{round(download.torrent_info().ratio, 3)}"
                msg += f" | <b>Time: </b>{get_readable_time(download.torrent_info().seeding_time)}"
                msg += (
                    f"\n<code>/{BotCommands.CancelMirror} {download.gid()}</code>\n\n"
                )
                msg += "▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            else:
                msg += f"\n<b>Size: </b>{download.size()}"
            msg += "\n"
            if STATUS_LIMIT is not None and index == STATUS_LIMIT:
                break
        currentTime = get_readable_time(time() - botStartTime)
        bmsg = f"<b>CPU:</b> {cpu_percent()}% | <b>FREE:</b> {get_readable_file_size(disk_usage(DOWNLOAD_DIR).free)}"
        dlspeed_bytes = 0
        upspeed_bytes = 0
        for download in list(download_dict.values()):
            spd = download.speed()
            if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                if "K" in spd:
                    dlspeed_bytes += float(spd.split("K")[0]) * 1024
                elif "M" in spd:
                    dlspeed_bytes += float(spd.split("M")[0]) * 1048576
            elif download.status() == MirrorStatus.STATUS_UPLOADING:
                if "KB/s" in spd:
                    upspeed_bytes += float(spd.split("K")[0]) * 1024
                elif "MB/s" in spd:
                    upspeed_bytes += float(spd.split("M")[0]) * 1048576
        dlspeed = get_readable_file_size(dlspeed_bytes)
        ulspeed = get_readable_file_size(upspeed_bytes)
        recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
        sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
        bmsg += f"\n<b>RAM:</b> {virtual_memory().percent}% | <b>UPTIME:</b> {currentTime}\n"
        bmsg += f"<b>🔻 DL:</b> {dlspeed}/s | {recv}\n"
        bmsg += f"<b>🔺 UL:</b> {ulspeed}/s | {sent}\n"
        buttons = ButtonMaker()
        buttons.sbutton("Refresh", str(ONE))
        buttons.sbutton("Stats", str(THREE))
        buttons.sbutton("Close", str(TWO))
        sbutton = InlineKeyboardMarkup(buttons.build_menu(3))
        if STATUS_LIMIT is not None and tasks > STATUS_LIMIT:
            msg += f"\n<b>Page:</b> <code>{PAGE_NO}</code>/<code>{pages}</code>\n\n"
            buttons = ButtonMaker()
            buttons.sbutton("Previous Page", "pre")
            buttons.sbutton("Refresh", str(ONE))
            buttons.sbutton("Next Page", "nex")
            buttons.sbutton("Stats", str(THREE))
            buttons.sbutton("Close", str(TWO))
            button = InlineKeyboardMarkup(buttons.build_menu(3))
            return msg + bmsg, button
        return msg + bmsg, sbutton


def turn(data):
    try:
        with download_dict_lock:
            global COUNT, PAGE_NO
            if data[1] == "nex":
                if PAGE_NO == pages:
                    COUNT = 0
                    PAGE_NO = 1
                else:
                    COUNT += STATUS_LIMIT
                    PAGE_NO += 1
            elif data[1] == "pre":
                if PAGE_NO == 1:
                    COUNT = STATUS_LIMIT * (pages - 1)
                    PAGE_NO = pages
                else:
                    COUNT -= STATUS_LIMIT
                    PAGE_NO -= 1
        return True
    except BaseException:
        return False


def get_readable_time(seconds: int) -> str:
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f"{days}d"
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f"{hours}h"
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f"{minutes}m"
    seconds = int(seconds)
    result += f"{seconds}s"
    return result


def is_url(url: str):
    url = findall(URL_REGEX, url)
    return bool(url)


def is_gdrive_link(url: str):
    return "drive.google.com" in url


def is_gdtot_link(url: str):
    url = match(r"https?://.*\.gdtot\.\S+", url)
    return bool(url)


def is_appdrive_link(url: str):
    url = match(r"https?://(?:\S*\.)?(?:appdrive|driveapp)\.in/\S+", url)
    return bool(url)


def is_mega_link(url: str):
    return "mega.nz" in url or "mega.co.nz" in url


def get_mega_link_type(url: str):
    if "folder" in url:
        return "folder"
    elif "file" in url:
        return "file"
    elif "/#F!" in url:
        return "folder"
    return "file"


def is_magnet(url: str):
    magnet = findall(MAGNET_REGEX, url)
    return bool(magnet)


def new_thread(fn):
    """To use as decorator to make a function call threaded.
    Needs import
    from threading import Thread"""

    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def get_content_type(link: str):
    try:
        res = rhead(
            link, allow_redirects=True, timeout=5, headers={"user-agent": "Wget/1.12"}
        )
        content_type = res.headers.get("content-type")
    except BaseException:

        try:
            res = urlopen(link, timeout=5)
            info = res.info()
            content_type = info.get_content_type()
        except BaseException:
            content_type = None
    return content_type


ONE, TWO, THREE = range(3)


def refresh(update, context):
    query = update.callback_query
    query.edit_message_text(text="Refreshing Status...⏳")
    sleep(2)
    update_all_messages()


def close(update, context):
    chat_id = update.effective_chat.id
    user_id = update.callback_query.from_user.id
    bot = context.bot
    query = update.callback_query
    admins = bot.get_chat_member(chat_id, user_id).status in [
        "creator",
        "administrator",
    ] or user_id in [OWNER_ID]
    if admins:
        delete_all_messages()
    else:
        query.answer(text="You Don't Have Admin Rights!", show_alert=True)


def pop_up_stats(update, context):
    query = update.callback_query
    stats = bot_sys_stats()
    query.answer(text=stats, show_alert=True)


def bot_sys_stats():
    currentTime = get_readable_time(time() - botStartTime)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage(DOWNLOAD_DIR).percent
    total, used, free = shutil.disk_usage(DOWNLOAD_DIR)
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    stats = f"""
BOT UPTIME 🕐 : {currentTime}

CPU : {progress_bar(cpu)} {cpu}%
RAM : {progress_bar(mem)} {mem}%

DISK : {progress_bar(disk)} {disk}%
TOTAL : {total}

USED : {used} || FREE : {free}
SENT : {sent} || RECV : {recv}
"""
    return stats


dispatcher.add_handler(CallbackQueryHandler(refresh, pattern="^" + str(ONE) + "$"))
dispatcher.add_handler(CallbackQueryHandler(close, pattern="^" + str(TWO) + "$"))
dispatcher.add_handler(
    CallbackQueryHandler(pop_up_stats, pattern="^" + str(THREE) + "$")
)
