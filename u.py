from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    
    context = browser.new_context(viewport={"width": 1280, "height": 1280})
    
    page = context.new_page()
    
    page.goto("https://saint.ssu.ac.kr/irj/portal")
    
    page.wait_for_selector("button.btn_login", timeout=10000)
    page.click("button.btn_login")
    
    page.wait_for_selector('input[placeholder="직번/학번을 입력하세요"]', timeout=10000)
    page.fill('input[placeholder="직번/학번을 입력하세요"]', "aaa")
    
    page.wait_for_selector('input[placeholder="비밀번호를 입력하세요"]', timeout=10000)
    page.fill('input[placeholder="비밀번호를 입력하세요"]', "aaa")
    
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

        for span in spans[16:]:
            text = span.text.strip()

            if text != previous_text:
                print(text)
                previous_text = text
                if text.isdigit() and len(text) >= 4:
                    print("========")

    except Exception as e:
        print(f"요소를 찾지 못했거나 클릭할 수 없습니다: {e}")

    time.sleep(2)
    
    # 컨텍스트와 브라우저를 닫습니다.
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
