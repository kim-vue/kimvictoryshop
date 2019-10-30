<template>
  <div class="inner-box">
    <form @submit.prevent="query">
      <!-- Header -->
      <div class="content-name">
        <h2 class="dp-ib">부서별 예산/실적 내역</h2>
        <div class="btn-wrap btn-type1 clearfix">
          <button type="submit" class="btn-size btn-gray fl_left">
            <span class="btn-icon"><i class="fas fa-search"></i></span>
            조회
          </button>
        </div>
      </div>
      <!-- //Header -->

      <!-- 검색 Form -->
      <div class="search-form">
        <div class="form-group">
          <label class="control-label">조회연월</label>
          <div class="form-input">
            <div class="datepicker w-type-ymd02">
              <dhx-calendar class="input ddate sDate" v-model="params.budYm" :config="{ format: 'YYYY-MM', outputFormat: 'YYYYMM', dateFormat: '%Y-%m' }" />
            </div>
          </div>
        </div>
        <search-cctr title="부서" v-model="params" :options="{ type: '02', cctrCd: 'budCctrCd', cctrNm: 'budCctrNm' }" @submit="query" />
        <search-account title="계정코드" v-model="params" :options="{ type: '02', acctCd: 'budAcctCd', acctNm: 'budAcctNm' }" @submit="query" />
      </div>
      <!-- //검색 Form -->
    </form>

    <div class="table-area">
      <div class="table-b">
        <div class="table-header">
          <div class="table-name">
            <h3 class="ico_table_name">예산/실적 내역</h3>
          </div>
          <div class="btn-wrap btn-type1 clearfix" @click="toExcel()">
            <button class="btn-size btn-excel">엑셀 저장</button>
          </div>
        </div>

        <dhx-grid ref="grid" v-model="data" :config="config" @constructGridSuccessful="constructGridSuccessful" />
      </div>
    </div>
  </div>
</template>

<script>
/**
 * EA-03-05
 * 부서별 예산/실적 내역
 */

import assert from '@/libs/assert'

import DhxCalendar from '@/components/DhxCalendar.vue'
import DhxGrid from '@/components/DhxGrid.vue'

import BdgtUseLstPop from '@/components/BdgtUseLstPop.vue'
import BdgtReqLstPop from '@/components/BdgtReqLstPop.vue'

export default {
  components: {
    DhxCalendar,
    DhxGrid
  },
  data() {
    return {
      data: [],
      params: {
        budYm: this.$moment().format('YYYYMM'),
        budCctrCd: undefined,
        budCctrNm: undefined,
        budAcctCd: undefined,
        budAcctNm: undefined
      },
      config: {
        columns: [{
          value: 'No.',
          type: 'cntr',
          width: 50
        }, {
          id: 'budAcctCd',
          value: '계정코드',
          width: 120
        }, {
          id: 'budAcctNm',
          value: '계정명',
          align: 'left',
          width: 180
        }, {
          id: 'baseAmt',
          value: '기초예산',
          align: 'right',
          type: 'ron'
        }, {
          id: 'plusAmt',
          value: '증액예산',
          align: 'right',
          type: 'ron'
        }, {
          id: 'trswAmt',
          value: '전용대기',
          align: 'right',
          type: 'ron'
        }, {
          id: 'trsfAmt',
          value: '전용예산',
          align: 'right',
          type: 'ron'
        }, {
          id: 'sliwAmt',
          value: '미확정실적',
          align: 'right',
          type: 'ron'
        }, {
          id: 'slifAmt',
          value: '확정실적',
          align: 'right',
          type: 'ron'
        }, {
          id: 'rmMonthAmt',
          value: '잔여예산<br>(해당월)',
          align: 'right',
          type: 'ron'
        }, {
          id: 'rmQuaAmt',
          value: '잔여예산<br>(통제기간)',
          align: 'right',
          type: 'ron'
        }],
        events: {
          onRowDblClicked(rId, cInd, event, row) {
            let component = undefined
            let cellFgCd = undefined

            switch (cInd) {
              case 4: // 증액예산
                component = BdgtReqLstPop
                cellFgCd = 'BP'
                break
              case 5: // 전용대기
                component = BdgtReqLstPop
                cellFgCd = 'BW'
                break
              case 6: // 전용예산
                component = BdgtReqLstPop
                cellFgCd = 'BF'
                break
              case 7: // 미확정실적
                component = BdgtUseLstPop
                cellFgCd = 'SU'
                break
              case 8: // 확정실적
                component = BdgtUseLstPop
                cellFgCd = 'SF'
                break
            }

            if (component !== undefined && cellFgCd !== undefined) {
              this.$modal.open({
                component,
                props: {
                  budYm: row.budYm,
                  budCctrCd: row.budCctrCd,
                  budAcctCd: row.budAcctCd,
                  cellFgCd
                },
                parent: this
              })
            }
          }
        },
        autoWidth: false,
        height: '50vh'
      }
    }
  },
  methods: {
    constructGridSuccessful(grid) {
      grid.setNumberFormat('0,000', 3, '.', ',')
      grid.setNumberFormat('0,000', 4, '.', ',')
      grid.setNumberFormat('0,000', 5, '.', ',')
      grid.setNumberFormat('0,000', 6, '.', ',')
      grid.setNumberFormat('0,000', 7, '.', ',')
      grid.setNumberFormat('0,000', 8, '.', ',')
      grid.setNumberFormat('0,000', 9, '.', ',')
      grid.setNumberFormat('0,000', 10, '.', ',')
    },
    query() {
      try {
        assert.apply(this, [this.params.budYm, '조회연월을 입력해주세요.'])
        assert.apply(this, [this.params.budCctrCd, '부서를 입력해주세요.'])

        this.$store.commit('loading')
        return this.$http.post('/api/budget/manage/list', this.params)
          .then(response => {
            this.data = response.data
            return response
          })
          .finally(() => {
            this.$store.commit('finish')
          })
      } catch (e) {
        this.$swal({
          type: 'error',
          text: e
        })
      }
    },
    /**
     * Event handlers
     */
    buttonClickEvent_Search() {
      this.query()
    },
    toExcel() {
      this.$refs.grid.toExcel()
    }
  },
  created() {
    let login = undefined
    try {
      login = this.$store.state.loginInfo

      this.params.budCctrCd = login.loginDeptCd
      this.params.budCctrNm = login.loginDeptNm
    } catch (e) {
      login = undefined
    } finally {
      this.query()
    }
  }
}
</script>

<style lang="scss" scoped>
.table-b {
  :global(table) {
    :global(td) {
      vertical-align: middle !important;
    }
  }
}
</style>
