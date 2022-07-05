import faulthandler
import logging
import socket
from json import loads as jsnloads
from os import environ
from os import path as ospath
from os import remove as osremove
from subprocess import Popen, check_output
from subprocess import run as srun
from threading import Lock, Thread
from time import sleep, time

from aria2p import API as ariaAPI
from aria2p import Client as ariaClient
from dotenv import load_dotenv
from megasdkrestclient import MegaSdkRestClient
from megasdkrestclient import errors as mega_err
from pyrogram import Client
from qbittorrentapi import Client as qbClient
from requests import get as rget
from telegram.ext import Updater as tgUpdater

faulthandler.enable()

socket.setdefaulttimeout(600)

botStartTime = time()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)

load_dotenv("config.env", override=True)


def getConfig(name: str):
    return environ[name]


try:
    NETRC_URL = getConfig("NETRC_URL")
    if len(NETRC_URL) == 0:
        raise KeyError
    try:
        res = rget(NETRC_URL)
        if res.status_code == 200:
            with open(".netrc", "wb+") as f:
                f.write(res.content)
        else:
            logging.error(f"Failed to download .netrc {res.status_code}")
    except Exception as e:
        logging.error(f"NETRC_URL: {e}")
except KeyError:
    pass
try:
    SERVER_PORT = getConfig("SERVER_PORT")
    if len(SERVER_PORT) == 0:
        raise KeyError
except KeyError:
    SERVER_PORT = 80

PORT = environ.get("PORT", SERVER_PORT)
web = Popen([f"gunicorn web.wserver:app --bind 0.0.0.0:{PORT}"], shell=True)
alive = Popen(["python3", "alive.py"])
srun(["qbittorrent-nox", "-d", "--profile=."])
if not ospath.exists(".netrc"):
    srun(["touch", ".netrc"])
srun(["cp", ".netrc", "/root/.netrc"])
srun(["chmod", "600", ".netrc"])
srun(["chmod", "+x", "aria.sh"])
a2c = Popen(["./aria.sh"], shell=True)
sleep(1)

Interval = []
DRIVES_NAMES = []
DRIVES_IDS = []
INDEX_URLS = []
ALT_INDEX_URLS = []

try:
    if bool(getConfig("_____REMOVE_THIS_LINE_____")):
        logging.error("The README.md file there to be read! Exiting now!")
        exit()
except KeyError:
    pass

aria2 = ariaAPI(
    ariaClient(
        host="http://localhost",
        port=6800,
        secret="",
    )
)


def get_client():
    return qbClient(host="localhost", port=8090)


trackers = check_output(
    [
        "curl -Ns https://raw.githubusercontent.com/XIU2/TrackersListCollection/master/all.txt https://ngosang.github.io/trackerslist/trackers_all_http.txt https://newtrackon.com/api/all | awk '$0'"
    ],
    shell=True,
).decode("utf-8")
trackerslist = set(trackers.split("\n"))
trackerslist.remove("")
trackerslist = "\n\n".join(trackerslist)
get_client().application.set_preferences({"add_trackers": f"{trackerslist}"})

DOWNLOAD_DIR = None
BOT_TOKEN = None

download_dict_lock = Lock()
status_reply_dict_lock = Lock()
# Key: update.effective_chat.id
# Value: telegram.Message
status_reply_dict = {}
# Key: update.message.message_id
# Value: An object of Status
download_dict = {}
# key: rss_title
# value: [rss_feed, last_link, last_title, filter]
rss_dict = {}

AUTHORIZED_CHATS = set()
SUDO_USERS = set()
MOD_USERS = set()
AS_DOC_USERS = set()
AS_MEDIA_USERS = set()
MIRROR_LOGS = set()
LINK_LOGS = set()
LEECH_LOG = set()
LEECH_LOG_ALT = set()
EXTENTION_FILTER = set([".torrent"])

