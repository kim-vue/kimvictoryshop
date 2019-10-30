<template>
<table class="table">
  <tbody>
    <!-- 기준정보  -->
    <tr v-if="!isNew">
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

    <tr v-if="!isNew">
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
      <th>증빙유형</th>
      <td colspan="2">{{ value.evdTypeNm }}</td>

      <th>정산구분</th>
      <td>
        <div v-if="value.stlFgCd === 'Y'">선급금정산</div>
        <div v-else>미정산</div>
      </td>

      <th>증빙일자</th>
      <td colspan="2">{{ this.$moment(value.evdDt).format('YYYY-MM-DD') }}</td>
    </tr>

    <tr>
      <th>세금코드</th>
      <td colspan="2">[{{ value.taxCd }}] {{ value.taxNm }}</td>

      <!-- TODO::선급금정산, 사용안함 -->
      <th>선급금정산</th>
      <td class="clearfix">&nbsp;</td>

      <th>전기일자</th>
      <td colspan="2">{{ this.$moment(value.postDt).format('YYYY-MM-DD') }}</td>
    </tr>

    <tr>
      <th>거래처</th>
      <td colspan="2">{{ value.evdCustCd }} / {{ value.evdCustNm }}</td>

      <td class="bd-l-none">
        <input type="checkbox" id="check02" v-model="actualEvdPay" disabled="disabled" />
        <label for="check02">실지급처</label>
      </td>
      <td class="bd-l-none" v-if="actualEvdPay">{{ value.payCustCd }} / {{ value.payCustNm }}</td>
      <td class="bd-l-none" v-else></td>

      <th>지급조건</th>
      <td colspan="2">{{ value.payTermNm }}</td>
    </tr>

    <tr>
      <th>공급가액</th>
      <td class="Rt-M tar" colspan="2">{{ this.$numeral(value.supAmt).format('0,0') }}</td>

      <th>기준부서</th>
      <td>{{ value.baseDeptCd }} / {{ value.baseDeptNm }}</td>

      <th>지급예정일</th>
      <td colspan="2">{{ this.$moment(value.payDueDt, 'YYYYMMDD').format('YYYY-MM-DD') }}</td>
    </tr>

    <tr>
      <th>부가세액</th>
      <td class="Rt-M tar" colspan="2">{{ this.$numeral(value.vatAmt).format('0,0') }}</td>

      <th>대변계정</th>
      <td>{{ value.apAcctCd }} / {{ value.apAcctNm }}</td>

      <th>지급계좌</th>
      <td colspan="2">{{ value.custAcctNo }}</td>
    </tr>

    <tr>
      <th>총 금액</th>
      <td class="Rt-M tar" colspan="2">{{ this.$numeral(value.totAmt).format('0,0') }}</td>

      <th>적요</th>
      <td colspan="4">{{ value.hdSgtxt }}</td>
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
      id: 'RO'
    }
  },
  computed: {
    actualEvdPay(value) {
      return !!value.payCustCd
    }
  }
}
</script>
