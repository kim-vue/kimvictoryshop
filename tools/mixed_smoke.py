"""Optional real-browser mixed collections / detach / reconnect validation."""
from pathlib import Path
import json
import re
import shutil
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from playwright.sync_api import sync_playwright
from zoomconnect.positions_server import make_position_server


def main():
    server=make_position_server(0)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    output=ROOT/'docs'/'screenshots';output.mkdir(parents=True,exist_ok=True)
    checks=[];errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
            try:
                page=browser.new_page(viewport={'width':1660,'height':1100},device_scale_factor=1,timezone_id='Asia/Seoul')
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{server.server_port}',wait_until='networkidle')
                page.wait_for_function("document.querySelector('#here').textContent === '0:0'")
                state=page.evaluate("fetch('/api/state?actor=USER').then(r=>r.json())")
                workspace=state['workspace'];w=workspace[0]
                page.locator('#main-board').get_by_role('button',name=f"0:{state['workspace_entry']} · USER 혼합 작업판 열기 선택",exact=True).click()
                page.wait_for_function(f"document.querySelector('#here').textContent === '{w}:0'")
                checks.append('enter_owned_workspace_through_zoombar')
                page.locator('#mix').click()
                page.wait_for_function("document.querySelector('#notice').textContent.includes('MIXED')")
                state=page.evaluate("fetch('/api/state?actor=USER').then(r=>r.json())")
                assert [s['target'] for s in state['view']['slots'][2:5]]==[e['target'] for e in state['mix_targets']]
                checks.append('actual_bridge_layer_bookmark_in_one_collection')
                page.get_by_role('button',name=f'{w}:2 · 연결 분리',exact=True).click()
                page.wait_for_function("document.querySelector('#notice').textContent.includes('SEPARATED')")
                assert page.locator('#main-board').get_by_role('button',name=f'{w}:2 · 위치 BRIDGE 연결 선택',exact=True).is_disabled()
                page.screenshot(path=str(output/'mixed-desktop.png'),full_page=True)
                checks.append('separate_preserves_cell_and_blocks_only_that_link')
                page.get_by_role('button',name=f'{w}:2 · 같은 칸 다시 연결',exact=True).click()
                page.wait_for_function("document.querySelector('#notice').textContent.includes('RECONNECTED')")
                page.locator('#main-board').get_by_role('button',name=f'{w}:2 · 위치 BRIDGE 연결 선택',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '4:0'")
                checks.append('reconnect_same_position_and_open_bridge')
                page.locator('#out').click()
                page.wait_for_function(f"document.querySelector('#here').textContent === '{w}:0'")
                page.locator('#main-board').get_by_role('button',name=f'{w}:3 · 배달 LAYER 연결 선택',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '1:0'")
                checks.append('same_open_engine_for_layer')
                page.locator('#out').click()
                page.wait_for_function(f"document.querySelector('#here').textContent === '{w}:0'")
                page.locator('#main-board').get_by_role('button',name=f'{w}:4 · 나의 BOOKMARK 연결 선택',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '7:0'")
                page.get_by_role('button',name='7:1 · 연결 분리',exact=True).click()
                page.wait_for_function("document.querySelector('#notice').textContent.includes('SEPARATED')")
                page.get_by_role('button',name='7:1 · 같은 칸 다시 연결',exact=True).click()
                page.wait_for_function("document.querySelector('#notice').textContent.includes('RECONNECTED')")
                state=page.evaluate("fetch('/api/state?actor=USER').then(r=>r.json())")
                assert state['view']['slots'][1]['traversable'] is False
                checks.append('real_bookmark_separate_reconnect_keeps_reference_policy')
                page.locator('#connection-title').fill('책갈피에서 레이어 연결')
                page.locator('#connection-target').fill('1:0')
                page.locator('#connection-form').get_by_role('button',name='연결 추가',exact=True).click()
                page.wait_for_function("document.querySelector('#notice').textContent.includes('CONNECTED')")
                page.locator('#main-board').get_by_role('button',name='7:5 · 책갈피에서 레이어 연결 선택',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '1:0'")
                checks.append('explicit_physical_connection_from_bookmark_to_layer')
                page.locator('#out').click()
                page.wait_for_function("document.querySelector('#here').textContent === '7:0'")
                page.locator('#bookmark-boards').get_by_role('button',name=re.compile(r'쿠팡 선택$')).click()
                page.wait_for_function("document.querySelector('#here').textContent === '2:0'")
                page.locator('#run').click()
                page.wait_for_function("document.querySelector('#run-result').textContent.includes('13500')")
                checks.append('bookmark_finds_real_route_and_hash_execution_still_works')
                page.get_by_role('button',name='AI의 독립 ZOOMBAR 보기',exact=True).click()
                page.wait_for_function("document.querySelector('#here').textContent === '0:0'")
                checks.append('other_actor_keeps_independent_private_worlds')
                page.set_viewport_size({'width':390,'height':844})
                assert not page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
                page.screenshot(path=str(output/'mixed-mobile.png'),full_page=True)
                checks.append('mobile_layout_without_document_overflow')
                assert not errors,errors
                checks.append('no_uncaught_browser_errors')
                report={'passed':len(checks),'failed':0,'checks':checks,'page_errors':errors}
                (ROOT/'.local'/'mixed-browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
                print(json.dumps(report,ensure_ascii=False,indent=2))
            finally:
                browser.close()
    finally:
        server.shutdown();thread.join(timeout=3);server.server_close();server.application.demo.world.close()


if __name__=='__main__':
    main()
