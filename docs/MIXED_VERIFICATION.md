# 혼합·분리·재연결 실제 검증

검증일 2026-11-02 (Asia/Seoul). Linux / Python 3.12.14 / Chromium에서 실행했습니다. Windows 직접 실행·파일 전송은 수행하지 않았습니다.

## 결과

| 실행 | 실제 결과 |
|---|---|
| 전체 unittest discovery | **164개 통과, 실패·건너뜀 0개** |
| 새 혼합 코어 검사 | **17개 통과** |
| 새 HTTP 추가 검사 | **3개 통과** |
| 실제 브라우저 혼합 흐름 | **11개 확인, 미처리 JS 오류 0개** |
| mixed-demo | BRIDGE·LAYER·실제 BOOKMARK 진입, 분리·동일 위치 재연결, 감사 일치 |

기존 144개와 이번 추가 20개를 구분합니다. 전체 숫자를 모두 이번 기능의 신규 검사로 부르지 않습니다.

## 검증한 동작

- 진짜 소유자 BOOKMARK·BRIDGE·LAYER가 같은 목록에 공존하고 같은 open으로 이동.
- LAYER → BRIDGE → BOOKMARK의 실제 중첩 방문 경로.
- 분리는 연결 칸의 내용·좌표를 보존하고 해당 칸만 끔.
- 같은 목적지의 다른 연결과 다른 컬렉션의 연결은 유지.
- 재연결은 같은 좌표, 새 revision, 이전 조회 거부.
- 새 대상 재연결, 빈 칸 명시 재사용, 점유 칸 덮어쓰기 거부.
- 사용 중인 연결을 분리하면 STALE_PATH와 SAFE_RETURN, 재연결 후 다시 진입.
- 혼합 배치 중 한 대상이 거부되면 전체 롤백, 부분 연결·성공 이벤트 없음.
- 다른 소유자 사적 컬렉션·대상 READ/MOVE 부족·게시판 WRITE 부족 거부.
- 북마크 참조의 traversable=False를 유지하고, 명시적으로 추가한 실제 연결만 이동 경로로 사용.
- 실제 BOOKMARK에 새 LAYER 연결 추가·이동 후 목적지 경로 탐색과 13500 HASH 실행.
- 두 독립 DB 연결이 동일 조회로 동시에 혼합하면 한 배치만 적용.
- 보호된 ZOOMBAR 시스템 이력 편집 거부.

## 화면 검증

`python tools/mixed_smoke.py`를 실행했습니다. Playwright·Chromium은 선택 개발 검사 도구이며 앱 실행 의존성은 아닙니다.

실제 화면: `screenshots/mixed-desktop.png`, `screenshots/mixed-mobile.png`.
결과 원문: `mixed-test-results.txt`, `mixed-browser-results.json`, `mixed-demo-result.json`.

## 범위

혼합은 독립된 대상 위치 참조를 한 컬렉션에 함께 배치하는 기능입니다. 대상 내부 데이터·권한·신원을 합치거나 다른 렌즈를 소유하는 기능은 아닙니다. 이동은 실제 ZOOMBAR와 권한·revision 검사를 계속 거칩니다.

운영 MASTER 일회용 승인·롤백, 전체 CHECK/LENSFIX/SELF_GROWTH, REA 자동 제작 공장, 비신뢰 플러그인의 OS 격리는 여전히 미구현입니다.
