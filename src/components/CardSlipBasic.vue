<template>
    <div>
        <div class="table-a fixed-th">
            <div class="table-name">
                <h3 class="ico_table_name">{{title}}</h3>
            </div>
            <table id="basic" class="table">
                <tbody>
                    <tr>
                        <th>전표번호</th>
                        <td width="12%">{{form.eaSlipNo}}</td>
                        <td width="8%"></td>

                        <th>전표유형</th>
                        <td>{{form.slipTypeNm}}</td>

                        <th>전표상태</th>
                        <td><span class="color_table_org">{{form.slipStatNm}}</span></td>
                    </tr>
                    <tr>
                        <th>작성부서</th>
                        <td>{{form.wrtDeptCd}} / {{form.wrtDeptNm}}</td>
                        <td>{{form.bpNm}}</td>

                        <th>작성자</th>
                        <td>{{form.wrtNm}}</td>

                        <th>작성일자</th>
                        <td class="Rt-M">{{this.$moment(form.wrtDtm).format('YYYY-MM-DD')}}</td>
                    </tr>
                    <tr>
                        <th>카드번호</th>
                        <td colspan="2">{{form.crdNo}}</td>

                        <th>승인번호</th>
                        <td>{{form.crdApprNo}}</td>

                        <th>증빙일자</th>
                        <td>{{form.evdDt}}</td>
                    </tr>
                    <tr>
                        <th>카드소유자</th>
                        <td colspan="2">{{form.crdPssrNm}} {{form.crdPssrTitle}}</td>

                        <th>카드구분</th>
                        <td>{{form.crdFgNm}}</td>

                        <th class="tp-a">회계일자</th>
                        <td>
                            <div class="datepicker w-type-ymd">
                                <input type="text" v-model="form.postDt" id="calPostDt" autocomplete="off" class="input">
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <th>승인금액</th>
                        <td  colspan="2">
                            <input class="input Rt-M tar" type="text" v-model="form.totAmt" disabled>
                        </td>

                        <th>가맹점명</th>
                        <td>{{form.crdMerchNm}}</td>

                        <th>승인시간</th>
                        <!-- <td>{{this.$moment(form.apprDate).format("YYYY-MM-DD") + ' ' + form.apprTime}}</td> -->
                        <td v-if="form.apprDate">{{apprDateTime}}</td>
                        <td v-else>&nbsp;</td>
                    </tr>
                    <tr>
                        <th>공급가액</th>
                        <td  colspan="2">
                            <input class="input Rt-M tar" type="text" v-model="form.supAmt" @keyup="calcVatAmt" :disabled="hideSupAmt">
                        </td>

                        <th>가맹점주소</th>
                        <td colspan="3">{{form.merchAddr}}</td>
                    </tr>
                    <tr>
                        <th>부가세액</th>
                        <td  colspan="2">
                            <input class="input Rt-M tar" type="text" ref="vat" v-model="form.vatAmt" :disabled="hideVatAmt">
                        </td>

                        <th>과세유형/업종</th>
                        <td>{{form.taxTypeNm}}/{{form.mccName}}</td>

                        <th>경비처리기한</th>
                        <td>{{form.procPeriod}}</td>
                    </tr>
                    <tr>
                        <th>봉사료</th>
                        <td  colspan="2"> <input class="input  Rt-M tar" type="text" v-model="form.tips" disabled> </td>

                        <th>공제구분</th>
                        <td> 
                            <span v-for="item in crdDdctCds" :key="item.detailCd">
                                <input type="radio" name="crdDdctCd" 
                                    :id="'rdo'+item.detailCd" 
                                    :value="item.detailCd" 
                                    :disabled="disableCrdDdct" 
                                    v-model="form.crdDdctCd" 
                                    @change="checkCrdDdct" />
                                <label :for="'rdo'+item.detailCd">{{item.detailNm}}</label>
                            </span>
                        </td>
                        <th class="tp-a">기준부서</th>
                        <td>
                            <div class="td-s-thumb search-area">
                                <input class="input input-bg mr5 Rt-M rs-mt2" type="text" v-model="form.baseDeptCd" style="width:105px;" disabled>
                                <div class="ip-box rs-mt2">
                                    <input class="input" type="text" v-model="form.baseDeptNm" @input="initCctr" @keydown.enter="popCctr">
                                    <button class="icon is-right" @click="popCctr(true)"><i class="fas fa-search"></i></button>
                                </div>
                                <button class="remove_text trash-input rs-mb2" @click="initCctr(true)"><i class="far fa-trash-alt"></i></button>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <th class="tp-a"> 적요</th>
                        <td  colspan="6"> <input class="input" type="text" v-model="form.hdSgtxt" ></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <slip-grid ref="detail" :slipDetails="slipDetails" :form="form" @checkNdct="checkNdct"/>

        <!--파일업로드-->
        <div class="file-upload">
            <div class="table-name">
            <h3 class="ico_table_name">증빙첨부</h3>
            </div>
            <!-- 20190520 퍼블수정 -->
            <div class="file has-name">
            <div class="file-label" @click="openUploadEvidencePopup()">
                <span class="file-cta">
                <span class="file-label"> Files Count</span>
                <span class="icon-bar"><img src="/img/bar.png" alt="" /></span>
                </span>
                <span class="file-name">{{ this.$numeral(evidFileSize).format('00') }}<i class="far fa-file-alt"></i></span>
            </div>
            </div>
            <!-- //20190520 퍼블수정 -->
        </div>
        <!--//파일업로드-->

        <!--팝업-->
        <b-modal :active.sync="showCctrModal" has-modal-card @receive="receiveCctr">
            <cctr :param="form.baseDeptNm"></cctr>
        </b-modal>
        <!--//팝업 -->
    </div>

