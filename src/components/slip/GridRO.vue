<template>
<div class="table-b">
  <div class="table-header">
    <div class="table-name">
      <h3 class="ico_table_name">세부항목</h3>
    </div>
  </div>

  <!-- DhxGrid component -->
  <dhx-grid ref="grid" class="slip-grid" v-model="data" :config="config" @constructGridSuccessful="constructGridSuccessful" />
  <!-- //DhxGrid component -->
</div>
</template>

<script>
import Vue from 'vue'

// Import DhxGrid
import DhxGrid from '@/components/DhxGrid.vue'
import Cctr from '@/components/Cctr.vue'
import Account from '@/components/Account.vue'
import SlipMngItemPop from '@/components/SlipMngItemPop.vue'

const eventBus = new Vue()

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

export default {
  props: ['value', 'status'],
  components: {
    DhxGrid,
    Cctr,
    Account
  },
  data() {
    return {
      id: 'RO',
      data: [],
      options: {
        'OIL_KIND_CD': []
      },
      config_def: {
        columns: [{
          id: 'itemSeq',
          align: 'center',
          value: 'No.',
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
          align: 'center',
          value: 'IO',
          width: 80
        }, {
          id: 'cctrCd',
          align: 'center',
          value: '귀속부서',
          width: 100
        }, {
          id: 'cctrNm',
          align: 'left',
          value: '귀속부서명',
          width: 120
        }, {
          id: 'acctCd',
          align: 'center',
          value: '계정코드',
          width: 80
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
                    data: this.value,
                    readonly: true
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
          id: 'acctNm',
          align: 'left',
          value: '계정명',
          width: 140
        }, {
          id: 'debitAmt',
          align: 'right',
          value: '차변금액',
          width: 90,
          type: 'ron'
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
          width: 150
        }],
        height: 220
      },
      config_E6: {
        columns: [{
          id: 'itemSeq',
          value: 'No.',
          width: 35
        }, {
          id: 'useDt',
          value: '사용일자',
          width: 40,
          component: {
            props: ['index', 'value', 'field'],
            template: `
              <span>{{ $moment(value.useDt).format('YYYY-MM-DD') }}</span>
            `
          }
        }, {
          id: 'stptPlc',
          width: 60,
          value: '출발지',
          align: 'left'
        }, {
          id: 'dstnPlc',
          width: 60,
          value: '도착지',
          align: 'left'
        }, {
          id: 'biztrpObj',
          width: 100,
          value: '출장목적',
          align: 'left'
        }, {
          id: 'tpsTypeNm',
          width: 100,
          value: '교통비유형'
        }, {
          id: 'tpsDst',
          value: '거리',
          width: 80,
          align: 'right',
          type: 'ron'
        }, {
          id: 'oilKindCd',
          value: '유종',
          width: 100,
          component: {
            template: `<span>{{ text }}</span>`,
            props: ['index', 'value', 'field'],
            data() {
              return {
                text: undefined
              }
            },
            methods: {
              setText() {
                let vm = this.$parent.$parent
                if (vm.options['OIL_KIND_CD'].length > 0) {
                  let result = vm.options['OIL_KIND_CD'].filter(x => x.detailCd === this.value[this.field])[0]
                  if (result !== undefined) {
                    this.text = result.detailNm
                  }
                }
              }
            },
            created() {
              this.setText()
              this.$parent.$parent.$on('options.OIL_KIND_CD.updated', () => {
                this.setText()
              })
            }
          }
        }, {
          id: 'oilUpc',
          value: '유류단가/연비',
          width: 80,
          component: {
            props: ['index', 'value', 'field'],
            template: `<span v-if="value.oilUpc && value.oilEff">{{ this.$numeral(value.oilUpc).format('0,0') }} / {{ this.$numeral(value.oilEff).format('0,0') }}</span>`
          }
        }, {
          id: 'acctAmt',
          value: '사용금액',
          width: 90,
          align: 'right',
          type: 'ron'
        }, {
          id: 'acctCd',
          align: 'center',
          value: '계정코드',
          width: 50
        }, {
          id: 'acctNm',
          align: 'left',
          value: '계정명',
          width: 80
        }],
        height: 220
      }
    }
  },
  computed: {
    config() {
      switch (this.value.slipTypeCd) {
        case 'E6':
          return this.config_E6
        default:
          return this.config_def
      }
    }
  },
  created() {
    this.$watch(() => this.value.slipDetails, (nValue, oValue) => {
      if (nValue === undefined) {
        this.data = []
      } else if (nValue !== undefined && Array.isArray(nValue)) {
        this.data = this.value.slipDetails
      }
    }, {
      immediate: true,
      deep: true
    })

    this.$http.get('/api/code/detail', {
      params: {
        groupCd: 'OIL_KIND_CD'
      }
    }).then(response => {
      this.options['OIL_KIND_CD'] = response.data
      this.$emit('options.OIL_KIND_CD.updated', response.data)
    })
  },
  methods: {
    constructGridSuccessful(grid) {
      var header_style = 'color:#222;text-align:center;'
      var stat_total_text = 'color:red;text-align:right;padding-right:10px !important;'
      if (this.value.slipTypeCd === 'E6') {
        grid.attachHeader(
          ['합계', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#stat_total', '', ''],
          [header_style, '', '', '', '', '', '', '', '', stat_total_text, '', '']
        )
        grid.setNumberFormat('0,000', 6, '.', ',')
        grid.setNumberFormat('0,000', 9, '.', ',')
      } else {
        grid.attachHeader(
          ['합계', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#stat_total', '#stat_total', ''],
          [header_style, '', '', '', '', '', '', '', '', stat_total_text, stat_total_text, '']
        )
        grid.setNumberFormat('0,000', 9, '.', ',')
        grid.setNumberFormat('0,000', 10, '.', ',')
      }
      grid.callEvent('ongridreconstructed', [])
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
