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
                    <th class="tp-a ">증빙유형</th>
                    <td colspan="2">
                        <b-select class="select is-fullwidth" v-model="form.evdTypeCd" :disabled="hideEvdType">
                            <option
                                    v-for="item in evdTypes"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </td>

                    <th>정산구분</th>
                    <td>
                        <div class="control">
                            <div class="dp-ib fl_left">
                                <input type="radio" id="radio01" v-model="form.stlFgCd" value="N"/>
                                <label for="radio01" class="NotoM">미정산</label>
                            </div>
                            <div class="dp-ib fl_left">
                                <input type="radio" id="radio02" v-model="form.stlFgCd" value="Y" disabled/>
                                <label for="radio02" class="NotoM">선급금정산</label>
                            </div>
                        </div>
                    </td>

                    <th class="tp-a">증빙일자</th>
                    <td>
                        <div class="datepicker w-type-ymd">
                            <!-- <b-datepicker icon="calendar-today"></b-datepicker> -->
                            <!-- <datepicker placeholder="Select Date" v-model="form.evdDt" @change="setPayDueDt"></datepicker> -->
                            <!-- <input type="text" class="input date sDate" v-model="form.evdDt" @change="setPayDueDt(form.payTermCd)"/> -->
                            <input type="text" v-model="form.evdDt" id="calEvdDt" autocomplete="off" class="input"
                                   @change="setPayDueDt(form.payTermCd)" :disabled="hideEvdDt"/>
                        </div>
                    </td>
                </tr>
                <tr>
                    <th class="tp-a">세금코드</th>
                    <td colspan="2">
                        <b-select class="select is-fullwidth" v-model="form.taxCd">
                            <option
                                    v-for="item in taxes"
                                    :key="item.taxCd"
                                    :value="item.taxCd"
                                    :rt="item.taxRt"
                                    v-text="`[${item.taxCd}] ${item.taxNm}`"/>
                        </b-select>
                    </td>

                    <th>선급금정산</th>
                    <td class="clearfix">
                        <div class="control is-expanded search-area">
                            <div class="ip-box rs-mt2" style="width:80%;">
                                <input class="input input-bg" type="text" value=""
                                       onkeydown="if(event.keyCode==13){openPopLayer();}" disabled>
                                <button class="icon is-right" onclick="openPopLayer();" disabled><i
                                        class="fas fa-search"></i></button>
                            </div>
                            <button class="remove_text rs-mt2 rs-mb2" disabled><i class="far fa-trash-alt"></i></button>
                        </div>
                    </td>

                    <th class="tp-a">회계일자</th>
                    <td>
                        <div class="datepicker w-type-ymd">
                            <!-- <input type="text" class="input date sDate" v-model="form.postDt"/> -->
                            <input type="text" v-model="form.postDt" id="calPostDt" autocomplete="off" class="input">
                        </div>
                    </td>
                </tr>
                <tr>
                    <th class="tp-a">거래처</th>
                    <td colspan="2">
                        <div class="td-s-thumb search-area">
                            <input class="input input-bg mr5 Rt-M rs-mt2" type="text" v-model="form.evdCustCd"
                                   style="width:66px;" disabled>
                            <div class="ip-box ip-box-w02 rs-mt2" @keydown.enter="popVendor1">
                                <input class="input" type="text" v-model="form.evdCustNm" @keyup.delete="initVendor1">
                                <button class="icon is-right" @click="popVendor1(true)"><i class="fas fa-search"></i>
                                </button>
                            </div>
                            <button class="remove_text trash-input rs-mb2" @click="initVendor1(true)"><i
                                    class="far fa-trash-alt"></i></button>
                        </div>
                    </td>
                    <td class="bd-l-none">
                        <input type="checkbox" id="payCust" @click="checkActual"/><label for="payCust">실지급처</label>
                    </td>
                    <td class="bd-l-none">
                        <div class="td-s-thumb search-area">
                            <input class="input input-bg mr5 Rt-M rs-mt2" type="text" ref="payCustCd"
                                   v-model="form.payCustCd" style="width:105px;" disabled>
                            <div class="ip-box rs-mt2" @keydown.enter="popVendor2">
                                <input class="input actual" type="text" v-model="form.payCustNm"
                                       @keyup.delete="initVendor2" disabled>
                                <button class="icon is-right actual" @click="popVendor2(true)" disabled><i
                                        class="fas fa-search"></i></button>
                            </div>
                            <button class="remove_text trash-input rs-mb2 actual" @click="initVendor2(true)" disabled><i
                                    class="far fa-trash-alt"></i></button>
                        </div>
                    </td>
                    <th>지급조건</th>
                    <td>
                        <b-select class="select is-fullwidth" v-model="form.payTermCd">
                            <option
                                    v-for="item in payTerms"
                                    :key="item.detailCd"
                                    :value="item.detailCd"
                                    v-text="item.detailNm"/>
                        </b-select>
                    </td>
                </tr>
                <tr>
                    <th class="tp-a">공급가액</th>
                    <td colspan="2">
                        <input class="input Rt-M tar" type="text" v-model="form.supAmt" @keyup="calcVatAmt"
                               :disabled="hideSupAmt">
                    </td>

                    <th class="tp-a">기준부서</th>
                    <td>
                        <div class="td-s-thumb search-area">
                            <input class="input input-bg mr5 Rt-M rs-mt2" type="text" v-model="form.baseDeptCd"
                                   style="width:105px;" disabled>
                            <div class="ip-box rs-mt2">
                                <input class="input" type="text" v-model="form.baseDeptNm" @input="initCctr"
                                       @keydown.enter="popCctr">
                                <button class="icon is-right" @click="popCctr(true)"><i class="fas fa-search"></i>
                                </button>
                            </div>
                            <button class="remove_text trash-input rs-mb2" @click="initCctr(true)"><i
                                    class="far fa-trash-alt"></i></button>
                        </div>
                    </td>

                    <th class="tp-a">지급예정일</th>
                    <td>
                        <div class="datepicker w-type-ymd">
                            <!-- <input type="text" class="input date sDate" v-model="form.payDueDt"/> -->
                            <input type="text" v-model="form.payDueDt" id="calPayDueDt" autocomplete="off"
                                   class="input">
                        </div>
                    </td>
                </tr>
                <tr>
                    <th>부가세액</th>
                    <td colspan="2">
                        <input class="input Rt-M tar" type="text" ref="vat" v-model="form.vatAmt"
                               :disabled="hideVatAmt">
                    </td>

                    <th>대변계정</th>
                    <td>
                        <b-select class="select is-fullwidth" v-model="form.apAcctCd"
                                  @change.native="changeCreditAccount">
                            <option
                                    v-for="item in accounts"
                                    :key="item.key"
                                    :value="item.key"
                                    :name="item.value"
                                    v-text="`[${item.key}] ${item.value}`"/>
                        </b-select>
                    </td>

                    <th class="tp-a">지급계좌</th>
                    <td>
                        <b-select class="select is-fullwidth" v-if="vendAccts.length > 0" v-model="custAccount"
                                  @input="changeVendorAccount">
                            <option
                                    v-for="item in vendAccts"
                                    :key="item.bnkCd+'|'+item.acctNo"
                                    :value="item.bnkCd+'|'+item.acctNo"
                                    v-text="item.acctNo"/>
                        </b-select>
                        <div class="select is-fullwidth" v-else>
                            <select>
                                <option value="" selected>== 지급계좌 없음==</option>
                            </select>
                        </div>
                    </td>
                </tr>
                <tr>
                    <th>기타금액</th>
                    <td colspan="2"><input class="input  Rt-M tar" type="text" v-model="form.etcAmt"
                                           :disabled="hideEtcAmt"></td>

                    <th>{{columnTitle}}</th>
                    <td v-if="slipTypeCd === 'E2'"><input class="input input-bg Rt-M tal" type="text"
                                                          v-model="form.etaxNo" disabled></td>
                    <td v-else><span class="NotoM">{{form.curCd}}</span></td>

                    <th class="tp-a">사업장</th>
                    <td>
                        <b-select class="select is-fullwidth" v-model="form.bpCd">
                            <option
                                    v-for="item in bizPlaces"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </td>
                </tr>
                <tr>
                    <th>총금액</th>
                    <td colspan="2"><input class="input input-bg  Rt-M tar" type="text" v-model="totAmt" disabled></td>

                    <th class="tp-a"> 적요</th>
                    <td colspan="3"><input class="input" type="text" v-model="form.hdSgtxt"></td>
                </tr>
                </tbody>
            </table>
        </div>

        <slip-grid ref="detail" :slipDetails="slipDetails" :form="form" @setHideVat="setHideVat"/>

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
                      <span class="icon-bar"><img src="/img/bar.png" alt=""/></span>
                    </span>
                    <span class="file-name">{{ this.$numeral(evidFileSize).format('00') }}<i class="far fa-file-alt"></i></span>
                </div>
            </div>
            <!-- //20190520 퍼블수정 -->
        </div>
        <!--//파일업로드-->

        <!--팝업-->
        <b-modal :active.sync="showVendorModal1" has-modal-card @receive="receiveVendor1">
            <vendor :param="form.evdCustNm" :slipTypeCd="slipTypeCd"></vendor>
        </b-modal>
        <b-modal :active.sync="showVendorModal2" has-modal-card @receive="receiveVendor2">
            <vendor :param="form.payCustNm" :slipTypeCd="slipTypeCd"></vendor>
        </b-modal>
        <b-modal :active.sync="showCctrModal" has-modal-card @receive="receiveCctr">
            <cctr :param="form.baseDeptNm"></cctr>
        </b-modal>
        <!--//팝업 -->
    </div>

