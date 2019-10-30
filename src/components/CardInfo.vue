<template>
    <div>
        <div class="table-a fixed-th">
            <div class="table-name">
                <h3 class="ico_table_name">{{title}}</h3>
            </div>
            <table id="basic" class="table">
                <tbody>
                <tr>
                    <th class="tp-a">카드번호</th>
                    <td colspan="2">
                        <input v-if="form.crdNoHidden===''" class="input" type="text" v-model="form.crdNo" maxlength="19">
                        <input v-else class="input" type="text" v-model="form.crdNo" disabled>
                    </td>

                    <th>카드사</th>
                    <td>
                        <b-select class="select is-fullwidth" v-model="form.crdCompCd">
                            <option
                                    v-for="item in crdCompCds"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </td>

                    <th>카드상태</th>
                    <td>
                        <b-select class="select is-fullwidth" v-model="form.crdStatCd">
                            <option
                                    v-for="item in crdStatCds"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </td>
                </tr>
                <tr>
                    <th class="tp-a">카드소유자</th>
                    <td colspan="4">
                        <div class="td-s-thumb search-area">
                            <input class="input input-bg" type="text" style="width:65px;" v-model="form.crdPssrId" disabled>

                            <div class="ip-box ip-box-w02" style="width: 120px;">
                                <input class="input" type="text" v-model="form.crdPssrNm" @input="initEmp" @keydown.enter="popEmp">
                                <button class="icon is-right" @click="popEmp(true)"><i class="fas fa-search"></i>
                                </button>
                            </div>
                            <div class="ip-box ip-box-w02">
                                <input class="input" type="text" style="width:80px;" v-model="form.crdPssrDut" disabled>
                                <input class="input" type="text" style="width:120px;" v-model="form.crdPssrDept" disabled>
                                <input class="input" type="text" style="width:150px;" v-model="form.crdPssrCompNm" disabled>
                            </div>
                        </div>
                    </td>

                    <th>카드용도</th>
                    <td>
                        <b-select class="select is-fullwidth" v-model="form.crdUsgCd">
                            <option
                                    v-for="item in crdUsgCds"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </td>
                </tr>
                <tr>
                    <th class="tp-a">발급일자</th>
                    <td colspan="2">
                        <div class="datepicker w-type-ymd">
                            <dhx-calendar class="input ddate sDate" v-model="form.crdPubcDt" />
                        </div>
                    </td>

                    <th>해지일자</th>
                    <td>
                        <div class="datepicker w-type-ymd">
                            <dhx-calendar class="input ddate sDate" v-model="form.crdAbltDt" />
                        </div>
                    </td>

                    <th class="tp-a">한도금액</th>
                    <td>
                        <input class="input Rt-M tar" type="text" v-model="form.crdPlmtAmt"/>
                    </td>
                </tr>
                <tr>
                    <th class="tp-a">유효기간</th>
                    <td colspan="2">
                        <div style="float: left">
                            <b-select class="select" v-model="form.crdVldYy">
                                <option value="">=년도=</option>
                                <option
                                        v-for="year in years"
                                        :value="year"
                                        v-text="year"/>
                            </b-select>
                        </div>
                        <span style="float: left; padding: 5px 3px;"></span>
                        <div style="float: left">
                            <b-select class="select" v-model="form.crdVldMm">
                                <option value=''>=월=</option>
                                <option
                                        v-for="item in 12"
                                        :key="item"
                                        :value="item"
                                        v-text="item"/>
                            </b-select>
                        </div>
                    </td>

                    <th>기존카드번호</th>
                    <td><input class="input" type="text" v-model="form.preCrdNo"></td>

                    <th>카드구분</th>
                    <td>
                        <div class="control">
                            <div class="dp-ib fl_left">
                                <input type="radio" id="radio01" v-model="form.crdFgCd" value="C"/>
                                <label for="radio01" class="NotoM">공용</label>
                            </div>
                            <div class="dp-ib fl_left">
                                <input type="radio" id="radio02" v-model="form.crdFgCd" value="P"/>
                                <label for="radio02" class="NotoM">개인</label>
                            </div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <th>사용자(대여)</th>
                    <td colspan="4">
                        <div class="td-s-thumb search-area" style="width: 200px">
                            <input class="input input-bg" type="text" style="width:65px;" v-model="form.crdUseId" disabled>
                            <div class="ip-box ip-box-w02">
                                <input class="input" type="text" v-model="form.crdUseNm" @input="initUseEmp" @keydown.enter="popUseEmp">
                                <button class="icon is-right" @click="popUseEmp(true)"><i class="fas fa-search"></i>
                                </button>
                            </div>
                        </div>
                    </td>

                    <th class="tp-a">결제 은행/일</th>
                    <td>
                        <div style="float: left">
                        <b-select class="select" v-model="form.bnkCd">
                            <option value=''>==선택==</option>
                            <option
                                    v-for="item in bnkCds"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                        </div>
                        <span style="float: left; padding: 5px 3px;"></span>
                        <div style="float: left">
                        <b-select class="select" v-model="form.stlDd">
                            <option value=''>==선택==</option>
                            <option
                                    v-for="item in 31"
                                    :key="item"
                                    :value="item"
                                    v-text="item"/>
                        </b-select>
                        </div>
                    </td>
                </tr>
                <tr>
                <tr>
                    <th>사용기간</th>
                    <td colspan="4">
                        <div class="datepicker w-type-ymd02" style="float: left;">
                            <dhx-calendar class="input ddate sDate" v-model="form.crdUseStrDt" />
                        </div>
                        <span style="float: left; padding: 5px 6px;">~</span>
                        <div class="datepicker w-type-ymd02" style="float: left;">
                            <dhx-calendar class="input ddate sDate" v-model="form.crdUseEndDt" />
                        </div>
                    </td>

                    <th>결제계좌</th>
                    <td><input class="input" type="text" v-model="form.stlBacctNo"></td>
                </tr>
                <tr>
                    <th> 적요</th>
                    <td colspan="4"><input class="input" type="text" v-model="form.crdOln"></td>
                    <th>거래처 코드/명</th>
                    <td>
                        <div class="td-s-thumb search-area">
                            <input class="input input-bg mr5 Rt-M rs-mt2" type="text" v-model="form.vendCd" style="width:66px;" disabled>
                            <div class="ip-box ip-box-w02 rs-mt2" @keydown.enter="popVendor1">
                                <input class="input" type="text" v-model="form.vendNm" @keyup.delete="initVendor1">
                                <button class="icon is-right" @click="popVendor1(true)"><i class="fas fa-search"></i></button>
                            </div>
                            <button class="remove_text trash-input rs-mb2" @click="initVendor1(true)"><i class="far fa-trash-alt"></i></button>
                        </div>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>

        <!--팝업-->
        <b-modal :active.sync="showEmpModal" has-modal-card @receive="receiveEmp">
            <emp :param="form.crdPssrNm"></emp>
        </b-modal>
        <b-modal :active.sync="showEmpModal1" has-modal-card @receive="receiveUseEmp">
            <emp :param="form.crdUseNm"></emp>
        </b-modal>
        <b-modal :active.sync="showVendorModal1" has-modal-card @receive="receiveVendor1">
            <vendor :param="form.vendNm" :slipTypeCd="slipTypeCd"></vendor>
        </b-modal>
        <!--//팝업 -->
    </div>

