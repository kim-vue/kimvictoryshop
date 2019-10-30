<template>
<div class="table-b">
  <div class="table-header">
    <div class="table-name">
      <h3 class="ico_table_name">세부항목</h3>
    </div>
    <div class="btn-wrap btn-type2">
      <button class="btn-size btn-w-gray" @click="buttenClickEventReset()">
        <span class="btn-icon">
          <i class="fas fa-redo"></i>
        </span>
        초기화
      </button>
      <button class="btn-size btn-w-gray" @click="buttonClickEventAdd()">
        <span class="btn-icon">
          <i class="fas fa-plus"></i>
        </span>
        행추가
      </button>
      <button class="btn-size btn-w-gray" @click="buttonClickEventRemove()">
        <span class="btn-icon">
          <i class="fas fa-trash-alt"></i>
        </span>
        행삭제
      </button>
    </div>
  </div>

  <!-- DhxGrid component -->
  <dhx-grid ref="grid" class="slip-grid" v-model="data" :config="config" @constructGridSuccessful="constructGridSuccessful" />
  <!-- //DhxGrid component -->
</div>
</template>

<script>
// For global event bus
import Vue from 'vue'
import _ from 'lodash'
import Join from '@/libs/join'
// Import DhxGrid
import DhxGrid from '@/components/DhxGrid.vue'
import Cctr from '@/components/Cctr_new.vue'
import Account from '@/components/Account_new.vue'
import IO from '@/components/IO_new.vue'
import SlipMngItemPop from '@/components/SlipMngItemPop.vue'
import mixin from '@/mixin/slip-common'

import DhxCalendar from '@/components/DhxCalendar.vue'
import NumberInput from '@/components/NumberInput.vue'
import GridInput from '@/components/grid/GridInput.vue'
import GridNumberInput from '@/components/grid/GridNumberInput.vue'
import GridSelect from '@/components/grid/GridSelect.vue'

const eventBus = new Vue()
const _url = Join.url

// For grid events handling
const modalStatus = {
  Cctr: false,
  Account: false
}

const options = {}

var queryTpsTypeCd_run = false
var queryOilKinCd_run = false
var queryOilPrice_run = {}

function queryTpsTypeCd() {
  if (options['E6_tpsTypeCd'] === undefined && !queryTpsTypeCd_run) {
    queryTpsTypeCd_run = true
    this.$http.get('/api/code/detail', {
      params: {
        groupCd: 'TPS_TYPE_CD'
      }
    }).then(response => {
      options['E6_tpsTypeCd'] = response.data
    }).catch(response => {
      options['E6_tpsTypeCd'] = undefined
      return response
    }).finally(() => {
      eventBus.$emit('E6_tpsTypeCd.updated')
      queryTpsTypeCd_run = false
    })
  }
}

function queryOilKinCd() {
  if (options['E6_oilKindCd'] === undefined && !queryOilKinCd_run) {
    queryOilKinCd_run = true
    this.$http.get('/api/code/detail', {
      params: {
        groupCd: 'OIL_KIND_CD'
      }
    }).then(response => {
      options['E6_oilKindCd'] = response.data
    }).catch(response => {
      options['E6_oilKindCd'] = undefined
      return response
    }).finally(() => {
      eventBus.$emit('E6_oilKindCd.updated')
      queryOilKinCd_run = false
    })
  }
}

function queryOilPrice(baseYm) {
  options['E6_oilPrice'] = options['E6_oilPrice'] || {}
  if (options['E6_oilPrice'][baseYm] === undefined && !queryOilPrice_run[baseYm]) {
    queryOilPrice_run[baseYm] = true
    this.$http.post('/api/oilPrice/list', {
      baseYm: baseYm
    }).then(response => {
      options['E6_oilPrice'][baseYm] = response.data
      return response
    }).catch(response => {
      options['E6_oilPrice'][baseYm] = undefined
      return response
    }).finally(() => {
      eventBus.$emit('E6_oilPrice.updated', baseYm)
      queryOilPrice_run[baseYm] = undefined
    })
  }
}

/**
 * 계정 관련 추가 정보
 */
