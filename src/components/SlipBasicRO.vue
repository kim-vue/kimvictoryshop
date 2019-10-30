<template>
    <div>
        <div class="table-a fixed-th">
            <div class="table-name">
                <h3 class="ico_table_name">{{title}}</h3>
            </div>
            <table class="table">
                <tbody>
                    <tr>
                        <th>전표번호</th>
                        <td width="12%">{{form.eaSlipNo}}</td>
                        <td width="8%"></td>

                        <th>전표유형</th>
                        <td>{{form.slipTypeNm}}</td>

                        <th>전표상태</th>
                        <td><span class="color_table_org">{{form.slipStatNm}}</span></td>
                        <td></td>
                    </tr>
                    <tr>
                        <th>작성부서</th>
                        <td>{{form.wrtDeptCd}} / {{form.wrtDeptNm}}</td>
                        <td >{{form.bpNm}}</td>

                        <th>작성자</th>
                        <td>{{form.wrtNm}}</td>

                        <th>작성일자</th>
                        <td class="Rt-M" colspan="2">{{this.$moment(form.wrtDtm).format('YYYY-MM-DD')}}</td>
                    </tr>
                    <tr>
                        <th>증빙유형</th>
                        <td  colspan="2">
                            {{form.evdTypeNm}}
                        </td>

                        <th>정산구분</th>
                        <td>
                            <div v-if="form.stlFgCd === 'Y'">선급금정산</div>
                            <div v-else>미정산</div>
                        </td>

                        <th>증빙일자</th>
                        <td colspan="2">{{this.$moment(form.evdDt).format('YYYY-MM-DD')}}</td>
                    </tr>
                    <tr>
                        <th>세금코드</th>
                        <td  colspan="2">
                            [{{form.taxCd}}] {{form.taxNm}}
                        </td>

                        <th>선급금정산</th>
                        <td class="clearfix">&nbsp;</td>

                        <th>회계일자</th>
                        <td colspan="2">{{this.$moment(form.postDt).format('YYYY-MM-DD')}}</td>
                    </tr>
                    <tr>
                        <th>거래처</th>
                        <td colspan="2">
                            {{form.evdCustCd}} / {{form.evdCustNm}}
                        </td>
                        <td class="bd-l-none" colspan="2" v-if="form.payCustCd">
                            <input type="checkbox" id="check02" checked disabled/><label for="check02">실지급처</label>
                            &nbsp;&nbsp;{{form.payCustCd}} / {{form.payCustNm}}
                        </td>
                        <td class="bd-l-none" colspan="2" v-else>&nbsp;</td>
                        <th>지급조건</th>
                        <td colspan="2">
                            {{form.payTermNm}}
                        </td>
                    </tr>
                    <tr>
                        <th>공급가액</th>
                        <td class="Rt-M tar" colspan="2">
                            {{form.supAmt | number}}
                        </td>

                        <th>기준부서</th>
                        <td>
                            {{form.baseDeptCd}} / {{form.baseDeptNm}}
                        </td>

                        <th>지급예정일</th>
                        <td colspan="2">
                            {{this.$moment(form.payDueDt).format('YYYY-MM-DD')}}
                        </td>
                    </tr>
                    <tr>
                        <th>부가세액</th>
                        <td  class="Rt-M tar" colspan="2">
                            {{form.vatAmt | number}}
                        </td>

                        <th>대변계정</th>
                        <td>
                            {{form.apAcctCd}} / {{form.apAcctNm}}
                        </td>

                        <th>지급계좌</th>
                        <td colspan="2">
                            {{form.custAcctNo}}
                        </td>
                    </tr>
                    <tr>
                        <th>기타금액</th>
                        <td  class="Rt-M tar" colspan="2"> {{form.etcAmt | number}} </td>

                        <th>{{columnTitle}}</th>
                        <td v-if="form.slipTypeCd === 'E2'"> <span class="NotoM">{{form.etaxNo}}</span></td>
                        <td v-else> <span class="NotoM">{{form.curCd}}</span></td>

                        <th>사업장</th>
                        <td colspan="2">
                            {{form.bpCd}} / {{form.bpNm}}
                        </td>
                    </tr>
                    <tr>
                        <th>총금액</th>
                        <td  class="Rt-M tar" colspan="2" > {{form.totAmt | number}} </td>

                        <th> 적요</th>
                        <td  colspan="4"> {{form.hdSgtxt}}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <slip-grid ref="detail" :slipDetails="slipDetails" />

    </div>

</template>

<script>
/* eslint-disable */
import moment from 'moment'
import mixin from '@/mixin';
import _ from 'lodash'

import SlipGrid from '@/components/SlipGridRO.vue';

export default {
  name: 'SlipBasicRO',
  props: ['slipHeader','slipDetails'],
  mixins: [ mixin ],
  components: { SlipGrid },
  data() {
    return {
      title: '기본정보',
      form: {},
    };
  },
  methods: {
  },
  computed: {
      columnTitle() {
          return this.form.slipTypeCd === 'E2' ? '전자승인번호' : '통화';
      }
  },
  mounted() {
  },
  watch: {
    slipHeader() {
        this.form = this.slipHeader;
    },
  }
};
</script>

<style>
</style>

