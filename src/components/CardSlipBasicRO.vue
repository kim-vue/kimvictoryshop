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
                        <th>카드번호</th>
                        <td colspan="2">{{form.crdNo}}</td>

                        <th>승인번호</th>
                        <td>{{form.crdApprNo}}</td>

                        <th>증빙일자</th>
                        <td colspan="2">{{this.$moment(form.evdDt).format('YYYY-MM-DD')}}</td>
                    </tr>
                    <tr>
                        <th>카드소유자</th>
                        <td colspan="2">{{form.crdPssrNm}} {{form.crdPssrTitle}}</td>

                        <th>카드구분</th>
                        <td>{{form.crdFgNm}}</td>

                        <th>회계일자</th>
                        <td colspan="2">{{this.$moment(form.postDt).format('YYYY-MM-DD')}}</td>
                    </tr>
                    <tr>
                        <th>승인금액</th>
                        <td  class="Rt-M tar" colspan="2"> {{form.totAmt | number}}</td>

                        <th>가맹점명</th>
                        <td>{{form.crdMerchNm}}</td>

                        <th>승인시간</th>
                        <td colspan="2" v-if="form.apprDate">{{apprDateTime}}</td>
                        <td colspan="2" v-else>&nbsp;</td>
                    </tr>
                    <tr>
                        <th>공급가액</th>
                        <td  class="Rt-M tar" colspan="2"> {{form.supAmt | number}}</td>

                        <th>가맹점주소</th>
                        <td colspan="4">{{form.merchAddr}}</td>
                    </tr>
                    <tr>
                        <th>부가세액</th>
                        <td  class="Rt-M tar" colspan="2">{{form.vatAmt | number}}</td>

                        <th>과세유형/업종</th>
                        <td>{{form.etc3}}/{{form.mccName}}</td>

                        <th>경비처리기한</th>
                        <td colspan="2">{{form.procPeriod}}</td>
                    </tr>
                    <tr>
                        <th>봉사료</th>
                        <td  class="Rt-M tar" colspan="2">{{form.tips | number}}</td>

                        <th>공제구분</th>
                        <td>{{form.crdDdctCd}}</td>
                        <th>기준부서</th>
                        <td colspan="2">{{form.baseDeptCd}} / {{form.baseDeptNm}}</td>
                    </tr>
                    <tr>
                        <th> 적요</th>
                        <td  colspan="7">{{form.hdSgtxt}}</td>
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
  name: 'CardSlipBasicRO',
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
    apprDateTime() {
        const dt = _.trim(this.form.apprDate + this.form.apprTime);
        return (dt.length===14) ? this.$moment(dt,'YYYYMMDDHHmiss').format("YYYY-MM-DD HH:mm:ss") :
               (dt.length===8) ? this.$moment(dt,'YYYYMMDD').format("YYYY-MM-DD") : "";
    },
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

