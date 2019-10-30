<template>
<table class="table">
  <tbody>
    <table-header v-model="value" :readonly="readonly" v-if="showHeader" />

    <tr>
      <table-select title="증빙유형" v-model="value" field="evdTypeCd" code="key" text="value" :options="options['EVD_TYPE_CD']" :readonly="readonly" @input="evdTypeChangeEvent" :colspan="2" />

      <table-radio title="정산구분" v-model="value" field="stlFgCd" :options="options['STL_FG']" :disabled="true" :readonly="readonly" />

      <table-calendar title="증빙일자" v-model="value" field="evdDt" :required="true" :readonly="readonly" :colspan="2" @input="evdDtChangeEvent" />
    </tr>

    <tr>
      <evd-cust title="지급처" v-model="value" :readonly="readonly" :colspan="2" :required="true" @input="evdCustCdChangeEvent" />

      <adv-req title="선급금정산" v-model="value" :readonly="readonly" />

      <table-calendar title="회계일자" v-model="value" field="postDt" :required="true" :readonly="readonly" :colspan="2" />
    </tr>

    <tr>
      <table-number-input title="총 금액" v-model="value" field="totAmt" :disabled="true" :readonly="readonly" :colspan="2" />

      <table-select title="대변계정" v-model="value" field="apAcctCd" code="key" text="value" :options="options['ACCOUNT']" :readonly="readonly" @input="apAcctCdChangeEvent" />

      <table-select title="지급조건" v-model="value" field="payTermCd" :options="options['PAY_TERM_CD']" :readonly="readonly" :colspan="2" @input="payTermCdChangeEvent" />
    </tr>

    <tr>
      <base-dept title="기준부서" v-model="value" :required="true" :readonly="readonly" :colspan="2" @input="baseDeptCdChangeEvent" />

      <th>통화</th>
      <td>{{ value.curCd }}</td>

      <table-calendar title="지급예정일" v-model="value" field="payDueDt" :required="true" :readonly="readonly" :colspan="2" />
    </tr>

    <tr>
      <table-input title="적요" v-model="value" field="hdSgtxt" :required="true" :readonly="readonly" :colspan="4" @input="hdSgtxtChangeEvent" />

      <table-select title="지급계좌" v-model="value" field="custAccount" code="key" text="value" :options="options['VENT_ACCTS']" :required="true" :readonly="readonly" :colspan="2" />
    </tr>

  </tbody>
</table>
</template>

<script>
import slip_table from '@/mixin/slip-table-new'

export default {
  mixins: [slip_table]
}
</script>

<style lang="scss" scoped>
table {
  table-layout: fixed;

  :global(th) {
    width: 88px;
  }

  :global(td) {
    width: 180px;
  }
}
</style>
