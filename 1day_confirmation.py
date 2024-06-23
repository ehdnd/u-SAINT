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
        slack_token = os.getenv("SLACK_TOKEN")
        client = WebClient(token=slack_token)
        channel_id = os.getenv("CHANNEL_ID")

        client.chat_postMessage(
            channel=channel_id,
            text=text
        )
    except SlackApiError as e:
        print(f"Slack API error occurred: {e.response['error']}")

def run(page, ID, PASSWORD):
    try:
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
            
            return messages

        except Exception as e:
            send_slack_message(f"요소를 찾지 못했거나 클릭할 수 없습니다: {e}")
            return None
    
    except Exception as e:
        send_slack_message(f"스크립트 실행 중 오류 발생: {e}")
        return None

def main():
    previous_message = None
    start_time = time.time()
    duration = 24 * 60 * 60

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 1280})
        page = context.new_page()

        ID = os.getenv("ID")
        PASSWORD = os.getenv("PASSWORD")

        try:
            while True:
                current_time = time.time()
                elapsed_time = current_time - start_time

                if elapsed_time > duration:
                    break

                current_message = run(page, ID, PASSWORD)

                if previous_message is not None and previous_message != current_message:
                    send_slack_message("<!channel> 성적 업데이트")
                    send_slack_message("\n".join(current_message))

                previous_message = current_message
                time.sleep(1800)
                page.reload()
                
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    main()