const account = {}
const account_lock = {}

function queryAccountAddon(acctCd) {
  return new Promise((resolve, reject) => {
    if (!acctCd || account[acctCd] !== undefined || account_lock[acctCd]) {
      resolve(0)
    } else {
      account_lock[acctCd] = true
      this.$http.post('/api/slip/managementItem', {
        acctCd: acctCd,
        useYn: 'Y'
      }).then(response => {
        let filter = response.data.filter(x => x.acctCd === acctCd)
        account[acctCd] = filter.length
        eventBus.$emit(['account', acctCd].join('_'), filter.length)
      }).finally(() => {
        delete account_lock[acctCd]
      })
    }
  })
}

const budget = {}
const budget_mutex = {}

function queryRemainBudget(postDt, cctrCd, acctCd) {
  return new Promise((resolve, reject) => {
    let id = [postDt, cctrCd, acctCd].join('_')
    let valid = postDt && cctrCd && acctCd
    if (valid && !budget_mutex[id] && budget[id] === undefined) {
      budget_mutex[id] = true
      this.$http.get('/api/budget/remain', {
        params: {
          postDt,
          cctrCd,
          acctCd
        }
      }).then(response => {
        budget[id] = this.$numeral(response.data).value()
        eventBus.$emit('budget', budget[id])
        return resolve(budget[id])
      }).catch(response => {
        return reject(budget[id])
      }).finally(() => {
        delete budget_mutex[id]
      })
    } else {
      resolve(budget[id])
    }
  })
}

