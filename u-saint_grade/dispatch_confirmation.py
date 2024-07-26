from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

load_dotenv()

def send_slack_message(text):
    try:
        slack_token = os.getenv("SLACK_TOKEN")  # 환경 변수에서 Slack 토큰 불러오기
        client = WebClient(token=slack_token)
        channel_id = os.getenv("GRADE_CHANNEL_ID")  # 환경 변수에서 채널 ID 불러오기

        client.chat_postMessage(
            channel=channel_id,
            text=text
        )
    except SlackApiError as e:
        print(f"Slack API error occurred: {e.response['error']}")

def run(playwright):

    ID = os.getenv("ID")
    PASSWORD = os.getenv("PASSWORD")

    browser = playwright.chromium.launch(headless=True)
    
    context = browser.new_context(viewport={"width": 1280, "height": 1280})
    
    page = context.new_page()
    
    page.goto("https://saint.ssu.ac.kr/irj/portal")
    
    page.wait_for_selector("button.btn_login", timeout=10000)
    page.click("button.btn_login")
    
    page.wait_for_selector('input[placeholder="직번/학번을 입력하세요"]', timeout=10000)
    page.fill('input[placeholder="직번/학번을 입력하세요"]', ID)
    
    page.wait_for_selector('input[placeholder="비밀번호를 입력하세요"]', timeout=10000)
    page.fill('input[placeholder="비밀번호를 입력하세요"]', PASSWORD)
    
    page.keyboard.press("Enter")
    
    page.wait_for_selector('li.c_node > a.depth1.c_nodeA:has-text("학사관리")', timeout=10000)
    
    page.click('li.c_node > a.depth1.c_nodeA:has-text("학사관리")')
    
    page.wait_for_selector('li.c_node > a.c_nodeA:has-text("성적/졸업")', timeout=10000)
    page.click('li.c_node > a.c_nodeA:has-text("성적/졸업")')
    
    page.wait_for_load_state('networkidle')
    
    iframe = page.frame(name="isolatedWorkArea")

    # 여기만 바꿔주면 됩니다.
    try:
        iframe.wait_for_selector(".lsButton--design-previous", timeout=10000)
        iframe.click(".lsButton--design-previous")

        time.sleep(5)

        html_content = iframe.content() 

        soup = BeautifulSoup(html_content, 'html.parser')

        tbody = soup.find("tbody", id="WD0173-contentTBody")

        spans = tbody.find_all("span")

        previous_text = None

        messages = ["==========="]

        for span in spans[16:]:
            text = span.text.strip()

            if text != previous_text and text != "조회":
                messages.append(text)
                previous_text = text
                if text.isdigit() and len(text) >= 4:
                    messages.append("===========")
        
        if messages:
            send_slack_message("<!channel> 성적을 불러왔어요")
            send_slack_message("\n".join(messages))

    except Exception as e:
        send_slack_message(f"요소를 찾지 못했거나 클릭할 수 없습니다: {e}")

    time.sleep(2)
    
    # 컨텍스트와 브라우저를 닫습니다.
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