</template>

<script>
    /* eslint-disable */
    // import moment from 'moment'
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import moment from 'moment'
    import _ from 'lodash'
    import DhxCalendar from '@/components/DhxCalendar.vue'

    // PopUp
    import Emp from '@/components/Emp.vue';
    import Vendor from '@/components/Vendor.vue';

    const defaultParams = {
        crdNo : '',
        crdStatCd : 'Open',
        crdStatNm : '',
        crdUsgCd : 'HIP',
        crdUsgNm : '',
        crdFgCd : 'P',
        crdFgNm : '',
        crdPssrId : '',
        crdPssrNm : '',
        crdPssrDut : '',
        crdPssrDept : '',
        crdPssrCompNm : '',
        crdPssrCompCd : '',
        crdPubcDt : moment().format('YYYY-MM-DD'),
        crdVldYm : '',
        crdVldYy : '',
        crdVldMm : '',
        crdAbltDt : '',
        crdCuryCd : '',
        crdPlmtAmt : '',
        crdCompCd : 'BC',
        crdCompNm : '',
        bnkCd : '',
        stlBacctNo : '',
        stlDd : '',
        dpstrNm : '',
        preCrdNo : '',
        crdOln : '',
        delYn : '',
        vendCd : '',
        vendNm : '',
        bacctTctlYn : '',
        slipProcDeptCd : '',
        crdUseId : '',
        crdUseNm : '',
        crdUseStrDt : '',
        crdUseEndDt : '',
        crdNoHidden : ''
    }

    export default {
        name: 'CardInfo',
        props: ['cardDetail'],
        mixins: [mixin, mixinSlip],
        components: {Emp, Vendor, DhxCalendar},
        data() {
            return {
                title: '법인카드 정보',
                crdStatCds: [],
                crdCompCds: [],
                crdUsgCds: [],
                bnkCds: [],
                slipTypeCd: 'E3',
                form: {
                    //카드번호
                    crdNo: '',
                    //카드상태코드
                    crdStatCd: 'Open',
                    crdStatNm: '',
                    //카드용도코드
                    crdUsgCd: 'HIP',
                    crdUsgNm: '',
                    //카드구분코드
                    crdFgCd: 'P',
                    crdFgNm: '',
                    //카드소유주ID
                    crdPssrId: '',
                    crdPssrNm: '',
                    crdPssrDut: '',
                    crdPssrDept: '',
                    crdPssrCompNm: '',
                    crdPssrCompCd: '',
                    //카드발행(발급)일자
                    crdPubcDt: this.$moment().format('YYYY-MM-DD'),
                    //카드유효년월(기간)
                    crdVldYm: '',
                    crdVldYy: '',
                    crdVldMm: '',
                    //카드폐기(해지)일자
                    crdAbltDt: '',
                    //카드통화코드
                    crdCuryCd: '',
                    //카드한도금액
                    crdPlmtAmt: 0,
                    //카드회사코드
                    crdCompCd: 'BC',
                    crdCompNm: '',
                    //은행코드
                    bnkCd: '',
                    //카드결제계좌번호
                    stlBacctNo: '',
                    //카드결제일
                    stlDd: '',
                    //예금주명
                    dpstrNm: '',
                    //이전(기존)카드번호
                    preCrdNo: '',
                    //카드적요
                    crdOln: '',
                    //삭제여부
                    delYn: '',
                    //거래처코드
                    vendCd: '',
                    //거래처명
                    vendNm: '',
                    //계좌이관대상여부
                    bacctTctlYn: '',
                    //경비처리부서코드
                    slipProcDeptCd: '',
                    //카드사용자ID
                    crdUseId: '',
                    crdUseNm: '',
                    //카드사용시작일자
                    crdUseStrDt: '',
                    //카드사용종료일자
                    crdUseEndDt: '',
                    crdNoHidden: '',
                },
                showEmpModal: false,
                showEmpModal1: false,
                showVendorModal1: false,
            };
        },
        methods: {
            getCardCompCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "CRD_COMP_CD"}})
                    .then(response => {
                        this.crdCompCds = response.data;
                    });
            },
            getCardStatCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "CRD_STAT_CD"}})
                    .then(response => {
                        this.crdStatCds = response.data;
                    });
            },
            getCardUsgCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "CRD_USG_CD"}})
                    .then(response => {
                        this.crdUsgCds = response.data;
                    });
            },
            getBnkCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "BNK_CD"}})
                    .then(response => {
                        this.bnkCds = response.data;
                    });
            },
            popEmp(clear) {
                if (clear === true) {
                    this.form.crdPssrId = '';
                    this.form.crdPssrNm = '';
                    this.form.crdPssrDut = '';
                    this.form.crdPssrDept = '';
                    this.form.crdPssrCompNm = '';
                    this.form.crdPssrCompCd = '';
                }
                this.showEmpModal = true;
            },
            receiveEmp(obj) {
                this.form.crdPssrId = obj.empNo;
                this.form.crdPssrNm = obj.empNm;
                this.form.crdPssrDut = obj.dutNm;
                this.form.crdPssrDept = obj.deptNm;
                this.form.crdPssrCompNm = obj.compNm;
                this.form.crdPssrCompCd = obj.compCd;

            },
            initEmp(force) {
                if (force === true) this.form.crdPssrNm = '';
                if (this.form.crdPssrNm === '') {
                    this.form.crdPssrId = '';
                    this.form.crdPssrDut = '';
                    this.form.crdPssrDept = '';
                    this.form.crdPssrCompNm = '';
                    this.form.crdPssrCompCd = '';
                }
            },
            popUseEmp(clear) {
                if (clear === true) {
                    this.form.crdUseId = '';
                    this.form.crdUseNm = '';
                }
                this.showEmpModal1 = true;
            },
            receiveUseEmp(obj) {
                this.form.crdUseId = obj.empNo;
                this.form.crdUseNm = obj.empNm;
            },
            initUseEmp(force) {
                if (force === true) this.form.crdUseNm = '';
                if (this.form.crdUseNm === '') this.form.crdUseId = '';
            },
            popVendor1(clear) {
                if(clear===true) {
                    this.form.vendCd = '';
                    this.form.vendNm = '';
                }
                this.showVendorModal1 = true;
            },
            initVendor1(force) {
                if(force===true) this.form.vendNm = '';
                if(this.form.vendNm === '') {
                    this.form.vendCd = '';
                }
            },
            receiveVendor1(obj) {
                this.form.vendCd = obj.vendCd;
                this.form.vendNm = obj.vendNm;
            },
            validation() {
                const cardInfo = JSON.parse(JSON.stringify(this.form));
                const stripFields = ['crdNo','crdPubcDt','crdVldYm','crdAbltDt','crdPlmtAmt','stlBacctNo','preCrdNo','crdUseStrDt','crdUseEndDt'];
                _.forEach(stripFields, (name) => cardInfo[name] = this.toPure(cardInfo[name]));

                if (!cardInfo.crdNo) {
                    this.$swal({type: 'warning', text: '카드번호를 입력해 주세요.'});
                    return false;
                }
                if (cardInfo.crdNo.length!==16) {
                    this.$swal({type: 'warning', text: '카드번호 16자리 수를 채워주세요.'});
                    return false;
                }
                if (!cardInfo.crdPssrId) {
                    this.$swal({type: 'warning', text: '카드소유자를 선택해 주세요.'});
                    return false;
                }
                if (!cardInfo.crdPubcDt) {
                    this.$swal({type: 'warning', text: '발급일자를 입력해 주세요.'});
                    return false;
                }
                if (_.toInteger(cardInfo.crdPlmtAmt) === 0) {
                    this.$swal({type: 'warning', text: '한도금액을 입력해 주세요.'});
                    return false;
                }
                if (!cardInfo.crdVldYy) {
                    this.$swal({type: 'warning', text: '유효기간을 입력해 주세요.'});
                    return false;
                }
                if (!cardInfo.crdVldMm) {
                    this.$swal({type: 'warning', text: '유효기간을 입력해 주세요.'});
                    return false;
                }
                if (!cardInfo.bnkCd) {
                    this.$swal({type: 'warning', text: '결제은행을 선택해 주세요.'});
                    return false;
                }
                if (!cardInfo.stlDd) {
                    this.$swal({type: 'warning', text: '결제일을 선택해 주세요.'});
                    return false;
                }
                if (cardInfo.crdStatCd==='Close') {
                    if (!cardInfo.crdAbltDt) {
                        this.$swal({type: 'warning', text: '카드상태가 CLOSE입니다. 해지일자를 선택해 주세요.'});
                        return false;
                    }
                }
                return true;
            },
            newPage() {
                this.$swal({
                    type: 'warning',
                    text: `법인카드 정보 항목을 초기화합니다. 계속 하시겠습니까?`,
                    showCancelButton: true,
                    confirmButtonText: '예',
                    cancelButtonText: '아니오',
                }).then((result) => {
                    if (result.value) {
                        this.form = _.clone(defaultParams)
                    }
                });
            },
            newPageSkip() {
                this.form = _.clone(defaultParams)
            },
            setCardInfo() {
                Object.assign(this.form, this.cardDetail);
                // format date
                if (this.form.crdPubcDt) this.form.crdPubcDt = this.$moment(this.form.crdPubcDt).format('YYYY-MM-DD');
                if (this.form.crdAbltDt) this.form.crdAbltDt = this.$moment(this.form.crdAbltDt).format('YYYY-MM-DD');
                if (this.form.crdUseStrDt) this.form.crdUseStrDt = this.$moment(this.form.crdUseStrDt).format('YYYY-MM-DD');
                if (this.form.crdUseEndDt) this.form.crdUseEndDt = this.$moment(this.form.crdUseEndDt).format('YYYY-MM-DD');
                if (this.form.crdVldYm) this.form.crdVldYm = this.$moment(this.form.crdVldYm, 'YYYYMM').format('YYYY-MM');
                if (this.form.crdVldYm) this.form.crdVldYy = this.$moment(this.form.crdVldYm, 'YYYYMM').format('YYYY');
                if (this.form.crdVldYm) {
                    this.form.crdVldMm = this.toPure(this.$moment(this.form.crdVldYm, 'YYYYMM').format('MM'));
                    this.form.crdVldMm = this.form.crdVldMm.replace(/0/g, '');
                }
                if (this.form.crdNo) this.form.crdNo = this.getFormattedPureCardNumber(this.form.crdNo);
                if (this.form.preCrdNo) this.form.preCrdNo = this.getFormattedPureCardNumber(this.form.preCrdNo);

                this.form.crdNoHidden = this.form.crdNo;
            },
        },
        computed: {
            years () {
                const year = new Date().getFullYear();
                return Array.from({length: 30}, (value, index) => year + index);
            }
        },
        watch: {
            cardDetail() {
                this.setCardInfo();
            },
            'form.crdPlmtAmt'(value) {
                this.form.crdPlmtAmt = this.$filters.number(value);
            },
            'form.crdNo'() {
                let val = this.form.crdNo.replace(/-/g, '').replace(/[^0-9]/g,'');
                this.form.crdNo = val.replace(/(\d{4})(\d{4})(\d{4})(\d{4})/, '$1-$2-$3-$4');
            },
            'form.crdVldYy'() {
                let tempMm = this.form.crdVldMm;
                if(tempMm === 10 || tempMm === 11 || tempMm === 12) {
                    this.form.crdVldYm = this.form.crdVldYy.toString() + tempMm;
                } else {
                    tempMm = "0".toString()+tempMm.toString();
                    this.form.crdVldYm = this.form.crdVldYy.toString() + tempMm;
                }
            },
            'form.crdVldMm'() {
                let tempMm = this.form.crdVldMm;
                if(tempMm === 10 || tempMm === 11 || tempMm === 12) {
                    this.form.crdVldYm = this.form.crdVldYy.toString() + tempMm;
                } else {
                    tempMm = "0".toString()+tempMm.toString();
                    this.form.crdVldYm = this.form.crdVldYy.toString() + tempMm;
                }
            }
        },
        mounted() {
            this.getCardCompCdCombo();
            this.getCardStatCdCombo();
            this.getCardUsgCdCombo();
            this.getBnkCdCombo();
        },
    };
</script>


<style scoped>
    .td-s-thumb.search-area .ip-box.ip-box-w02 {
        width: 60%;
        margin-left: 6px;
    }
</style>