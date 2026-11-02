# ZOOMCONNECT 작업 기준

사용자가 확정한 세계관을 우선한다.

- LENS = WORLD = COMPONENT. 독립된 평면 구조다. 최신 사용자 결정: 신원은 고정 UID가 아니라 컬렉션 위치와 칸 위치 Address(b,s) 자체다.
- USER, AI, MASTER, AGENT, CODE의 모든 LENS 이동은 공통 ZOOMBAR를 통한다.
- BOOKMARK는 목적지 LENS를 찾는 책갈피다. 필수 중간 공간이나 접근 권한이 아니다.
- 링크·URL도 실제 이동 검증을 우회할 수 없다.
- BRIDGE·LAYER도 독립 LENS이며 공통 연결 원리를 따른다.
- LENS 내부를 A.B.C로 따라가거나 직접 실행 객체를 넘겨 우회하지 않는다.
- 모든 컬렉션·ZOOMBAR·BRIDGE·LAYER·BOOKMARK는 공통 컬렉션/슬롯 모델을 사용한다. 배열은 실제 위치 데이터이며 종류별 실행 분기표가 아니다.
- 재정렬은 해당 위치의 내용을 옮긴다. 기존 참조는 좌표를 유지하고 원래 내용을 추적하지 않는다. 버전은 오래된 선택 검사값이며 신원의 일부가 아니다.
- LENS 이름/종류별 조건문, 배열·딕셔너리 분기표로 사례를 끼워 맞추지 않는다.
- 일반 안전검증을 없애거나 판단을 다른 파일에 숨겨 ‘조건문 0개’로 포장하지 않는다.
- ZOOMCYCLE은 BASE_PIN → COMMON_ACTION → INNER_LENS → UNIQUE_ACTION → ZOOMCYCLE_CODE의 정확한 5요소다.
- PARAMETER_HASH·실행 종류를 여섯 번째 요소로 추가하지 않는다.
- HASH 참조와 READ/WRITE/EXECUTE 권한은 별개다.
- 구현/실제 실행/시험 통과/제작자 주장/시뮬레이션/미구현을 구분한다.

현재 기본 실행은 v0.3 위치 기반 혼합 컬렉션 프로토타입이다. v0.1 UID 그래프 core.py/demo.py/server.py는 기존 검증과 비교를 위해 보존하며 새 설계의 실행 경로가 아니다. README의 미구현·차이점을 확인하고 완제품으로 주장하지 않는다. 원본 첨부 시뮬레이션과의 동등성은 검증되지 않았다.

현재 사용자는 Windows 작업 경로 `C:\project\AiWork\gpt\ZOOMCONNECT5`를 지정했으나 이 세션에는 Windows 원격 도구가 없다. 이후 사용자가 가능한 환경에서 코드 제작과 제시를 허용해 클라우드 `/workspace/ZOOMCONNECT`에서 제작했다. Windows에 직접 파일을 썼다고 주장하지 않는다.

기본 검증: `python -m unittest discover -s tests -v`, `python -m zoomconnect demo`. 웹 변경 시 실제 브라우저 이동과 HASH 결과도 확인한다. 이미 통과한 검사는 관련 수정이나 구체적인 우려가 있을 때만 재실행한다.
