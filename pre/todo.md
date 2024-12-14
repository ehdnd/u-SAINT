# chat-gpt에게 질문

1. 현재 파일 디렉토리 상황
   .:
   u-saint_grade u-saint_scholarship u.py u_text.py

./u-saint_grade:
1day_confirmation.py dispatch_confirmation.py

./u-saint_scholarship:
scholarship.py

2. 현재 필요한 파일

   1. u-saint_grade/dispatch_confirmation.py: 웹사이트에 로그인해서 성적 파트만 불러온 후 슬랙 메시지 전송
   2. u-saint_scholarship/scholarship.py: 웹사이트에 로그인해서 장학 파트만 불러온 후 슬랙 메시지 전송

3. 현재 필요한 파일에 있어서 겹치는 함수들이 있음. 모듈화 해서 관리하고 싶다

4. 참고를 위한 현재 프로그램 내용

   1. dispatch

   ```
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

       # page.wait_for_selector('li.c_node > a.depth1.c_nodeA:has-text("학사관리")', timeout=10000)
       # page.click('li.c_node > a.depth1.c_nodeA:has-text("학사관리")')

       page.wait_for_selector('li.c_node > a.depth1.c_nodeA:has-text("학사관리")', timeout=10000)
       page.click('li.c_node > a.depth1.c_nodeA:has-text("학사관리")')

       # page.wait_for_selector('li.c_node > a.c_nodeA:has-text("성적/졸업")', timeout=10000)
       # page.click('li.c_node > a.c_nodeA:has-text("성적/졸업")')

       page.wait_for_selector('li.c_node.active > div.depth2_w > ul > li > a.c_nodeA', timeout=10000)
       page.click('li.c_node.active > div.depth2_w > ul > li > a.c_nodeA:has-text("성적/졸업")')

       page.wait_for_load_state('networkidle')

       iframe = page.frame(name="isolatedWorkArea")

       try:
           iframe.wait_for_selector(".lsButton--design-previous", timeout=10000)
           # 이전 버튼
           # iframe.click(".lsButton--design-previous")

           time.sleep(5)

           html_content = iframe.content()

           soup = BeautifulSoup(html_content, 'html.parser')


           # id 계속 변경됨
           tbody = soup.find("tbody", id="WD0188-contentTBody")

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

   ```

   2. scholarship.py 파일

   ```
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

   ```

5. 요구사항

   1. 제시된 파일을 보고 목적과 상황에 맞게 파일 구조를 디자인해줘
   2. 어떤 식으로 모듈화 해야할 지 추천해줘
   3. 파일명과 함수명 또한 추천부탁해

6. 최종 목적?
   이러한 코드의 최종 목표는 서버가 없는 상황에서 깃허브 워크플로우를 사용하는 거야
   워크 플로우를 실행하면 웹 스크래핑 해서 슬랙으로 필요한 정보를 보내주는거지
