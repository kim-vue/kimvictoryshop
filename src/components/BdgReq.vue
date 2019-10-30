<template>
<div>
  <div class="table-area">
    <div class="table-a fixed-th">
      <div class="table-name">
        <h3 class="ico_table_name">신청구분</h3>
      </div>
      <table class="table">
        <tbody>
          <!-- 헤더 -->
          <tr v-if="isSaved">
            <th>신청서번호</th>
            <td>{{ data.budReqNo }}</td>

            <th>회사</th>
            <td>{{ data.compNm }}</td>

            <th>신청서상태</th>
            <td>{{ data.budStatNm }}</td>
          </tr>

          <tr v-if="isSaved">
            <th>신청자</th>
            <td>{{ data.wrtNm }}</td>

            <th>소속부서</th>
            <td>{{ data.deptNm }}</td>

            <th>신청일자</th>
            <td>{{ this.$moment(data.wrtDt).format('YYYY-MM-DD') }}</td>
          </tr>
          <!-- //헤더 -->

          <tr>
            <th>예산구분</th>
            <td colspan="5">{{ data.budFgNm }}</td>
          </tr>

          <tr>
            <table-radio title="신청유형" v-model="data" field="brwTypeCd" :options="options['BRW_TYPE_CD']" :colspan="5" :required="!isReadonly" :disabled="isReadonly" @input="brwTypeCdChangeEvent" />
          </tr>

          <tr>
            <th :class="{ 'tp-a': !isReadonly }">신청사유</th>
            <td colspan="5">
              <textarea v-model="data.reqRsn" :disabled="isReadonly"></textarea>
            </td>
          </tr>

          <tr v-if="(manage && ['40', '50', '60', '70'].indexOf(data.budStatCd) >= 0) || (!manage && ['40', '70'].indexOf(data.budStatCd) >= 0)">
            <th>반려사유</th>
            <td colspan="5">
              <textarea v-model="data.rejRsn" :disabled="!manage || (manage && ['40', '70'].indexOf(data.budStatCd) >= 0)"></textarea>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">신청항목</h3>
        </div>
        <div class="btn-wrap btn-type2" v-if="!isReadonly">
          <button class="btn-size btn-w-gray" @click="buttonClickEvent_ResetRow">
            <span class="btn-icon"><i class="fas fa-redo"></i></span>
            초기화
          </button>
          <button class="btn-size btn-w-gray" @click="buttonClickEvent_AddRow">
            <span class="btn-icon"><i class="fas fa-plus"></i></span>
            행추가
          </button>
          <button class="btn-size btn-w-gray" @click="buttonClickEvent_RemoveRow">
            <span class="btn-icon"><i class="fas fa-trash-alt"></i></span>
            행삭제
          </button>
        </div>
      </div>
      <dhx-grid ref="grid" class="slip-grid" v-model="data.budgetDetails" :config="config" @constructGridSuccessful="constructGridSuccessful" v-if="Array.isArray(data.budgetDetails)" />
    </div>
  </div>
</div>
</template>

<script>
import Vue from 'vue'
import assert from '@/libs/assert'
import {
  url as _url
} from '@/libs/join'

import DhxGrid from '@/components/DhxGrid.vue'
import TableRadio from '@/components/slip/table/libs/TableRadio'

import Cctr from '@/components/Cctr_new.vue'
import Account from '@/components/Account_new.vue'

const CctrSearchButton = {
  props: ['index', 'value', 'field'],
  template: `
    <button type="button" class="icon" @click="openModal()"><i class="fas fa-search"></i></button>
  `,
  methods: {
    openModal() {
      let vm = this
      this.$modal.open({
        component: Cctr,
        parent: this,
        events: {
          close(data) {
            if (vm.onSubmit !== undefined && typeof vm.onSubmit === 'function') {
              vm.onSubmit.apply(vm, [data])
            }
          }
        }
      })
    }
  }
}

const AcctSearchButton = {
  props: ['index', 'value', 'field'],
  template: `
    <button type="button" class="icon" @click="openModal()"><i class="fas fa-search"></i></button>
  `,
  methods: {
    openModal() {
      let vm = this
      this.$modal.open({
        component: Account,
        props: {
          queryFunction() {
            this.$store.commit('loading')
            this.$http.get(_url('/api/ctrlAccount', this.search))
              .then(response => {
                this.data = response.data
              })
              .finally(() => {
                this.$store.commit('finish')
              })
          }
        },
        parent: this,
        events: {
          close(data) {
            if (vm.onSubmit !== undefined && typeof vm.onSubmit === 'function') {
              vm.onSubmit.apply(vm, [data])
            }
          }
        }
      })
    }
  }
}

