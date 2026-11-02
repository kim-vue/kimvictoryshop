"""Optional real-browser validation of the positional collection model."""
from pathlib import Path
import json
import re
import shutil
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from playwright.sync_api import sync_playwright
from zoomconnect.positions_server import make_position_server


def main():
    server = make_position_server(0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    output = ROOT / 'docs' / 'screenshots'
    output.mkdir(parents=True, exist_ok=True)
    checks, errors = [], []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
            try:
                page = browser.new_page(viewport={'width':1600,'height':1100},device_scale_factor=1,timezone_id='Asia/Seoul')
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(f'http://127.0.0.1:{server.server_port}',wait_until='networkidle')
                page.wait_for_function("document.querySelector('#here').textContent === '0:0'")
                checks.append('real_root_collection_at_0_0')
                page.locator('#bookmark-boards').get_by_role('button',name=re.compile(r'쿠팡 선택$')).click()
                page.wait_for_function("document.querySelector('#here').textContent === '2:0'")
                assert page.locator('#url-input').input_value() == 'zoom://world/0:0/1/1'
                checks.append('bookmark_selects_reference_and_walks_real_positions')
                page.locator('#run').click()
                page.wait_for_function("document.querySelector('#run-result').textContent.includes('13500')")
                checks.append('positional_hash_execution_13500')
                page.screenshot(path=str(output/'positions-execution.png'),full_page=True)
                page.locator('#root').click()
                page.wait_for_function("document.querySelector('#here').textContent === '0:0'")
                page.locator('#main-board').get_by_role('button',name='0:1 · 배달 목록 열기 선택',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '1:0'")
                old_revision=page.evaluate("fetch('/api/state?actor=USER').then(r=>r.json()).then(s=>s.view.revision)")
                page.get_by_role('button',name='1:1 · 아래 칸과 내용 교환',exact=True).click()
                page.wait_for_function("document.querySelector('#change-list').textContent.includes('쿠팡으로 가는 칸 → 배민으로 가는 칸')")
                checks.append('reorder_keeps_1_1_and_changes_occupant_to_baemin')
                stale=page.evaluate("""async (revision)=>{const r=await fetch('/api/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({actor:'USER',action:'open',position:1,expected_revision:revision})});return {status:r.status,body:await r.json()};}""",old_revision)
                assert stale['status']==400 and stale['body']['error']['code']=='STALE_VIEW',stale
                checks.append('old_view_cannot_select_changed_content')
                page.screenshot(path=str(output/'positions-desktop.png'),full_page=True)
                page.locator('#main-board').get_by_role('button',name='1:1 · 배민으로 가는 칸 선택',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '3:0'")
                checks.append('same_slot_now_opens_new_target_3_0')
                page.get_by_role('button',name='코드의 독립 ZOOMBAR 보기',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '0:0'")
                page.locator('#main-board').get_by_role('button',name='0:2 · 고정 위치 참조 열기 선택',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '6:0'")
                page.locator('#main-board').get_by_role('button',name='6:1 · 배달 목록의 1번 칸 참조 선택',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '1:1'")
                current=page.evaluate("fetch('/api/state?actor=CODE').then(r=>r.json()).then(s=>s.current)")
                assert current['target']==[3,0] and current['title']=='배민으로 가는 칸',current
                checks.append('independent_pinned_reference_stays_at_1_1_not_old_content')
                page.get_by_role('button',name='사용자의 독립 ZOOMBAR 보기',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '3:0'")
                checks.append('actors_keep_independent_zoombar_collections')
                page.locator('#out').click()
                page.wait_for_function("document.querySelector('#here').textContent === '1:0'")
                checks.append('out_uses_saved_visit_cells')
                page.set_viewport_size({'width':390,'height':844})
                assert not page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
                page.screenshot(path=str(output/'positions-mobile.png'),full_page=True)
                checks.append('mobile_no_document_overflow')
                assert not errors,errors
                checks.append('no_uncaught_browser_errors')
                report={'passed':len(checks),'failed':0,'checks':checks,'page_errors':errors}
                (ROOT/'.local').mkdir(exist_ok=True)
                (ROOT/'.local'/'positions-browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
                print(json.dumps(report,ensure_ascii=False,indent=2))
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()
        server.application.demo.world.close()


if __name__=='__main__':
    main()
