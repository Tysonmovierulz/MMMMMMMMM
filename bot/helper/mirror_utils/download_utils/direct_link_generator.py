# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Helper Module containing various sites direct links generators. This module is copied and modified as per need
from https://github.com/AvinashReddy3108/PaperplaneExtended . I hereby take no credit of the following code other
than the modifications. See https://github.com/AvinashReddy3108/PaperplaneExtended/commits/master/userbot/modules/direct_links.py
for original authorship. """

import re
from base64 import b64decode, standard_b64encode
from json import loads as jsnloads
from urllib.parse import unquote, urlparse

import cloudscraper
import requests
from bs4 import BeautifulSoup
from cfscrape import create_scraper
from fake_useragent import UserAgent
from lk21 import Bypass
from lxml import etree

from bot import APPDRIVE_EMAIL, APPDRIVE_PASS
from bot import CLONE_LOCATION as GDFOL_ID
from bot import (
    CRYPT,
    DB_CRYPT,
    HUBD_CRYPT,
    LOGGER,
    UPTOBOX_TOKEN,
    Sharerpw_laravel,
    Sharerpw_XSRF,
    drivefire_CRYPT,
    gadrive_CRYPT,
    jiodrive_CRYPT,
    katdrive_CRYPT,
    kolop_CRYPT,
)
from bot.helper.ext_utils.bot_utils import is_gdtot_link
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.telegram_helper.bot_commands import BotCommands

fmed_list = [
    "fembed.net",
    "fembed.com",
    "femax20.com",
    "fcdn.stream",
    "feurl.com",
    "layarkacaxxi.icu",
    "naniplay.nanime.in",
    "naniplay.nanime.biz",
    "naniplay.com",
    "mm9842.com",
]


def direct_link_generator(link: str):
    """direct links generator"""
    if "youtube.com" in link or "youtu.be" in link:
        raise DirectDownloadLinkException(
            f"ERROR: Use /{BotCommands.WatchCommand} to mirror Youtube link\nUse /{BotCommands.ZipWatchCommand} to make zip of Youtube playlist"
        )
    elif "zippyshare.com" in link:
        return zippy_share(link)
    elif (
        "yadi.sk" in link
        or "disk.yandex.com" in link
        or "yandex.com.tr" in link
        or "yandex.com.ru" in link
    ):
        return yandex_disk(link)
    elif "mediafire.com" in link:
        return mediafire(link)
    elif "uptobox.com" in link:
        return uptobox(link)
    elif "osdn.net" in link:
        return osdn(link)
    elif "github.com" in link:
        return github(link)
    elif "hxfile.co" in link:
        return hxfile(link)
    elif "files.im" in link:
        return filesIm(link)
    elif "linkpoi" in link:
        return linkpoi(link)
    elif "mirrored" in link:
        return mirrored(link)
    elif "reupload" in link:
        return reupload(link)
    elif "uservideo" in link:
        return uservideo(link)
    elif "anonfiles.com" in link:
        return anonfiles(link)
    elif "letsupload.io" in link:
        return letsupload(link)
    elif "1drv.ms" in link:
        return onedrive(link)
    elif "pixeldrain.com" in link:
        return pixeldrain(link)
    elif "antfiles.com" in link:
        return antfiles(link)
    elif "streamtape.com" in link:
        return streamtape(link)
    elif "bayfiles.com" in link:
        return anonfiles(link)
    elif "racaty.net" in link:
        return racaty(link)
    elif "1fichier.com" in link:
        return fichier(link)
    elif "solidfiles.com" in link:
        return solidfiles(link)
    elif "krakenfiles.com" in link:
        return krakenfiles(link)
    elif is_gdtot_link(link):
        return gdtot(link)
    elif "drivebuzz" in link:
        return drivebuzz_dl(link)
    elif (
        "appdrive" in link
        or "driveapp" in link
        or "drivehub" in link
        or "gdflix" in link
        or "drivesharer" in link
        or "drivebit" in link
        or "drivelink" in link
        or "driveace" in link
        or "drivepro" in link
    ):
        return appdrive_dl(link)
    elif "hubdrive" in link:
        return hubdrive_dl(link)
    elif "kolop" in link:
        return kolop_dl(link)
    elif "katdrive" in link:
        return katdrive_dl(link)
    elif "gadrive" in link:
        return gadrive_dl(link)
    elif "jiodrive" in link:
        return jiodrive_dl(link)
    elif "drivefire" in link:
        return drivefire_dl(link)
    elif "gofile.io" in link:
        return gofile_ddl(link)
    elif "megaup.net" in link:
        return megaup_dl(link)
    elif "mdisk" in link:
        return mdisk_ddl(link)
    elif "wetransfer.com" in link or "we.tl" in link:
        return wetransfer_ddl(link)
    elif "sharer.pw" in link:
        return sharerpw_dl(link)
    elif any(x in link for x in fmed_list):
        return fembed(link)
    elif any(
        x in link for x in ["sbembed.com", "watchsb.com", "streamsb.net", "sbplay.org"]
    ):
        return sbembed(link)
    else:
        raise DirectDownloadLinkException(f"No Direct link function found for {link}")


def zippy_share(url: str) -> str:
    """ZippyShare direct link generator
    Based on https://github.com/KenHV/Mirror-Bot
             https://github.com/jovanzers/WinTenCermin
    try:
        link = re.findall(r'\bhttps?://.*zippyshare\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("ERROR: No Zippyshare links found")
    try:
        base_url = re.search('http.+.zippyshare.com/', link).group()
        response = requests.get(link).content
        pages = BeautifulSoup(response, "lxml")
        try:
            js_script = pages.find("div", {"class": "center"})
            if js_script is not None:
                js_script = js_script.find_all("script")[1]
            else:
                raise DirectDownloadLinkException("ERROR: No Zippyshare links found")
        except IndexError:
            js_script = pages.find("div", {"class": "right"})
            if js_script is not None:
                js_script = js_script.find_all("script")[0]
            else:
                raise DirectDownloadLinkException("ERROR: No Zippyshare links found")
        js_content = re.findall(r'\.href.=."/(.*?)";', str(js_script))
        js_content = str(js_content[0]).split('"')
         n = str(js_script).split('var n = ')[1].split(';')[0].split('%')
         n = int(n[0]) % int(n[1])
         b = str(js_script).split('var b = ')[1].split(';')[0].split('%')
         b = int(b[0]) % int(b[1])
         z = int(str(js_script).split('var z = ')[1].split(';')[0])
         math_ = str(n + b + z - 3)
        math = re.findall("\d+",js_content[1])
        math_ = int(math[0]) % int(math[1]) + int(math[2]) % int(math[3])
        return base_url + str(js_content[0]) + str(math_) + str(js_content[2])
    except IndexError:
        raise DirectDownloadLinkException("ERROR: Can't find download button")"""
    return Bypass().bypass_zippyshare(url)


def yandex_disk(url: str) -> str:
    """Yandex.Disk direct link generator
    Based on https://github.com/wldhx/yadisk-direct"""
    try:
        link = re.findall(
            r"\b(https?://(yadi.sk|disk.yandex.com|yandex.com.ru|yandex.com.tr)\S+)",
            url,
        )[0][0]
    except IndexError:
        return "No Yandex.Disk links found\n"
    api = "https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}"
    try:
        return requests.get(api.format(link)).json()["href"]
    except KeyError:
        raise DirectDownloadLinkException(
            "ERROR: File not found/Download limit reached\n"
        )


def uptobox(url: str) -> str:
    """Uptobox direct link generator
    based on https://github.com/jovanzers/WinTenCermin"""
    try:
        link = re.findall(r"\bhttps?://.*uptobox\.com\S+", url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Uptobox links found\n")
    if UPTOBOX_TOKEN is None:
        LOGGER.error("UPTOBOX_TOKEN not provided!")
        dl_url = link
    else:
        try:
            link = re.findall(r"\bhttp?://.*uptobox\.com/dl\S+", url)[0]
            dl_url = link
        except BaseException:
            file_id = re.findall(r"\bhttps?://.*uptobox\.com/(\w+)", url)[0]
            file_link = "https://uptobox.com/api/link?token=%s&file_code=%s" % (
                UPTOBOX_TOKEN,
                file_id,
            )
            req = requests.get(file_link)
            result = req.json()
            dl_url = result["data"]["dlLink"]
    return dl_url


def mediafire(url: str) -> str:
    """MediaFire direct link generator"""
    try:
        link = re.findall(r"\bhttps?://.*mediafire\.com\S+", url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No MediaFire links found\n")
    page = BeautifulSoup(requests.get(link).content, "lxml")
    info = page.find("a", {"aria-label": "Download file"})
    return info.get("href")


def osdn(url: str) -> str:
    """OSDN direct link generator"""
    osdn_link = "https://osdn.net"
    try:
        link = re.findall(r"\bhttps?://.*osdn\.net\S+", url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No OSDN links found\n")
    page = BeautifulSoup(requests.get(link, allow_redirects=True).content, "lxml")
    info = page.find("a", {"class": "mirror_link"})
    link = unquote(osdn_link + info["href"])
    mirrors = page.find("form", {"id": "mirror-select-form"}).findAll("tr")
    urls = []
    for data in mirrors[1:]:
        mirror = data.find("input")["value"]
        urls.append(re.sub(r"m=(.*)&f", f"m={mirror}&f", link))
    return urls[0]


def github(url: str) -> str:
    """GitHub direct links generator"""
    try:
        re.findall(r"\bhttps?://.*github\.com.*releases\S+", url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No GitHub Releases links found\n")
    download = requests.get(url, stream=True, allow_redirects=False)
    try:
        return download.headers["location"]
    except KeyError:
        raise DirectDownloadLinkException("ERROR: Can't extract the link\n")


def hxfile(url: str) -> str:
    """Hxfile direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    return Bypass().bypass_filesIm(url)


def filesIm(url: str) -> str:
    """Files.im direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    # return Bypass().bypass_filesIm(url)
    return "вσт ¢αииσт ∂σωиℓσα∂ тнιѕ ℓιик"


def anonfiles(url: str) -> str:
    """Anonfiles direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    return Bypass().bypass_anonfiles(url)


def letsupload(url: str) -> str:
    """Letsupload direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        link = re.findall(r"\bhttps?://.*letsupload\.io\S+", url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Letsupload links found\n")
    return Bypass().bypass_url(link)


def linkpoi(url: str) -> str:
    """Linkpoi direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    # return Bypass().bypass_linkpoi(url)
    return "вσт ¢αииσт ∂σωиℓσα∂ тнιѕ ℓιик"


def fembed(link: str) -> str:
    """Fembed direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    dl_url = Bypass().bypass_fembed(link)
    count = len(dl_url)
    lst_link = [dl_url[i] for i in dl_url]
    return lst_link[count - 1]


def sbembed(link: str) -> str:
    """Sbembed direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    dl_url = Bypass().bypass_sbembed(link)
    count = len(dl_url)
    lst_link = [dl_url[i] for i in dl_url]
    return lst_link[count - 1]


def mirrored(url: str) -> str:
    """Mirrored.to direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    # return Bypass().bypass_mirrored(url)
    return "вσт ¢αииσт ∂σωиℓσα∂ тнιѕ ℓιик"


def reupload(url: str) -> str:
    """ReUpload direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    # return Bypass().bypass_reupload(url)
    return "вσт ¢αииσт ∂σωиℓσα∂ тнιѕ ℓιик"


def uservideo(url: str) -> str:
    """UserVideo direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    # return Bypass().bypass_uservideo(url)
    return "вσт ¢αииσт ∂σωиℓσα∂ тнιѕ ℓιик"


def onedrive(link: str) -> str:
    """Onedrive direct link generator
    Based on https://github.com/UsergeTeam/Userge"""
    link_without_query = urlparse(link)._replace(query=None).geturl()
    direct_link_encoded = str(
        standard_b64encode(bytes(link_without_query, "utf-8")), "utf-8"
    )
    direct_link1 = (
        f"https://api.onedrive.com/v1.0/shares/u!{direct_link_encoded}/root/content"
    )
    resp = requests.head(direct_link1)
    if resp.status_code != 302:
        raise DirectDownloadLinkException(
            "ERROR: Unauthorized link, the link may be private"
        )
    dl_link = resp.next.url
    dl_link.rsplit("/", 1)[1]
    requests.head(dl_link)
    return dl_link


def pixeldrain(url: str) -> str:
    """Based on https://github.com/yash-dk/TorToolkit-Telegram"""
    url = url.strip("/ ")
    file_id = url.split("/")[-1]
    if url.split("/")[-2] == "l":
        info_link = f"https://pixeldrain.com/api/list/{file_id}"
        dl_link = f"https://pixeldrain.com/api/list/{file_id}/zip"
    else:
        info_link = f"https://pixeldrain.com/api/file/{file_id}/info"
        dl_link = f"https://pixeldrain.com/api/file/{file_id}"
    resp = requests.get(info_link).json()
    if resp["success"]:
        return dl_link
    else:
        raise DirectDownloadLinkException(
            "ERROR: Cant't download due {}.".format(resp["message"])
        )


def antfiles(url: str) -> str:
    """Antfiles direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    return Bypass().bypass_antfiles(url)


def streamtape(url: str) -> str:
    """Streamtape direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    return Bypass().bypass_streamtape(url)


def racaty(url: str) -> str:
    """Racaty direct link generator
    based on https://github.com/SlamDevs/slam-mirrorbot"""
    dl_url = ""
    try:
        link = re.findall(r"\bhttps?://.*racaty\.net\S+", url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Racaty links found\n")
    scraper = create_scraper()
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    op = soup.find("input", {"name": "op"})["value"]
    ids = soup.find("input", {"name": "id"})["value"]
    rpost = scraper.post(url, data={"op": op, "id": ids})
    rsoup = BeautifulSoup(rpost.text, "lxml")
    dl_url = rsoup.find("a", {"id": "uniqueExpirylink"})["href"].replace(" ", "%20")
    return dl_url


def fichier(link: str) -> str:
    """1Fichier direct link generator
    Based on https://github.com/Maujar
    """
    regex = r"^([http:\/\/|https:\/\/]+)?.*1fichier\.com\/\?.+"
    gan = re.match(regex, link)
    if not gan:
        raise DirectDownloadLinkException("ERROR: The link you entered is wrong!")
    if "::" in link:
        pswd = link.split("::")[-1]
        url = link.split("::")[-2]
    else:
        pswd = None
        url = link
    try:
        if pswd is None:
            req = requests.post(url)
        else:
            pw = {"pass": pswd}
            req = requests.post(url, data=pw)
    except BaseException:
        raise DirectDownloadLinkException("ERROR: Unable to reach 1fichier server!")
    if req.status_code == 404:
        raise DirectDownloadLinkException(
            "ERROR: File not found/The link you entered is wrong!"
        )
    soup = BeautifulSoup(req.content, "lxml")
    if soup.find("a", {"class": "ok btn-general btn-orange"}) is not None:
        dl_url = soup.find("a", {"class": "ok btn-general btn-orange"})["href"]
        if dl_url is None:
            raise DirectDownloadLinkException(
                "ERROR: Unable to generate Direct Link 1fichier!"
            )
        else:
            return dl_url
    elif len(soup.find_all("div", {"class": "ct_warn"})) == 2:
        str_2 = soup.find_all("div", {"class": "ct_warn"})[-1]
        if "you must wait" in str(str_2).lower():
            numbers = [int(word) for word in str(str_2).split() if word.isdigit()]
            if not numbers:
                raise DirectDownloadLinkException(
                    "ERROR: 1fichier is on a limit. Please wait a few minutes/hour."
                )
            else:
                raise DirectDownloadLinkException(
                    f"ERROR: 1fichier is on a limit. Please wait {numbers[0]} minute."
                )
        elif "protect access" in str(str_2).lower():
            raise DirectDownloadLinkException(
                f"ERROR: This link requires a password!\n\n<b>This link requires a password!</b>\n- Insert sign <b>::</b> after the link and write the password after the sign.\n\n<b>Example:</b>\n<code>/{BotCommands.MirrorCommand} https://1fichier.com/?smmtd8twfpm66awbqz04::love you</code>\n\n* No spaces between the signs <b>::</b>\n* For the password, you can use a space!"
            )
        else:
            raise DirectDownloadLinkException(
                "ERROR: Error trying to generate Direct Link from 1fichier!"
            )
    elif len(soup.find_all("div", {"class": "ct_warn"})) == 3:
        str_1 = soup.find_all("div", {"class": "ct_warn"})[-2]
        str_3 = soup.find_all("div", {"class": "ct_warn"})[-1]
        if "you must wait" in str(str_1).lower():
            numbers = [int(word) for word in str(str_1).split() if word.isdigit()]
            if not numbers:
                raise DirectDownloadLinkException(
                    "ERROR: 1fichier is on a limit. Please wait a few minutes/hour."
                )
            else:
                raise DirectDownloadLinkException(
                    f"ERROR: 1fichier is on a limit. Please wait {numbers[0]} minute."
                )
        elif "bad password" in str(str_3).lower():
            raise DirectDownloadLinkException(
                "ERROR: The password you entered is wrong!"
            )
        else:
            raise DirectDownloadLinkException(
                "ERROR: Error trying to generate Direct Link from 1fichier!"
            )
    else:
        raise DirectDownloadLinkException(
            "ERROR: Error trying to generate Direct Link from 1fichier!"
        )


def solidfiles(url: str) -> str:
    """Solidfiles direct link generator
    Based on https://github.com/Xonshiz/SolidFiles-Downloader
    By https://github.com/Jusidama18"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    pageSource = requests.get(url, headers=headers).text
    mainOptions = str(re.search(r"viewerOptions\'\,\ (.*?)\)\;", pageSource).group(1))
    return jsnloads(mainOptions)["downloadUrl"]


def krakenfiles(page_link: str) -> str:
    """krakenfiles direct link generator
    Based on https://github.com/tha23rd/py-kraken
    By https://github.com/junedkh"""
    page_resp = requests.session().get(page_link)
    soup = BeautifulSoup(page_resp.text, "lxml")
    try:
        token = soup.find("input", id="dl-token")["value"]
    except BaseException:
        raise DirectDownloadLinkException(f"Page link is wrong: {page_link}")

    hashes = [
        item["data-file-hash"]
        for item in soup.find_all("div", attrs={"data-file-hash": True})
    ]
    if not hashes:
        raise DirectDownloadLinkException(f"Hash not found for : {page_link}")

    dl_hash = hashes[0]

    payload = f'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="token"\r\n\r\n{token}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--'
    headers = {
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        "cache-control": "no-cache",
        "hash": dl_hash,
    }

    dl_link_resp = requests.session().post(
        f"https://krakenfiles.com/download/{hash}", data=payload, headers=headers
    )

    dl_link_json = dl_link_resp.json()

    if "url" in dl_link_json:
        return dl_link_json["url"]
    else:
        raise DirectDownloadLinkException(
            f"Failed to acquire download URL from kraken for : {page_link}"
        )


def gdtot(url: str) -> str:
    """Gdtot google drive link generator
    By https://github.com/xcscxr"""

    if CRYPT is None:
        raise DirectDownloadLinkException("ERROR: CRYPT cookie not provided")

    match = re.findall(r"https?://(.+)\.gdtot\.(.+)\/\S+\/\S+", url)[0]

    with requests.Session() as client:
        client.cookies.update({"crypt": CRYPT})
        res = client.get(url)
        res = client.get(
            f"https://{match[0]}.gdtot.{match[1]}/dld?id={url.split('/')[-1]}"
        )
    matches = re.findall("gd=(.*?)&", res.text)
    try:
        decoded_id = b64decode(str(matches[0])).decode("utf-8")
    except BaseException:
        raise DirectDownloadLinkException(
            "ERROR: Try in your broswer, mostly file not found or user limit exceeded!"
        )
    return f"https://drive.google.com/open?id={decoded_id}"


def drivebuzz_dl(url: str) -> str:
    """DriveBuzz google drive link generator
    By https://github.com/xcscxr"""

    if DB_CRYPT is None:
        raise DirectDownloadLinkException("ERROR: DriveBuzz CRYPT cookie not provided")

    match = re.findall(r"https?://(.+)\.drivebuzz\.(.+)\/\S+\/\S+", url)[0]

    with requests.Session() as client:
        client.cookies.update({"crypt": DB_CRYPT})
        res = client.get(url)
        res = client.get(
            f"https://{match[0]}.drivebuzz.{match[1]}/dld?id={url.split('/')[-1]}"
        )
    matches = re.findall("gd=(.*?)&", res.text)
    try:
        decoded_id = b64decode(str(matches[0])).decode("utf-8")
    except BaseException:
        raise DirectDownloadLinkException(
            "ERROR: Try in your broswer, mostly file not found or user limit exceeded!"
        )
    return f"https://drive.google.com/open?id={decoded_id}"


def appdrive(url: str) -> str:
    """AppDrive/DriveApp/DriveHub/GDFlix/DriveSharer/DriveBit/DriveLink/DriveAce/DrivePro google drive link generator
    By https://github.com/xcscxr"""

    if APPDRIVE_EMAIL is None or APPDRIVE_PASS is None or GDFOL_ID is None:
        raise DirectDownloadLinkException(
            "AppDrive/DriveApp/DriveHub/GDFlix/DriveSharer/DriveBit/DriveLink Credentials not Found!"
        )

    try:
        account = {"email": APPDRIVE_EMAIL, "passwd": APPDRIVE_PASS}
        client = requests.Session()
        client.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
            }
        )
        data = {"email": account["email"], "password": account["passwd"]}
        client.post(f"https://{urlparse(url).netloc}/login", data=data)
        data = {"root_drive": "", "folder": GDFOL_ID}
        client.post(f"https://{urlparse(url).netloc}/account", data=data)
        res = client.get(url)
        key = re.findall('"key",\s+"(.*?)"', res.text)[0]
        ddl_btn = etree.HTML(res.content).xpath("//button[@id='drc']")
        info = re.findall(">(.*?)<\/li>", res.text)
        info_parsed = {}
        for item in info:
            kv = [s.strip() for s in item.split(":", maxsplit=1)]
            info_parsed[kv[0].lower()] = kv[1]
        info_parsed = info_parsed
        info_parsed["error"] = False
        info_parsed["link_type"] = "login"  # direct/login
        headers = {
            "Content-Type": f"multipart/form-data; boundary={'-'*4}_",
        }
        data = {"type": 1, "key": key, "action": "original"}
        if len(ddl_btn):
            info_parsed["link_type"] = "direct"
            data["action"] = "direct"
        while data["type"] <= 3:
            boundary = f'{"-"*6}_'
            data_string = ""
            for item in data:
                data_string += f"{boundary}\r\n"
                data_string += f'Content-Disposition: form-data; name="{item}"\r\n\r\n{data[item]}\r\n'
            data_string += f"{boundary}--\r\n"
            gen_payload = data_string
            try:
                response = client.post(url, data=gen_payload, headers=headers).json()
                break
            except BaseException:
                data["type"] += 1
        if "url" in response:
            info_parsed["gdrive_link"] = response["url"]
        elif "error" in response and response["error"]:
            info_parsed["error"] = True
            info_parsed["error_message"] = response["message"]
        else:
            info_parsed["error"] = True
            info_parsed["error_message"] = "Something went wrong :("
        if info_parsed["error"]:
            return info_parsed
        if urlparse(url).netloc == "driveapp.in" and not info_parsed["error"]:
            res = client.get(info_parsed["gdrive_link"])
            drive_link = etree.HTML(res.content).xpath(
                "//a[contains(@class,'btn')]/@href"
            )[0]
            info_parsed["gdrive_link"] = drive_link
        info_parsed["src_url"] = url
        if urlparse(url).netloc == "drivehub.in" and not info_parsed["error"]:
            res = client.get(info_parsed["gdrive_link"])
            drive_link = etree.HTML(res.content).xpath(
                "//a[contains(@class,'btn')]/@href"
            )[0]
            info_parsed["gdrive_link"] = drive_link
        info_parsed["src_url"] = url
        if urlparse(url).netloc == "gdflix.pro" and not info_parsed["error"]:
            res = client.get(info_parsed["gdrive_link"])
            drive_link = etree.HTML(res.content).xpath(
                "//a[contains(@class,'btn')]/@href"
            )[0]
            info_parsed["gdrive_link"] = drive_link
        info_parsed["src_url"] = url
        if urlparse(url).netloc == "drivesharer.in" and not info_parsed["error"]:
            res = client.get(info_parsed["gdrive_link"])
            drive_link = etree.HTML(res.content).xpath(
                "//a[contains(@class,'btn')]/@href"
            )[0]
            info_parsed["gdrive_link"] = drive_link
        info_parsed["src_url"] = url
        if urlparse(url).netloc == "drivebit.in" and not info_parsed["error"]:
            res = client.get(info_parsed["gdrive_link"])
            drive_link = etree.HTML(res.content).xpath(
                "//a[contains(@class,'btn')]/@href"
            )[0]
            info_parsed["gdrive_link"] = drive_link
        info_parsed["src_url"] = url
        if urlparse(url).netloc == "drivelinks.in" and not info_parsed["error"]:
            res = client.get(info_parsed["gdrive_link"])
            drive_link = etree.HTML(res.content).xpath(
                "//a[contains(@class,'btn')]/@href"
            )[0]
            info_parsed["gdrive_link"] = drive_link
        info_parsed["src_url"] = url
        if urlparse(url).netloc == "driveace.in" and not info_parsed["error"]:
            res = client.get(info_parsed["gdrive_link"])
            drive_link = etree.HTML(res.content).xpath(
                "//a[contains(@class,'btn')]/@href"
            )[0]
            info_parsed["gdrive_link"] = drive_link
        info_parsed["src_url"] = url
        if urlparse(url).netloc == "drivepro.in" and not info_parsed["error"]:
            res = client.get(info_parsed["gdrive_link"])
            drive_link = etree.HTML(res.content).xpath(
                "//a[contains(@class,'btn')]/@href"
            )[0]
            info_parsed["gdrive_link"] = drive_link
        info_parsed["src_url"] = url
        if info_parsed["error"]:
            raise DirectDownloadLinkException(f"{info_parsed['error_message']}")
        return info_parsed["gdrive_link"]

    except BaseException:
        raise DirectDownloadLinkException(f"Unable to Extract GDrive Link")


def hubdrive_dl(url: str) -> str:
    """HubDrive google drive link generator
    By https://github.com/xcscxr"""

    if HUBD_CRYPT is None:
        raise DirectDownloadLinkException("ERROR: HubDrive CRYPT cookie not provided")

    try:
        with requests.Session() as client:
            client.cookies.update({"crypt": HUBD_CRYPT})
            res = client.get(url)
            up = urlparse(url)
            req_url = f"{up.scheme}://{up.netloc}/ajax.php?ajax=download"
            file_id = url.split("/")[-1]
            data = {"id": file_id}
            headers = {"x-requested-with": "XMLHttpRequest"}
        try:
            res = client.post(req_url, headers=headers, data=data).json()["file"]
            gd_id = re.findall("gd=(.*)", res, re.DOTALL)[0]
        except BaseException:
            raise DirectDownloadLinkException(
                "ERROR: Try in your broswer, mostly file not found or user limit exceeded!"
            )
        return f"https://drive.google.com/open?id={gd_id}"

    except BaseException:
        raise DirectDownloadLinkException(f"Unable to Extract GDrive Link")


def kolop_dl(url: str) -> str:
    """Kolop google drive link generator
    By https://github.com/xcscxr"""

    if kolop_CRYPT is None:
        raise DirectDownloadLinkException("ERROR: Kolop CRYPT cookie not provided")

    try:
        with requests.Session() as client:
            client.cookies.update({"crypt": kolop_CRYPT})
            res = client.get(url)
            up = urlparse(url)
            req_url = f"{up.scheme}://{up.netloc}/ajax.php?ajax=download"
            file_id = url.split("/")[-1]
            data = {"id": file_id}
            headers = {"x-requested-with": "XMLHttpRequest"}
        try:
            res = client.post(req_url, headers=headers, data=data).json()["file"]
            gd_id = re.findall("gd=(.*)", res, re.DOTALL)[0]
        except BaseException:
            raise DirectDownloadLinkException(
                "ERROR: Try in your broswer, mostly file not found or user limit exceeded!"
            )
        return f"https://drive.google.com/open?id={gd_id}"

    except BaseException:
        raise DirectDownloadLinkException(f"Unable to Extract GDrive Link")


def katdrive_dl(url: str) -> str:
    """KatDrive google drive link generator
    By https://github.com/xcscxr"""

    if katdrive_CRYPT is None:
        raise DirectDownloadLinkException("ERROR: Katdrive CRYPT cookie not provided")

    try:
        with requests.Session() as client:
            client.cookies.update({"crypt": katdrive_CRYPT})
            res = client.get(url)
            up = urlparse(url)
            req_url = f"{up.scheme}://{up.netloc}/ajax.php?ajax=download"
            file_id = url.split("/")[-1]
            data = {"id": file_id}
            headers = {"x-requested-with": "XMLHttpRequest"}
        try:
            res = client.post(req_url, headers=headers, data=data).json()["file"]
            gd_id = re.findall("gd=(.*)", res, re.DOTALL)[0]
        except BaseException:
            raise DirectDownloadLinkException(
                "ERROR: Try in your broswer, mostly file not found or user limit exceeded!"
            )
        return f"https://drive.google.com/open?id={gd_id}"

    except BaseException:
        raise DirectDownloadLinkException(f"Unable to Extract GDrive Link")


def gadrive_dl(url: str) -> str:
    """GaDrive google drive link generator
    By https://github.com/xcscxr"""

    if gadrive_CRYPT is None:
        raise DirectDownloadLinkException("ERROR: GaDrive CRYPT cookie not provided")

    try:
        with requests.Session() as client:
            client.cookies.update({"crypt": gadrive_CRYPT})
            res = client.get(url)
            up = urlparse(url)
            req_url = f"{up.scheme}://{up.netloc}/ajax.php?ajax=download"
            file_id = url.split("/")[-1]
            data = {"id": file_id}
            headers = {"x-requested-with": "XMLHttpRequest"}
        try:
            res = client.post(req_url, headers=headers, data=data).json()["file"]
            gd_id = re.findall("gd=(.*)", res, re.DOTALL)[0]
        except BaseException:
            raise DirectDownloadLinkException(
                "ERROR: Try in your broswer, mostly file not found or user limit exceeded!"
            )
        return f"https://drive.google.com/open?id={gd_id}"

    except BaseException:
        raise DirectDownloadLinkException(f"Unable to Extract GDrive Link")


def jiodrive_dl(url: str) -> str:
    """JioDrive google drive link generator
    By https://github.com/xcscxr"""

    if jiodrive_CRYPT is None:
        raise DirectDownloadLinkException("ERROR: JioDrive CRYPT cookie not provided")

    try:
        with requests.Session() as client:
            client.cookies.update({"crypt": jiodrive_CRYPT})
            res = client.get(url)
            up = urlparse(url)
            req_url = f"{up.scheme}://{up.netloc}/ajax.php?ajax=download"
            file_id = url.split("/")[-1]
            data = {"id": file_id}
            headers = {"x-requested-with": "XMLHttpRequest"}
        try:
            res = client.post(req_url, headers=headers, data=data).json()["file"]
            gd_id = re.findall("gd=(.*)", res, re.DOTALL)[0]
        except BaseException:
            raise DirectDownloadLinkException(
                "ERROR: Try in your broswer, mostly file not found or user limit exceeded!"
            )
        return f"https://drive.google.com/open?id={gd_id}"

    except BaseException:
        raise DirectDownloadLinkException(f"Unable to Extract GDrive Link")


def drivefire_dl(url: str) -> str:
    """DriveFire google drive link generator
    By https://github.com/xcscxr"""

    if drivefire_CRYPT is None:
        raise DirectDownloadLinkException("ERROR: DriveFire CRYPT cookie not provided")

    try:
        with requests.Session() as client:
            client.cookies.update({"crypt": drivefire_CRYPT})
            res = client.get(url)
            up = urlparse(url)
            req_url = f"{up.scheme}://{up.netloc}/ajax.php?ajax=download"
            file_id = url.split("/")[-1]
            data = {"id": file_id}
            headers = {"x-requested-with": "XMLHttpRequest"}
        try:
            res = client.post(req_url, headers=headers, data=data).json()["file"]
            gd_id = re.findall("gd=(.*)", res, re.DOTALL)[0]
        except BaseException:
            raise DirectDownloadLinkException(
                "ERROR: Try in your broswer, mostly file not found or user limit exceeded!"
            )
        return f"https://drive.google.com/open?id={gd_id}"

    except BaseException:
        raise DirectDownloadLinkException(f"Unable to Extract GDrive Link")


def gofile_ddl(url: str) -> str:
    """Gofile.io DDL link generator
    By https://github.com/xcscxr"""
    """
    check = re.findall(r"\bhttps?://.*gofile\S+", url)
    if not check:
        textx = f"Invalid Gofile url"
        return textx
    else:
        api_uri = "https://api.gofile.io"

        client = requests.Session()
        res = client.get(api_uri + "/createAccount").json()
        data = {
            "contentId": url.split("/")[-1],
            "token": res["data"]["token"],
            "websiteToken": "12345",
            "cache": "true",
        }
        try:
            res = client.get(api_uri + "/getContent", params=data).json()
            for item in res["data"]["contents"].values():
                content = item
        except BaseException:
            return "Invalid Link"

        return content["directLink"] """
    return "вσт ¢αииσт ∂σωиℓσα∂ gσfιℓє.ισ ℓιикѕ"


def _prepare_session() -> requests.Session:
    """Prepare a wetransfer.com session.
    Return a requests session that will always pass the required headers
    and with cookies properly populated that can be used for wetransfer
    requests.
    """
    s = requests.Session()
    r = s.get("https://wetransfer.com/")
    m = re.search('name="csrf-token" content="([^"]+)"', r.text)
    s.headers.update(
        {
            "x-csrf-token": m.group(1),
            "x-requested-with": "XMLHttpRequest",
        }
    )

    return s


WETRANSFER_API_URL = "https://wetransfer.com/api/v4/transfers"
WETRANSFER_DOWNLOAD_URL = WETRANSFER_API_URL + "/{transfer_id}/download"


def wetransfer_ddl(url: str) -> str:
    """WeTransfer.com DDL link generator
    By https://github.com/dishapatel010"""

    if url.startswith("https://we.tl/"):
        r = requests.head(url, allow_redirects=True)
        url = r.url

    recipient_id = None
    params = urlparse(url).path.split("/")[2:]

    if len(params) == 2:
        transfer_id, security_hash = params
    elif len(params) == 3:
        transfer_id, recipient_id, security_hash = params
    else:
        return None

    j = {
        "intent": "entire_transfer",
        "security_hash": security_hash,
    }
    if recipient_id:
        j["recipient_id"] = recipient_id
    s = _prepare_session()
    r = s.post(WETRANSFER_DOWNLOAD_URL.format(transfer_id=transfer_id), json=j)

    j = r.json()
    if "direct_link" in j:
        return j["direct_link"]
    else:
        xo = f"The content is expired/deleted."
        return xo


def mdis_k(urlx):
    scraper = cloudscraper.create_scraper(interpreter="nodejs", allow_brotli=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    apix = f"http://x.egraph.workers.dev/?param={urlx}"
    time.sleep(3)
    try:
        response = scraper.get(apix, headers=headers)
        query = response.json()
    except BaseException:
        return "Invalid Link"
    return query


def mdisk_ddl(url: str) -> str:
    """MDisk DDL link generator
    By https://github.com/dishapatel010"""

    check = re.findall(r"\bhttps?://.*mdisk\S+", url)
    if not check:
        textx = f"Invalid mdisk url"
        return textx
    else:
        try:
            fxl = url.split("/")
            urlx = fxl[-1]
            uhh = mdis_k(urlx)
            try:
                text = uhh["download"]
            except BaseException:
                return "Invalid Link"
            return text
        except ValueError:
            textx = f"The content is deleted."
            return


def parse_info(res):
    f = re.findall(">(.*?)<\/td>", res.text)
    info_parsed = {}
    for i in range(0, len(f), 3):
        info_parsed[f[i].lower().replace(" ", "_")] = f[i + 2]
    return info_parsed


def sharerpw_dl(url: str, forced_login=False) -> str:
    """Sharerpw DDL link generator
    By https://github.com/xcscxr"""

    if Sharerpw_XSRF is None or Sharerpw_laravel is None:
        raise DirectDownloadLinkException("ERROR: Sharerpw Cookies not Found!")

    try:
        scraper = cloudscraper.create_scraper(allow_brotli=False)

        scraper.cookies.update(
            {"XSRF-TOKEN": Sharerpw_XSRF, "laravel_session": Sharerpw_laravel}
        )

        res = scraper.get(url)
        token = re.findall("_token\s=\s'(.*?)'", res.text, re.DOTALL)[0]

        ddl_btn = etree.HTML(res.content).xpath("//button[@id='btndirect']")

        info_parsed = parse_info(res)
        info_parsed["error"] = True
        info_parsed["src_url"] = url
        info_parsed["link_type"] = "login"  # direct/login
        info_parsed["forced_login"] = forced_login

        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
        }

        data = {"_token": token}

        if len(ddl_btn):
            info_parsed["link_type"] = "direct"
        if not forced_login:
            data["nl"] = 1

        try:
            res = scraper.post(url + "/dl", headers=headers, data=data).json()
        except BaseException:
            return info_parsed

        if "url" in res and res["url"]:
            info_parsed["error"] = False
            info_parsed["gdrive_link"] = res["url"]

        if len(ddl_btn) and not forced_login and "url" not in info_parsed:
            # retry download via login
            return sharerpw(url, forced_login=True)

        return info_parsed["gdrive_link"]

    except BaseException:
        raise DirectDownloadLinkException(f"Unable to Extract GDrive Link")


def megaup_dl(url: str) -> str:
    """client = cloudscraper.create_scraper(allow_brotli=False)
    resp = client.get(url)
    data = resp.text.split("DeObfuscate_String_and_Create_Form_With_Mhoa_URL(", 2)[2].split(");")[0].split(",")
    data = [a.strip("' ") for a in data]
    time.sleep(3)
    idurl = ""
    for i in range(int(len(data[0])/4) - 1, -1, -1):
        idurl += data[0][i]
    for i in range(int(len(data[0]) / 4 * 3 - 1), int(len(data[0]) / 4 * 2) - 1, -1):
        idurl += data[0][i]
    for i in range(int((len(data[1]) - 3) / 2 + 2), 2, -1):
        idurl += data[1][i]
    try:
        des_url = f"https://download.megaup.net/?idurl={idurl}&idfilename={data[2]}&idfilesize={data[3]}"
        return des_url
    except BaseException:
        return "Invalid Link" """
    return "вσт ¢αииσт ∂σωиℓσα∂ мєgαυρ.иєт ℓιикѕ"


"""
def cyberdrop_dl(url: str) -> str:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    items = soup.find_all("a", class_="image")
    for item in items:
        item_url = item['href']
        return item_url   """
