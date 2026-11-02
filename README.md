# ZOOMCONNECT 0.3 — 컬렉션 · 혼합 · 분리 · 재연결

**신원은 위치 자체입니다.** 컬렉션 목록의 위치 `b`, 그 안의 칸 위치 `s`가 `Address(b,s)`입니다. 숨은 LENS UID로 이전 내용을 추적하지 않습니다. ZOOMBAR·BRIDGE·LAYER·BOOKMARK는 같은 컬렉션 저장 구조와 게시판 렌더러를 사용합니다.

현재는 실행 가능한 로컬 프로토타입입니다. 전체 ASTRA/REA 제작 공장 또는 운영 시스템의 완성을 뜻하지 않습니다. 이전 v0.1은 비교용으로 보존했고 새 기본 실행은 `positional.py`입니다. 과거 설명은 `docs/V0_1.md`에 있습니다.

## 실행

Python 3.11 이상과 표준 라이브러리만 사용합니다.

```powershell
Set-Location 'C:\project\AiWork\gpt\ZOOMCONNECT5'
py -3 -m unittest discover -s tests -v
py -3 -m zoomconnect demo
py -3 -m zoomconnect mixed-demo
py -3 -m zoomconnect serve --port 8765
```

이 명령은 코드가 해당 폴더에 있을 때의 실행 방법입니다. 이 세션에서는 Windows에 직접 저장·실행하지 않았으며 첨부 다운로드도 해결되지 않았습니다. 현재 코드는 클라우드 `/workspace/ZOOMCONNECT`에 있습니다.

화면은 `http://127.0.0.1:8765`에서 열립니다. 종료는 Ctrl+C입니다. `py`가 없는 환경에서는 `python`을 사용합니다. 별도 pip/npm 설치는 없습니다. 화면 데모는 메모리 DB이며 종료하면 사라집니다. 파일 DB의 재시작·복원은 자동 테스트로 확인합니다.

이전 예제는 `python -m zoomconnect legacy-demo`입니다. 기존 78개 검사는 v0.1 검증이며 새 위치 모델의 검사와 구분합니다.

## 실제 공통 구조

```text
컬렉션 목록
 [0] MASTER   : [0 자기 헤더, 1 배달 목록 참조, 2 고정 위치 참조]
 [1] LAYER    : [0 자기 헤더, 1 쿠팡 참조, 2 배민 참조, ...]
 [4] BRIDGE   : [0 자기 헤더, 1 GPS 참조]
 [7] BOOKMARK : [0 자기 헤더, 1 목적지 참조, ...]
 [8] ZOOMBAR  : [0 자기 헤더, 1 출발 방문, 2 다음 방문, ...]
```

숫자는 기본 데모의 실제 생성 순서입니다. 0번 슬롯은 컬렉션 자신의 설명을 가진 LENS 자리로 보호하며 일반 칸은 1번부터 시작합니다. 목록 포함은 저장·연결 관계이고 부모·자식 소유 관계가 아닙니다.

모든 슬롯은 `revision`과 `record`를 가진 자리입니다. 레코드에는 제목·표시 종류·대상 좌표·활성 상태·이동 허용 여부·메타데이터가 있습니다. revision은 신원의 일부가 아니라 오래된 조회·방문·실행을 검사하는 값입니다.

## 위치를 바꾼다는 의미

```text
변경 전                       변경 후
1:1 쿠팡 참조 → 2:0            1:1 배민 참조 → 3:0
1:2 배민 참조 → 3:0            1:2 쿠팡 참조 → 2:0
별도 참조 target=1:1           여전히 target=1:1
```

원래 쿠팡 레코드를 따라 새 좌표로 연결을 고치지 않습니다. 같은 위치의 내용이 바뀝니다. 참조 칸의 이동과 그 칸이 가리키는 다른 컬렉션 자체의 이동은 별개입니다.

`swap_collections()`는 초기 설정 권한으로 두 공개 컬렉션의 내용 전체를 전역 위치에서 교환합니다. 모든 참조와 권한 좌표는 그대로이며 목적지 각 자리의 revision이 증가합니다. 루트·사용자 출발점·사적 컬렉션·보호된 이력은 교환하지 못합니다. 전역 목록 전체 압축은 제공하지 않습니다.

삭제는 빈 칸을 남겨 이웃 번호를 몰래 바꾸지 않습니다. 재정렬만 명시적으로 내용을 옮깁니다. 대상 내용이 바뀌면 그것을 참조하는 원본 목록의 조회 버전도 무효화하지만 참조 좌표는 고치지 않습니다.

## 동일한 ZOOMBAR

```python
view = bar.view()
bar.open(1, expected_revision=view['revision'])

view = bar.view()
bar.reorder(1, 2, expected_revision=view['revision'])

fresh = bar.view()
bar.open(1, expected_revision=fresh['revision'])
```

모든 주체가 같은 코드를 사용합니다. open은 현재 목록의 실제 칸을 선택해 그 참조로 한 단계만 이동합니다. 목적지의 참조를 임의로 연쇄 추적하지 않습니다. 오래된 화면 선택은 STALE_VIEW, 바뀐 방문 근거는 STALE_PATH로 거부합니다. OUT은 마지막 유효한 경로까지 안전 복귀합니다.

위치 URL `zoom://world/0:0/1/1`은 출발 0:0에서 각 목록의 1번 칸을 차례로 선택한다는 뜻입니다. URL도 단계마다 동일한 open 검사를 통과합니다.

