<template>
<div class="inner-box">
  <form @submit.prevent="query">
    <div class="content-name">
      <h2 class="dp-ib">계정과목 관리</h2>
      <div class="btn-wrap btn-type1 clearfix">
        <button type="submit" class="btn-size btn-gray fl_left">
          <span class="btn-icon"><i class="fas fa-search"></i></span>
          조회
        </button>
        <button type="button" class="btn-size btn-blue fl_left" @click="buttonClickEventSave()">
          <span class="btn-icon"><i class="fas fa-save"></i></span>
          저장
        </button>
      </div>
    </div>

    <!-- 검색영역 -->
    <div class="search-form">
      <search-comp v-model="params" :options="{ type: '02', compCd: 'compCd', authorize: true }" />
      <div class="form-group">
        <label class="control-label">계정 코드/명</label>
        <div class="form-input">
          <input type="text" class="input" v-model="params.searchVal" />
        </div>
      </div>
    </div>
    <!-- //검색영역 -->
  </form>

  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">계정과목 내역</h3>
        </div>
        <div class="btn-wrap btn-type2 clearfix">
          <button class="btn-size btn-w-gray" @click="buttonClickEventAddRow()">
            <span class="btn-icon"><i class="fas fa-plus"></i></span>
            행추가
          </button>
          <button class="btn-size btn-w-gray" @click="buttonClickEventRemoveRow()">
            <span class="btn-icon"><i class="fas fa-trash-alt"></i></span>
            행삭제
          </button>
          <button class="btn-size btn-excel" @click="buttonClickEventToExcel()">엑셀 저장</button>
        </div>
      </div>

      <dhx-grid ref="grid" v-model="data" :config="config" @constructGridSuccessful="constructGridSuccessful" />
    </div>
  </div>
</div>
</template>

<script>
import assert from '@/libs/assert'
import debug from '@/libs/debug'
import DhxGrid from '@/components/DhxGrid.vue'

const _debug = debug('AcctMng')