</template>

<script>
/* eslint-disable */
// import moment from 'moment'
import mixin from '@/mixin';
import mixinSlip from '@/mixin/slip';
import _ from 'lodash'
// PopUp
import Cctr from '@/components/Cctr.vue';
import SlipGrid from '@/components/CardSlipGrid.vue';
import EvidAtchPop from '@/components/EvidAtchPop.vue'

export default {
  name: 'CardSlipBasic',
  props: ['slipTypeCd','slipHeader','slipDetails'],
  mixins: [ mixin, mixinSlip ],
  components: { Cctr, SlipGrid },
  data() {
    return {
      title: '기본정보',
      taxes: [],
      crdDdctCds: [],
      rcps: [],
      ndctMccNames: '',
      form: {
        // 전표유형
        slipTypeNm: '',
        // 전표상태
        slipStatNm: '',
        // 작성부서
        wrtDeptCd: '',
        wrtDeptNm: '',
        // 작성자
        wrtNm: '',
        // 작성일자
        wrtDtm: '',
        // 카드번호 
        crdNo: '',
        // 승인번호 
        crdApprNo: '',
        // 증빙일자 
        evdDt: '',
        // 카드소유주ID 
        crdPssrId: '',
        crdPssrNm: '',
        crdPssrTitle: '',
        // 카드구분 
        crdFgCd: '',
        crdFgNm: '',
        // 회계일자
        postDt: this.$moment().format('YYYY-MM-DD'),
        // 승인금액
        // purchTot: '',
        totAmt: '',
        // 가맹점명 
        crdMerchNm: '',
        // 승인일자 
        apprDate: '',
        // 승인시각 
        apprTime: '',
        // 가맹점주소
        merchAddr: '',
        // 과세유형
        taxTypeNm: '',
        // 업종
        mccName: '',
        // 공급가액 
        // apprAmt: '',
        supAmt: '',
        // 부가세액 
        // vat: '',
        vatAmt: '',
        // 봉사료 
        tips: '',
        // 경비처리기한 
        procPeriod: '',
        // 공제구분 
        crdDdctCd: '',
        // 기준부서
        baseDeptCd: 'O000000023',
        baseDeptNm: '연구개발팀',
        // 적요
        hdSgtxt: '',
        /* 내부설정사항 */
        // 전표유형
        slipTypeCd: 'E1',
        // 전표상태코드 
        slipStatCd: '10',
        // 증빙유형코드 
        evdTypeCd: '10',
        // 세금코드 
        taxCd: '',
        // 정산구분코드 
        stlFgCd: 'N',
        // 시스템구분코드WM 
        sysFgCd: 'W',
        // 세금코드 
        taxCd: '',
        // 지급조건 
        payTermCd: '',
        // 지급만기일(지급예정일) 
        payDueDt: this.$moment().format('YYYY-MM-DD'),
        // 거래처계좌번호 
        custAcctNo: '',
        // 거래처계좌은행코드 
        custBnkCd: '',
        // 통화코드 
        curCd: 'KRW',
        // 사업장코드 
        bpCd: '',
        length: ''
      },
      viewMode: false,
      showCctrModal: false,
      hideSupAmt: false,
      hideVatAmt: false,
      disableCrdDdct: false,
      evidFileSize: 0
    };
  },
  methods: {
    getTaxCombo() {
        this.$http.get(`/api/taxes`, { params: {evdTypeCd: this.form.evdTypeCd} })
            .then(response => {
                this.taxes = response.data;
            });
    },
    getCrdDdctCombo() {
        this.$http.get(`/api/code/detail`, { params: {groupCd: "CRD_DDCT_CD" } })
            .then(response => {
                this.crdDdctCds = response.data;
                if(this.viewMode == false) this.setCrdDdctRadio();
            });
    },
    getRcpAccounts() {
        this.$http.get(`/api/accounts/rcp`)
            .then(response => {
                this.rcps = response.data;
            });
    },
    getNdctMccName() {
        this.$http.get(`/api/code/detail`, { params: {groupCd: "NDCT_MCC_NAME"} })
            .then(({data}) => {
                if(data && data.length > 0)
                    this.ndctMccNames = data[0].remark1;
            });
    },
    setCrdDdctRadio() {
        const item = _.find(this.crdDdctCds, (o) => o.remark1 === this.form.taxCd);
        if(item) {
            this.form.crdDdctCd = item.detailCd;
        }
        // 활성화 (부가세액 존재, 일반과세자)
        if(_.toInteger(this.form.vatAmt) > 0 && this.form.taxTypeCd === '1001') {
            this.setHideSup(false);
            this.setHideVat(false);
            this.disableCrdDdct = false;
        } else {
            this.setHideSup(true);
            this.setHideVat(true);
            // 불공제, 비활성
            if(this.form.taxTypeCd === '2001') {
                this.form.crdDdctCd = '20';
                this.disableCrdDdct = true;
            // 면세, 비활성 (간이과세자, 면세사업자)
            } else if(this.form.taxTypeCd === '1002' || this.form.taxTypeCd === '1003') {
                this.form.crdDdctCd = '30';
                this.disableCrdDdct = true;
            }
        }
    },
    checkCrdDdct(event) {
        const item = _.find(this.crdDdctCds, (o) => o.detailCd === this.form.crdDdctCd);
        if(item) {
            this.form.taxCd = item.remark1
            if(this.form.taxCd === 'C1') {
                this.setHideSup(false);
                this.setHideVat(false);
                this.calcVatAmt();
            } else {
                this.setHideSup(true);
                this.setHideVat(true);
            }
        }
    },
    checkNdct(acct) { // 불공제
        // const acctCd = this.$refs.detail.$refs.grid.cells2(3,7).getValue();
        if(acct && acct.acctCd !== '') {
            // 접대비계정 여부
            let isRcp = (_.find(this.rcps, (o) => o.acctCd === acct.acctCd) === undefined) ? false : true;
            // 불공제업종 여부
            let isNdct = (_.find(this.ndctMccNames.split(","), (name) => name === acct.acctNm) === undefined) ? false : true;

            if(isRcp || isNdct) {
                // 불공제 선택 후 비활성화
                this.form.crdDdctCd = '20';
                this.disableCrdDdct = true;
            }
        }
    },
    popCctr(clear) {
        if(clear===true) {
            this.form.baseDeptCd = '';
            this.form.baseDeptNm = '';
        }
        this.showCctrModal = true;
    },
    receiveCctr(obj) {
        this.form.baseDeptCd = obj.cctrCd;
        this.form.baseDeptNm = obj.cctrNm;
    },
    initCctr(force) {
        if(force===true) this.form.baseDeptNm = '';
        if(this.form.baseDeptNm === '') this.form.baseDeptCd = '';
    },
    selectOne(o) {
        if(o && o.data.length > 0) {
            // 등록 시 기본값 셋팅
            if(!this.viewMode) {
                this.form[o.target] = (o.key) ? o.data[0][o.key] : o.data[0].key;
            }
        }
    },
    showWritedRow() {
        if(this.form.eaSlipNo != undefined && this.form.slipStatCd === '10') {
            $("#basic tr:lt(2)").show();
        } else {
            $("#basic tr:lt(2)").hide();
        }
    },
    calcVatAmt() {
        const item = this.taxes.find(e => e.taxCd === this.form.taxCd);
        if(item) {
            const supAmt = _.toInteger(this.toPure(this.form.supAmt));
            const vatAmt = Math.floor((supAmt/item.taxRt)/10)*10;
            this.form.vatAmt = this.$filters.number(vatAmt+'');
        }
    },
    validation() {
      const header = JSON.parse(JSON.stringify(this.form));
      const stripFields = ['evdDt','postDt','supAmt','vatAmt'];
      _.forEach(stripFields, (name) => header[name] = this.toPure(header[name]));

      if(!header.postDt)    { this.$swal({ type: 'warning', text: '회계일자를 입력해 주세요.' }); return false; }
      if(!header.baseDeptCd)  { this.$swal({ type: 'warning', text: '기준부서를 선택해 주세요.' }); return false; }
      if(!header.hdSgtxt)    { this.$swal({ type: 'warning', text: '적요를 입력해 주세요.' }); return false; }
      if(header.crdDdctCd === '10' && _.toInteger(header.vatAmt) === 0 ) {
          this.$swal({ type: 'warning', text: '부가세액을 입력해 주세요.' });
          return false; 
      }

      if(!this.$refs.detail.validation()) return false;

      return true;
    },
    setHideSup(hide) {
        this.hideSupAmt = hide;
    },
    setHideVat(hide) {
        this.hideVatAmt = hide;
    },
    calendarLoad() {
      // 회계일자
      const iljinCalendar2 = new dhtmlXCalendarObject('calPostDt');
      iljinCalendar2.setDate(new Date());
      iljinCalendar2.hideTime();
      iljinCalendar2.attachEvent('onChange', (v) => { this.form.postDt = this.$refs.calPostDt.getFormatedDate() });
      iljinCalendar2.attachEvent("onButtonClick", (d) => { if (d === null) { this.form.postDt = this.$refs.calPostDt.getFormatedDate() } });
      this.$refs.calPostDt = iljinCalendar2;
    },
    setSlipHeader() {
        Object.assign(this.form, this.slipHeader);
        // format date
        if(this.form.evdDt) this.form.evdDt = this.$moment(this.form.evdDt).format('YYYY-MM-DD');
        if(this.form.postDt) this.form.postDt = this.$moment(this.form.postDt).format('YYYY-MM-DD');
        if(this.form.crdNo) this.form.crdNo = this.getFormattedCardNumber(this.form.crdNo);

        if(this.form.eaSlipNo !== undefined) {
            this.viewMode = true;
            this.$emit("changeViewMode", this.viewMode);
            this.showWritedRow();
            this.queryEvidFile(this.form.eaSlipNo)
        } else {
            this.$http.get('/api/tmp/documentMngNo')
                .then(response => {
                this.form.eaSlipNo = response.data
                this.queryEvidFile(this.form.eaSlipNo)
            })
        }
    },
    queryEvidFile() {
      /**
       * 증빙파일이 얼마나 첨부되었는지 확인해보자
       */
      this.$http.get(`/api/evid/fileList/${this.form.eaSlipNo}`)
        .then(response => {
          this.evidFileSize = ((response.data || {}).aFiles || []).length
        })
    },
    openUploadEvidencePopup() {
      let vm = this
      this.$modal.open({
        component: EvidAtchPop,
        props: {
          docMngNo: this.form.eaSlipNo,
          readonly: this.form.slipStatCd !== '10'
        },
        parent: this,
        width: 1200,
        events: {
          close(value) {
            vm.evidFileSize = value.length
          }
        }
      })
    }
  },
  computed: {
    apprDateTime() {
        const dt = _.trim(this.form.apprDate + this.form.apprTime);
        return (dt.length===14) ? this.$moment(dt,'YYYYMMDDHHmiss').format("YYYY-MM-DD HH:mm:ss") :
               (dt.length===8) ? this.$moment(dt,'YYYYMMDD').format("YYYY-MM-DD") : "";
    },
  },
  watch: {
    slipHeader() {
        this.setSlipHeader();
        this.getTaxCombo();
        this.getRcpAccounts();
        this.getNdctMccName();
        this.getCrdDdctCombo();
    },
    'form.totAmt'(value) {
        this.form.totAmt = this.$filters.number(value);
    },
    'form.supAmt'(value) {
        this.form.supAmt = this.$filters.number(value);
    },
    'form.vatAmt'(value) {
        this.form.vatAmt = this.$filters.number(value);
    },
    'form.tips'(value) {
        this.form.tips = this.$filters.number(value);
    },
  },
  mounted() {
    this.calendarLoad();
    this.showWritedRow();	
  },
};
</script>

<style>
</style>