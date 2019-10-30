<template>
<table class="table">
  <tbody>
    <!-- 기준정보  -->
    <tr>
      <th>전표번호</th>
      <td width="12%">{{ value.eaSlipNo }}</td>
      <td width="8%"></td>

      <th>전표유형</th>
      <td>{{ value.slipTypeNm }}</td>

      <th>전표상태</th>
      <td>
        <span class="color_table_org">{{ value.slipStatNm }}</span>
      </td>
      <td></td>
    </tr>

    <tr>
      <th>작성부서</th>
      <td>{{ value.wrtDeptCd }} / {{ value.wrtDeptNm }}</td>
      <td>{{ value.bpNm }}</td>

      <th>작성자</th>
      <td>{{ value.wrtNm }}</td>

      <th>작성일자</th>
      <td class="Rt-M" colspan="2">{{ this.$moment(value.wrtDtm).format('YYYY-MM-DD') }}</td>
    </tr>
    <!-- //기준정보  -->

    <tr>
      <th>카드번호</th>
      <td colspan="2">{{ value.crdNo }}</td>

      <th>승인번호</th>
      <td>{{ value.crdApprNo }}</td>

      <th>증빙일자</th>
      <td class="Rt-M" colspan="2">{{ this.$moment(value.evdDt).format('YYYY-MM-DD') }}</td>
    </tr>

    <tr>
      <th>카드소유자</th>
      <td colspan="2">{{ value.crdPssrNm}} {{ value.crdPssrTitle }}</td>

      <th>카드구분</th>
      <td>{{ value.crdFgNm }}</td>

      <th>회계일자</th>
      <td colspan="2">{{ this.$moment(value.postDt).format('YYYY-MM-DD') }}</td>
    </tr>

    <tr>
      <th>승인금액</th>
      <td class="Rt-M tar" colspan="2">{{ this.$numeral(value.totAmt).format('0,0') }}</td>

      <th>가맹점명</th>
      <td>{{ value.crdMerchNm }}</td>

      <th>승인시간</th>
      <td colspan="2">{{ apprDatetime }}</td>
    </tr>

    <tr>
      <th>공급가액</th>
      <td class="Rt-M tar" colspan="2">{{ this.$numeral(value.supAmt).format('0,0') }}</td>

      <th>가맹점주소</th>
      <td colspan="4">{{ value.merchAddr }}</td>
    </tr>

    <tr>
      <th>부가세액</th>
      <td class="Rt-M tar" colspan="2">{{ this.$numeral(value.vatAmt).format('0,0') }}</td>

      <th>과세유형/업종</th>
      <td>{{ value.taxTypeNm }}/{{ value.mccName }}</td>

      <th>경비처리기한</th>
      <td colspan="2">{{ this.$moment(value.payDueDt).format('YYYY-MM-DD') }}</td>
    </tr>

    <tr>
      <th>봉사료</th>
      <td class="Rt-M tar" colspan="2">{{ this.$numeral(value.tips).format('0,0') }}</td>

      <th>공제구분</th>
      <td>{{ getCrdDdctNm(value.crdDdctCd) }}</td>

      <th>기준부서</th>
      <td colspan="2">{{ value.baseDeptCd }} / {{ value.baseDeptNm }}</td>
    </tr>

    <tr>
      <th>적요</th>
      <td colspan="7">{{ value.hdSgtxt }}</td>
    </tr>
  </tbody>
</table>
</template>

<script>
import mixin from '@/mixin/slip-table'
import DhxCalendar from '@/components/DhxCalendar.vue'
import NumberInput from '@/components/NumberInput.vue'

export default {
  props: ['value', 'eventBus', 'isNew', 'readonly'],
  mixins: [mixin],
  components: {
    DhxCalendar,
    NumberInput
  },
  data() {
    return {
      id: 'RO',
      options: {
        'CRD_DDCT_CD': []
      }
    }
  },
  created() {
    this.$http.get('/api/code/detail', {
      params: {
        groupCd: 'CRD_DDCT_CD'
      }
    }).then(response => {
      this.options['CRD_DDCT_CD'] = response.data
    })
  },
  methods: {
    getCrdDdctNm(value) {
      let result = this.options['CRD_DDCT_CD'].filter(x => x.detailCd === value)
      if (result && result.length === 1) {
        return result[0].detailNm
      } else {
        return ''
      }
    }
  },
  computed: {
    apprDatetime() {
      let dt = [String(this.value.apprDate || '').trim(), String(this.value.apprTime || '').trim()].join('')
      return dt.replace(/(\d{4})(\d{2})(\d{2})((\d{2})(\d{2})(\d{2}))?/g, '$1-$2-$3 $5:$6:$7').replace(/( ::)|(-- )|(-- ::)/g, '')
    }
  }
}
</script>
