<template>
    <div class="inner-box">
        <div class="content-name">
            <h2 class="dp-ib">{{title}}</h2>
            <div class="btn-wrap btn-type1 clearfix">
                <button class="btn-size btn-blue fl_left" @click="goSearch"><span class="btn-icon"><i class="fas fa-pen-alt"></i></span> 조회</button>
            </div>
        </div>

        <!-- 검색조건 영역 -->
        <div class="desc-content search-border">
            <div class="item desc-left">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 결제연월</span>
                    </div>
                    <div class="desc">
                        <div class="datepicker w-type-ymd02">
                            <input type="text" class="input date sDate" id="reqYm" v-model="form.reqYm" readonly/>
                        </div>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 사용일자</span>
                    </div>
                    <div class="desc">
                        <div class="datepicker w-type-ymd02">
                            <input type="text" class="input date sDate" id="searchDtmFr" v-model="form.searchDtmFr" readonly/>
                        </div>
                        <span class="wave"> ~ </span>
                        <div class="datepicker w-type-ymd02">
                            <input type="text" class="input date sDate" id="searchDtmTo" v-model="form.searchDtmTo" readonly/>
                        </div>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 카드소유자</span>
                    </div>
                    <div class="desc">
                        <div class="td-s-thumb search-area" style="width: 410px;">
                            <input class="input input-bg" type="text" style="width:65px;" v-model="form.crdPssrId" disabled>
                            <div class="ip-box ip-box-w02" style="width:120px;">
                                <input class="input" type="text" v-model="form.crdPssrNm" @input="initEmp" @keydown.enter="popEmp">
                                <button class="icon is-right" @click="popEmp(true)"><i class="fas fa-search"></i>
                                </button>
                            </div>
                            <div class="ip-box ip-box-w02" style="width:200px;">
                                <input class="input input-bg" type="text" style="width:80px;" v-model="form.crdPssrDut" disabled>
                                <input class="input input-bg" type="text" style="width:120px;" v-model="form.crdPssrDept" disabled>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="item desc-center">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 회사</span>
                    </div>
                    <div v-if="authority==='ADMIN'" class="desc">
                        <b-select class="select is-fullwidth" v-model="form.compCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in compCds"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </div>
                    <div v-else class="desc">
                        <b-select class="select is-fullwidth" v-model="form.compCd" disabled>
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in compCds"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 대사상태</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.recncPrgsCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in recncPrgsCds"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 카드사</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.crdCompCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in crdCompCds"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </div>
                </div>
            </div>
            <div class="item desc-right">
                <div class="desc-item" style="height: 25px">
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 카드번호</span>
                    </div>
                    <div class="desc">
                        <input class="input Rt-M tal" type="text" v-model="form.crdNo">
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 카드구분</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.crdFgCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in crdFgCds"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
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
                        <h3 class="ico_table_name">법인카드 사용내역</h3>
                    </div>
                    <div class="btn-wrap btn-type1 clearfix">
                        <button class="btn-size btn-excel" @click="saveExcel">엑셀 저장</button>
                    </div>
                </div>

                <div class="grid-wrap">
                    <dhx-grid class="slip-grid" ref="grid" v-model="invDetails" :config="config" @constructGridSuccessful="constructGridSuccessful"/>
                </div>
            </div>
        </div>
        <!-- //테이블 -->

        <!--팝업-->
        <b-modal :active.sync="showEmpModal" has-modal-card @receive="receiveEmp">
            <emp :param="form.crdPssrNm"></emp>
        </b-modal>
        <!--//팝업 -->
    </div>
</template>

