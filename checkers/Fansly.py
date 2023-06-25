import time
from selenium.webdriver.common.by import By
from SeleniumDriverCreator import SeleniumDriverCreator
from Constants import Constants
import StaticMethods


def isModelOnline(fansUrl):
    thumbUrl = ""
    icon = 'images/errIcon.png'
    isOnline = False
    title = Constants.fansDefaultTitle
    driverCreator = SeleniumDriverCreator()
    driver = driverCreator.createDriver()
    driver.get(fansUrl)
    time.sleep(10)
    #driver.get_screenshot_as_file("Fansscreenshot.png")
    online = driver.find_elements(By.XPATH, '/html/body/app-root/div/div[1]/div/app-profile-route/div/div/div/div[1]/div[2]/div[1]/app-account-avatar/div')
    iconEle = driver.find_elements(By.TAG_NAME, 'img')
    if len(iconEle) >= 5:
        byte = StaticMethods.get_file_content_chrome(driver, iconEle[4].get_attribute('src'))
        file = open("images/fansIcon.jpg", 'wb')
        file.write(byte)
        file.close()
        icon = "images/fansIcon.jpg"
    driver.quit()
    if len(online) > 0:
        isOnline = True
    return isOnline, title, thumbUrl, icon


    