import requests
import random
import nodriver as uc
import globals
import asyncio
import ctypes
import os
import platform
import psutil
import logging
from DefaultConstants import Settings as Settings

baseSettings = Settings()

logger = logging.getLogger(__name__)
logger.setLevel(baseSettings.SASSBOT_LOG_LEVEL)

def KillUnconncetedBrowsers():
    PROCNAMES = ["google-chrome",
                "chromium",
                "chromium-browser",
                "chrome",
                "google-chrome-stable"]
    numBrowserProcesses = 0
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() in PROCNAMES:
            numBrowserProcesses = numBrowserProcesses + 1
            try:
                proc.terminate()
            except Exception as e:
                proc.kill()
                logger.warning(e)
    if numBrowserProcesses > 0:
        logger.debug(f"Tried to kill {numBrowserProcesses} browser processes.")

def getUserAgent():
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/127.0.2651.105"
        try:
            page = requests.get('https://jnrbsn.github.io/user-agents/user-agents.json')
            userAgentsJson = page.json()
            userAgent = random.choice(userAgentsJson)
            page.close()
        except Exception:
            logger.warning("Trouble getting user agent from jnrbsn's github. Using default")
        return userAgent

def LogProcessMemory(stage, browser=None, checkName=None):
    try:
        process = psutil.Process()
        children = process.children(recursive=True)
        childRss = 0
        browserRss = 0
        for child in children:
            try:
                rss = child.memory_info().rss
                childRss += rss
                if browser and child.pid == getattr(browser, "_process_pid", None):
                    browserRss = rss
            except psutil.Error:
                continue
        ownRss = process.memory_info().rss
        logger.debug(
            "process memory platform=%s stage=%s python_rss_mib=%.1f child_count=%d "
            "child_rss_mib=%.1f browser_pid=%s browser_rss_mib=%.1f",
            checkName or "unknown",
            stage,
            ownRss / (1024 * 1024),
            len(children),
            childRss / (1024 * 1024),
            getattr(browser, "_process_pid", None),
            browserRss / (1024 * 1024),
        )
    except psutil.Error:
        logger.debug("could not collect process memory platform=%s stage=%s", checkName or "unknown", stage, exc_info=True)

async def GetBrowser(proxy="", checkName=None):
    while globals.browserOpen:
        await asyncio.sleep(2 * baseSettings.NODRIVER_WAIT_MULTIPLIER)
    try:
        globals.browserOpen = True
        await asyncio.sleep(1 * baseSettings.NODRIVER_WAIT_MULTIPLIER)
        toSandbox = not IsRoot()
        toHeadless = False if platform.system() == "Linux" else True
        dataDir = "/ndTemp" if platform.system() == "Linux" else None
        if proxy:
            browser = await uc.start(sandbox=toSandbox,
                                headless=toHeadless,
                                browser_args=[f'--proxy-server={proxy}','--mute-audio','--disable-3d-apis','--disable-dev-shm-usage','--disable-gpu'],
                                retries = baseSettings.NODRIVER_BROWSER_CONNECT_RETRIES,
                                user_data_dir=dataDir
                                )
        else:
            browser = await uc.start(sandbox=toSandbox,
                                headless=toHeadless,
                                browser_args=['--mute-audio','--disable-3d-apis','--disable-dev-shm-usage','--disable-gpu'],
                                retries = baseSettings.NODRIVER_BROWSER_CONNECT_RETRIES,
                                user_data_dir=dataDir
                                )
        LogProcessMemory("browser_started", browser, checkName)
        return browser
    except Exception as e:
        logger.warning(f"error creating browser in GetBrowser: {e}")
        await asyncio.sleep(1 *  baseSettings.NODRIVER_WAIT_MULTIPLIER)
        KillUnconncetedBrowsers()
        await asyncio.sleep(1 *  baseSettings.NODRIVER_WAIT_MULTIPLIER)
        globals.browserOpen = False

# Taken from https://github.com/ultrafunkamsterdam/nodriver/blob/1bb6003c7f0db4d3ec05fdf3fc8c8e0804260103/nodriver/core/config.py#L240
def IsRoot():
    """
    helper function to determine if user trying to launch chrome
    under linux as root, which needs some alternative handling
    :return:
    :rtype:
    """

    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

async def CloseNDBrowser(browser, page=None, checkName=None):
    try:
        if page is not None:
            try:
                await page.close()
            except Exception:
                logger.debug("could not close browser page", exc_info=True)
        if browser is not None:
            LogProcessMemory("browser_closing", browser, checkName)
            try:
                browser.stop()
            except Exception:
                logger.warning("could not stop browser", exc_info=True)
            await asyncio.sleep(1 * baseSettings.NODRIVER_WAIT_MULTIPLIER)
        if browser is not None and platform.system() == "Linux":
            try:
                KillUnconncetedBrowsers()
            except Exception:
                logger.warning("could not clean up remaining browser processes", exc_info=True)
    finally:
        globals.browserOpen = False
        LogProcessMemory("browser_closed", checkName=checkName)
