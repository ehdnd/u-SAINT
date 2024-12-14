from utils.scraper import Scraper
from utils.slack_notifier import SlackNotifier
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os


def grade_scraper():
    ID = os.getenv("ID")
    PASSWORD = os.getenv("PASSWORD")
    SLACK_TOKEN = os.getenv("SLACK_TOKEN")
    GRADE_CHANNEL_ID = os.getenv("GRADE_CHANNEL_ID")

    notifier = SlackNotifier(SLACK_TOKEN, GRADE_CHANNEL_ID)
    url = "https://saint.ssu.ac.kr/irj/portal"

    with sync_playwright() as p:
        scraper = Scraper(ID, PASSWORD)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            scraper.login(page, url)
            content = scraper.fetch_page_content(
                page,
                'li.c_node > a.depth1.c_nodeA:has-text("학사관리")',
                "isolatedWorkArea",
            )

            soup = BeautifulSoup(content, "html.parser")
            tbody = soup.find("tbody", id="WD0188-contentTBody")
            spans = tbody.find_all("span")

            messages = ["==========="]
            for span in spans[16:]:
                text = span.text.strip()
                if text.isdigit() and len(text) >= 4:
                    messages.append("===========")
                messages.append(text)

            notifier.send_message("<!channel> 성적을 불러왔어요")
            notifier.send_message("\n".join(messages))
        except Exception as e:
            notifier.send_message(f"오류 발생: {e}")
        finally:
            context.close()
            browser.close()
