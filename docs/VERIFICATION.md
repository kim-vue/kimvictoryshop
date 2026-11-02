# 실제 검증 기록

검증일: 2026-11-02 (Asia/Seoul). 실행 환경: Linux, Python 3.12.14, Chromium.

## 실행한 검사

| 검사 | 실제 결과 |
|---|---|
| `python -m unittest discover -s tests -v` | **78개 실행, 78개 통과, 실패·건너뜀 0개** |
| `python -m zoomconnect demo` | 실제 이동, 독립 주체, 결과 `13500`, 업무 반환값 `None`, 감사 체인 일치 |
| `python tools/browser_smoke.py` | **8개 실제 브라우저 흐름 확인**, 실패·미처리 JS 오류 0개 |
| 데스크톱 화면 | 실제 API로 쿠팡 이동·계산 후 캡처 |
| 모바일 화면 | 폭 390px에서 가로 넘침 없음, 실제 화면 캡처 |
| Python 컴파일 | 통과 |
| UI JavaScript `node --check` | 통과 |
| 코어 AST | If / IfExp / While / Match / 중첩 Attribute: 각각 0개 |

시험 원문은 `test-results.txt`, 브라우저 흐름 결과는 `browser-results.json`, CLI 결과는 `demo-result.json`에 있습니다. 이미지는 `screenshots/`에 있습니다.

## 의미 있는 실행 검증

- 기존 코어 변경 없이 임의의 새 LENS 종류로 이동.
- BRIDGE와 LAYER에 같은 ZOOMBAR 동작 적용.
- UID·URL·북마크를 알아도 연결 또는 권한이 없으면 이동 거부.
- USER와 CODE의 독립 방문 이력, 같은 주체의 독립 세션.
- 남의 세션 ID나 actor ID만으로 인증 우회 불가.
- 한방향 신규 진입과 기존 방문 경로 복귀 구분.
- 연결 단절·권한 회수 후 SAFE_RETURN.
- READ만으로 WRITE 불가, EXECUTE만으로 결과 WRITE 불가.
- 현재 LENS와 다른 HASH 읽기 거부, 저장 시 원본 자료의 스냅샷 유지.
- SQLite 재시작 후 경로·데이터·감사 이력 복원.
- 다중 스레드와 독립 DB 연결에서 이동·쓰기·감사 검증.
- 동일 DB·동일 세션에서 동시 두 방향 이동 40라운드: 매번 한 이동만 성공.
- 잘못된 실행 입력으로 CYCLE_DONE 성공 이벤트가 생기지 않음.
- 기록 내용 변경·잘못된 JSON·꼬리 삭제·전체 삭제 검출.

## 실제로 발견하고 수정한 결함

1. 읽기 권한만으로 쓰기가 가능했던 초기 코드: WRITE 권한 분리와 회귀시험으로 수정.
2. 사용자별 출발점 보호와 연결이 끊긴 조상 경로에서의 실행 우회: 출발점 및 전체 경로 검사로 수정.
3. 서로 다른 DB 연결에서 동시에 이동할 때 잘못된 경로가 붙는 경쟁 상태: 검증 전에 BEGIN IMMEDIATE를 시작하도록 수정.
4. 동시 쓰기 중 감사 이벤트와 앵커를 다른 시점에서 읽어 생기는 오판: 동일 트랜잭션 스냅샷으로 수정.

일반 샌드박스에서 HTTP 소켓 생성이 EPERM으로 거부된 초기 시도가 있었습니다. 로컬 소켓을 허용한 실행에서 HTTP 검사까지 다시 실행하여 최종 78개를 모두 통과했습니다. 실패한 초기 실행을 통과로 계산하지 않았습니다.

## 확인하지 않은 범위

- Windows PC 직접 실행·설치·파일 작성: **미실행**.
- 원본 첨부 735행 시뮬레이션: **미실행**, 동일 API 또는 동등 동작을 주장하지 않음.
- REA 실제 분석, 자동 코드 제작, 운영 MASTER 승인, 완전한 CHECK/LENSFIX/SELF_GROWTH: **미구현**.
- 별도 ZOOMCYCLE_CODE LENS로 실제 왕복하는 cycle_path: **미구현**. 현재는 인증된 ZOOMBAR의 run이 최종 실행 경계.
- 대규모 성능, 실제 서비스 연동, 비신뢰 Python 플러그인 OS 격리: **미검증/미구현**.

UI의 해시체인 일치 표시는 이 기록 검사만 의미하며, 운영용 CHECK 전체 PASS를 의미하지 않습니다.
