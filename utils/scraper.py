from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, id, password):
        self.id = id
        self.password = password

    def login(self, page, url):
        page.goto(url)
        page.wait_for_selector("button.btn_login", timeout=10000)
        page.click("button.btn_login")
        page.fill('input[placeholder="직번/학번을 입력하세요"]', self.id)
        page.fill('input[placeholder="비밀번호를 입력하세요"]', self.password)
        page.keyboard.press("Enter")

    # def fetch_page_content(self, page, selector, iframe_name=None):
    #     page.wait_for_selector(selector, timeout=10000)
    #     page.click(selector)
    #     page.wait_for_load_state("networkidle")
    #     if iframe_name:
    #         iframe = page.frame(name=iframe_name)
    #         return iframe.content()
    #     return page.content()

    def fetch_page_content(
        self, page, selectors, isPrev, iframe_name="isolatedWorkArea"
    ):
        for selector in selectors:
            page.wait_for_selector(selector, timeout=10000)
            page.click(selector)

        page.wait_for_load_state("networkidle")

        iframe = page.frame(name=iframe_name)
        if isPrev:
            iframe.wait_for_selector(".lsButton--design-previous", timeout=10000)
            iframe.click(".lsButton--design-previous")

        # page.wait_for_load_state("networkidle")
        time.sleep(5)

        return iframe.content()
