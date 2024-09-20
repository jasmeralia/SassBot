from Constants import Constants
import re
import asyncio
import nodriver as uc
import NoDriverBrowserCreator as ndb

async def GetIcon(page:uc.Tab):
    icon = 'images/errIcon.png'
    reString = r'^https:\/\/.+avatar.jpg$'
    try:
        imageElements = await page.find_all("data-v-325c6981")
        for element in imageElements:
            if element.attrs.get("src") and re.search(reString, element.attrs.get("src")):
                icon = element.attrs.get("src")
    except:
        pass
    return icon

async def IsLiveBadge(page:uc.Tab):
    live = False
    try:
        liveBadge = await page.find("g-avatar__icon m-live", best_match=True)
        if liveBadge:
            live = True
    except TimeoutError:
        pass
    return live

async def GetOnlineStatus(ofUserName):
    isOnline = False
    ofUrl = f"https://onlyfans.com/{ofUserName}"
    title = Constants.ofDefaultTitle
    thumbUrl = ""
    icon = 'images/errIcon.png'
    try:
        browser = await ndb.GetBrowser()
        asyncio.sleep(10)
        page = await browser.get(ofUrl)
        isOnline = await IsLiveBadge(page)
        icon  = await GetIcon(page)
        await page.close()
        ndb.killBrowser(browser)
    except Exception as e:
        print(f"Error getting browser for Onylyfans: {e}")
    return isOnline, title, thumbUrl, icon


def isModelOnline(ofUserName):
    isOnline, title, thumbUrl, icon = uc.loop().run_until_complete(GetOnlineStatus(ofUserName))

    return isOnline, title, thumbUrl, icon
