import time
from selenium.webdriver.common.by import By
import requests
from Constants import Constants
from bs4 import BeautifulSoup

def isModelOnline(mfcUserName):
    isOnline = False
    title = Constants.mfcDefaultTitle
    thumbUrl = ""
    icon = 'images/errIcon.png'
    try:
        print(f"Checking https://share.myfreecams.com/{mfcUserName} ...")
        request = requests.get(f"https://share.myfreecams.com/{mfcUserName}")
        time.sleep(1)
        soup = BeautifulSoup(request.content, "html.parser")
        vidPreview = soup.find(class_='campreview-link')
        if vidPreview:
            isOnline = True
            icon = soup.find(class_='avatar online').find("img")['src'] if soup.find(class_='avatar online') else soup.find(class_='avatar').find("img")['src']
    except requests.exceptions.ConnectTimeout:
        print("connection timed out to share.myfreecams.com. Bot detection or rate limited?")
    print(f"MFC isOnline = {isOnline}")
    return isOnline, title, thumbUrl, icon