| 표시 종류 | 공통 컬렉션에 실제 저장하는 내용 |
|---|---|
| LAYER | 작업 문맥에 묶은 참조 칸 |
| BRIDGE | 다른 위치로 이어지는 참조 칸 |
| BOOKMARK | 소유자의 목적지 참조 칸 |
| ZOOMBAR | 실제 방문과 경유 위치를 기록한 칸 |

kind 문자열로 이동 코드를 선택하지 않습니다. 북마크는 실제 연결을 탐색한 뒤 open을 수행합니다. 북마크·과거 방문 칸은 traversable=False이므로 새 물리 연결이나 접근 권한을 만들지 않습니다.

OUT은 ZOOMBAR 방문 칸을 삭제·재번호화하지 않고 runtime cursor만 이전 방문으로 옮깁니다. 다음 방문은 새로운 칸에 추가됩니다. cursor는 신원이 아닙니다.

## 혼합 · 분리 · 재연결

출발 목록에서 해당 주체의 혼합 작업판을 열고 함께 연결 버튼을 누르면 BRIDGE·LAYER·실제 소유자 BOOKMARK 참조가 한 목록에 추가됩니다. 일반 현재 목록도 같은 API로 편집합니다.

```python
slots = bar.mix([
    {'title': '위치 연결', 'target': bridge_address},
    {'title': '작업 문맥', 'target': layer_address},
    {'title': '책갈피', 'target': bookmark_address},
], expected_revision=bar.view()['revision'])
bar.separate(slots[0].slot, bar.view()['revision'])
bar.reconnect(slots[0].slot, bar.view()['revision'])
```

분리는 해당 칸만 끄며 제목·대상·위치를 보존합니다. 재연결은 같은 칸을 활성화하고 revision을 증가시킵니다. 삭제는 별도 remove입니다. reconnect에 target을 명시하면 같은 좌표의 목적지를 바꿀 수도 있습니다.

connect는 끝에 추가하거나 명시한 빈 칸만 재사용합니다. 점유된 칸을 덮어쓰거나 이웃을 밀지 않습니다. 동일 대상을 여러 칸에 연결할 수 있고 한 칸 분리는 다른 연결에 영향을 주지 않습니다. mix는 1~256개 연결을 한 트랜잭션으로 검증·추가하며 하나라도 거부되면 전체를 되돌립니다.

일반 책갈피 목적지 참조는 분리·재연결 후에도 traversable=False를 유지합니다. 명시적 connect로 추가한 새 칸만 실제 이동 연결입니다. BOOKMARK에서 LAYER로 실제 연결을 추가하는 것도 같은 함수입니다. 보호된 ZOOMBAR 방문 기록은 편집 API로 바꾸지 못합니다.

현재 컬렉션 WRITE, 대상 MOVE/READ, 사적 컬렉션 소유권을 검사합니다. 사적 혼합 작업판·북마크는 각 주체만 접근합니다. 실제 검증은 docs/MIXED_VERIFICATION.md에 기록합니다.

## HASH 실행

```python
h = bar.put({
    'BASE_PIN': '0:0', 'COMMON_ACTION': '정산',
    'INNER_LENS': '2:0', 'UNIQUE_ACTION': '일별 합계',
    'data': [4500, 3800, 5200],
})
bar.run(h)  # 업무 반환값 None
result = bar.read(bar.last_result_hash())
```

현재 위치·실제 경로·READ/WRITE/EXECUTE·HASH 주소와 revision·계약을 검사한 뒤 결과 HASH와 CYCLE_DONE을 기록합니다. 설치 계약도 대상 위치 revision에 결합되어 다른 점유자에게 예전 계약을 적용하지 못합니다. ZOOMCYCLE은 정확히 다섯 요소입니다.

## 구현과 검증

| 파일 | 책임 |
|---|---|
| zoomconnect/positional.py | 위치 신원, 공통 컬렉션, 인증·권한, ZOOMBAR, 책갈피, HASH, 감사 |
| zoomconnect/positions_demo.py | 예제 목록·참조·권한 |
| zoomconnect/positions_server.py | 실제 코어를 호출하는 로컬 HTTP |
| zoomconnect/web/positions.html | 일반 목록·BOOKMARK·ZOOMBAR의 공통 게시판 렌더러 |
| zoomconnect/execution.py | 승인된 계산과 입력 계약 검증 |
| tests/test_positional*.py | 새 모델 위치·보안·복원·동시성 검사 |
| docs/POSITIONAL_VERIFICATION.md | 실제 검사 결과와 미확인 범위 |

## 한계

일반 입력·권한·BFS에는 조건문이 있습니다. 배열은 실제 순서와 위치 데이터이며 종류별 실행 분기표가 아닙니다. 전체가 조건문 0개라고 주장하지 않습니다.

현재 작은 모델의 정확성을 우선해 SQLite 한 행에 전체 상태 JSON을 저장하고 감사 이벤트는 append-only 테이블에 기록합니다. 대규모 성능·증분 저장·세계별 캐시는 미검증입니다.

Builder는 초기 설정 경계입니다. 일반 현재 목록 편집은 bar의 컬렉션 WRITE 검사를 통하지만 운영 MASTER의 일회용 승인·제안·롤백은 아직 없습니다. 화면의 다섯 주체는 동등 권한의 격리 데모입니다.

별도 ZOOMCYCLE_CODE LENS로 왕복하는 모델, CHECK 네 조건, LENSFIX, SELF_GROWTH, WORKER_POOL 복구, REA 자동 제작, 비신뢰 Python 코드의 OS 격리는 미구현입니다. 해시체인 일치를 전체 운영 PASS로 표시하지 않습니다.
