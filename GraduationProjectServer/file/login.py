#!/usr/bin/python3
import time
from selenium import webdriver
browser = webdriver.Chrome()
try:
    browser.get("http://210.31.224.243/0.htm")
except:
    print("open fail")
elem_username = browser.find_element_by_id("username")
ele_passwd = browser.find_element_by_id("password")
elem_username.send_keys("2014405A111")
ele_passwd.send_keys("20111114guang.")
elem = browser.find_element_by_id("submit")
elem.click()
time.sleep(2)
browser.quit()