const DateRenderer = {
  props: ['index', 'value', 'field'],
  template: `
    <span v-if="value[field]">{{ this.$moment(value[field], 'YYYYMM').format('YYYY-MM') }}</span>
    <span v-else></span>
  `
}

const $bus = new Vue()

const budget = {}
const bdg_mutex = {}

function queryRemainBudget(postDt, cctrCd, acctCd) {
  return new Promise(resolve => {
    let id = [postDt, cctrCd, acctCd].join('_')
    let valid = (postDt !== undefined && cctrCd !== undefined && acctCd !== undefined)
    if (bdg_mutex[id] || !valid) {
      resolve(id)
    } else {
      bdg_mutex[id] = true
      this.$http.get('/api/budget/remain', {
        params: {
          postDt,
          cctrCd,
          acctCd
        }
      }).then(response => {
        budget[id] = this.$numeral(response.data).value()
        $bus.$emit('BUDGET_CMPL', id)
      }).finally(() => {
        delete bdg_mutex[id]
        resolve(budget[id])
      })
    }
  })
}

export default {
  props: {
    id: {
      type: String,
      required: false
    },
    budReqNo: {
      type: String,
      required: false
    },
    manage: {
      type: Boolean,
      required: false,
      default: false
    },
    value: {
      type: Object,
      required: false,
      default () {
        return {
          //예산신청번호
          budReqNo: undefined,
          budgetDetails: [],
          //회사코드
          compCd: undefined,
          //신청상태코드
          budStatCd: '10',
          //예산구분코드
          budFgCd: '10',
          budFgNm: undefined,
          //전용유형코드
          brwTypeCd: undefined,
          //신청총금액
          reqTotAmt: 0,
          //신청사유
          reqRsn: '',
          //ERP관리번호
          erpMngNo: undefined,
          //최종결재일시
          fnlApprDtm: undefined,
          //최종결재자ID
          fnlAprverId: undefined,
          //전자결재ID
          elecApprId: undefined,
          //전자결재기안일시
          elecApprDtm: undefined,
          //반려사유
          rejRsn: undefined,
          //작성자ID
          wrtId: undefined,
          //작성부서코드
          wrtDeptCd: undefined,
          //작성일자
          wrtDt: undefined,
          //증빙관리번호
          evdMngNo: undefined,
          //문서고유값
          docInVal: undefined
        }
      }
    },
    status: {
      type: Object,
      required: false,
      default () {
        return {
          memento: [],
          readonly: false
        }
      }
    },
    readonly: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  components: {
    DhxGrid,
    TableRadio
  },
  data() {
    return {
      data: {},
      config_e: {
        columns: [{
          id: 'budSeq',
          value: 'No.',
          type: 'cntr',
          width: 50
        }, {
          id: 'brwTypeNm',
          value: '신청유형'
        }, {
          id: 'sndYm',
          value: '주는 대상',
          align: 'center',
          type: 'dhxCalendarA'
        }, {
          id: 'sndCctrCd',
          value: '#cspan'
        }, {
          id: 'sndCctrNm',
          value: '#cspan',
          width: 150,
          align: 'left'
        }, {
          id: 'sndCctrSrch',
          value: '#cspan',
          width: 50,
          component: CctrSearchButton,
          mixin: {
            methods: {
              onSubmit(data) {
                this.value.sndCctrCd = data.cctrCd
                this.value.sndCctrNm = data.cctrNm

                switch (this.value.brwTypeCd) {
                  case '20':
                  case '30':
                    this.value.rcvCctrCd = data.cctrCd
                    this.value.rcvCctrNm = data.cctrNm
                    break
                }
              }
            }
          }
        }, {
          id: 'sndAcctCd',
          value: '#cspan'
        }, {
          id: 'sndAcctNm',
          value: '#cspan',
          width: 150,
          align: 'left'
        }, {
          id: 'sndAcctSrch',
          value: '#cspan',
          width: 50,
          component: AcctSearchButton,
          mixin: {
            methods: {
              onSubmit(data) {
                this.value.sndAcctCd = data.acctCd
                this.value.sndAcctNm = data.acctNm

                switch (this.value.brwTypeCd) {
                  case '20':
                  case '40':
                    this.value.rcvAcctCd = data.acctCd
                    this.value.rcvAcctNm = data.acctNm
                    break
                }
              }
            }
          }
        }, {
          id: 'rmdAmt',
          value: '#cspan',
          align: 'right',
          component: {
            props: ['index', 'value', 'field'],
            template: `
              <span style="padding-right: 10px;" v-if="data !== undefined">{{ this.$numeral(data).format('0,0') }}</span>
              <span v-else></span>
            `,
            data() {
              return {
                data: undefined
              }
            },
            created() {
              let id = [this.value.sndYm, this.value.sndCctrCd, this.value.sndAcctCd].join('_')
              this.data = this.value.rmdAmt = budget[id]

              if (this.data === undefined) {
                queryRemainBudget.apply(this, [this.value.sndYm, this.value.sndCctrCd, this.value.sndAcctCd])
              }

              $bus.$on('BUDGET_CMPL', () => {
                this.data = this.value.rmdAmt = budget[id]
              })
            },
            watch: {
              immediate: true,
              deep: true,
              handler() {
                queryRemainBudget.apply(this, [this.value.sndYm, this.value.sndCctrCd, this.value.sndAcctCd])
              }
            }
          }
        }, {
          id: 'rcvYm',
          value: '받는 대상',
          align: 'center',
          type: 'dhxCalendarA'
        }, {
          id: 'rcvCctrCd',
          value: '#cspan'
        }, {
          id: 'rcvCctrNm',
          value: '#cspan',
          width: 150,
          align: 'left'
        }, {
          id: 'rcvCctrSrch',
          value: '#cspan',
          width: 50,
          component: CctrSearchButton,
          mixin: {
            methods: {
              onSubmit(data) {
                this.value.rcvCctrCd = data.cctrCd
                this.value.rcvCctrNm = data.cctrNm
              }
            }
          }
        }, {
          id: 'rcvAcctCd',
          value: '#cspan'
        }, {
          id: 'rcvAcctNm',
          value: '#cspan',
          width: 150,
          align: 'left'
        }, {
          id: 'rcvAcctSrch',
          value: '#cspan',
          width: 50,
          component: AcctSearchButton,
          mixin: {
            methods: {
              onSubmit(data) {
                this.value.rcvAcctCd = data.acctCd
                this.value.rcvAcctNm = data.acctNm
              }
            }
          }
        }, {
          id: 'reqAmt',
          value: '신청금액',
          align: 'right',
          type: 'edn'
        }],
        events: {
          onEditCell(stage, rId, cInd, nValue, oValue) {
            if (stage === 2) {
              if (nValue !== oValue) {
                var index = this.instance.getRowIndex(rId)
                let row = this.value[index]
                let c = this.options.columns[cInd]

                if (c.id === 'sndYm' && (row.brwTypeCd === '30' || row.brwTypeCd === '40')) {
                  row.rcvYm = nValue
                } else if (c.id === 'reqAmt') {
                  row.reqAmt = this.$numeral(nValue).value()
                  let reqTotAmt = this.value.map(x => this.$numeral(x.reqAmt).value()).reduce((ac, v) => ac + v)
                  this.$parent.data.reqTotAmt = reqTotAmt
                }
              }
            }
          }
        },
        beforeRefreshData(grid, data) {
          if (grid && Array.isArray(data)) {
            _.forEach(data, (r, i) => {
              var rId = String(i + 1)
              this.unlockAllCells(rId)

              switch (r.brwTypeCd) {
                case '10':
                  this.lockCells(rId, [2, 3, 4, 5, 6, 7, 8, 9])
                  break;
                case '20':
                  this.lockCells(rId, [11, 12, 13, 14, 15, 16])
                  break;
                case '30':
                  this.lockCells(rId, [10, 11, 12, 13])
                  break;
                case '40':
                  this.lockCells(rId, [10, 14, 15, 16])
                  break;
              }
            })
          }
        },
        afterRefreshData(grid, data) {
          if (grid && Array.isArray(data)) {
            this.$nextTick(() => {
              _.forEach(data, (r, i) => {
                var rId = grid.getRowId(i)
                this.setColumnClassName(rId, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], 'bg-grey', true)
                this.setColumnClassName(rId, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], 'bg-lightpink', true)
                this.setColumnClassName(rId, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], 'bg-yellow', true)
                switch (r.brwTypeCd) {
                  case '10':
                    this.setColumnClassName(rId, [2, 3, 4, 5, 6, 7, 8, 9], 'bg-grey')
                    this.setColumnClassName(rId, [10, 12, 13, 15, 16, 17], 'bg-lightpink')
                    break
                  case '20':
                    this.setColumnClassName(rId, [11, 12, 13, 14, 15, 16], 'bg-grey')
                    this.setColumnClassName(rId, [2, 4, 5, 7, 8, 10, 17], 'bg-lightpink')
                    this.setColumnClassName(rId, 9, 'bg-yellow')
                    break
                  case '30':
                    this.setColumnClassName(rId, [10, 11, 12, 13], 'bg-grey')
                    this.setColumnClassName(rId, [2, 4, 5, 7, 8, 15, 16, 17], 'bg-lightpink')
                    this.setColumnClassName(rId, 9, 'bg-yellow')
                    break
                  case '40':
                    this.setColumnClassName(rId, [10, 14, 15, 16], 'bg-grey')
                    this.setColumnClassName(rId, [2, 4, 5, 7, 8, 12, 13, 17], 'bg-lightpink')
                    this.setColumnClassName(rId, 9, 'bg-yellow')
                    break
                }
              })
              grid.callEvent('ongridreconstructed', [])
            })
          }
        }
      },
      config_r: {
        columns: [{
          id: 'budSeq',
          value: 'No.',
          width: 50
        }, {
          id: 'brwTypeNm',
          value: '신청유형'
        }, {
          id: 'sndYm',
          value: '주는 대상',
          component: DateRenderer
        }, {
          id: 'sndCctrCd',
          value: '#cspan'
        }, {
          id: 'sndCctrNm',
          value: '#cspan',
          width: 150,
          align: 'left'
        }, {
          id: 'sndAcctCd',
          value: '#cspan'
        }, {
          id: 'sndAcctNm',
          value: '#cspan',
          width: 150,
          align: 'left'
        }, {
          id: 'rcvYm',
          value: '받는 대상',
          component: DateRenderer
        }, {
          id: 'rcvCctrCd',
          value: '#cspan'
        }, {
          id: 'rcvCctrNm',
          value: '#cspan',
          width: 150,
          align: 'left'
        }, {
          id: 'rcvAcctCd',
          value: '#cspan'
        }, {
          id: 'rcvAcctNm',
          value: '#cspan',
          width: 150,
          align: 'left'
        }, {
          id: 'reqAmt',
          value: '신청금액',
          align: 'right',
          type: 'ron'
        }],
        afterRefreshData(grid, data) {
          if (grid && Array.isArray(data)) {
            this.$nextTick(() => {
              _.forEach(data, (r, i) => {
                var rId = grid.getRowId(i)
                this.setColumnClassName(rId, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'bg-grey', true)
                switch (r.brwTypeCd) {
                  case '10':
                    this.setColumnClassName(rId, [2, 3, 4, 5, 6], 'bg-grey')
                    break
                  case '20':
                    this.setColumnClassName(rId, [8, 9, 10, 11], 'bg-grey')
                    break
                  case '30':
                    this.setColumnClassName(rId, [7, 8, 9], 'bg-grey')
                    break
                  case '40':
                    this.setColumnClassName(rId, [7, 10, 11], 'bg-grey')
                    break
                }
              })
              grid.callEvent('ongridreconstructed', [])
            })
          }
        }
      },
      options: {
        'BRW_TYPE_CD': [],
        'BUD_FG_CD': []
      },
      mutex: {}
    }
  },
  computed: {
    isNew() {
      return this.getId === undefined && this.data.budReqNo === undefined
    },
    isSaved() {
      return this.getId !== undefined || this.data.budReqNo !== undefined
    },
    config() {
      return this.isReadonly ? this.config_r : this.config_e
    },
    getId() {
      return this.budReqNo || this.id
    },
    isReadonly() {
      return this.status.readonly || this.readonly
    }
  },
  methods: {
    queryBrwTypeCd() {
      return new Promise(resolve => {
        if (this.mutex['BRW_TYPE_CD']) {
          resolve()
        } else {
          this.mutex['BRW_TYPE_CD'] = true
          this.$store.commit('loading')
          this.$http.get('/api/code/combo', {
            params: {
              groupCd: 'BRW_TYPE_CD'
            }
          }).then(response => {
            this.options['BRW_TYPE_CD'] = response.data.map(x => {
              x.label = x.value
              x.value = x.key
              return x
            })
          }).finally(() => {
            this.$store.commit('finish')
            delete this.mutex['BRW_TYPE_CD']
            return resolve()
          })
        }
      })
    },
    queryBudFgCd() {
      return new Promise(resolve => {
        if (this.mutex['BUD_FG_CD']) {
          resolve()
        } else {
          this.mutex['BUD_FG_CD'] = true
          this.$store.commit('loading')
          this.$http.get('/api/code/combo', {
            params: {
              groupCd: 'BUD_FG_CD'
            }
          }).then(response => {
            this.options['BUD_FG_CD'] = response.data
          }).finally(() => {
            this.$store.commit('finish')
            delete this.mutex['BUD_FG_CD']
            return resolve()
          })
        }
      })
    },
    queryBdgtReq() {
      return new Promise((resolve, reject) => {
        this.$store.commit('loading')
        this.$http.get(`/api/budget/${this.getId}`)
          .then(response => {
            let data = response.data.budgetHeader
            data.budgetDetails = response.data.budgetDetails

            this.data = data
            this.$emit('input', this.data)

            if (this.manage) {
              this.status.readonly = true
            } else {
              this.status.readonly = (this.data.budStatCd !== '10')
            }

            return resolve(response)
          })
          .catch(response => {
            return reject(response)
          })
          .finally(() => {
            this.$store.commit('finish')
          })
      })
    },
    constructGridSuccessful(grid) {
      var header_style = 'color:#222;text-align:center;'
      var stat_total_text = 'color:red;text-align:right;padding-right:10px !important;'

      if (!this.isReadonly) {
        grid.attachHeader(
          ['#rspan', '#rspan', '연월', '부서', '#cspan', '#cspan', '계정', '#cspan', '#cspan', '잔액', '연월', '부서', '#cspan', '#cspan', '계정', '#cspan', '#cspan', '#rspan']
        )
        grid.attachHeader(
          ['합계', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#stat_total'],
          [header_style, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', stat_total_text]
        )

        grid.setDateFormat('%Y-%m', '%Y%m')
        grid.setNumberFormat('0,000', 9, '.', ',')
        grid.setNumberFormat('0,000', 17, '.', ',')
      } else {
        grid.attachHeader(
          ['#rspan', '#rspan', '연월', '부서', '#cspan', '계정', '#cspan', '연월', '부서', '#cspan', '계정', '#cspan', '#rspan']
        )
        grid.attachHeader(
          ['합계', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#stat_total'],
          [header_style, '', '', '', '', '', '', '', '', '', '', '', stat_total_text]
        )

        grid.setNumberFormat('0,000', 12, '.', ',')
      }
    },
    reset_rows() {
      this.data.budgetDetails = []
      this.add_row_alter()
    },
    add_row(data) {
      data = data || {}
      this.data.budgetDetails.push({
        budReqNo: this.data.budReqNo,
        budSeq: undefined,
        compCd: this.data.compCd,
        brwTypeCd: this.data.brwTypeCd,
        brwTypeNm: this.data.brwTypeNm,
        sndYm: data.sndYm,
        sndCctrCd: data.sndCctrCd,
        sndCctrNm: data.sndCctrNm,
        sndAcctCd: data.sndAcctCd,
        sndAcctNm: data.sndAcctNm,
        rmdAmt: data.rmdAmt,
        rcvYm: data.rcvYm,
        rcvCctrCd: data.rcvCctrCd,
        rcvCctrNm: data.rcvCctrNm,
        rcvAcctCd: data.rcvAcctCd,
        rcvAcctNm: data.rcvAcctNm,
        reqAmt: 0
      })
    },
    add_row_alter() {
      switch (this.data.brwTypeCd) {
        case '10':
          this.add_row({
            rcvYm: this.$moment().format('YYYYMM'),
            rcvCctrCd: this.data.deptCd,
            rcvCctrNm: this.data.deptNm
          })
          break
        case '20':
          this.add_row({
            sndYm: this.$moment().format('YYYYMM'),
            sndCctrCd: this.data.deptCd,
            sndCctrNm: this.data.deptNm,
            rcvYm: this.$moment().format('YYYYMM'),
            rcvCctrCd: this.data.deptCd,
            rcvCctrNm: this.data.deptNm
          })
          break
        case '30':
          this.add_row({
            sndYm: this.$moment().format('YYYYMM'),
            sndCctrCd: this.data.deptCd,
            sndCctrNm: this.data.deptNm,
            rcvYm: this.$moment().format('YYYYMM'),
            rcvCctrCd: this.data.deptCd,
            rcvCctrNm: this.data.deptNm
          })
          break
        case '40':
          this.add_row({
            sndYm: this.$moment().format('YYYYMM'),
            sndCctrCd: this.data.deptCd,
            sndCctrNm: this.data.deptNm,
            rcvYm: this.$moment().format('YYYYMM'),
            rcvCctrCd: this.data.deptCd,
            rcvCctrNm: this.data.deptNm
          })
          break
      }
    },
    /**
     * 신청유형 변경 이벤트
     */
    brwTypeCdChangeEvent() {
      let f = this.options['BRW_TYPE_CD'].filter(x => x.value === this.data.brwTypeCd)[0]
      this.data.brwTypeNm = f !== undefined ? f.label : this.data.brwTypeCd
      this.reset_rows()
    },
    /**
     * 버튼 이벤트
     */
    buttonClickEvent_ResetRow() {
      this.reset_rows()
    },
    buttonClickEvent_AddRow() {
      this.add_row_alter()
    },
    buttonClickEvent_RemoveRow() {
      var rId = this.$refs.grid.instance.getSelectedRowId()
      if (rId === null) {
        this.$swal({
          type: 'warning',
          text: '삭제하려는 행을 선택해주십시오.'
        })
      } else {
        var index = this.$refs.grid.instance.getRowIndex(rId)
        this.data.budgetDetails.splice(index, 1)
      }
    }
  },
  created() {
    this.queryBrwTypeCd()
      .then(() => {
        if (this.data.brwTypeCd === undefined) {
          this.data.brwTypeCd = this.options['BRW_TYPE_CD'][0].value
          this.data.brwTypeNm = this.options['BRW_TYPE_CD'][0].label
          if (this.isNew) {
            this.reset_rows()
          }
          this.status.memento = [JSON.stringify(this.data)]
        }
      })

    if (this.isNew) {
      this.queryBudFgCd()
        .then(() => {
          let f = this.options['BUD_FG_CD'].filter(x => x.key === this.data.budFgCd)[0]
          this.data.budFgNm = f !== undefined ? f.value : this.data.budFgCd
          this.status.memento = [JSON.stringify(this.data)]
        })
    }

    if (this.isSaved) {
      this.queryBdgtReq()
        .then(() => {
          this.status.memento = [JSON.stringify(this.data)]
        })
    }

    // find logged in user
    let l = undefined
    try {
      l = this.$store.state.loginInfo.loginId
    } catch (e) {
      l = undefined
    }
    this.$http.get(_url('/api/emp', l))
      .then(response => {
        if (response.data.length > 0) {
          this.data.deptCd = response.data[0].deptCd
          this.data.deptNm = response.data[0].deptNm
          if (this.isNew) {
            this.reset_rows()
          }
        }
      })
      .finally(() => {
        this.status.memento = [JSON.stringify(this.data)]
      })
  },
  watch: {
    'data': {
      deep: true,
      handler(value) {
        let v = JSON.stringify(value)
        var index = this.status.memento.indexOf(v)
        if (index >= 0) {
          this.status.memento.splice(0, index)
        } else {
          this.status.memento.unshift(v)
        }
      }
    },
    'value': {
      immediate: true,
      deep: true,
      handler(value) {
        this.data = value
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.table-area table {
    table-layout: fixed;
}

.table-area table th {
    width: 150px;
}

.table-area .table-a table tr td {
    width: calc(33.33% - 150px);
    vertical-align: middle;
}

.table-area {
    :global(table) {
        :global(th) {
            vertical-align: middle !important;
        }

        :global(td) {
            vertical-align: middle !important;
        }
    }
}

.table-area .table-a table th.tp-a:before {
    content: "*";
    position: absolute;
    left: 11px;
    top: calc(50% + 2px);
    transform: translateY(-50%);
}
</style>