</template>

<script>
    /* eslint-disable */
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import _ from 'lodash'
    // PopUp
    import Vendor from '@/components/Vendor.vue';
    import Account from '@/components/Account.vue';
    import Cctr from '@/components/Cctr.vue';
    import SlipGrid from '@/components/SlipGrid.vue';
    import EvidAtchPop from '@/components/EvidAtchPop.vue'

    export default {
        name: 'SlipBasic',

        props: {
            slipTypeCd: {
                type: String,
                required: false
            },
            slipHeader: {
                type: Object,
                required: false
            },
            slipDetails: {
                type: Array,
                required: false
            },
            readonly: {
                type: Boolean,
                required: false,
                default: false
            },
            showEvidAtchPop: {
                type: Boolean,
                required: false,
                default: true
            }
        },

        //props: ['slipTypeCd','slipHeader','slipDetails'],
        mixins: [mixin, mixinSlip],
        components: {Vendor, Account, Cctr, SlipGrid},
        data() {
            return {
                title: '기본정보',
                evdTypes: [],
                taxes: [],
                payTerms: [],
                vendAccts: [],
                bizPlaces: [],
                accounts: [],
                form: {
                    // 전표상태코드
                    slipStatCd: '10',
                    // 증빙유형코드
                    evdTypeCd: '',
                    // 정산구분코드
                    stlFgCd: 'N',
                    // 시스템구분코드WM
                    sysFgCd: 'W',
                    // 세금코드
                    taxCd: '',
                    // 증빙일자
                    evdDt: this.$moment().format('YYYY-MM-DD'),
                    // 회계일자
                    postDt: this.$moment().format('YYYY-MM-DD'),
                    // 증빙거래처코드
                    evdCustCd: '',
                    // 증빙거래처명
                    evdCustNm: '',
                    // 증빙거래처사업자번호
                    evdCustBizNo: '',
                    // 지급거래처코드
                    payCustCd: '',
                    // 지급거래처명
                    payCustNm: '',
                    // 지급거래처사업자번호
                    payCustBizNo: '',
                    // 지급방법
                    payMthdCd: '',
                    // 지급조건
                    payTermCd: '',
                    // 지급만기일(지급예정일)
                    payDueDt: '',
                    // 거래처계좌번호
                    custAcctNo: '',
                    // 거래처계좌은행코드
                    custBnkCd: '',
                    // 작성일시
                    wrtDtm: '',
                    // 작성자
                    wrtId: '',
                    // 작성부서코드
                    wrtDeptCd: '',
                    // 기준부서코드
                    baseDeptCd: this.$store.state.loginInfo.loginDeptCd,
                    // 기준부서명
                    baseDeptNm: this.$store.state.loginInfo.loginDeptNm,
                    // 미지급계정코드
                    apAcctCd: '',
                    // 대표계정코드
                    stnAcctCd: '',
                    // 공급가액
                    supAmt: '',
                    // 부가세액
                    vatAmt: '',
                    // 기타금액
                    etcAmt: '',
                    // 총금액
                    totAmt: '',
                    // 통화코드
                    curCd: 'KRW',
                    // 사업장코드
                    bpCd: '',
                    // 전표적요
                    hdSgtxt: '',
                },
                evidFileSize: 0,
                viewMode: false,
                showVendorModal1: false,
                showVendorModal2: false,
                showCctrModal: false,
                hideEvdType: false,
                hideEvdDt: false,
                hideSupAmt: false,
                hideVatAmt: false,
                hideEtcAmt: false,
            };
        },
        methods: {
            // 증빙유형
            getEvdTypeCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "EVD_TYPE_CD", remark1: this.slipTypeCd}})
                    .then(response => {
                        this.evdTypes = response.data;
                        this.selectOne({data: this.evdTypes, target: 'evdTypeCd'});
                    });
            },
            // 세금코드
            getTaxCombo(view) {
                // viewMode가 false인 경우에만, selectOne이 동작함
                if (view != undefined) this.viewMode = view;

                this.$http.get(`/api/taxes`, {params: {evdTypeCd: this.form.evdTypeCd}})
                    .then(response => {
                        this.taxes = response.data;
                        this.selectOne({data: this.taxes, target: 'taxCd', key: 'taxCd'});
                        this.setVatDisabled();
                    });
            },
            // 지급조건
            getPayTermCombo() {
                this.$http.get(`/api/code/detail`, {params: {groupCd: "PAY_TERM_CD", remark3: this.form.evdTypeCd}})
                    .then(response => {
                        this.payTerms = response.data;
                        this.selectOne({data: this.payTerms, target: 'payTermCd', key: 'detailCd'});
                    });
            },
            getVendorAccountCombo(value) {
                this.$http.get(`/api/vendor/account/${value}`)
                    .then(response => {
                        this.vendAccts = response.data;

                        if (this.vendAccts.length > 0) {
                            this.form.custBnkCd = this.vendAccts[0].bnkCd;
                            this.form.custAcctNo = this.vendAccts[0].acctNo;
                            this.form.custAcctNo = this.vendAccts[0].acctNo;
                        } else {
                            this.form.custBnkCd = '';
                            this.form.custAcctNo = '';
                            this.form.custAcctNo = '';
                        }
                    });
            },
            // 사업장
            getBizPlaceCombo() {
                this.$http.get(`/api/bp/combo`)
                    .then(response => {
                        this.bizPlaces = response.data;
                        this.selectOne({data: this.bizPlaces, target: 'bpCd'});
                    });
            },
            // 대변계정
            getAccountCombo() {
                this.$http.get(`/api/account/combo/${this.slipTypeCd}`)
                    .then(response => {
                        this.accounts = response.data;
                        this.selectOne({data: this.accounts, target: 'apAcctCd'});
                        this.selectOne({data: this.accounts, target: 'apAcctNm', key: 'value'});
                    });
            },
            changeCreditAccount(event) {
                this.form.apAcctNm = $(event.target).children("option:selected").attr("name");
            },
            changeVendorAccount(value) {
                const valueArr = value.split("|");
                if (valueArr.length === 2) {
                    this.form.custBnkCd = valueArr[0];
                    this.form.custAcctNo = valueArr[1];
                }
            },
            popVendor1(clear) {
                if (clear === true) {
                    this.form.evdCustCd = '';
                    this.form.evdCustNm = '';
                    this.form.evdCustBizNo = '';
                }
                this.showVendorModal1 = true;
            },
            popVendor2(clear) {
                if (clear === true) {
                    this.form.payCustCd = '';
                    this.form.payCustNm = '';
                    this.form.payCustBizNo = '';
                }
                this.showVendorModal2 = true;
            },
            popCctr(clear) {
                if (clear === true) {
                    this.form.baseDeptCd = '';
                    this.form.baseDeptNm = '';
                }
                this.showCctrModal = true;
            },
            receiveCctr(obj) {
                this.form.baseDeptCd = obj.cctrCd;
                this.form.baseDeptNm = obj.cctrNm;
            },
            receiveVendor1(obj) {
                this.form.evdCustCd = obj.vendCd;
                this.form.evdCustNm = obj.vendNm;
                this.form.evdCustBizNo = obj.bizNo;
            },
            receiveVendor2(obj) {
                this.form.payCustCd = obj.vendCd;
                this.form.payCustNm = obj.vendNm;
                this.form.payCustBizNo = obj.bizNo;
            },
            initVendor1(force) {
                if (force === true) this.form.evdCustNm = '';
                if (this.form.evdCustNm === '') {
                    this.form.evdCustCd = '';
                    this.form.evdCustBizNo = '';
                }
            },
            initVendor2(force) {
                if (force === true) this.form.payCustNm = '';
                if (this.form.payCustNm === '') {
                    this.form.payCustCd = '';
                    this.form.payCustBizNo = '';
                }
            },
            initCctr(force) {
                if (force === true) this.form.baseDeptNm = '';
                if (this.form.baseDeptNm === '') this.form.baseDeptCd = '';
            },
            checkActual(event) {
                if ($(event.target).is(":checked")) {
                    $(".actual").attr("disabled", false);
                    this.getVendorAccountCombo(this.form.payCustCd);
                } else {
                    $(".actual").attr("disabled", true);
                    this.getVendorAccountCombo(this.form.evdCustCd);
                }
            },
            selectOne(o) {
                if (o && o.data.length > 0) {
                    // 등록 시 기본값 셋팅
                    if (!this.viewMode) {
                        this.form[o.target] = (o.key) ? o.data[0][o.key] : o.data[0].key;
                    }
                }
            },
            showWritedRow() {
                if (String(this.form.eaSlipNo||'').match(/^EA.*$/g) && this.form.slipStatCd === '10') {
                    $("#basic tr:lt(2)").show();
                } else {
                    $("#basic tr:lt(2)").hide();
                }
            },
            setDept(cd, nm) {
                this.form.baseDeptCd = cd;
                this.form.baseDeptNm = nm;
            },
            setCreditAccount(cd, nm) {
                this.form.apAcctCd = cd;
                this.form.apAcctNm = nm;
            },
            setHdSgtxt(txt) {
                this.form.hdSgtxt = txt;
            },
            calcVatAmt() {
                const item = this.taxes.find(e => e.taxCd === this.form.taxCd);
                if (item) {
                    const supAmt = _.toInteger(this.toPure(this.form.supAmt));
                    const vatAmt = Math.floor((supAmt / item.taxRt) / 10) * 10;
                    this.form.vatAmt = this.$filters.number(vatAmt + '');
                }
            },
            validation() {
                const header = JSON.parse(JSON.stringify(this.form));
                const stripFields = ['evdDt', 'postDt', 'payDueDt', 'supAmt', 'vatAmt', 'etcAmt', 'totAmt'];
                _.forEach(stripFields, (name) => header[name] = this.toPure(header[name]));

                if (!header.evdTypeCd) {
                    this.$swal({type: 'warning', text: '증빙유형을 선택해 주세요.'});
                    return false;
                }
                if (!header.stlFgCd) {
                    this.$swal({type: 'warning', text: '정산구분을 선택해 주세요.'});
                    return false;
                }
                if (!header.evdDt) {
                    this.$swal({type: 'warning', text: '증빙일자를 입력해 주세요.'});
                    return false;
                }
                if (!header.postDt) {
                    this.$swal({type: 'warning', text: '회계일자를 입력해 주세요.'});
                    return false;
                }
                if (!header.evdCustCd) {
                    this.$swal({type: 'warning', text: '거래처를 선택해 주세요.'});
                    return false;
                }
                if (_.toInteger(header.supAmt) == 0) {
                    this.$swal({type: 'warning', text: '공급가액을 입력해 주세요.'});
                    return false;
                }
                if (!header.baseDeptCd) {
                    this.$swal({type: 'warning', text: '기준부서를 선택해 주세요.'});
                    return false;
                }
                if (!header.payDueDt) {
                    this.$swal({type: 'warning', text: '지급예정일을 입력해 주세요.'});
                    return false;
                }
                //   if(!header.custAcctNo)  { this.$swal({ type: 'warning', text: '지급계좌를 선택해 주세요.' }); return false; }
                if (!header.bpCd) {
                    this.$swal({type: 'warning', text: '사업장을 선택해 주세요.'});
                    return false;
                }
                if (!header.hdSgtxt) {
                    this.$swal({type: 'warning', text: '적요를 입력해 주세요.'});
                    return false;
                }

                if (!this.$refs.detail.validation()) return false;

                return true;
            },
            setVatDisabled() {
                const tax = this.taxes.find(x => x.taxCd == this.form.taxCd);
                if (tax && tax.taxRt === 0) {
                    this.setHideVat(true);
                } else {
                    this.setHideVat(false);
                    this.calcVatAmt();
                }
            },
            setHideVat(hide) {
                this.hideVatAmt = hide;
            },
            setPayDueDt(value) {
                if (value) {
                    const obj = this.payTerms.find(x => x.detailCd === value);
                    if (obj) {
                        const m = parseInt(obj.remark1, 10);
                        const d = parseInt(obj.remark2, 10);

                        if (m === 0) {
                            this.form.payDueDt = '';
                        } else {
                            let dt = this.$moment().add(m, 'month');

                            if (this.form.evdDt) dt = this.$moment(this.form.evdDt).add(m, 'month');

                            if (d === 31) {
                                dt = this.$moment(dt).endOf('month');
                            } else {
                                dt = this.$moment(dt).date(d);
                            }
                            this.form.payDueDt = dt.format('YYYY-MM-DD');
                        }
                    }
                }
            },
            calendarLoad() {
                // 증빙일자
                const iljinCalendar1 = new dhtmlXCalendarObject('calEvdDt');
                iljinCalendar1.setDate(new Date());
                iljinCalendar1.hideTime();
                iljinCalendar1.attachEvent('onChange', (v) => {
                    this.form.evdDt = this.$refs.calEvdDt.getFormatedDate();
                    this.setPayDueDt(this.form.payTermCd);
                });
                iljinCalendar1.attachEvent("onButtonClick", (d) => {
                    if (d === null) {
                        this.form.evdDt = this.$refs.calEvdDt.getFormatedDate()
                    }
                });
                this.$refs.calEvdDt = iljinCalendar1;

                // 회계일자
                const iljinCalendar2 = new dhtmlXCalendarObject('calPostDt');
                iljinCalendar2.setDate(new Date());
                iljinCalendar2.hideTime();
                iljinCalendar2.attachEvent('onChange', (v) => {
                    this.form.postDt = this.$refs.calPostDt.getFormatedDate()
                });
                iljinCalendar2.attachEvent("onButtonClick", (d) => {
                    if (d === null) {
                        this.form.postDt = this.$refs.calPostDt.getFormatedDate()
                    }
                });
                this.$refs.calPostDt = iljinCalendar2;

                // 지급예정일
                const iljinCalendar3 = new dhtmlXCalendarObject('calPayDueDt');
                iljinCalendar3.setDate(new Date());
                iljinCalendar3.hideTime();
                iljinCalendar3.attachEvent('onChange', (v) => {
                    this.form.payDueDt = this.$refs.calPayDueDt.getFormatedDate()
                });
                iljinCalendar3.attachEvent("onButtonClick", (d) => {
                    if (d === null) {
                        this.form.payDueDt = this.$refs.calPayDueDt.getFormatedDate()
                    }
                });
                this.$refs.calPayDueDt = iljinCalendar3;
            },
            checkVendorInfo() {
                this.form.evdCustId = '';
                this.form.evdCustNm = '';
                this.$http.get(`/api/vendor/${this.slipTypeCd}/${this.form.evdCustBizNo}`)
                    .then(({data}) => {
                        if (data && data.length > 0) {
                            this.form.evdCustId = data[0].vendCd;
                            this.form.evdCustNm = data[0].vendNm;
                            this.form.evdCustBizNo = data[0].bizNo;
                        }
                    });
            },
            checkTrustedInfo() {
                this.form.payCustCd = '';
                this.form.payCustNm = '';
                this.$http.get(`/api/vendor/${this.slipTypeCd}/${this.form.payCustBizNo}`)
                    .then(({data}) => {
                        if (data && data.length > 0) {
                            this.form.payCustCd = data[0].vendCd;
                            this.form.payCustNm = data[0].vendNm;
                            this.form.payCustBizNo = data[0].bizNo;
                            $("#payCust").click();
                        }
                    });
            },
            setFieldDisabled() {
                this.hideEvdType = true;
                this.hideEvdDt = true;
                this.hideSupAmt = true;
                this.hideVatAmt = true;
                this.hideEtcAmt = true;
            },
            setSlipHeader() {
                Object.assign(this.form, this.slipHeader);

                console.log('eaSlipNo! : ' + this.form.eaSlipNo)
                // format date
                if (this.form.evdDt) this.form.evdDt = this.$moment(this.form.evdDt).format('YYYY-MM-DD');
                if (this.form.postDt) this.form.postDt = this.$moment(this.form.postDt).format('YYYY-MM-DD');
                if (this.form.payDueDt) this.form.payDueDt = this.$moment(this.form.payDueDt).format('YYYY-MM-DD');

                if (this.slipTypeCd === 'E2') {
                    // 거래처 검증
                    this.checkVendorInfo();
                    // 수탁거래
                    if (this.form.payCustBizNo !== '') this.checkTrustedInfo();
                    // 입력항목 비활성화
                    this.setFieldDisabled();

                    if (this.form.eaSlipNo !== undefined) {
                        this.viewMode = true;
                        this.$emit("changeViewMode", this.viewMode);
                        this.showWritedRow();
                    }
                } else {
                    // 증빙일자
                    this.evdDt = this.$moment().format('YYYY-MM-DD');

                    this.viewMode = true;
                    this.$emit("changeViewMode", this.viewMode);
                    this.showWritedRow();
                }
            },
            queryEvidFile() {
                /**
                 * 증빙파일이 얼마나 첨부되었는지 확인해보자
                 */
                this.$http.get(`/api/evid/fileList/${this.getId}`)
                    .then(response => {
                        this.evidFileSize = ((response.data || {}).aFiles || []).length
                    })
            },
            openUploadEvidencePopup() {
                // if (this.form.eaSlipNo === undefined) {
                //     this.$swal({type: 'warning', text: '저장 후 작업해주세요.'});
                //     return false;
                // }

                let vm = this
                console.log(this.form.eaSlipNo, this.form.slipStatCd)
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
            totAmt() {
                let supAmt = _.parseInt(this.toPure(this.form.supAmt) || 0);
                let vatAmt = _.parseInt(this.toPure(this.form.vatAmt) || 0);
                let etcAmt = _.parseInt(this.toPure(this.form.etcAmt) || 0);
                return this.$filters.number(_.toString(supAmt + vatAmt + etcAmt));
            },
            custAccount() {
                return this.form.custBnkCd + "|" + this.form.custAcctNo;
            },
            columnTitle() {
                return this.slipTypeCd === 'E2' ? '전자승인번호' : '통화';
            }
        },
        watch: {
            slipHeader() {
                this.setSlipHeader();
            },
            'form.evdTypeCd'() {
                this.getPayTermCombo();
                this.getTaxCombo(false);
            },
            'form.evdCustCd'(value) {
                this.getVendorAccountCombo(value);
            },
            'form.payCustCd'(value) {
                this.getVendorAccountCombo(value);
            },
            'form.payTermCd'(value) {
                this.setPayDueDt(value);
            },
            'form.supAmt'(value) {
                this.form.supAmt = this.$filters.number(value);
            },
            'form.vatAmt'(value) {
                this.form.vatAmt = this.$filters.number(value);
            },
            'form.etcAmt'(value) {
                this.form.etcAmt = this.$filters.number(value);
            },
            totAmt(value) {
                this.form.totAmt = this.$filters.number(value);
            },
        },
        mounted() {
            window.setPayDueDt = () => this.setPayDueDt(this.form.payTermCd);

            if (this.form.eaSlipNo === undefined) {
                this.$http.get('/api/tmp/documentMngNo')
                    .then(response => {
                    this.form.eaSlipNo = response.data
                    this.queryEvidFile(this.form.eaSlipNo)
                })
            } else {
                this.queryEvidFile(this.form.eaSlipNo)
            }

            this.calendarLoad();
            this.getEvdTypeCombo();
            this.getPayTermCombo();
            this.getBizPlaceCombo();
            this.getAccountCombo();
            this.showWritedRow();
        },
    };
</script>

<style>
</style>
