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
        channel_id = os.getenv("SCHOLARSHIP_CHANNEL_ID")  # 환경 변수에서 채널 ID 불러오기

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
    
    page.wait_for_selector('li.c_node > a.depth1.c_nodeA:has-text("등록/장학")', timeout=10000)
    page.click('li.c_node > a.depth1.c_nodeA:has-text("등록/장학")')
    
    # page.wait_for_selector('li.c_node > a.c_nodeA:has-text("장학")', timeout=10000)
    # page.click('li.c_node > a.c_nodeA:has-text("장학")')

    # "장학" 링크를 선택하여 클릭합니다.
    page.wait_for_selector('li.c_node.active > div.depth2_w > ul > li > a.c_nodeA', timeout=10000)
    page.click('li.c_node.active > div.depth2_w > ul > li > a.c_nodeA:has-text("장학")')

    
    page.wait_for_load_state('networkidle')
    
    iframe = page.frame(name="isolatedWorkArea")

    # 여기만 바꿔주면 됩니다.
    try:
        html_content = iframe.content() 

        soup = BeautifulSoup(html_content, 'html.parser')

        tbody = soup.find("tbody", id="WDFD-contentTBody")

        previous_text = None

        # 2학기 (sst="1") 인 요소 찾기
        selected_tr = []
        for tr in tbody.find_all("tr"):
            sst_value = int(tr.get('sst', -1))
            if sst_value == 1:
                selected_tr.append(tr)

        # cc가 2부터 8인 <td> 요소 찾기
        selected_td = []
        for tr in selected_tr:
            for td in tr.find_all("td"):  # 각 <tr> 내부의 <td> 요소를 찾아야 합니다.
                cc_value = int(td.get('cc', -1))
                if 2 <= cc_value <= 8:
                    selected_td.append(td)

        # 선택된 <td> 요소의 <span> 요소 가져오기
        a = []
        previous_text = None

        for td in selected_td:
            spans = td.find_all("span")
            for span in spans:
                text = span.text.strip()
                if text != previous_text:
                    if text == "1 학기" or text == "2 학기":
                        a.append("===========")
                    a.append(text)
                    previous_text = text
        if a:
            send_slack_message("<!channel> 장학정보를 불러왔어요")
            send_slack_message("\n".join(a))


    except Exception as e:
        send_slack_message(f"요소를 찾지 못했거나 클릭할 수 없습니다: {e}")

    time.sleep(2)
    
    # 컨텍스트와 브라우저를 닫습니다.
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
