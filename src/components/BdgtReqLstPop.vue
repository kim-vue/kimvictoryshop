<template>
  <div class="modal-card">
    <header class="modal-card-head pop-header">
      <p class="modal-card-title tit">
        예산 전용 내역
        <button class="btn-pop-close delete" aria-label="close" @click="$parent.close()"></button>
      </p>
    </header>
    <section class="modal-card-body pop-content">
      <div class="inner-box">
        <div class="table-area">
          <div class="table-b">
            <dhx-grid ref="grid" v-model="data" :config="config" @constructGridSuccessful="constructGridSuccessful" />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
/**
 * EA-03-07
 * 예산 전용 내역
 */
import DhxGrid from '@/components/DhxGrid.vue'

const DateFormatter = {
  props: ['index', 'value', 'field'],
  template: `
    <span v-if="value[field]">{{ this.$moment(value[field], 'YYYYMM').format('YYYY-MM') }}</span>
    <span v-else></span>
  `
}

export default {
  props: {
    budYm: {
      type: String,
      required: true
    },
    budCctrCd: {
      type: String,
      required: true
    },
    budAcctCd: {
      type: String,
      required: true
    },
    cellFgCd: {
      type: String,
      required: true
    }
  },
  components: {
    DhxGrid
  },
  data() {
    return {
      data: [],
      config: {
        columns: [{
          value: 'No.',
          type: 'cntr',
          width: 50
        }, {
          id: 'budTypeNm',
          value: '신청유형',
          width: 150
        }, {
          id: 'srFgNm',
          value: '구분'
        }, {
          id: 'budYm',
          value: '연월',
          component: DateFormatter
        }, {
          id: 'budCctrCd',
          value: '비용부서',
          width: 120
        }, {
          id: 'budCctrNm',
          value: '비용부서명',
          align: 'left',
          width: 160
        }, {
          id: 'budAcctCd',
          value: '계정코드',
          width: 120
        }, {
          id: 'budAcctNm',
          value: '계정명',
          align: 'left',
          width: 160
        }, {
          id: 'docNo',
          value: '신청서번호',
          width: 150
        }, {
          id: 'reqAmt',
          value: '금액',
          align: 'right',
          type: 'ron'
        }],
        autoWidth: false,
        height: 300
      }
    }
  },
  methods: {
    constructGridSuccessful(grid) {
      grid.setNumberFormat('0,000', 9, '.', ',')
    },
    query() {
      this.$http.post('/api/budget/manage/list/bdgtPop', {
        budYm: this.budYm,
        budCctrCd: this.budCctrCd,
        budAcctCd: this.budAcctCd,
        cellFgCd: this.cellFgCd
      }).then(response => {
        this.data = response.data
      })
    }
  },
  created() {
    this.query()
  }
}
</script>