export default {
  props: ['slipType', 'value', 'status'],
  mixins: [mixin],
  components: {
    DhxGrid,
    Cctr,
    Account,
    DhxCalendar
  },
  computed: {
    config() {
      switch (this.slipType) {
        case 'E6':
          return this.config_E6
        default:
          return this.config_def
      }
    }
  },
  data() {
    return {
      id: 'ED',
      data: [],
      config_def: {
        columns: [{
          id: 'itemSeq',
          align: 'center',
          value: 'No.',
          type: 'cntr',
          width: 35
        }, {
          id: 'dcNm',
          align: 'center',
          value: '유형',
          width: 40
        }, {
          id: 'taxCd',
          align: 'center',
          value: '세금코드',
          width: 60
        }, {
          id: 'ioNo',
          width: 80,
          value: 'IO'
        }, {
          value: '#cspan',
          align: 'center',
          width: 40,
          component: {
            props: ['index', 'value', 'field'],
            template: `<button type="button" class="icon" @click="updateIoNo()"><i class="fas fa-search"></i></button>`,
            methods: {
              updateIoNo() {
                const value = this.$parent.value[this.index]
                this.$modal.open({
                  component: IO,
                  parent: this,
                  width: 700,
                  events: {
                    close(object) {
                      value.ioNo = object.ioCd
                    }
                  }
                })
              }
            }
          }
        }, {
          id: 'cctrCd',
          align: 'center',
          value: '귀속부서',
          width: 100
        }, {
          id: 'cctrNm',
          align: 'left',
          value: '귀속부서명',
          width: 120,
          type: 'ed'
        }, {
          id: 'cctrSrch',
          align: 'center',
          value: '#cspan',
          width: 40,
          component: {
            props: ['index', 'value', 'field'],
            template: `<button type="button" class="icon" @click="updateCctr()"><i class="fas fa-search"></i></button>`,
            methods: {
              updateCctr() {
                const vm = this
                this.$modal.open({
                  component: Cctr,
                  parent: this,
                  width: 700,
                  events: {
                    close(object) {
                      vm.value.cctrCd = object.cctrCd
                      vm.value.cctrNm = object.cctrNm
                    }
                  }
                })
              }
            }
          }
        }, {
          id: 'acctCd',
          align: 'center',
          value: '계정코드',
          width: 80
        }, {
          id: 'acctNm',
          align: 'left',
          value: '계정명',
          width: 140,
          type: 'ed'
        }, {
          id: 'acctSrch',
          align: 'center',
          value: '#cspan',
          width: 40,
          component: {
            props: ['index', 'value', 'field'],
            template: `<button type="button" class="icon" @click="updateAccount()"><i class="fas fa-search"></i></button>`,
            methods: {
              updateAccount() {
                const vm = this
                this.$modal.open({
                  component: Account,
                  parent: this,
                  props: {
                    slipTypeCd: vm.$parent.$parent.value.slipTypeCd
                  },
                  width: 700,
                  events: {
                    close(object) {
                      vm.value.acctCd = object.acctCd
                      vm.value.acctNm = object.acctNm
                      vm.value.ctrlYn = object.ctrlYn
                    }
                  }
                })
              }
            }
          }
        }, {
          id: 'acctAddon',
          value: '#cspan',
          width: 40,
          component: {
            props: ['index', 'value', 'field'],
            template: `
              <button type="button" class="icon" v-if="visible" @click="openAddon()"><i class="fas fa-search"></i></button>
            `,
            data() {
              return {
                visible: false
              }
            },
            methods: {
              openAddon() {
                let vm = this
                this.$modal.open({
                  component: SlipMngItemPop,
                  props: {
                    acctCd: this.value.acctCd,
                    data: this.value
                  },
                  parent: this,
                  events: {
                    close(data) {
                      for (var i = 1; i <= 10; i++) {
                        let id = ['ref', i].join('')
                        vm.value[id] = data[id]
                      }
                    }
                  }
                })
              }
            },
            created() {
              let length = account[this.value.acctCd]
              if (length === undefined) {
                queryAccountAddon.apply(this, [this.value.acctCd])
              } else {
                this.visible = length > 0
                this.value.hasAddon = this.visible
              }

              eventBus.$on(['account', this.value.acctCd].join('_'), () => {
                this.visible = account[this.value.acctCd] > 0
                this.value.hasAddon = this.visible
              })
            },
            watch: {
              value: {
                immediate: true,
                deep: true,
                handler() {}
              }
            }
          }
        }, {
          id: 'bdgAmt',
          value: '잔여예산',
          width: 80,
          type: 'ron',
          align: 'right',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span style="padding-right: 8px;">{{ this.$numeral(data).format('0,0') }}</span>`,
            data() {
              return {
                data: 0
              }
            },
            methods: {
              changeData(val) {
                try {
                  let value = val || 0
                  let filter = this.$parent.value.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'D_ITEM' && x.acctCd === this.value.acctCd && x.cctrCd === this.value.cctrCd)
                  let sum = filter.map(x => x.acctAmt).reduce((ac, cv) => ac + cv)
                  this.data = this.value.ctrlYn === 'Y' ? value - sum : 0
                } catch (e) {}
              }
            },
            created() {
              let postDt = this.$parent.$parent.value.postDt
              let cctrCd = this.value.cctrCd
              let acctCd = this.value.acctCd
              let id = [postDt, cctrCd, acctCd].join('_')

              if (budget[id] === undefined) {
                queryRemainBudget.apply(this, [postDt, cctrCd, acctCd])
              } else {
                this.value.bdgAmt = budget[id]
                this.changeData(budget[id])
              }

              eventBus.$on('budget', val => {
                this.value.bdgAmt = budget[id]
                this.changeData(budget[id])
              })
            },
            watch: {
              value: {
                immediate: true,
                deep: true,
                handler(value) {
                  this.changeData(value[this.field])

                  let postDt = this.$parent.$parent.value.postDt
                  let cctrCd = this.value.cctrCd
                  let acctCd = this.value.acctCd
                  queryRemainBudget.apply(this, [postDt, cctrCd, acctCd])
                }
              }
            }
          }
        }, {
          id: 'debitAmt',
          value: '차변금액',
          width: 90,
          type: 'edn',
          align: 'right'
        }, {
          id: 'creditAmt',
          align: 'right',
          value: '대변금액',
          width: 90,
          type: 'ron'
        }, {
          id: 'lnSgtxt',
          align: 'left',
          value: '적요',
          type: 'ed',
          width: 200
        }],
        height: 260,
        events: {
          onEditCell(stage, rId, cInd, nValue, oValue) {
            let row = this.data[rId - 1]
            let colDef = this.options.columns[cInd]

            // Edit event handler
            if (stage === 2 && nValue !== oValue) {
              switch (colDef.id) {
                case 'cctrNm': // 귀속부서
                  // Delay 200ms
                  setTimeout(() => {
                    if (row.cctrNm) {
                      _findCctr.apply(this, [row.cctrNm])
                    } else {
                      row.cctrNm = String(oValue)
                    }
                  }, 200)
                  break
                case 'acctNm': // 계정
                  // Delay 200ms
                  setTimeout(() => {
                    if (row.acctNm) {
                      _findAccount.apply(this, [row.acctNm])
                    } else {
                      row.acctNm = String(oValue)
                    }
                  }, 200)
                  break
                case 'debitAmt':
                  row.acctAmt = row.debitAmt = this.$numeral(nValue || 0).value()
                  break
              }
            }

            return true

            function _findCctr(searchStr) {
              this.$store.commit('loading')
              this.$http.get(_url('/api/cctr', searchStr))
                .then(response => {
                  if (Array.isArray(response.data)) {
                    if (response.data.length === 1) {
                      row.cctrCd = response.data[0].cctrCd
                      row.cctrNm = response.data[0].cctrNm
                    } else {
                      _openCctrModal.apply(this, [searchStr])
                    }
                  } else {
                    _openCctrModal.apply(this, [searchStr])
                  }
                }).finally(() => {
                  this.$store.commit('finish')
                })
            }

            function _openCctrModal(searchStr) {
              if (!modalStatus.Cctr) {
                modalStatus.Cctr = true
                this.$modal.open({
                  component: Cctr,
                  props: {
                    title: '귀속부서',
                    searchStr
                  },
                  parent: this,
                  events: {
                    close(data) {
                      row.cctrCd = data.cctrCd
                      row.cctrNm = data.cctrNm
                      modalStatus.Cctr = false
                    },
                    dismiss() {
                      row.cctrNm = String(oValue)
                      modalStatus.Cctr = false
                    }
                  }
                })
              }
            }

            function _findAccount(searchStr) {
              this.$store.commit('loading')
              this.$http.get(_url('/api/account', searchStr))
                .then(response => {
                  if (Array.isArray(response.data)) {
                    if (response.data.length === 1) {
                      row.acctCd = response.data[0].acctCd
                      row.acctNm = response.data[0].acctNm
                      row.ctrlYn = response.data[0].ctrlYn
                    } else {
                      _openAccountModal.apply(this, [searchStr])
                    }
                  } else {
                    _openAccountModal.apply(this, [searchStr])
                  }
                }).finally(() => {
                  this.$store.commit('finish')
                })
            }

            function _openAccountModal(searchStr) {
              if (!modalStatus.Account) {
                modalStatus.Account = true
                this.$modal.open({
                  component: Account,
                  props: {
                    title: '귀속부서',
                    searchStr
                  },
                  parent: this,
                  events: {
                    close(data) {
                      row.acctCd = data.acctCd
                      row.acctNm = data.acctNm
                      row.ctrlYn = data.ctrlYn
                      modalStatus.Account = false
                    },
                    dismiss() {
                      row.acctNm = String(oValue)
                      modalStatus.Account = false
                    }
                  }
                })
              }
            }
          }
        },
        afterRefreshData(grid, data) {
          if (grid !== undefined && data !== undefined && Array.isArray(data)) {
            this.$nextTick(() => {
              _.forEach(data, (item, index) => {
                var rowIndex = index + 1
                var val = [item.dcCd, item.lnTypeCd].join('_')

                switch (val) {
                  case 'C_ITEM':
                    grid.lockRow(rowIndex, true)
                    break
                  case 'D_TAX':
                    grid.lockRow(rowIndex, true)
                    break
                  case 'D_ITEM':
                    this.setColumnClassName(rowIndex, [6, 7, 9, 10, 13, 15], 'bg-lightpink')
                    break
                }
              })
            })
          }
        }
      },
      config_E6: {
        columns: [{
          id: 'itemSeq',
          value: 'No.',
          width: 35
        }, {
          id: 'useDt',
          value: '사용일자',
          width: 60,
          align: 'left',
          type: 'dhxCalendarA'
        }, {
          id: 'stptPlc',
          width: 60,
          value: '출발지',
          align: 'left',
          type: 'ed'
        }, {
          id: 'dstnPlc',
          width: 60,
          value: '도착지',
          align: 'left',
          type: 'ed'
        }, {
          id: 'biztrpObj',
          width: 60,
          value: '출장목적',
          align: 'left',
          type: 'ed'
        }, {
          id: 'tpsTypeCd',
          width: 60,
          value: '교통비유형',
          component: GridSelect,
          mixin: {
            data() {
              return {
                options: []
              }
            },
            created() {
              this.options = options['E6_tpsTypeCd']
              eventBus.$on('E6_tpsTypeCd.updated', () => {
                this.options = options['E6_tpsTypeCd']
              })
            },
            methods: {
              onSubmit() {
                if (this.value.tpsTypeCd === '10') {
                  this.value.acctAmt = 0
                  this.value.tpsDst = 0
                  this.value.oilKindCd = 'GSL'
                } else {
                  this.value.tpsDst = undefined
                  this.value.oilUpc = undefined
                  this.value.oilEff = undefined
                  this.value.acctAmt = 0
                  this.value.oliKindCd = undefined
                }
              }
            }
          }
        }, {
          id: 'tpsDst',
          value: '거리',
          width: 60,
          align: 'right',
          type: 'edn'
        }, {
          id: 'oilKindCd',
          value: '유종',
          width: 60,
          component: GridSelect,
          mixin: {
            data() {
              return {
                options: []
              }
            },
            created() {
              if (this.value.tpsTypeCd !== '10') {
                this.showIf = false
              }
              this.options = options['E6_oilKindCd']
              this.onSubmit()
              eventBus.$on('E6_oilKindCd.updated', () => {
                this.options = options['E6_oilKindCd']
                this.onSubmit()
              })
            },
            methods: {
              onSubmit() {
                if (this.value.tpsTypeCd === '10') {
                  if (options['E6_oilPrice']) {
                    var search = (options['E6_oilPrice'][this.$moment(this.value.useDt).format('YYYYMM')] || []).filter(x => x.oilKindCd === this.value.oilKindCd)
                    // found
                    if (search.length > 0) {
                      this.value.oilUpc = search[0].oilUpce
                      this.value.oilEff = search[0].oilEff
                      if (this.value.tpsTypeCd === '10') {
                        var tpsDst = this.$numeral(this.value.tpsDst).value()
                        var oilUpc = this.$numeral(this.value.oilUpc).value()
                        var oilEff = this.$numeral(this.value.oilEff).value()
                        try {
                          this.value.supAmt = this.value.acctAmt = Math.floor(tpsDst / oilEff * oilUpc)
                        } catch (e) {
                          this.value.supAmt = this.value.acctAmt = 0
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }, {
          id: 'oilUpc',
          value: '유류단가/연비',
          width: 80,
          component: {
            props: ['index', 'value', 'field'],
            template: `<span v-if="value.oilUpc && value.oilEff">{{ this.$numeral(value.oilUpc).format('0,0') }} / {{ this.$numeral(value.oilEff).format('0,0') }}</span>`,
            data() {
              return {
                options: []
              }
            },
            created() {
              this.options = options['E6_oilPrice'] ? options['E6_oilPrice'][this.$moment(this.value.useDt).format('YYYYMM')] : []
              this.updateOilPriceInfo()

              eventBus.$on('E6_oilPrice.updated', baseYm => {
                this.options = options['E6_oilPrice'][baseYm]
                this.updateOilPriceInfo()
              })
            },
            methods: {
              updateOilPriceInfo() {
                if (options['E6_oilPrice'] && this.value.tpsTypeCd === '10') {
                  var search = (options['E6_oilPrice'][this.$moment(this.value.useDt).format('YYYYMM')] || []).filter(x => x.oilKindCd === this.value.oilKindCd)
                  // found
                  if (search.length > 0) {
                    this.value.oilUpc = search[0].oilUpce
                    this.value.oilEff = search[0].oilEff
                    if (this.value.tpsTypeCd === '10') {
                      var tpsDst = this.$numeral(this.value.tpsDst).value()
                      var oilUpc = this.$numeral(this.value.oilUpc).value()
                      var oilEff = this.$numeral(this.value.oilEff).value()
                      try {
                        this.value.supAmt = this.value.acctAmt = Math.floor(tpsDst / oilEff * oilUpc)
                      } catch (e) {
                        this.value.supAmt = this.value.acctAmt = 0
                      }
                    }
                  }
                }
              }
            }
          }
        }, {
          id: 'acctAmt',
          value: '사용금액',
          width: 60,
          align: 'right',
          type: 'edn'
        }, {
          id: 'acctCd',
          align: 'center',
          value: '계정코드',
          width: 50
        }, {
          id: 'acctNm',
          align: 'left',
          value: '계정명',
          width: 80,
          type: 'ed'
        }, {
          id: 'acctSrch',
          align: 'center',
          value: '#cspan',
          width: 20,
          component: {
            props: ['index', 'value', 'field'],
            template: `<button type="button" class="icon" @click="updateAccount()"><i class="fas fa-search"></i></button>`,
            methods: {
              updateAccount() {
                const value = this.$parent.value[this.index]
                const self = this.$parent
                this.$modal.open({
                  component: Account,
                  parent: this,
                  props: {
                    slipTypeCd: self.$parent.value.slipTypeCd
                  },
                  width: 700,
                  events: {
                    close(object) {
                      value.acctCd = object.acctCd
                      value.acctNm = object.acctNm
                      value.ctrlYn = object.ctrlYn
                    }
                  }
                })
              }
            }
          }
        }],
        height: 260,
        events: {
          onEditCell(stage, rId, cInd, nValue, oValue) {
            let row = this.data[rId - 1]
            let colDef = this.options.columns[cInd]

            // Before start
            if (stage === 0) {
              // 교통비유형이 10인 경우, 금액 수정 불가
              if (colDef.id === 'acctAmt' && row.tpsTypeCd === '10') {
                return false
              }
              // 교통비유형이 10이 아닌 경우, 거리 수정 불가
              else if (colDef.id === 'tpsDst' && row.tpsTypeCd !== '10') {
                return false
              }
            }
            // Edit event handler
            else if (stage === 2 && nValue !== oValue && colDef.id === 'acctNm') {
              setTimeout(() => {
                if (row.acctNm) {
                  _findAccount.apply(this, [row.acctNm])
                } else {
                  row.acctNm = String(oValue)
                }
              }, 200)
            }

            return true

            function _findAccount(searchStr) {
              this.$store.commit('loading')
              this.$http.get(_url('/api/account', searchStr))
                .then(response => {
                  if (Array.isArray(response.data)) {
                    if (response.data.length === 1) {
                      row.acctCd = response.data[0].acctCd
                      row.acctNm = response.data[0].acctNm
                      row.ctrlYn = response.data[0].ctrlYn
                    } else {
                      _openAccountModal.apply(this, [searchStr])
                    }
                  } else {
                    _openAccountModal.apply(this, [searchStr])
                  }
                }).finally(() => {
                  this.$store.commit('finish')
                })
            }

            function _openAccountModal(searchStr) {
              if (!modalStatus.Account) {
                modalStatus.Account = true
                this.$modal.open({
                  component: Account,
                  props: {
                    title: '귀속부서',
                    searchStr
                  },
                  parent: this,
                  events: {
                    close(data) {
                      row.acctCd = data.acctCd
                      row.acctNm = data.acctNm
                      row.ctrlYn = data.ctrlYn
                      modalStatus.Account = false
                    },
                    dismiss() {
                      row.acctNm = String(oValue)
                      modalStatus.Account = false
                    }
                  }
                })
              }
            }
          },
          onCellChanged(rId, cInd, nValue) {
            let row = this.data[this.instance.getRowIndex(rId)]
            let colDef = this.options.columns[cInd]

            if (colDef.id === 'useDt') {
              let max = String(Math.max.apply(this, this.value.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'D_ITEM').map(x => x.useDt)))
              this.$parent.value.payDueDt = max
              _.forEach(this.value.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'C_ITEM'), x => {
                x.useDt = max
              })
            } else if (colDef.id === 'tpsDst') {
              if (row.tpsTypeCd === '10') {
                var tpsDst = this.$numeral(row.tpsDst).value()
                var oilUpc = this.$numeral(row.oilUpc).value()
                var oilEff = this.$numeral(row.oilEff).value()
                try {
                  row.supAmt = row.acctAmt = Math.floor(tpsDst / oilEff * oilUpc)
                } catch (e) {
                  // this.value[rId - 1].supAmt = this.value[rId - 1].acctAmt = 0
                }
              }
            } else if (colDef.id === 'acctAmt') {
              let id = [row.dcCd, row.lnTypeCd].join('_')
              if (id === 'D_ITEM') {
                let totAmt = this.value.filter(x => [x.dcCd, row.lnTypeCd].join('_') === 'D_ITEM').map(x => x.acctAmt).reduce((a, v) => a + v)
                let taxRt = this.$parent.value.taxRt / 100.0
                let taxAmt = Math.floor(taxRt * totAmt / (1 + taxRt))
                let supAmt = totAmt - taxAmt

                this.$parent.value.totAmt = totAmt
                this.$parent.value.supAmt = supAmt
                this.$parent.value.taxAmt = taxAmt

                // _.forEach(this.value.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'C_ITEM'), x => {
                //   x.acctAmt = totAmt
                // })
              }
            }
          }
        },
        afterRefreshData(grid, data) {
          if (grid !== undefined && data !== undefined && Array.isArray(data)) {
            this.$nextTick(() => {
              _.forEach(data, (item, index) => {
                var rowIndex = index + 1
                var val = [item.dcCd, item.lnTypeCd].join('_')

                switch (val) {
                  case 'C_ITEM':
                    grid.lockRow(rowIndex, true)
                    break
                  case 'D_TAX':
                    grid.lockRow(rowIndex, true)
                    break
                  case 'D_ITEM':
                    this.setColumnClassName(rowIndex, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'bg-lightpink', true)
                    if (item.tpsTypeCd === '10')
                      this.setColumnClassName(rowIndex, [1, 2, 3, 4, 5, 6, 7, 11, 12], 'bg-lightpink')
                    else
                      this.setColumnClassName(rowIndex, [1, 2, 3, 4, 5, 9, 11, 12], 'bg-lightpink')
                    break
                }
              })
            })
          }
        }
      }
    }
  },
  created() {
    if (this.slipType === 'E6') {
      queryTpsTypeCd.apply(this, [])
      queryOilKinCd.apply(this, [])
      queryOilPrice.apply(this, [this.$moment(this.value.evdDt).format('YYYYMM')])
    }
  },
  methods: {
    buttenClickEventReset() {
      // TODO::물어봐요
      // 데이터 리셋
      this.reset_rows()
      this.$refs.grid.instance.callEvent('onGridReconstructed', [])
    },
    buttonClickEventAdd() {
      let dupv = 0
      if (this.data.length > 0 && this.slipTypeCd !== 'E6') {
        var sum = this.data.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'D_ITEM').map(x => x.acctAmt).reduce((a, v) => a + v)
        dupv = this.value.supAmt - sum
        dupv = dupv < 0 ? 0 : dupv
      }
      this.add_row({
        dcCd: 'D',
        lnTypeCd: 'ITEM',
        useDt: this.slipType === 'E6' ? this.value.evdDt : undefined,
        tpsTypeCd: this.slipType === 'E6' ? '10' : undefined,
        oilKindCd: this.slipType === 'E6' ? 'GSL' : undefined,
        acctAmt: this.slipType !== 'E6' ? dupv : undefined
      })
      this.$refs.grid.instance.callEvent('onGridReconstructed', [])
    },
    buttonClickEventRemove() {
      try {
        if (this.$refs.grid.instance.getSelectedRowId() == null)
          throw '선택된 행이 없습니다.'
        let index = this.$refs.grid.instance.getSelectedRowId() - 1
        let row = this.value.slipDetails[index]
        let id = [row.dcCd, row.lnTypeCd].join('_')
        if (id !== 'D_ITEM') {
          this.$swal({
            type: 'warning',
            text: '선택하신 행은 삭제할 수 없습니다.'
          })
        } else {
          var size = this.value.slipDetails.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'D_ITEM').length
          this.value.slipDetails.splice(index, 1)
          if (size === 1) {
            this.add_row({
              dcCd: 'D',
              lnTypeCd: 'ITEM',
              useDt: this.value.slipTypeCd === 'E6' ? this.value.evdDt : undefined,
              tpsTypeCd: this.value.slipTypeCd === 'E6' ? '10' : undefined,
              oilKindCd: this.value.slipTypeCd === 'E6' ? 'GSL' : undefined,
              acctAmt: this.value.slipTypeCd !== 'E6' ? this.value.supAmt : undefined
            })
          }
          this.$refs.grid.instance.callEvent('onGridReconstructed', [])
        }
      } catch (e) {
        this.$swal({
          type: 'warning',
          text: e
        })
      }
    },
    constructGridSuccessful(grid) {
      var header_style = 'color:#222;text-align:center;'
      var stat_total_text = 'color:red;text-align:right;padding-right:10px !important;'
      let vm = this
      if (this.slipType === 'E6') {
        /**
         * Custom summary function
         */
        grid._in_header_stat_total = function(tag, index, data) {
          let calc = function() {
            let sum = 0
            try {
              sum = vm.data.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'D_ITEM').map(x => x.acctAmt).reduce((a, x) => a + x)
            } catch (e) {
              sum = 0
            }
            return vm.$numeral(sum).format('0,0')
          }
          this._stat_in_header(tag, calc, index, data, data)
        }

        grid.attachHeader(
          ['합계', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#stat_total', '', '', ''],
          [header_style, '', '', '', '', '', '', '', '', stat_total_text, '', '', '']
        )

        grid.setDateFormat('%Y-%m-%d', '%Y%m%d')
        grid.setNumberFormat('0,000', 6, '.', ',')
        grid.setNumberFormat('0,000', 9, '.', ',')
      } else {
        grid._in_header_stat_total = function(tag, index, data) {
          let calc = function() {
            let c = vm.config.columns[index]
            let sum = 0
            if (c !== undefined) {
              try {
                switch (c.id) {
                  case 'debitAmt':
                    sum = vm.data.filter(x => [x.dcCd, x.lnTypeCd].join('_') !== 'C_ITEM').map(x => x.acctAmt).reduce((a, x) => a + x)
                    break
                  case 'creditAmt':
                    sum = vm.data.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'C_ITEM').map(x => x.acctAmt).reduce((a, x) => a + x)
                    break
                }
              } catch (e) {
                sum = 0
              }
            }
            return vm.$numeral(sum).format('0,0')
          }
          this._stat_in_header(tag, calc, index, data, data)
        }

        grid.attachHeader(
          ['합계', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#stat_total', '#stat_total', ''],
          [header_style, '', '', '', '', '', '', '', '', '', '', '', '', stat_total_text, stat_total_text, '']
        )
        grid.setNumberFormat('0,000', 12, '.', ',')
        grid.setNumberFormat('0,000', 13, '.', ',')
        grid.setNumberFormat('0,000', 14, '.', ',')
      }
    }
  },
  watch: {
    'value': {
      immediate: true,
      deep: true,
      handler(value) {
        this.data = value.slipDetails
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.slip-grid {
    :global(.xhdr table tbody tr:last-child) {
        background-color: #f9f9f3;
    }

    :global(.xhdr table tbody tr:last-child td) {
        background-color: transparent !important;
    }

    :global(.xhdr table tbody tr:last-child td div) {
        background-color: transparent !important;
        color: inherit !important;
        text-align: inherit !important;
    }
}
</style>
