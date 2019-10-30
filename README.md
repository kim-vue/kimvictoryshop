# laser-front
## 사전요건
* git 설치
* node.js 설치 및 환경변수 등록
* [01 개발환경 설정 (VS Code)](http://rnd2.iljincns.co.kr:8888/341002/laser-front/wikis/01-%EA%B0%9C%EB%B0%9C%ED%99%98%EA%B2%BD-%EC%84%A4%EC%A0%95-(VS-Code))


## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Run your unit tests
```
npm run test:unit
```

---
# 컴포넌트 개발 가이드


## 권장사항
1. 사용처가 많거나 개발 중인 컴포넌트는 ./components 바로 아래에 작성
2. 어느 정도 볼륨이 되거나 기능 단위가 식별되면 ./components 하위 디렉토리로 이동
3. views 디렉토리의 컴포넌트는 wrapper 역할을 하며 실제로 화면으로 기능하D는 요소들만 작성

## 필수사항
1. 컴포넌트 명은 반드시 식별성이 좋아야 함.
2. 화면명+역할명.vue ex) UserMng.vue, UserList.vue UserModal.vue
3. 2회 이상 반복되는 메서드 식별 시 mixin으로 구성할 것.

## Tip
1. 부모-자식-손자 컴포넌트에서 부모 - 손자 간 이벤트 처리가 필요하면 이벤트 버스를 이용할 것.
2. App 전체적으로 관리할 대상이 아니면 store 사용은 피할 것.
3. 결재선 시각화 관련 참조 https://www.npmjs.com/package/bulma-o-steps
4. buefy https://buefy.github.io/documentation/
5. bulma http://bulma.io

# 공통 컴포넌트 가이드
## DHX Grid Component
### 1. 기본 사용법
```html
<dhx-grid v-model="data" v-bind:config="config"></dhx-grid>
```

```javascript
import DhxGrid from '@/components/DhxGrid.vue'

export default {
	...
	components: {
		DhxGrid
	},
	data() {
		return {
			...
			config: {
				columns: [{
					id: 'column1',
					value: 'ColumnText',
					width: 100,
					align: 'left'
				}]
			},
			data: [],
			...
		}
	},
	...
}
```
---
### 2. config
DHX 그리드를 설정할 수 있습니다.