if ospath.exists("authorized_chats.txt"):

    with open("authorized_chats.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            AUTHORIZED_CHATS.add(int(line.split()[0]))

if ospath.exists("sudo_users.txt"):
    with open("sudo_users.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            SUDO_USERS.add(int(line.split()[0]))

if ospath.exists("mod_users.txt"):
    with open("mod_users.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            MOD_USERS.add(int(line.split()[0]))
try:
    achats = getConfig("AUTHORIZED_CHATS")
    achats = achats.split(" ")
    for chats in achats:
        AUTHORIZED_CHATS.add(int(chats))
except BaseException:
    pass
try:
    schats = getConfig("SUDO_USERS")
    schats = schats.split(" ")
    for chats in schats:
        SUDO_USERS.add(int(chats))
except BaseException:
    pass

try:
    schats = getConfig("MOD_USERS")
    schats = schats.split(" ")
    for chats in schats:
        MOD_USERS.add(int(chats))
except BaseException:
    pass

if ospath.exists("logs_chat.txt"):
    with open("logs_chat.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            #    LOGGER.info(line.split())
            MIRROR_LOGS.add(int(line.split()[0]))
try:
    achats = getConfig("MIRROR_LOGS")
    achats = achats.split(" ")
    for chats in achats:
        MIRROR_LOGS.add(int(chats))
except BaseException:
    logging.warning("Mirror Logs Chat Details not provided! Proceeding Without it")

if ospath.exists("link_logs.txt"):
    with open("link_logs.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            #    LOGGER.info(line.split())
            LINK_LOGS.add(int(line.split()[0]))
try:
    achats = getConfig("LINK_LOGS")
    achats = achats.split(" ")
    for chats in achats:
        LINK_LOGS.add(int(chats))
except BaseException:
    logging.warning("LINK_LOGS Chat id not provided, Proceeding Without it")

if ospath.exists("logs_chat.txt"):
    with open("logs_chat.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            #    LOGGER.info(line.split())
            LEECH_LOG.add(int(line.split()[0]))

if ospath.exists("leech_logs.txt"):
    with open("leech_logs.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            #    LOGGER.info(line.split())
            LEECH_LOG_ALT.add(int(line.split()[0]))
try:
    achats = getConfig("LEECH_LOG")
    achats = achats.split(" ")
    for chats in achats:
        LEECH_LOG.add(int(chats))
except BaseException:
    logging.warning("Leech Log Channel ID not Provided!")
try:
    achats = getConfig("LEECH_LOG_ALT")
    achats = achats.split(" ")
    for chats in achats:
        LEECH_LOG_ALT.add(int(chats))
except BaseException:
    logging.warning("Leech Log alt Channel ID not Provided!")
try:
    fx = getConfig("EXTENTION_FILTER")
    if len(fx) > 0:
        fx = fx.split(" ")
        for x in fx:
            EXTENTION_FILTER.add(x.lower())
except BaseException:
    pass
try:
    BOT_TOKEN = getConfig("BOT_TOKEN")
    parent_id = getConfig("GDRIVE_FOLDER_ID")
    DOWNLOAD_DIR = getConfig("DOWNLOAD_DIR")
    if not DOWNLOAD_DIR.endswith("/"):
        DOWNLOAD_DIR = DOWNLOAD_DIR + "/"
    DOWNLOAD_STATUS_UPDATE_INTERVAL = int(getConfig("DOWNLOAD_STATUS_UPDATE_INTERVAL"))
    OWNER_ID = int(getConfig("OWNER_ID"))
    AUTO_DELETE_MESSAGE_DURATION = int(getConfig("AUTO_DELETE_MESSAGE_DURATION"))
    AUTO_DELETE_UPLOAD_MESSAGE_DURATION = int(
        getConfig("AUTO_DELETE_UPLOAD_MESSAGE_DURATION")
    )
    TELEGRAM_API = getConfig("TELEGRAM_API")
    TELEGRAM_HASH = getConfig("TELEGRAM_HASH")
except KeyError as e:
    LOGGER.error("One or more env variables missing! Exiting now")
    LOGGER.error(str(e) + " Env Variable Is Missing.")
    exit(1)

LOGGER.info("Generating BOT_STRING_SESSION")
app = Client(
    "pyrogram",
    api_id=int(TELEGRAM_API),
    api_hash=TELEGRAM_HASH,
    bot_token=BOT_TOKEN,
    parse_mode="html",
    no_updates=True,
)

try:
    USER_STRING_SESSION = getConfig("USER_STRING_SESSION")
    if len(USER_STRING_SESSION) == 0:
        raise KeyError
    rss_session = Client(
        name="rss_session",
        api_id=int(TELEGRAM_API),
        api_hash=TELEGRAM_HASH,
        session_string=USER_STRING_SESSION,
        parse_mode="html",
    )
except BaseException:
    USER_STRING_SESSION = None
    rss_session = None


def aria2c_init():
    try:
        logging.info("Initializing Aria2c")
        link = (
            "https://releases.ubuntu.com/21.10/ubuntu-21.10-desktop-amd64.iso.torrent"
        )
        dire = DOWNLOAD_DIR.rstrip("/")
        aria2.add_uris([link], {"dir": dire})
        sleep(3)
        downloads = aria2.get_downloads()
        sleep(30)
        for download in downloads:
            aria2.remove([download], force=True, files=True)
    except Exception as e:
        logging.error(f"Aria2c initializing error: {e}")


if not ospath.isfile(".restartmsg"):
    sleep(1)
    Thread(target=aria2c_init).start()
    sleep(1.5)

try:
    DB_URI = getConfig("DATABASE_URL")
    if len(DB_URI) == 0:
        raise KeyError
except KeyError:
    DB_URI = None
try:
    TG_SPLIT_SIZE = getConfig("TG_SPLIT_SIZE")
    if len(TG_SPLIT_SIZE) == 0 or int(TG_SPLIT_SIZE) > 2097151000:
        raise KeyError
    else:
        TG_SPLIT_SIZE = int(TG_SPLIT_SIZE)
except KeyError:
    TG_SPLIT_SIZE = 2097151000
try:
    STATUS_LIMIT = getConfig("STATUS_LIMIT")
    if len(STATUS_LIMIT) == 0:
        raise KeyError
    else:
        STATUS_LIMIT = int(STATUS_LIMIT)
except KeyError:
    STATUS_LIMIT = None
try:
    MEGAREST = getConfig("MEGAREST")
    MEGAREST = MEGAREST.lower() == "true"
except KeyError:
    MEGAREST = False
try:
    MEGA_API_KEY = getConfig("MEGA_API_KEY")
except KeyError:
    MEGA_API_KEY = None
    LOGGER.info("MEGA API KEY NOT AVAILABLE")
if MEGAREST is True:
    # Start megasdkrest binary
    Popen(["megasdkrest", "--apikey", MEGA_API_KEY])
    sleep(3)  # Wait for the mega server to start listening
    mega_client = MegaSdkRestClient("http://localhost:6090")
    try:
        MEGA_EMAIL_ID = getConfig("MEGA_EMAIL_ID")
        MEGA_PASSWORD = getConfig("MEGA_PASSWORD")
        if len(MEGA_EMAIL_ID) > 0 and len(MEGA_PASSWORD) > 0:
            try:
                mega_client.login(MEGA_EMAIL_ID, MEGA_PASSWORD)
            except mega_err.MegaSdkRestClientException as e:
                logging.error(e.message["message"])
                exit(0)
        else:
            LOGGER.info(
                "Mega API KEY provided but credentials not provided. Starting mega in anonymous mode!"
            )
            MEGA_EMAIL_ID = None
            MEGA_PASSWORD = None
    except KeyError:
        LOGGER.info(
            "Mega API KEY provided but credentials not provided. Starting mega in anonymous mode!"
        )
        MEGA_EMAIL_ID = None
        MEGA_PASSWORD = None
else:
    MEGA_EMAIL_ID = None
    MEGA_PASSWORD = None

try:
    UPTOBOX_TOKEN = getConfig("UPTOBOX_TOKEN")
    if len(UPTOBOX_TOKEN) == 0:
        raise KeyError
except KeyError:
    UPTOBOX_TOKEN = None
try:
    INDEX_URL = getConfig("INDEX_URL").rstrip("/")
    if len(INDEX_URL) == 0:
        raise KeyError
    else:
        INDEX_URLS.append(INDEX_URL)
except KeyError:
    INDEX_URL = None
    INDEX_URLS.append(None)
try:
    ALT_INDEX_URL = getConfig("ALT_INDEX_URL").rstrip("/")
    if len(ALT_INDEX_URL) == 0:
        raise KeyError
    else:
        ALT_INDEX_URLS.append(ALT_INDEX_URL)
except KeyError:
    ALT_INDEX_URL = None
    ALT_INDEX_URLS.append(None)
try:
    SEARCH_API_LINK = getConfig("SEARCH_API_LINK").rstrip("/")
    if len(SEARCH_API_LINK) == 0:
        raise KeyError
except KeyError:
    SEARCH_API_LINK = None
try:
    RSS_COMMAND = getConfig("RSS_COMMAND")
    if len(RSS_COMMAND) == 0:
        raise KeyError
except KeyError:
    RSS_COMMAND = None
try:
    TORRENT_DIRECT_LIMIT = getConfig("TORRENT_DIRECT_LIMIT")
    if len(TORRENT_DIRECT_LIMIT) == 0:
        raise KeyError
    else:
        TORRENT_DIRECT_LIMIT = float(TORRENT_DIRECT_LIMIT)
except KeyError:
    TORRENT_DIRECT_LIMIT = None
try:
    CLONE_LIMIT = getConfig("CLONE_LIMIT")
    if len(CLONE_LIMIT) == 0:
        raise KeyError
    else:
        CLONE_LIMIT = float(CLONE_LIMIT)
except KeyError:
    CLONE_LIMIT = None
try:
    MEGA_LIMIT = getConfig("MEGA_LIMIT")
    if len(MEGA_LIMIT) == 0:
        raise KeyError
    else:
        MEGA_LIMIT = float(MEGA_LIMIT)
except KeyError:
    MEGA_LIMIT = None
try:
    ZIP_UNZIP_LIMIT = getConfig("ZIP_UNZIP_LIMIT")
    if len(ZIP_UNZIP_LIMIT) == 0:
        raise KeyError
    else:
        ZIP_UNZIP_LIMIT = float(ZIP_UNZIP_LIMIT)
except KeyError:
    ZIP_UNZIP_LIMIT = None

try:
    RSS_CHAT_ID = getConfig("RSS_CHAT_ID")
    if len(RSS_CHAT_ID) == 0:
        raise KeyError
    else:
        RSS_CHAT_ID = int(RSS_CHAT_ID)
except KeyError:
    RSS_CHAT_ID = None
try:
    RSS_DELAY = getConfig("RSS_DELAY")
    if len(RSS_DELAY) == 0:
        raise KeyError
    else:
        RSS_DELAY = int(RSS_DELAY)
except KeyError:
    RSS_DELAY = 900
try:
    QB_TIMEOUT = getConfig("QB_TIMEOUT")
    if len(QB_TIMEOUT) == 0:
        raise KeyError
    else:
        QB_TIMEOUT = int(QB_TIMEOUT)
except KeyError:
    QB_TIMEOUT = None
try:
    ARIA_TIMEOUT = getConfig("ARIA_TIMEOUT")
    if len(ARIA_TIMEOUT) == 0:
        raise KeyError
    else:
        ARIA_TIMEOUT = int(ARIA_TIMEOUT)
except KeyError:
    ARIA_TIMEOUT = None
try:
    BUTTON_FOUR_NAME = getConfig("BUTTON_FOUR_NAME")
    BUTTON_FOUR_URL = getConfig("BUTTON_FOUR_URL")
    if len(BUTTON_FOUR_NAME) == 0 or len(BUTTON_FOUR_URL) == 0:
        raise KeyError
except KeyError:
    BUTTON_FOUR_NAME = None
    BUTTON_FOUR_URL = None
try:
    BUTTON_FIVE_NAME = getConfig("BUTTON_FIVE_NAME")
    BUTTON_FIVE_URL = getConfig("BUTTON_FIVE_URL")
    if len(BUTTON_FIVE_NAME) == 0 or len(BUTTON_FIVE_URL) == 0:
        raise KeyError
except KeyError:
    BUTTON_FIVE_NAME = None
    BUTTON_FIVE_URL = None
try:
    SOURCE_LINK = getConfig("SOURCE_LINK")
    SOURCE_LINK = SOURCE_LINK.lower() == "true"
except KeyError:
    SOURCE_LINK = False
try:
    STOP_DUPLICATE = getConfig("STOP_DUPLICATE")
    STOP_DUPLICATE = STOP_DUPLICATE.lower() == "true"
except KeyError:
    STOP_DUPLICATE = False
try:
    VIEW_LINK = getConfig("VIEW_LINK")
    VIEW_LINK = VIEW_LINK.lower() == "true"
except KeyError:
    VIEW_LINK = False
try:
    IS_TEAM_DRIVE = getConfig("IS_TEAM_DRIVE")
    IS_TEAM_DRIVE = IS_TEAM_DRIVE.lower() == "true"
except KeyError:
    IS_TEAM_DRIVE = False
try:
    USE_SERVICE_ACCOUNTS = getConfig("USE_SERVICE_ACCOUNTS")
    USE_SERVICE_ACCOUNTS = USE_SERVICE_ACCOUNTS.lower() == "true"
except KeyError:
    USE_SERVICE_ACCOUNTS = False
try:
    BLOCK_MEGA_FOLDER = getConfig("BLOCK_MEGA_FOLDER")
    BLOCK_MEGA_FOLDER = BLOCK_MEGA_FOLDER.lower() == "true"
except KeyError:
    BLOCK_MEGA_FOLDER = False
try:
    BLOCK_MEGA_LINKS = getConfig("BLOCK_MEGA_LINKS")
    BLOCK_MEGA_LINKS = BLOCK_MEGA_LINKS.lower() == "true"
except KeyError:
    BLOCK_MEGA_LINKS = False
try:
    WEB_PINCODE = getConfig("WEB_PINCODE")
    WEB_PINCODE = WEB_PINCODE.lower() == "true"
except KeyError:
    WEB_PINCODE = False
try:
    SHORTENER = getConfig("SHORTENER")
    SHORTENER_API = getConfig("SHORTENER_API")
    if len(SHORTENER) == 0 or len(SHORTENER_API) == 0:
        raise KeyError
except KeyError:
    SHORTENER = None
    SHORTENER_API = None
try:
    IGNORE_PENDING_REQUESTS = getConfig("IGNORE_PENDING_REQUESTS")
    IGNORE_PENDING_REQUESTS = IGNORE_PENDING_REQUESTS.lower() == "true"
except KeyError:
    IGNORE_PENDING_REQUESTS = False
try:
    BASE_URL = getConfig("BASE_URL_OF_BOT").rstrip("/")
    if len(BASE_URL) == 0:
        raise KeyError
except KeyError:
    logging.warning("BASE_URL_OF_BOT not provided!")
    BASE_URL = None

try:
    AS_DOCUMENT = getConfig("AS_DOCUMENT")
    AS_DOCUMENT = AS_DOCUMENT.lower() == "true"
except KeyError:
    AS_DOCUMENT = False

try:
    IMAGE_LEECH = getConfig("IMAGE_LEECH")
    IMAGE_LEECH = IMAGE_LEECH.lower() == "true"
except KeyError:
    IMAGE_LEECH = False

try:
    EQUAL_SPLITS = getConfig("EQUAL_SPLITS")
    EQUAL_SPLITS = EQUAL_SPLITS.lower() == "true"
except KeyError:
    EQUAL_SPLITS = False
try:
    QB_SEED = getConfig("QB_SEED")
    QB_SEED = QB_SEED.lower() == "true"
except KeyError:
    QB_SEED = False
try:
    WORD_BLACKLIST = getConfig("WORD_BLACKLIST")
    WORD_BLACKLIST = WORD_BLACKLIST.lower() == "true"
except KeyError:
    WORD_BLACKLIST = False
try:
    CUSTOM_FILENAME = getConfig("CUSTOM_FILENAME")
    if len(CUSTOM_FILENAME) == 0:
        raise KeyError
except KeyError:
    CUSTOM_FILENAME = None
try:
    CRYPT = getConfig("CRYPT")
    if len(CRYPT) == 0:
        raise KeyError
except KeyError:
    CRYPT = None

try:
    APPDRIVE_EMAIL = getConfig("APPDRIVE_EMAIL")
    APPDRIVE_PASS = getConfig("APPDRIVE_PASS")
    if len(APPDRIVE_EMAIL) == 0 or len(APPDRIVE_PASS) == 0:
        raise KeyError
except KeyError:
    APPDRIVE_EMAIL = None
    APPDRIVE_PASS = None

try:
    CLONE_LOCATION = getConfig("CLONE_LOCATION")
    if len(CLONE_LOCATION) == 0:
        raise KeyError
except KeyError:
    CLONE_LOCATION = ""

try:
    GD_INFO = getConfig("GD_INFO")
    if len(GD_INFO) == 0:
        GD_INFO = "Uploaded by Emily Mirror Bot"
except KeyError:
    GD_INFO = "Uploaded by Emily Mirror Bot"

try:
    TITLE_NAME = getConfig("TITLE_NAME")
    if len(TITLE_NAME) == 0:
        TITLE_NAME = "Emily-Mirror-Search"
except KeyError:
    TITLE_NAME = "Emily-Mirror-Search"

try:
    AUTHOR_NAME = getConfig("AUTHOR_NAME")
    if len(AUTHOR_NAME) == 0:
        AUTHOR_NAME = "Emily-Mirror-Bot"
except KeyError:
    AUTHOR_NAME = "Emily-Mirror-Bot"

try:
    AUTHOR_URL = getConfig("AUTHOR_URL")
    if len(AUTHOR_URL) == 0:
        AUTHOR_URL = "https://t.me/emilymirror"
except KeyError:
    AUTHOR_URL = "https://t.me/emilymirror"

try:
    BOT_PM = getConfig("BOT_PM")
    BOT_PM = BOT_PM.lower() == "true"
except KeyError:
    BOT_PM = False

try:
    FSUB = getConfig("FSUB")
    FSUB = FSUB.lower() == "true"
except KeyError:
    FSUB = False

try:
    FSUB_CHANNEL_ID = int(getConfig("FSUB_CHANNEL_ID"))
except Exception as error:
    LOGGER.warning(f"FSUB_CHANNEL_ID env is empty:\n{error}")
    FSUB_CHANNEL_ID = "-1001576780814"

try:
    CHANNEL_USERNAME: str = getConfig("CHANNEL_USERNAME").replace("@", "")
    if len(CHANNEL_USERNAME) == 0:
        CHANNEL_USERNAME = "emilymirror"
except KeyError:
    logging.warning("Channel Username for FSub not provided")
    CHANNEL_USERNAME = "emilymirror"

try:
    MIRROR_ENABLED = getConfig("MIRROR_ENABLED")
    MIRROR_ENABLED = MIRROR_ENABLED.lower() == "true"
    logging.info("Mirror Feature is Enabled!")
except KeyError:
    MIRROR_ENABLED = False
    logging.warning("Mirror Feature is Disabled!")

try:
    LEECH_ENABLED = getConfig("LEECH_ENABLED")
    LEECH_ENABLED = LEECH_ENABLED.lower() == "true"
    logging.info("Leech Feature is Enabled!")
except KeyError:
    LEECH_ENABLED = False
    logging.warning("Leech Feature is Disabled!")

try:
    TIMEZONE = getConfig("TIMEZONE")
    if len(TIMEZONE) == 0:
        TIMEZONE = None
except KeyError:
    TIMEZONE = "Asia/Kolkata"

try:
    CMD_INDEX = getConfig("CMD_INDEX")
    if len(CMD_INDEX) == 0:
        raise KeyError
except KeyError:
    CMD_INDEX = ""

try:
    STORAGE_THRESHOLD = getConfig("STORAGE_THRESHOLD")
    if len(STORAGE_THRESHOLD) == 0:
        raise KeyError
    else:
        STORAGE_THRESHOLD = float(STORAGE_THRESHOLD)
except KeyError:
    STORAGE_THRESHOLD = None

try:
    HUBD_CRYPT = getConfig("HUBD_CRYPT")
    if len(HUBD_CRYPT) == 0:
        logging.warning("HubDrive Crypt not provided!")
        raise KeyError
except KeyError:
    HUBD_CRYPT = None

try:
    VIRUSTOTAL_API = getConfig("VIRUSTOTAL_API")
    if len(VIRUSTOTAL_API) < 4:
        raise KeyError
except KeyError:
    logging.warning("VIRUSTOTAL_API not provided.")
    VIRUSTOTAL_API = None

try:
    VIRUSTOTAL_FREE = getConfig("VIRUSTOTAL_FREE").lower() == "true"
except KeyError:
    VIRUSTOTAL_FREE = True

try:
    Sharerpw_XSRF = getConfig("Sharerpw_XSRF")
    if len(Sharerpw_XSRF) == 0:
        logging.warning("Sharerpw XSRF Token not provided!")
        raise KeyError
except KeyError:
    Sharerpw_XSRF = None

try:
    Sharerpw_laravel = getConfig("Sharerpw_laravel")
    if len(Sharerpw_laravel) == 0:
        logging.warning("Sharerpw Laravel Session not provided!")
        raise KeyError
except KeyError:
    Sharerpw_laravel = None

try:
    DB_CRYPT = getConfig("DB_CRYPT")
    if len(DB_CRYPT) == 0:
        logging.warning("DriveBuzz Crypt not provided!")
        raise KeyError
except KeyError:
    DB_CRYPT = None

try:
    kolop_CRYPT = getConfig("kolop_CRYPT")
    if len(kolop_CRYPT) == 0:
        logging.warning("Kolop Crypt not provided!")
        raise KeyError
except KeyError:
    kolop_CRYPT = None

try:
    katdrive_CRYPT = getConfig("katdrive_CRYPT")
    if len(katdrive_CRYPT) == 0:
        logging.warning("KatDrive Crypt not provided!")
        raise KeyError
except KeyError:
    katdrive_CRYPT = None

try:
    drivefire_CRYPT = getConfig("drivefire_CRYPT")
    if len(drivefire_CRYPT) == 0:
        logging.warning("DriveFire Crypt not provided!")
        raise KeyError
except KeyError:
    drivefire_CRYPT = None

try:
    gadrive_CRYPT = getConfig("gadrive_CRYPT")
    if len(gadrive_CRYPT) == 0:
        logging.warning("GaDrive Crypt not provided!")
        raise KeyError
except KeyError:
    gadrive_CRYPT = None

try:
    jiodrive_CRYPT = getConfig("jiodrive_CRYPT")
    if len(jiodrive_CRYPT) == 0:
        logging.warning("JioDrive Crypt not provided!")
        raise KeyError
except KeyError:
    jiodrive_CRYPT = None

try:
    SEARCH_LIMIT = getConfig("SEARCH_LIMIT")
    if len(SEARCH_LIMIT) == 0:
        raise KeyError
    else:
        SEARCH_LIMIT = int(SEARCH_LIMIT)
except KeyError:
    SEARCH_LIMIT = 0

try:
    TOKEN_PICKLE_URL = getConfig("TOKEN_PICKLE_URL")
    if len(TOKEN_PICKLE_URL) == 0:
        raise KeyError
    try:
        res = rget(TOKEN_PICKLE_URL)
        if res.status_code == 200:
            with open("token.pickle", "wb+") as f:
                f.write(res.content)
        else:
            logging.error(
                f"Failed to download token.pickle, link got HTTP response: {res.status_code}"
            )
    except Exception as e:
        logging.error(f"TOKEN_PICKLE_URL: {e}")
except KeyError:
    pass
try:
    ACCOUNTS_ZIP_URL = getConfig("ACCOUNTS_ZIP_URL")
    if len(ACCOUNTS_ZIP_URL) == 0:
        raise KeyError
    else:
        try:
            res = rget(ACCOUNTS_ZIP_URL)
            if res.status_code == 200:
                with open("accounts.zip", "wb+") as f:
                    f.write(res.content)
            else:
                logging.error(
                    f"Failed to download accounts.zip, link got HTTP response: {res.status_code}"
                )
        except Exception as e:
            logging.error(f"ACCOUNTS_ZIP_URL: {e}")
            raise KeyError
        srun(["unzip", "-q", "-o", "accounts.zip"])
        srun(["chmod", "-R", "777", "accounts"])
        osremove("accounts.zip")
except KeyError:
    pass
try:
    MULTI_SEARCH_URL = getConfig("MULTI_SEARCH_URL")
    if len(MULTI_SEARCH_URL) == 0:
        raise KeyError
    try:
        res = rget(MULTI_SEARCH_URL)
        if res.status_code == 200:
            with open("drive_folder", "wb+") as f:
                f.write(res.content)
        else:
            logging.error(
                f"Failed to download drive_folder, link got HTTP response: {res.status_code}"
            )
    except Exception as e:
        logging.error(f"MULTI_SEARCH_URL: {e}")
except KeyError:
    pass
try:
    YT_COOKIES_URL = getConfig("YT_COOKIES_URL")
    if len(YT_COOKIES_URL) == 0:
        raise KeyError
    try:
        res = rget(YT_COOKIES_URL)
        if res.status_code == 200:
            with open("cookies.txt", "wb+") as f:
                f.write(res.content)
        else:
            logging.error(
                f"Failed to download cookies.txt, link got HTTP response: {res.status_code}"
            )
    except Exception as e:
        logging.error(f"YT_COOKIES_URL: {e}")
except KeyError:
    pass

DRIVES_NAMES.append("Main")
DRIVES_IDS.append(parent_id)
if ospath.exists("drive_folder"):
    with open("drive_folder", "r+") as f:
        lines = f.readlines()
        for line in lines:
            try:
                temp = line.strip().split()
                DRIVES_IDS.append(temp[1])
                DRIVES_NAMES.append(temp[0].replace("_", " "))
            except BaseException:
                pass
            try:
                INDEX_URLS.append(temp[2])
                ALT_INDEX_URLS.append(temp[2])
            except IndexError:
                INDEX_URLS.append(None)
                ALT_INDEX_URLS.append(None)
try:
    SEARCH_PLUGINS = getConfig("SEARCH_PLUGINS")
    if len(SEARCH_PLUGINS) == 0:
        raise KeyError
    SEARCH_PLUGINS = jsnloads(SEARCH_PLUGINS)
except KeyError:
    SEARCH_PLUGINS = None

updater = tgUpdater(
    token=BOT_TOKEN, request_kwargs={"read_timeout": 20, "connect_timeout": 15}
)
bot = updater.bot
dispatcher = updater.dispatcher
job_queue = updater.job_queue
