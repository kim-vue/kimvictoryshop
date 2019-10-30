<template>
    <div class="inner-box">
        <div class="content-name">
            <h2 class="dp-ib">{{title}}</h2>
            <div class="btn-wrap btn-type1 clearfix">
                <button class="btn-size btn-blue fl_left" @click="goSearch"><span class="btn-icon"><i
                        class="fas fa-pen-alt"></i></span> 조회
                </button>
            </div>
        </div>

        <!-- 검색조건 영역 -->
        <div class="desc-content search-border">
            <div class="item desc-left">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 회계일자</span>
                    </div>
                    <div class="desc">
                        <div class="datepicker w-type-ymd02">
                            <dhx-calendar class="input ddate sDate" v-model="form.postDtFrom" />
                        </div>
                        <span class="wave"> ~ </span>
                        <div class="datepicker w-type-ymd02">
                            <dhx-calendar class="input ddate sDate" v-model="form.postDtTo" />
                        </div>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 증빙일자</span>
                    </div>
                    <div class="desc">
                        <div class="datepicker w-type-ymd02">
                            <dhx-calendar class="input ddate sDate" v-model="form.evdDtFrom" />
                        </div>
                        <span class="wave"> ~ </span>
                        <div class="datepicker w-type-ymd02">
                            <dhx-calendar class="input ddate sDate" v-model="form.evdDtTo" />
                        </div>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 작성부서</span>
                    </div>
                    <div v-if="authority==='ADMIN'" class="desc">
                        <div class="td-s-thumb search-area" style="width: 350px">
                            <input class="input input-bg" type="text" style="width:100px;" v-model="form.wrtDeptCd">
                            <div class="ip-box ip-box-w02">
                                <input class="input" type="text" v-model="form.wrtDeptNm" @input="initCctr" @keydown.enter="popCctr">
                                <button class="icon is-right" @click="popCctr(true)"><i class="fas fa-search"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    <div v-else class="desc">
                        <div class="td-s-thumb search-area" style="width: 350px">
                            <input class="input input-bg" type="text" style="width:100px;" v-model="form.wrtDeptCd" disabled>
                            <div class="ip-box ip-box-w02">
                                <input class="input" type="text" v-model="form.wrtDeptNm" @input="initCctr" @keydown.enter="popCctr" disabled>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 전표번호</span>
                    </div>
                    <div class="desc">
                        <input class="input Rt-M tal" type="text" v-model="form.eaSlipNo">
                    </div>
                </div>
            </div>
            <div class="item desc-center">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 전표유형</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.slipTypeCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in slipTypes"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 거래처</span>
                    </div>
                    <div class="desc">
                        <input class="input Rt-M tal" type="text" v-model="form.evdCustNm">
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 작성자</span>
                    </div>
                    <div class="desc">
                        <div class="td-s-thumb search-area" style="width: 450px">
                            <input class="input input-bg" type="text" style="width:65px;" v-model="form.wrtId" disabled>
                            <div v-if="authority==='ADMIN'" class="ip-box ip-box-w02" style="width:120px;">
                                <input class="input" type="text" v-model="form.wrtNm" @input="initEmp" @keydown.enter="popEmp">
                                <button class="icon is-right" @click="popEmp(true)"><i class="fas fa-search"></i>
                                </button>
                            </div>
                            <div v-else class="ip-box ip-box-w02" style="width:120px;">
                                <input class="input" type="text" v-model="form.wrtNm" @input="initEmp" @keydown.enter="popEmp" disabled>
                            </div>
                            <div class="ip-box ip-box-w02" style="width:200px;">
                                <input class="input input-bg" type="text" style="width:80px;" v-model="form.wrtUserDut" disabled>
                                <input class="input input-bg" type="text" style="width:120px;" v-model="form.wrtUserDept" disabled>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- ERP전표번호</span>
                    </div>
                    <div class="desc">
                        <input class="input Rt-M tal" type="text" v-model="form.erpSlipNo">
                    </div>
                </div>
            </div>
            <div class="item desc-right">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 전표상태</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.slipStatCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in slipStats"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 지급처</span>
                    </div>
                    <div class="desc">
                        <input class="input Rt-M tal" type="text" v-model="form.payCustNm">
                    </div>
                </div>
            </div>
        </div>
        <!-- //검색조건 영역 -->

        <!-- 테이블 -->
        <div class="table-area">

            <div class="table-b">
                <div class="table-header">
                    <div class="table-name">
                        <h3 class="ico_table_name">전표내역</h3>
                    </div>
                    <div class="btn-wrap btn-type1 clearfix">
                        <button class="btn-size btn-excel" @click="saveExcel">엑셀 저장</button>
                    </div>
                </div>

                <div class="grid-wrap">
                    <dhx-grid ref="grid" v-model="slipList" :config="config" @constructGridSuccessful="constructGridSuccessful"/>
                </div>
            </div>

        </div>
        <!-- //테이블 -->

        <!--팝업-->
        <b-modal :active.sync="showCctrModal" has-modal-card @receive="receiveCctr">
            <cctr :param="form.wrtDeptNm"></cctr>
        </b-modal>
        <b-modal :active.sync="showEmpModal" has-modal-card @receive="receiveEmp">
            <emp :param="form.wrtNm"></emp>
        </b-modal>
        <!--//팝업 -->
    </div>