<script>
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import _ from 'lodash'
    import DhxGrid from '@/components/DhxGrid.vue'
    import Emp from '@/components/Emp.vue';

    export default {
        name: 'CardUseLst',
        mixins: [mixin, mixinSlip],
        components: {Emp, DhxGrid},
        data() {
            return {
                config : {
                    columns: [
                        {id: 'rn', type: 'cntr', align: 'center', sort: 'na', value: 'No.', width: 35},
                        {id: 'cardNo', type: 'ro', align: 'center', sort: 'na', value: '카드번호', width: 170},
                        {id: 'crdCompNm', type: 'ro', align: 'center', sort: 'na', value: '카드사', width: 150},
                        {id: 'crdFgNm', type: 'ro', align: 'center', sort: 'na', value: '카드구분', width: 100},
                        {id: 'apprNo', type: 'ro', align: 'center', sort: 'na', value: '승인번호', width: 120},
                        {id: 'billTypeNm', type: 'ro', align: 'center', sort: 'na', value: '청구구분', width: 100},
                        {id: 'originApprDate', type: 'ro', align: 'center', sort: 'na', value: '사용일자', width: 120},
                        {id: 'billTot', type: 'ron', align: 'right', sort: 'na', value: '사용금액', width: 150},
                        {id: 'merchName', type: 'ro', align: 'center', sort: 'na', value: '가맹점명', width: 200},
                        {id: 'taxTypeNm ', type: 'ro', align: 'center', sort: 'na', value: '과세구분', width: 100},
                        {id: 'reqNm', type: 'ro', align: 'center', sort: 'na', value: '결제년월', width: 120},
                        {id: 'recncPrgsNm', type: 'ro', align: 'center', sort: 'na', value: '대사상태', width: 100},
                        {id: 'crdPssrNm', type: 'ro', align: 'center', sort: 'na', value: '카드사용자', width: 100},
                        {id: 'crdPssrDutNm', type: 'ro', align: 'center', sort: 'na', value: '직급', width: 100},
                        {id: 'crdPssrDeptNm', type: 'ro', align: 'center', sort: 'na', value: '부서명', width: 150},
                        {id: 'erpSlipDtm', type: 'ro', align: 'right', sort: 'na', value: '전송일시', width: 150},
                    ],
                    height: 380,
                    enablePaging: true,
                    pagingSize: 8,
                    queryPage: (page) => {
                        page = page || 0
                        return new Promise((resolve, reject) => {
                            let data = {
                                contents: this.invDetails,
                                page: page,
                                totalPages: parseInt(this.invDetails.length / this.config.pagingSize) + (parseInt(this.invDetails.length % this.config.pagingSize) > 0 ? 1 : 0),
                                totalElements: 0
                            }
                            resolve({
                                data: data
                            })
                        })
                    },
                    afterRefreshData(grid, data) {
                        this.$nextTick(() => {
                            _.forEach(data, (item, index) => {
                                var rId = index + 1
                                grid.cells(rId, 1).setValue(this.$parent.getFormattedCardNumber(grid.cells(rId, 1).getValue()));
                                grid.cells(rId, 6).setValue(this.$moment(grid.cells(rId, 6).getValue()).format('YYYY-MM-DD'));
                                if(grid.cells(rId, 10).getValue()) grid.cells(rId, 10).setValue(this.$moment(grid.cells(rId, 10).getValue(), 'YYYYMM').format('YYYY-MM'));
                            })
                        })
                    }
                },
                title: '법인카드 청구현황',
                compCds: [],
                crdCompCds: [],
                recncPrgsCds: [],
                crdFgCds: [],
                invDetails: [],
                form: {
                    compCd: '',
                    crdCompCd: '',
                    recncPrgsCd: '',
                    crdFgCd: '',
                    crdNo: '',
                    crdPssrId: '',
                    crdPssrNm: '',
                    crdPssrTitle: '',
                    crdPssrDut: '',
                    crdPssrDept: '',
                    reqYm: this.$moment().format('YYYY-MM'),
                    searchDtmFr: this.$moment().add(-1, 'month').startOf('month').format('YYYY-MM-DD'),
                    searchDtmTo: this.$moment().format('YYYY-MM-DD'),
                },
                showEmpModal: false,
                authority: '',
            }
        },
        methods: {
            constructGridSuccessful(grid) {
                this.config.queryPage(0)
                var header_style = 'color:#222;text-align:center;'
                var stat_total_text = 'color:red;text-align:right;padding-right:10px !important;'

                grid.attachHeader(
                    ['합계', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#stat_total','', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan'],
                    [header_style, '', '', '', '', '', '', stat_total_text]
                )
                grid.setNumberFormat('0,000', 7, '.', ',')
            },
            getCompCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "COMP_CD"}})
                    .then(response => {
                        this.compCds = response.data
                    })
            },
            getCardCompCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "CRD_COMP_CD"}})
                    .then(response => {
                        this.crdCompCds = response.data
                    })
            },
            getRecncPrgsCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "RECNC_PRGS_CD"}})
                    .then(response => {
                        this.recncPrgsCds = response.data
                    })
            },
            getCardFgCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "CRD_FG_CD"}})
                    .then(response => {
                        this.crdFgCds = response.data
                    })
            },
            saveExcel() {
                this.downloadExcel(this.$refs.grid)
            },
            calendarLoad() {
                const iljinCalendar1 = new dhtmlXCalendarObject('searchDtmFr')
                iljinCalendar1.hideTime()
                iljinCalendar1.setPosition('bottom')
                iljinCalendar1.setDate(new Date())
                iljinCalendar1.attachEvent('onChange', (v) => {
                    this.form.searchDtmFr = this.$refs.searchDtmFr.getFormatedDate()
                })
                iljinCalendar1.attachEvent("onButtonClick", (d) => {
                    if (d === null) {
                        this.form.searchDtmFr = this.$refs.searchDtmFr.getFormatedDate()
                    }
                })
                this.$refs.searchDtmFr = iljinCalendar1

                const iljinCalendar2 = new dhtmlXCalendarObject('searchDtmTo')
                iljinCalendar2.hideTime()
                iljinCalendar2.setPosition('bottom')
                iljinCalendar2.setDate(new Date())
                iljinCalendar2.attachEvent('onChange', (v) => {
                    this.form.searchDtmTo = this.$refs.searchDtmTo.getFormatedDate()
                })
                iljinCalendar2.attachEvent("onButtonClick", (d) => {
                    if (d === null) {
                        this.form.searchDtmTo = this.$refs.searchDtmTo.getFormatedDate()
                    }
                })
                this.$refs.searchDtmTo = iljinCalendar2


                const iljinCalendar3 = new dhtmlXCalendarObject('reqYm')
                iljinCalendar3.hideTime()
                iljinCalendar3.setPosition('bottom')
                iljinCalendar3.setDate(new Date())
                iljinCalendar3.setDateFormat('%Y-%m')
                iljinCalendar3.attachEvent('onChange', (v) => {
                    this.form.reqYm = this.$refs.reqYm.getFormatedDate()
                })
                iljinCalendar3.attachEvent("onButtonClick", (d) => {
                    if (d === null) {
                        this.form.reqYm = this.$refs.reqYm.getFormatedDate()
                    }
                })
                this.$refs.reqYm = iljinCalendar3
            },
            goSearch() {
                const param = JSON.parse(JSON.stringify(this.form))
                const stripFields = ['searchDtmFr', 'searchDtmTo','crdNo','reqYm']
                _.forEach(stripFields, (name) => param[name] = this.toPure(param[name]))

                this.$store.commit('loading')
                this.$http.post(`/api/card/billReq/list`, {
                        reqYm: this.$moment(param.reqYm, 'YYYYMM').format('YYYYMM'),
                        compCd: param.compCd,
                        searchDtmFr: param.searchDtmFr,
                        searchDtmTo: param.searchDtmTo,
                        recncPrgsCd: param.recncPrgsCd,
                        cardNo: param.crdNo,
                        crdPssrId: param.crdPssrId,
                        crdCompCd: param.crdCompCd,
                        crdFgCd: param.crdFgCd
                    }
                )
                    .then(response => {
                        if (response.data) {
                            this.invDetails = response.data
                            this.config.queryPage(0)
                        }
                    })
            },
            popEmp(clear) {
                if (clear === true) {
                    this.form.crdPssrId = ''
                    this.form.crdPssrNm = ''
                    this.form.crdPssrDut = ''
                    this.form.crdPssrDept = ''
                }
                this.showEmpModal = true
            },
            receiveEmp(obj) {
                this.form.crdPssrId = obj.empNo
                this.form.crdPssrNm = obj.empNm
                this.form.crdPssrDut = obj.dutNm
                this.form.crdPssrDept = obj.deptNm
            },
            initEmp(force) {
                if (force === true) this.form.crdPssrNm = ''
                if (this.form.crdPssrNm === '') {
                    this.form.crdPssrId = ''
                    this.form.crdPssrDut = ''
                    this.form.crdPssrDept = ''
                }
            },
        },
        mounted() {
            this.form.compCd = this.$store.state.loginInfo.compCd
            this.authority = this.$store.state.loginInfo.authorities[0].roleCd
            this.calendarLoad()
            this.getCompCdCombo()
            this.getCardCompCdCombo()
            this.getRecncPrgsCdCombo()
            this.getCardFgCdCombo()
            this.goSearch()
        }
    }
</script>

<style scoped>
    .gridbox {
        height: 390px !important;
    }

    .gridbox .objbox {
        height: 350px !important;
    }

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

    .remove_text {
        margin-left: 0;
    }

    .contents div.gridbox_material.gridbox .xhdr {
        border-bottom: 1px solid #dfdfdf;
    }

    @media (max-width: 1580px) {
        .search-border .td-s-thumb.search-area .ip-box.ip-box-w02 {
            width: 50%;
        }
    }
</style>

<style lang="scss" scoped>
    .slip-grid {
        :global(.xhdr table tbody tr:last-child) {
            background-color: #f9f9f3;
        }

        :global(.xhdr table tbody tr:last-child td) {
            background-color: transparent !important;
        }

        :global(.xhdr table tbody tr:last-child td div) {
            background-color: transparent !important;
            color: inherit !important;
            text-align: inherit !important;
        }
    }
</style>
