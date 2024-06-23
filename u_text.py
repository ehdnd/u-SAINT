from playwright.sync_api import sync_playwright
import time

p = sync_playwright().start()

browser = p.chromium.launch(headless=False)

page = browser.new_page()

page.goto("https://saint.ssu.ac.kr/irj/portal")

time.sleep(1)

page.click("button.btn_login")

time.sleep(1)

page.get_by_placeholder("직번/학번을 입력하세요").fill("aaa")

time.sleep(1)

page.get_by_placeholder("비밀번호를 입력하세요").fill("aaa")

time.sleep(1)

page.keyboard.down("Enter")

time.sleep(1)

page.click('li.c_node > a.depth1.c_nodeA:has-text("학사관리")')

time.sleep(1)

page.click('li.c_node > a.c_nodeA:has-text("성적/졸업")')

time.sleep(3)

page.keyboard.down("End")


time.sleep(2)

p.stop()