</template>

<script>
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import _ from 'lodash'

    import DhxCalendar from '@/components/DhxCalendar.vue'
    import DhxGrid from '@/components/DhxGrid.vue'
    import Cctr from '@/components/Cctr.vue';
    import Emp from '@/components/Emp.vue';

    export default {
        name: 'SlipList',
        mixins: [mixin, mixinSlip],
        components: {Cctr, Emp, DhxGrid, DhxCalendar},
        data() {
            return {
                config: {
                    columns: [
                        {id: 'no', type: 'cntr', align: 'center', sort: 'na', value: 'No.', width: 35},
                        {id: 'eaSlipNo', type: 'ro', align: 'center', sort: 'na', value: '전표번호', width: 120},
                        {id: 'slipStatNm', type: 'ro', align: 'center', sort: 'na', value: '전표상태', width: 70},
                        {id: 'slipTypeNm', type: 'ro', align: 'center', sort: 'na', value: '전표유형', width: 100},
                        {id: 'postDt', type: 'ro', align: 'center', sort: 'na', value: '회계일자', width: 90},
                        {id: 'evdDt', type: 'ro', align: 'center', sort: 'na', value: '증빙일자', width: 90},
                        {id: 'supAmt', type: 'ron', align: 'right', sort: 'na', value: '공급가', width: 120},
                        {id: 'vatAmt', type: 'ron', align: 'right', sort: 'na', value: '부가세액', width: 100},
                        {id: 'totAmt', type: 'ron', align: 'right', sort: 'na', value: '총금액', width: 120},
                        {id: 'stnAcctCd', type: 'ro', align: 'center', sort: 'na', value: '계정코드', width: 80},
                        {id: 'stnAcctNm', type: 'ro', align: 'center', sort: 'na', value: '계정명', width: 120},
                        {id: 'expItemCnt', type: 'ro', align: 'center', sort: 'na', value: '계정라인', width: 60},
                        {id: 'erpSlipNo', type: 'ro', align: 'center', sort: 'na', value: 'ERP전표번호', width: 120},
                        {id: 'evdCustCd', type: 'ro', align: 'center', sort: 'na', value: '거래처코드', width: 80},
                        {id: 'evdCustNm', type: 'ro', align: 'center', sort: 'na', value: '거래처명', width: 100},
                        {id: 'payCustCd', type: 'ro', align: 'center', sort: 'na', value: '지급처코드', width: 80},
                        {id: 'payCustNm', type: 'ro', align: 'center', sort: 'na', value: '지급처명', width: 100},
                        {id: 'wrtDeptNm', type: 'ro', align: 'center', sort: 'na', value: '작성부서명', width: 100},
                        {id: 'wrtNm', type: 'ro', align: 'center', sort: 'na', value: '작성자', width: 60},
                        {id: 'hdSgtxt', type: 'ro', align: 'center', sort: 'na', value: '전표내용', width: 200},
                        {id: 'merchNm', type: 'ro', align: 'center', sort: 'na', value: '가맹점명', width: 140},
                        {id: 'merchAddr', type: 'ro', align: 'center', sort: 'na', value: '가맹점 주소', width: 200},
                        {id: 'mccName', type: 'ro', align: 'center', sort: 'na', value: '업종명', width: 120},
                        {id: 'apprDate', type: 'ro', align: 'center', sort: 'na', value: '승인일자', width: 100},
                        {id: 'apprTime', type: 'ro', align: 'center', sort: 'na', value: '승인시각', width: 100},
                        {id: 'slipStatCd', type: 'ro', align: 'center', sort: 'na', value: '', hidden: true},
                        {id: 'slipTypeCd', type: 'ro', align: 'center', sort: 'na', value: '', hidden: true},
                    ],
                    height: '425',
                    enablePaging: true,
                    pagingSize: 10
                },
                title: '전표처리내역',
                slipTypes: [],
                slipStats: [],
                slipList: [],
                authority: '',
                form: {
                    postDtFrom: this.$moment().add(-1, 'month').startOf('month').format('YYYY-MM-DD'),
                    postDtTo: this.$moment().format('YYYY-MM-DD'),
                    evdDtFrom: this.$moment().add(-1, 'month').startOf('month').format('YYYY-MM-DD'),
                    evdDtTo: this.$moment().format('YYYY-MM-DD'),
                    eaSlipNo: '',
                    slipTypeCd: '',
                    evdCustNm: '',
                    wrtId: '',
                    wrtNm: '',
                    wrtUserDut: '',
                    wrtUserDept: '',
                    wrtDeptCd: '',
                    wrtDeptNm: '',
                    slipStatCd: '',
                    payCustNm: '',
                },
                showCctrModal: false,
                showEmpModal: false,
            };
        },
        methods: {
            constructGridSuccessful(grid) {
                this.config.queryPage(0)
                grid.setColumnHidden(25,true)
                grid.setColumnHidden(26,true)
                grid.setNumberFormat('0,000', 6, '.', ',')
                grid.setNumberFormat('0,000', 7, '.', ',')
                grid.setNumberFormat('0,000', 8, '.', ',')

                grid.attachEvent('onRowDblClicked', (rId) => {
                    let eaSlipNo = grid.cells(rId, 1).getValue();
                    let slipStatCd = grid.cells(rId, 25).getValue();
                    let slipTypeCd = grid.cells(rId, 26).getValue();
                    this.goPage({eaSlipNo, slipStatCd, slipTypeCd});
                });
            },
            getSlipTypeCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "SLIP_TYPE_CD"}})
                    .then(response => {
                        this.slipTypes = response.data;
                    });
            },
            getSlipStatCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "SLIP_STAT_CD"}})
                    .then(response => {
                        this.slipStats = response.data;
                    });
            },
            saveExcel() {
                this.downloadExcel(this.$refs.grid);
            },
            goPage(params) {
                //this.$router.push({path: `/billSlipMng/${params.eaSlipNo}`});


                switch (params.slipTypeCd) {
                    case 'E1':
                        if(params.slipStatCd==='10')
                            this.$router.push({
                                name: 'cardSlipReg',
                                params
                            })
                        else
                            this.$router.push({
                                name: 'billSlipMng',
                                params
                            })
                        break
                    case 'E2':
                        if(params.slipStatCd==='10')
                            this.$router.push({
                                name: 'ebillSlipReg',
                                params
                            })
                        else
                            this.$router.push({
                                name: 'billSlipMng',
                                params
                            })
                        break
                    case 'E3':
                        if(params.slipStatCd==='10')
                            this.$router.push({
                                name: 'billSlipReg',
                                params
                            })
                        else
                            this.$router.push({
                                name: 'billSlipMng',
                                params
                            })
                        break
                    case 'E4':
                        this.$router.push({
                            name: 'evidSlipEdit',
                            params
                        })
                        break
                    case 'E6':
                        this.$router.push({
                            name: 'whtSlipEdit',
                            params
                        })
                        break
                    default :
                        break
                }

            },
            goSearch() {
                console.log("조회...")
                const param = JSON.parse(JSON.stringify(this.form));
                const stripFields = ['postDtFrom', 'postDtTo', 'evdDtFrom', 'evdDtTo'];
                _.forEach(stripFields, (name) => param[name] = this.toPure(param[name]));

                if (!this.validation(param)) return;

                this.$store.commit('loading');
                this.$http.post(`/api/slip/history`, param)
                    .then(response => {
                        if (response.data) {
                            this.slipList = response.data;
                            this.config.queryPage(0)
                        }
                    });
            },
            validation(param) {
                if (!param.postDtFrom || !param.postDtTo) {
                    this.$swal({type: 'warning', text: '회계일자를 입력해 주세요.'});
                    return false;
                }
                return true;
            },
            popCctr(clear) {
                if (clear === true) {
                    this.form.wrtDeptCd = '';
                    this.form.wrtDeptNm = '';
                }
                this.showCctrModal = true;
            },
            popEmp(clear) {
                if (clear === true) {
                    this.form.wrtId = '';
                    this.form.wrtNm = '';
                    this.form.wrtUserDut = '';
                    this.form.wrtUserDept = '';
                }
                this.showEmpModal = true;
            },
            receiveCctr(obj) {
                this.form.wrtDeptCd = obj.cctrCd;
                this.form.wrtDeptNm = obj.cctrNm;
            },
            receiveEmp(obj) {
                this.form.wrtId = obj.empNo;
                this.form.wrtNm = obj.empNm;
                this.form.wrtUserDut = obj.dutNm;
                this.form.wrtUserDept = obj.deptNm;
            },
            initCctr(force) {
                if (force === true) this.form.wrtDeptNm = '';
                if (this.form.wrtDeptNm === '') this.form.wrtDeptCd = '';
            },
            initEmp(force) {
                if (force === true) this.form.wrtNm = '';
                if (this.form.wrtNm === '') {
                    this.form.wrtId = '';
                    this.form.wrtUserDut = '';
                    this.form.wrtUserDept = '';
                }
            },
            setCallPageByParam(){
                if (this.$route.query) {
                    for (let member in this.form) {
                        if (this.$route.query[member] !== undefined) {
                            this.form[member] = this.$route.query[member]
                        }
                    }
                }
            }
        },
        mounted() {
            this.authority = this.$store.state.loginInfo.authorities[0].roleCd;
            console.log(JSON.stringify(this.$store.state.loginInfo.authorities))
            this.form.wrtDeptCd = this.$store.state.loginInfo.loginDeptCd;
            this.form.wrtDeptNm = this.$store.state.loginInfo.loginDeptNm;


            this.form.wrtId = this.$store.state.loginInfo.loginId;
            this.form.wrtNm = this.$store.state.loginInfo.userName;
            this.form.wrtUserDut = this.$store.state.loginInfo.loginDutNm;
            this.form.wrtUserDept = this.$store.state.loginInfo.loginDeptNm;

            this.setCallPageByParam()
            this.getSlipTypeCombo()
            this.getSlipStatCombo()
            this.goSearch()
        }
    };
