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
    </tr>

    <tr v-if="!isNew">
      <th>작성부서</th>
      <td>{{ value.wrtDeptCd }} / {{ value.wrtDeptNm }}</td>
      <td>{{ value.bpNm }}</td>

      <th>작성자</th>
      <td>{{ value.wrtNm }}</td>

      <th>작성일자</th>
      <td class="Rt-M">{{ this.$moment(value.wrtDtm).format('YYYY-MM-DD') }}</td>
    </tr>
    <!-- //기준정보  -->

    <tr>
      <th>증빙유형</th>
      <td colspan="2">
        <b-select class="select is-fullwidth" v-model="value.evdTypeCd" v-if="options['evdTypeCd'] && value.evdTypeCd" @input="evdTypeCdHandler()">
          <option v-for="{ key, value } in options['evdTypeCd']" :key="key" :value="key">{{ value }}</option>
        </b-select>
      </td>

      <th>정산구분</th>
      <td>
        <div class="control">
          <div class="dp-ib fl_left">
            <input type="radio" id="radio01" v-model="value.stlFgCd" value="N" />
            <label for="radio01" class="NotoM">미정산</label>
          </div>
          <div class="dp-ib fl_left">
            <input type="radio" id="radio02" v-model="value.stlFgCd" value="Y" disabled="disabled" />
            <label for="radio02" class="NotoM">선급금정산</label>
          </div>
        </div>
      </td>

      <th class="tp-a">증빙일자</th>
      <td>
        <div class="datepicker w-type-ymd">
          <dhx-calendar class="input" v-model="value.evdDt" />
        </div>
      </td>
    </tr>

    <tr>
      <th class="tp-a">지급처</th>
      <td colspan="2">
        <div class="td-s-thumb search-area">
          <input class="input input-bg mr5 Rt-M rs-mt2" type="text" v-model="value.evdCustCd" style="width:66px;" disabled="disabled" />
          <div class="ip-box ip-box-w02 rs-mt2">
            <input type="text" class="input" v-model="value.evdCustNm" @focus="openVendor()" />
            <button class="icon is-right" @click="openVendor()">
              <i class="fas fa-search"></i>
            </button>
          </div>
          <button class="remove_text trash-input rs-mb2" @click="value.evdCustCd = value.evdCustNm = undefined">
            <i class="far fa-trash-alt"></i>
          </button>
        </div>
      </td>

      <!--
        TODO::선급금정산
        사용 시, 개발이 필요함
      -->
      <th>선급금정산</th>
      <td class="clearfix">
        <div class="control is-expanded search-area">
          <div class="ip-box rs-mt2" style="width:80%;">
            <input class="input input-bg" type="text" value="" disabled="disabled" />
            <button class="icon is-right" disabled="disabled">
              <i class="fas fa-search"></i>
            </button>
          </div>
          <button class="remove_text rs-mt2 rs-mb2" disabled="disabled">
            <i class="far fa-trash-alt"></i>
          </button>
        </div>
      </td>

      <th class="tp-a">회계일자</th>
      <td>
        <div class="datepicker w-type-ymd">
          <dhx-calendar class="input" v-model="value.postDt" />
        </div>
      </td>
    </tr>

    <!-- 현금영수증인 경우 사용 -->
    <tr v-if="value.evdTypeCd === '40'">
      <th class="tp-a">상호명</th>
      <td colspan="2">
        <input type="text" class="input" v-model="value.crcptMerchNm" />
      </td>

      <th class="tp-a">사업자번호</th>
      <td>
        <input type="text" class="input" v-model="value.crcptBizNo" />
      </td>

      <th class="tp-a">승인번호</th>
      <td>
        <input type="text" class="input" v-model="value.crcptNo" />
      </td>
    </tr>
    <!-- //현금영수증인 경우 사용 -->

    <!-- 사내증빙인 경우 사용 -->
    <tr v-if="value.evdTypeCd === '42'">
      <th class="tp-a">사용유형</th>
      <td colspan="6">
        <div class="dp-ib fl_left" v-for="(option, index) in options['useTypeCd']" :key="option.key">
          <input type="radio" :id="getRadioId('useTypeCd', index)" v-model="value.useTypeCd" :value="option.key" />
          <label :for="getRadioId('useTypeCd', index)" class="NotoM">{{ option.value }}</label>
        </div>
      </td>
    </tr>
    <!-- //사내증빙인 경우 사용 -->

    <!-- 해외 사용인 경우 사용 -->
    <tr v-if="value.evdTypeCd === '43'">
      <th>사용국가</th>
      <td colspan="2">
        <b-select class="select is-fullwidth" v-model="value.frgnNatCd">
          <option v-for="{ key, value } in options['frgnNatCd']" :key="key" :value="key" v-text="value" />
        </b-select>
      </td>

      <th>거래통화</th>
      <td>
        <b-select class="select is-fullwidth" v-model="value.frgnCurCd">
          <option v-for="{ key, value } in options['frgnCurCd']" :key="key" :value="key" v-text="value" />
        </b-select>
      </td>

      <th>외화금액</th>
      <td>
        <number-input class="input" v-model="value.frgnAmt" />
      </td>
    </tr>
    <!-- //해외 사용인 경우 사용 -->

    <tr>
      <th class="tp-a">공급가액</th>
      <td colspan="2">
        <number-input class="input" v-model="value.supAmt" @input="totalAmountCalculator('supAmt')" />
      </td>

      <th>기타금액</th>
      <td>
        <number-input class="input" v-model="value.etcAmt" :disabled="['40'].indexOf(value.evdTypeCd) < 0" @input="totalAmountCalculator('etcAmt')" />
      </td>

      <th>지급조건</th>
      <td>
        <b-select class="select is-fullwidth" v-model="value.payTermCd" v-if="options['payTermCd'].length" @input="resetPayDueDt(value.payTermCd)">
          <option v-for="{ detailCd, detailNm } in options['payTermCd']" :key="detailCd" :value="detailCd">{{ detailNm }}</option>
        </b-select>
      </td>
    </tr>

    <tr>
      <th>부가세액</th>
      <td colspan="2">
        <number-input class="input" v-model="value.vatAmt" :disabled="['40'].indexOf(value.evdTypeCd) < 0" @input="totalAmountCalculator('vatAmt')" />
      </td>

      <th>총 금액</th>
      <td>
        <number-input class="input" v-model="value.totAmt" disabled="disabled" />
      </td>

      <th class="tp-a">지급예정일</th>
      <td>
        <div class="datepicker w-type-ymd">
          <dhx-calendar class="input" v-model="value.payDueDt" />
        </div>
      </td>
    </tr>

    <tr>
      <th class="tp-a">기준부서</th>
      <td colspan="2">
        <div class="td-s-thumb search-area">
          <input class="input input-bg mr5 Rt-M rs-mt2" type="text" v-model="value.baseDeptCd" style="width:105px;" disabled="disabled" />
          <div class="ip-box rs-mt2">
            <input class="input" type="text" v-model="value.baseDeptNm" @focus="openCctr({ 'cctrCd': 'baseDeptCd', 'cctrNm': 'baseDeptNm' }, updateSubDepartment)" />
            <button class="icon is-right" @click="openCctr({ cctrCd: 'baseDeptCd', cctrNm: 'baseDeptNm' }, updateSubDepartment)">
              <i class="fas fa-search"></i>
            </button>
          </div>
          <button class="remove_text trash-input rs-mb2" @click="() => {value.baseDeptCd = value.baseDeptNm = undefined; updateSubDepartment()}">
            <i class="far fa-trash-alt"></i>
          </button>
        </div>
      </td>

      <th>대변계정</th>
      <td>
        <b-select class="select is-fullwidth" v-model="value.apAcctCd" @input="changeApAcctCd()">
          <option v-for="item in this.options['accounts']" :key="item.key" :value="item.key" :name="item.value" v-text="`[${item.key}] ${item.value}`" />
        </b-select>
      </td>

      <th class="tp-a">지급계좌</th>
      <td>
        <b-select class="select is-fullwidth" v-model="value.custAccount" v-if="options['ventAccts'].length > 0">
          <option v-for="item in options['ventAccts']" :key="item.bnkCd + '|' + item.acctNo" :value="item.bnkCd + '|' + item.acctNo" v-text="item.acctNo" />
        </b-select>
        <div class="select is-fullwidth" v-else>
          <select>
            <option value="" selected>== 지급계좌 없음==</option>
          </select>
        </div>
      </td>
    </tr>

    <tr>
      <th class="tp-a">적요</th>
      <td colspan="6">
        <input type="text" class="input" v-model="value.hdSgtxt" @input="changeHdSgtxt()" />
      </td>
    </tr>
  </tbody>
</table>
</template>

<script>
import mixin from '@/mixin/slip-table'
import mixin_common from '@/mixin/slip-common'
import DhxCalendar from '@/components/DhxCalendar.vue'
import NumberInput from '@/components/NumberInput.vue'

export default {
  props: ['value', 'isNew'],
  mixins: [mixin_common, mixin],
  components: {
    DhxCalendar,
    NumberInput
  },
  data() {
    return {
      id: 'ED'
    }
  }
}
</script>

<style scoped>
.modal-content {
  width: 700px;
}
</style>
