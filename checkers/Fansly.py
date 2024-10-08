from Constants import Constants
import asyncio
import nodriver as uc
import NoDriverBrowserCreator as ndb
from pyvirtualdisplay import Display
import globals
import platform

def isModelOnline(fansUserName):
    isOnline, title, thumbUrl, icon = uc.loop().run_until_complete(GetOnlineStatus(fansUserName))
    return isOnline, title, thumbUrl, icon

async def GetOnlineStatus(fansUserName):
    fansUrl = f"https://fansly.com/{fansUserName}"
    thumbUrl = ""
    title = Constants.fansDefaultTitle
    isOnline = False
    icon = 'images/errIcon.png'
    try:
        if platform.system() == "Linux":
            display = Display(visible=0, size=(1080,720))
            display.start()
        browser = await ndb.GetBrowser()
        await asyncio.sleep(10)
        page = await browser.get(fansUrl)
        await asyncio.sleep(10)
        await ClickEnterButton(page)
        isOnline = await IsLiveBadge(page)
        await asyncio.sleep(2)
        icon = await GetIcon(page)
        await page.save_screenshot("Fansscreenshot.jpg")
        await page.close()
        await asyncio.sleep(2)
        browser.stop()
        await asyncio.sleep(2)
        globals.browserOpen = False
        if platform.system() == "Linux": display.stop()
    except Exception as e:
        print(f"Error when getting browser for Fansly: {e}")
        globals.browserOpen = False
    return isOnline, title, thumbUrl, icon

async def ClickEnterButton(page:uc.Tab):
    try:
        enterBtn = await page.find("Enter",best_match=True)
        if enterBtn:
            await enterBtn.click()
            await asyncio.sleep(5)
    except TimeoutError:
        pass

async def IsLiveBadge(page:uc.Tab):
    live = False
    try:
        liveBadge = await page.find("live-badge bold font-size-sm", best_match=True)
        if liveBadge:
            live = True
    except TimeoutError:
        pass
    return live

async def GetIcon(page:uc.Tab):
    icon = 'images/errIcon.png'
    try:
        iconElements = await page.find_all("image cover")
        await iconElements[1].click()
        await asyncio.sleep(2)
        iconElement = await page.find("image-overlay-flex", best_match=True)
        await iconElement.save_screenshot( "images/fansIcon.jpg")
        icon = "images/fansIcon.jpg"
    except:
        pass
    return icon