export default {
  components: {
    DhxGrid
  },
  data() {
    return {
      data: [],
      config: {
        columns: [{
          type: 'cntr',
          align: 'center',
          value: 'No.',
          width: 50
        }, {
          id: 'acctCd',
          align: 'center',
          type: 'ed',
          value: '계정코드'
        }, {
          id: 'acctNm',
          align: 'left',
          type: 'ed',
          value: '계정명칭',
          width: 220
        }, {
          id: 'acctShortNm',
          align: 'left',
          type: 'ed',
          value: '계정약어명칭'
        }, {
          id: 'acctGrCd',
          align: 'center',
          type: 'ed',
          value: '계정그룹코드'
        }, {
          id: 'erpUseYn',
          value: 'ERP_사용여부',
          type: 'ch',
          width: 90
        }, {
          id: 'eaUseYn',
          value: 'EA_사용여부',
          width: 90,
          type: 'ch'
        }, {
          id: 'crdYn',
          value: '법인카드',
          width: 90,
          type: 'ch'
        }, {
          id: 'bllYn',
          value: '세금계산서',
          width: 90,
          type: 'ch'
        }, {
          id: 'evdYn',
          value: '기타증빙',
          width: 90,
          type: 'ch'
        }, {
          id: 'trYn',
          value: '교통비',
          width: 90,
          type: 'ch'
        }, {
          id: 'ppdYn',
          value: '선급금',
          width: 90,
          type: 'ch'
        }, {
          id: 'rcpYn',
          value: '접대비',
          width: 90,
          type: 'ch'
        }, {
          id: 'apYn',
          value: '미지급',
          width: 90,
          type: 'ch'
        }, {
          id: 'vatYn',
          value: '부가세',
          width: 90,
          type: 'ch'
        }, {
          id: 'ctrlYn',
          value: '통제계정',
          width: 90,
          type: 'ch'
        }, {
          id: 'ppdOrderSeq',
          align: 'center',
          value: '선급금 계정 정렬순서',
          type: 'edn',
          width: 150
        }, {
          id: 'apOrderSeq',
          align: 'center',
          value: '미지급 계정 정렬순서',
          type: 'edn',
          width: 150
        }, {
          id: 'ref1',
          align: 'left',
          type: 'ed',
          value: '비고1'
        }, {
          id: 'ref2',
          align: 'left',
          type: 'ed',
          value: '비고2'
        }, {
          id: 'ref3',
          align: 'left',
          type: 'ed',
          value: '비고3'
        }, {
          id: 'chgNm',
          align: 'center',
          value: '수정자',
          width: 120
        }, {
          id: 'chgDtm',
          align: 'center',
          value: '수정 일시',
          width: 200
        }, {
          id: 'chg',
          hide: true
        }],
        height: '50vh',
        enablePaging: true,
        events: {
          onEditCell(state, rId, cInd, nValue, oValue) {
            const rowIndex = this.instance.getRowIndex(rId)
            const row = this.value[rowIndex]
            const cell = this.cellMap[cInd]

            if (state === 0 && (cInd >= 1 && cInd <= 4) && !row.new) {
              return false
            } else if (state === 2 && cInd === 1 && nValue !== oValue) {
              // 계정 코드 중복 확인
              const acctCd = String(nValue).toUpperCase()
              const dl = this.value.filter((x, i) => x.acctCd === acctCd && i !== rowIndex)
              if (dl.length > 0) {
                setTimeout(() => {
                  this.$swal({
                    type: 'error',
                    text: '중복된 계정코드는 사용할 수 없습니다.'
                  })
                }, 100)
                return false
              }
              row.chg = true
              return true
            } else if (state === 2 && nValue !== oValue) {
              row.chg = true
            }
            return true
          },
          onChange(rId, cInd, state){
            const rowIndex = this.instance.getRowIndex(cInd)
            const row = this.value[rowIndex]
            row.chg = true
            return true
          }
        },
        afterRefreshData(grid, data) {
          if (grid !== undefined && data !== undefined && data.length > 0) {
            this.$nextTick(() => {
              var i = 0
              const size = data.length
              for (; i < size; ++i) {
                const rId = grid.getRowId(i)
                this.setColumnClassName(rId, [1, 2, 3, 4], 'bg-lightpink', true)
                this.setColumnClassName(rId, [1, 2, 3, 4], 'bg-grey', true)
                if (data[i].new === true) {
                  this.setColumnClassName(rId, [1, 2, 3, 4], 'bg-lightpink')
                } else {
                  this.setColumnClassName(rId, [1, 2, 3, 4], 'bg-grey')
                }
              }
            })
          }
        }
      },
      params: {
        compCd: undefined,
        searchVal: undefined
      },
      memento: []
    }
  },
  methods: {
    constructGridSuccessful(grid) {
      grid.setNumberFormat('0,000', 16, '.', ',')
      grid.setNumberFormat('0,000', 17, '.', ',')
    },
    query() {
      this.$store.commit('loading')
      return this.$http.post('/api/account/list', this.params)
        .then(response => {
          const st = (new Date()).valueOf()
          this.data = response.data.map(x => {
            const chgDtm = this.$moment(x.chgDtm)
            return {
              acctCd: x.acctCd,
              acctNm: x.acctNm,
              acctShortNm: x.acctShortNm,
              acctGrCd: x.acctGrCd,
              erpUseYn: x.erpUseYn === 'Y' ? true : false,
              eaUseYn: x.eaUseYn === 'Y' ? true : false,
              crdYn: x.crdYn === 'Y' ? true : false,
              bllYn: x.bllYn === 'Y' ? true : false,
              evdYn: x.evdYn === 'Y' ? true : false,
              trYn: x.trYn === 'Y' ? true : false,
              ppdYn: x.ppdYn === 'Y' ? true : false,
              rcpYn: x.rcpYn === 'Y' ? true : false,
              apYn: x.apYn === 'Y' ? true : false,
              vatYn: x.vatYn === 'Y' ? true : false,
              ctrlYn: x.ctrlYn === 'Y' ? true : false,
              ppdOrderSeq: x.ppdOrderSeq,
              apOrderSeq: x.apOrderSeq,
              ref1: x.ref1,
              ref2: x.ref2,
              ref3: x.ref3,
              chgId: x.chgId,
              chgNm: x.chgNm || x.chgId,
              useYn: x.useYn,
              chgDtm: chgDtm.isValid() ? chgDtm.format('YYYY-MM-DD HH:mm:ss') : '',
              compCd: x.compCd,
              chg: false
            }
          })
        }).finally(() => {
          this.$store.commit('finish')
        })
    },
    buttonClickEventSave() {
      try {
        const data = this.data.filter(x => x.chg || x.new).map(x => {
          return {
            acctCd: x.acctCd,
            acctNm: x.acctNm,
            acctShortNm: x.acctShortNm,
            acctGrCd: x.acctGrCd,
            erpUseYn: x.erpUseYn ? 'Y' : 'N',
            eaUseYn: x.eaUseYn ? 'Y' : 'N',
            crdYn: x.crdYn ? 'Y' : 'N',
            bllYn: x.bllYn ? 'Y' : 'N',
            evdYn: x.evdYn ? 'Y' : 'N',
            trYn: x.trYn ? 'Y' : 'N',
            ppdYn: x.ppdYn ? 'Y' : 'N',
            rcpYn: x.rcpYn ? 'Y' : 'N',
            apYn: x.apYn ? 'Y' : 'N',
            vatYn: x.vatYn ? 'Y' : 'N',
            ctrlYn: x.ctrlYn ? 'Y' : 'N',
            ppdOrderSeq: x.ppdOrderSeq,
            apOrderSeq: x.apOrderSeq,
            ref1: x.ref1,
            ref2: x.ref2,
            ref3: x.ref3,
            useYn: x.useYn,
            compCd: x.compCd
          }
        })
        assert.apply(this, [data.length > 0, '변경된 행이 없습니다.'])

        let emptyAcctCd = data.filter(x => !x.acctCd)
        assert.apply(this, [emptyAcctCd.length === 0, '계정코드는 빈 값일 수 없습니다.'])

        let emptyAcctNm = data.filter(x => !x.acctNm)
        assert.apply(this, [emptyAcctNm.length === 0, '계정명칭은 빈 값일 수 없습니다.'])

        let emptyAcctGrCd = data.filter(x => !x.acctGrCd)
        assert.apply(this, [emptyAcctGrCd.length === 0, '계정그룹코드는 빈 값일 수 없습니다.'])

        this.$http.post('/api/account/save', data)
          .then(response => {
            this.$swal({
              type: 'success',
              text: '저장되었습니다.'
            })
          }).then(this.query)
      } catch (e) {
        this.$swal({
          type: 'error',
          text: e
        })
      }
    },
    buttonClickEventAddRow() {
      this.data.unshift({
        acctCd: undefined,
        acctNm: undefined,
        acctShortNm: undefined,
        acctGrCd: undefined,
        erpUseYn: true,
        eaUseYn: true,
        crdYn: true,
        bllYn: true,
        evdYn: true,
        trYn: true,
        ppdYn: true,
        rcpYn: true,
        apYn: true,
        vatYn: true,
        ctrlYn: true,
        ppdOrderSeq: undefined,
        apOrderSeq: undefined,
        ref1: undefined,
        ref2: undefined,
        ref3: undefined,
        chgId: undefined,
        chgDtm: undefined,
        useYn: 'Y',
        compCd: this.params.compCd,
        new: true,
        chg: false
      })
      this.$refs.grid.firstPage()
    },
    buttonClickEventRemoveRow() {
      const rId = this.$refs.grid.instance.getSelectedRowId()
      if (rId === null) {
        this.$swal({
          type: 'error',
          text: '삭제할 행을 선택하여주세요.'
        })
      } else {
        const rowIndex = this.$refs.grid.instance.getRowIndex(rId)
        const isNew = this.data[rowIndex].new
        const compCd = this.data[rowIndex].compCd
        const acctCd = this.data[rowIndex].acctCd

        this.data.splice(rowIndex, 1)

        if (!isNew) {
          this.$http.put('/api/account/delete', {
            compCd,
            acctCd
          }).then(response => {
            // Do nothing!
          })
        }
      }
    },
    buttonClickEventToExcel() {
      this.$refs.grid.toExcel()
    }
  },
  created() {
    try {
      this.params.compCd = this.$store.state.loginInfo.compCd
    } catch (e) {
      this.params.compCd = undefined
    }

    this.query()
  }
}
</script>
