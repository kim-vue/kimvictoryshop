"""Optional real-browser smoke test; Playwright + Chromium required only here."""
from pathlib import Path
import json
import shutil
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright
from zoomconnect.server import make_server


def main():
    server = make_server(0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    output = ROOT / 'docs' / 'screenshots'
    output.mkdir(parents=True, exist_ok=True)
    errors = []
    checks = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=shutil.which('chromium'), headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage'],
            )
            try:
                page = browser.new_page(
                    viewport={'width': 1536, 'height': 1100},
                    device_scale_factor=1, timezone_id='Asia/Seoul',
                )
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(f'http://127.0.0.1:{server.server_port}', wait_until='networkidle')
                page.wait_for_function("document.querySelector('#path-input').value === 'zoom://world/MASTER'")
                checks.append('initial_runtime_state')
                page.locator('#path-input').fill('zoom://world/MASTER/COUPANG')
                page.locator('#url-form').get_by_role('button').click()
                page.wait_for_function("document.querySelector('#notice-text').textContent.includes('NOT_IN_LIST')")
                page.wait_for_function("document.querySelector('#path-input').value === 'zoom://world/MASTER'")
                checks.append('url_direct_jump_rejected')
                page.get_by_role('button', name='AI의 ZOOMBAR 보기', exact=True).click()
                page.wait_for_function("document.querySelector('#path-input').value === 'zoom://world/MASTER'")
                page.get_by_role('button', name='코드의 ZOOMBAR 보기', exact=True).click()
                page.get_by_role('button', name='위치 찾기 북마크의 목적지로 ZOOMBAR 이동').click()
                page.wait_for_function("document.querySelector('#path-input').value.endsWith('/GPS')")
                code_path = page.locator('#path-input').input_value()
                assert code_path.count('/') >= 6, code_path
                page.locator('#out-button').click()
                page.wait_for_function("!document.querySelector('#path-input').value.endsWith('/GPS')")
                checks.append('code_uses_real_route_and_history_return')
                page.get_by_role('button', name='사용자의 ZOOMBAR 보기', exact=True).click()
                page.wait_for_function("document.querySelector('#path-input').value === 'zoom://world/MASTER'")
                checks.append('actor_positions_independent')
                page.get_by_role('button', name='쿠팡 정산 북마크의 목적지로 ZOOMBAR 이동').click()
                page.wait_for_function("document.querySelector('#path-input').value === 'zoom://world/MASTER/DELIVERY/COUPANG'")
                checks.append('bookmark_travels_each_connection')
                page.locator('#run-button').click()
                page.wait_for_function("document.querySelector('#result-value').textContent.includes('13500')")
                assert '해시체인 검사 일치' in page.locator('#integrity-label').inner_text()
                checks.append('hash_calculation_13500_and_verified_chain')
                page.screenshot(path=str(output / 'desktop.png'), full_page=True)
                page.set_viewport_size({'width': 390, 'height': 844})
                assert not page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
                page.screenshot(path=str(output / 'mobile.png'), full_page=True)
                checks.append('mobile_no_horizontal_overflow')
                assert not errors, errors
                checks.append('no_uncaught_browser_errors')
                report = {'passed': len(checks), 'failed': 0, 'checks': checks, 'page_errors': errors}
                (ROOT / '.local').mkdir(exist_ok=True)
                (ROOT / '.local' / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
                print(json.dumps(report, ensure_ascii=False, indent=2))
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()
        server.application.demo.world.close()


if __name__ == '__main__':
    main()