|field|Type|구현여부|Description|
|---|:---:|:---:|---|
|columns|array|O|그리드 열을 설정 (필수)
|events|object|O|그리드 이벤트 설정 [https://docs.dhtmlx.com/api__refs__dhtmlxgrid_events.html](https://docs.dhtmlx.com/api__refs__dhtmlxgrid_events.html)
|beforeRefreshData|function|O|그리드 행 데이터를 갱신하기 전 실행되는 이벤트 함수
|afterRefreshData|function|O|그리드 행 데이터 갱신 후 실행되는 이벤트 함수
|~~combos~~|~~array~~|~~O~~|~~/api/code/detail에서 데이터를 가져온다, 그룹 코드 목록으로 사용~~
|autoWidth|boolean|O|[https://docs.dhtmlx.com/api__dhtmlxgrid_enableautowidth.html](https://docs.dhtmlx.com/api__dhtmlxgrid_enableautowidth.html) (Default: false)
|autoHeight|boolean|O|[https://docs.dhtmlx.com/api__dhtmlxgrid_enableautoheight.html](https://docs.dhtmlx.com/api__dhtmlxgrid_enableautoheight.html) (Default: false)
|enablePaging|boolean|O|페이징 사용 여부 (Default: false)
|pagingSize|integer|O|페이지 당 행 수 (Default: 50)
|pageCount|integer|O|보여줄 페이지 선택 갯수 (Default: 10)
|pageHandler|response|O|페이지 영역 계산 함수
|queryPage|function|O|페이지 갱신 함수 *반드시 Promise 형식이어야함!!!!
---
### 3. columns
|field|type|Description
|---|:---:|---|
|id|string|Column field
|value|string|Column label
|width|integer|Column width (Default: 100)
|type|string|Column type (Default: 'ro') [https://docs.dhtmlx.com/grid__columns_types.html](https://docs.dhtmlx.com/grid__columns_types.html)
|align|string|Column align style: 'left', 'right', 'center' (Default: 'center')
|~~combo~~|~~string~~|~~config combos에서 설정한 코드 사용~~
|component|Vue Component|Vue Component
|mixin|Vue Component|Component의 mixin injection
---
### 4. 페이징
#### default pageHandler
```javascript
pageHandler(response) {
  if (response !== undefined && response.data !== undefined && typeof response.data === 'object') {
    // 페이지 총 수를 가져온다
    this.totalPages = response.data.totalPages || 1
    // 행 수를 가져온다
    this.totalItems = response.data.totalElements || 0
    // 현재의 페이지...
    this.page = response.data.page || 0

    // Calculate page range
    var fp = this.page - Math.ceil(this.options.pageCount / 2) + 1
    fp = fp < 1 ? 1 : fp
    var ep = fp + this.options.pageCount - 1
    ep = ep >= this.totalPages ? this.totalPages : ep
    ep === this.totalPages ? fp = ep - this.options.pageCount + 1 : 0
    fp = fp < 1 ? 1 : fp

    this.pageStartPoint = fp // 페이지 전시 시작 포인트
    this.pageEndPoint = ep // 페이지 전시 종료 포인트

    if (this.instance !== undefined) {
      this.instance.changePage(this.page + 1)
      this.setRowData(this.value)
    }
  }
  return response
}
```
여기서 this는 DhxGrid Component이다
페이징을 사용하는 경우, 자동으로 데이터를 초기화 해주지 않는다

---
### 5. Vue Component
DHX 그리드 컬럼에서 Vue Component를 사용할 수 있습니다.

```javascript
data() {
	return {
		config: {
			columns: [{
				id: 'column',
				value: 'Column Title',
				component: {
					template: `
						<input type="text" class="input" v-model="value.text" @input="onInput()" />
					`
				}
			}]
		}
	}
}
```

DhxGrid mixin은 폐기 됨

Sinle File Component로 만들거나 인라인 컴포넌트로 변경

컴포넌트 작성 시, inject 가능한 props

|props|Description|
|---|---|
|index|행 번호|
|value|행 데이터|
|field|열 필드 명|
|~~options~~|~~combo를 사용하는 경우만 사용가능~~|

사용가능한 Default Grid Components 추가
GridInput: 텍스트 박스
GridNumberInput: 숫자 입력 박스
GridSelect: ~~코드~~ 콤보 박스
GridCheckbox: 체크박스

## DHX Calendar
```html
<dhx-calendar v-model="date" :config="config"></dhx-calendar>
```
```javascript
import DhxCalendar from '@/components/DhxCalendar.vue'

export default {
	...
	components: {
		DhxCalendar
	},
	data() {
		return {
			config: {
				hideTime: false, // @See DHX Calendar hideTime()
				format: 'YYYY-MM-DD', // 전시 포멧
				outputFormat: 'YYYYMMDD' // 데이터 포멧
			},
			date: '20190101'
		}
	}
	...
}
```

## NumberInput
```html
<number-input v-model="value" format="0,0"></number-input>
```
```javascript
import NumberInput from '@/components/NumberInput.vue'

export default {
	...
	components: {
		NumberInput
	},
	data() {
		return {
			value: 2
		}
	}
}
```
NumberInput 컴포넌트 사용 시, 전시되는 데이터와 실제 데이터는 다릅니다.
전시 데이터는 format에 지정된 형식으로 변형되지만, 실제 데이터는 숫자 원형을 유지하고 있습니다.
format 방식에 대해서는 [http://numeraljs.com/#format](http://numeraljs.com/#format) 를 참조하시기 바랍니다.