</script>

<style scoped>
    .desc-content:after {
        clear: both;
        content: '';
        display: block;
    }

    .btn-wrap {
        margin-bottom: 20px;
    }

    .desc-content {
        border: 2px solid #9db6c9;
        background: #f9fafc;
        margin: 0 0 20px 0;
        border-radius: 4px;
        padding: 15px 2%;
        clear: both;
    }

    .desc-content .item {
        float: left;
    }

    .desc-content .item .desc-item {
        position: relative;
        padding-left: 82px;
        margin-bottom: 8px;
    }

    .desc-content .item .desc-item:last-child {
        margin-bottom: 0;
        height: 25px;
    }

    .desc-content .item .desc-item .tit {
        position: absolute;
        left: 0;
    }

    .desc-content .item .desc-item .label-tit {
        font-family: 'NotoM';
        color: #222;
        font-size: 15px;
    }

    .desc-content .item.desc-left .desc-item {
        padding-left: 90px;
    }

    .desc-content .item.desc-left .desc-item .desc:after {
        clear: both;
        content: '';
        display: block;
    }

    .desc-content .item.desc-left .desc-item .desc .datepicker {
        float: left;
    }

    .desc-content .item.desc-left .desc-item .desc span.wave {
        float: left;
        padding: 0 6px;
    }

    .desc-content .item.desc-left .desc-item .td-s-thumb.search-area:after {
        clear: both;
        content: '';
        display: block;
    }

    .desc-content .item.desc-left .desc-item .td-s-thumb.search-area input,
    .desc-content .item.desc-left .desc-item .td-s-thumb.search-area .ip-box {
        float: left;
    }

    .desc-content .item.desc-left .desc-item .desc.select select {
        width: 70%;
    }

    .desc-content .item.desc-left {
        width: 35%;
        padding-right: 40px;
    }

    .desc-content .item.desc-center {
        width: 35%;
        padding-right: 40px;
    }

    .desc-content .item.desc-right {
        width: 30%;
    }

    .search-area input {
        position: relative;
    }

    .search-area .icon {
        position: absolute;
        right: 8px;
        top: 1px;
        z-index: 100;
        cursor: pointer;
        font-size: 16px;
        color: #555;
    }

    .search-border .td-s-thumb {
        position: relative;
        display: inline-block;
    }

    .search-border .td-s-thumb.search-area > input,
    .search-border .td-s-thumb.search-area > .ip-box
    .search-border .td-s-thumb.search-area > button {
        float: left;
    }

    .search-border .td-s-thumb.search-area .ip-box.ip-box-w02 {
        width: 60%;
        margin-left: 6px;
    }

    .search-border .td-s-thumb.search-area .ip-box {
        vertical-align: top;
    }

    @media (max-width: 1580px) {
        .search-border .td-s-thumb.search-area .ip-box.ip-box-w02 {
            width: 50%;
        }
    }
</style>
