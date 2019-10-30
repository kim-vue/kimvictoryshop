<template>
<div class="inner-box">
  <form @submit.prevent="query">
    <!-- 헤더 -->
    <div class="content-name">
      <h2 class="dp-ib">예산 신청 내역</h2>
      <div class="btn-wrap btn-type1 clearfix">
        <button type="submit" class="btn-size btn-gray fl_left">
          <span class="btn-icon"><i class="fas fa-search"></i></span>
          조회
        </button>
      </div>
    </div>
    <!-- //헤더 -->

    <!-- 검색폼 -->
    <div class="search-form">
      <div class="form-group">
        <label class="control-label">신청일자</label>
        <div class="form-input">
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input ddate sDate" v-model="params.searchDtmFr" />
          </div>
          <span class="wave"> ~ </span>
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input ddate sDate" v-model="params.searchDtmTo" />
          </div>
        </div>
      </div>
      <div class="form-group">
        <label class="control-label">신청서상태</label>
        <div class="form-input">
          <select class="input" v-model="params.budStatCd">
            <option v-for="{ key, value } in options['BUD_STAT_CD']" :key="key" :value="key" v-text="value" />
          </select>
        </div>
      </div>
    </div>
    <!-- //검색폼 -->
  </form>

  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">신청항목</h3>
        </div>
      </div>
      <dhx-grid ref="grid" v-model="data" :config="config" @constructGridSuccessful="constructGridSuccessful" />
    </div>
  </div>
</div>
</template>

<script>
/**
 * EA-03-03
 * 예산 신청 내역 - 개인
 */

import assert from '@/libs/assert'

import DhxCalendar from '@/components/DhxCalendar.vue'
import DhxGrid from '@/components/DhxGrid.vue'

export default {
  components: {
    DhxCalendar,
    DhxGrid
  },
  data() {
    return {
      params: {
        searchDtmFr: this.$moment().subtract(1, 'months').startOf('month').format('YYYYMMDD'),
        searchDtmTo: this.$moment().format('YYYYMMDD'),
        budStatCd: undefined
      },
      data: [],
      options: {
        'BUD_STAT_CD': []
      },
      config: {
        columns: [{
          value: 'No.',
          type: 'cntr',
          width: 50
        }, {
          id: 'budReqNo',
          value: '신청서번호'
        }, {
          id: 'budFgNm',
          value: '예산구분'
        }, {
          id: 'brwTypeNm',
          value: '신청유형'
        }, {
          id: 'budStatNm',
          value: '신청서상태',
          width: 80
        }, {
          id: 'wrtDt',
          value: '신청일자'
        }, {
          id: 'reqTotAmt',
          value: '총 금액',
          width: 120,
          align: 'right',
          type: 'ron'
        }, {
          id: 'wrtNm',
          value: '신청자'
        }, {
          id: 'deptCd',
          value: '소속부서코드'
        }, {
          id: 'deptNm',
          value: '소속부서명',
          align: 'left'
        }],
        events: {
          onRowDblClicked(rId, cInd, event, row) {
            this.$router.push({
              name: 'bdgtReqEdit',
              params: {
                budReqNo: row.budReqNo
              }
            })
          }
        },
        height: '50vh'
      }
    }
  },
  methods: {
    constructGridSuccessful(grid) {
      grid.setNumberFormat('0,000', 6, '.', ',')
    },
    queryBudStatCd() {
      this.$http.get('/api/code/combo', {
        params: {
          groupCd: 'BUD_STAT_CD'
        }
      }).then(response => {
        this.options['BUD_STAT_CD'] = response.data
        this.options['BUD_STAT_CD'].unshift({
          key: undefined,
          value: '== 전체 =='
        })
      })
    },
    query() {
      try {
        assert.apply(this, [this.params.searchDtmFr, '신청일자를 입력해주세요.'])
        assert.apply(this, [this.params.searchDtmTo, '신청일자를 입력해주세요.'])

        this.$http.post('/api/budget/psnReqList', this.params)
          .then(response => {
            this.data = response.data.map(x => {
              x.wrtDt = this.$moment(x.wrtDt).format('YYYY-MM-DD')
              return x
            })
          })
      } catch (e) {
        this.$swal({
          type: 'error',
          text: e
        })
      }
    },
    setCallPageByParam(){
      if (this.$route.query) {
        for (let member in this.params) {
          if (this.$route.query[member] !== undefined) {
            this.params[member] = this.$route.query[member]
          }
        }
      }
    }
  },
  created() {
    // Query BUD_STAT_CD
    this.queryBudStatCd()

    // Query data
    this.query()
  },
  mounted() {
    this.setCallPageByParam()
  }
}
</script>
