<template>
<div class="inner-box">
  <div class="table-area">
    <div class="table-a">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">전표정보</h3>
        </div>
      </div>
      <table class="table">
        <tbody>
          <tr>
            <th>그룹전표번호</th>
            <td>{{ data.grSlipNo }}</td>
            <th>전표유형</th>
            <td>{{ data.slipTypeNm }}</td>
            <th>통화</th>
            <td>{{ data.currCode }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">전표내역</h3>
        </div>
      </div>
      <dhx-grid ref="grid" v-model="data.slipGroupDetails" :config="config" @constructGridSuccessful="constructGridSuccessful" />
    </div>
  </div>
</div>
</template>

<script>
import DhxGrid from '@/components/DhxGrid.vue'

export default {
  props: {
    value: {
      type: Object,
      required: false
    }
  },
  components: {
    DhxGrid
  },
  data() {
    return {
      data: {
        slipGroupDetails: []
      },
      // DhxGrid config
      config: {
        columns: [{
          value: 'No.',
          type: 'cntr',
          width: 50
        }, {
          id: 'totAmt',
          value: '전표금액',
          type: 'ron',
          align: 'right',
          width: 150
        }, {
          id: 'stnAcctNm',
          value: '계정명',
          align: 'left',
          width: 180
        }, {
          id: 'wrtDeptNm',
          value: '부서',
          align: 'left',
          width: 180
        }, {
          id: 'payCustNm',
          value: '지급처',
          width: 180
        }, {
          id: 'hdSgtxt',
          value: '전표내용',
          align: 'left',
          width: 250
        }, {
          id: 'merchNm',
          value: '가맹점명',
          align: 'left',
          width: 180
        }, {
          id: 'mccName',
          value: '업종명',
          align: 'left'
        }, {
          id: 'apprDate',
          value: '승인일자',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span>{{ format(value[field]) }}</span>`,
            methods: {
              format(value) {
                if (value !== undefined && value.match(/^\d{8}/g)) {
                  return value.replace(/(\d{4})(\d{2})(\d{2})/g, '$1-$2-$3')
                } else {
                  return ''
                }
              }
            }
          }
        }, {
          id: 'apprTime',
          value: '승인시각',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span>{{ format(value[field]) }}</span>`,
            methods: {
              format(value) {
                if (value !== undefined && value.match(/^\d{6}/g)) {
                  return value.replace(/(\d{2})(\d{2})(\d{2})/g, '$1:$2:$3')
                } else {
                  return ''
                }
              }
            }
          }
        }],
        height: 200,
        autoWidth: false
      }
    }
  },
  methods: {
    constructGridSuccessful(grid) {
      grid.setNumberFormat('0,000', 1, '.', ',')
    }
  },
  watch: {
    'value': {
      immediate: false,
      deep: true,
      handler(value) {
        this.data = value
      }
    }
  }
}
</script>

<style lang="scss" scoped>
table tbody tr th {
    width: 100px;
}

table tbody tr td {
    width: 180px;
}
</style>
