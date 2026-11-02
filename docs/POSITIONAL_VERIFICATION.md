# 위치 기반 컬렉션 모델 실제 검증

검증일: 2026-11-02, Asia/Seoul. 실행 환경은 Linux / Python 3.12.14 / Chromium입니다. Windows 직접 실행이나 파일 전송은 수행하지 않았습니다.

## 실제 결과

| 검사 | 결과 |
|---|---|
| 전체 unittest discovery | **144개 실행, 144개 통과, 건너뜀 0개** |
| 새 positional 계약 | **57개 통과** |
| 독립 positional 검토 | **3개 통과** |
| 새 positional HTTP 통합 | **6개 통과** |
| 보존한 v0.1 회귀 | **78개 통과** |
| 실제 Chromium 게시판 흐름 | **11개 확인, 실패 0개, 미처리 JS 오류 0개** |
| 최종 코어 정리 후 positional 재검사 | **60개 통과** |
| positional CLI 예제 | `1:1` 내용 쿠팡→배민, stale 선택 거부, 계산 `13500`, 감사 일치 |

전체 결과에서 기존 78개를 새 위치 모델 검사로 바꿔 부르지 않습니다. 새 모델은 57+3+6=66개의 자동 검사로 검증했습니다.

## 확인한 내용

- 좌표 자체가 신원이며 숨은 LENS UID가 없음.
- 재정렬 후 기존 참조는 원래 좌표를 유지하고 새 내용을 가리킴.
- 컬렉션 전체 교환도 같은 좌표 의미를 유지함.
- 위치의 revision이 원래 내용과 함께 이동하지 않고 해당 위치에서 증가함.
- 삭제는 tombstone이며 인접 주소를 자동 압축하지 않음.
- 대상 변경 시 원본 참조 목록의 예전 조회 버전도 거부함.
- ZOOMBAR·BRIDGE·LAYER·BOOKMARK 모두 공통 컬렉션 projection 사용.
- ZOOMBAR의 실제 방문 슬롯이 OUT 뒤에도 보존됨.
- BOOKMARK와 과거 기록이 물리 연결을 새로 만들지 않음.
- 같은 표시 이름의 계정도 HISTORY와 ZOOMBAR가 섞이지 않음.
- 한 칸 WRITE가 다른 칸 편집 권한으로 확장되지 않음.
- READ/WRITE/EXECUTE·BASE_PIN 경로·단일 HASH·결과 HASH 검사.
- 자리 내용이 바뀌면 기존 파라미터와 계약으로 새 점유자를 실행할 수 없음.
- SQLite 재시작 복원 및 별도 DB 연결 4개의 컬렉션 동시 생성.
- 상태·기록 변조와 기록 꼬리/전체 삭제 탐지, append-only 제약.

## 실제 브라우저

`python tools/positions_smoke.py`로 확인했습니다. 이 선택 검사는 Playwright와 Chromium이 설치된 개발 환경에서만 필요하며 앱 런타임 의존성은 아닙니다.

1. 실제 루트 컬렉션 0:0 표시
2. 북마크 참조를 선택하고 실제 위치 경로로 이동
3. 위치 기반 계약에서 13500 계산·HASH 기록
4. 1:1 주소 유지, 내용은 배민으로 변경
5. 이전 화면 선택 거부
6. 같은 칸 선택으로 새 목적지 3:0 이동
7. 별도 고정 참조도 계속 1:1을 가리키고 새 내용을 확인
8. 주체별 ZOOMBAR 컬렉션 격리
9. 방문 칸에 근거한 OUT
10. 폭 390px에서 문서 가로 넘침 없음
11. 미처리 JavaScript 오류 없음

스크린샷은 `screenshots/positions-desktop.png`, `positions-execution.png`, `positions-mobile.png`입니다. 결과 원문은 이 문서와 같은 디렉터리의 `positions-test-results.txt`, `positions-browser-results.json`, `positions-demo-result.json`입니다.

## 범위 밖

운영 MASTER의 승인·롤백, 별도 ZOOMCYCLE_CODE LENS로의 왕복 이동, 전체 외부 TYPE, CHECK 네 조건·LENSFIX·SELF_GROWTH·WORKER_POOL·REA 공장·OS 플러그인 격리는 완성하지 않았습니다. 감사 앵커는 동일 DB에 있으므로 DB 전체를 일관되게 다시 작성하는 공격의 외부 증명도 없습니다.

새 코어에는 공통 안전검증과 BFS의 조건문이 있습니다. 배열은 실제 순서·위치 데이터이며 종류별 실행을 고르는 우회 분기표가 아닙니다. 전체 코드의 조건문 0개를 주장하지 않습니다.
