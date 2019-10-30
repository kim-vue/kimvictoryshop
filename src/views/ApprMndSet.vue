<template>
    <div class="inner-box">
        <div class="content-name">
            <h2 class="dp-ib">{{title}}</h2>
            <div class="btn-wrap btn-type1 clearfix">
                <button class="btn-size btn-blue fl_left" @click="goSearch"><span class="btn-icon"><i
                        class="fas fa-pen-alt"></i></span> 조회
                </button>
                <button class="btn-size btn-gray fl_left" @click="popVendor(true)"><span class="btn-icon"><i
                        class="far fa-file"></i></span> 신규
                </button>
            </div>
        </div>

        <!-- 검색조건 영역 -->
        <div class="desc-content search-border">
            <div class="item desc-left">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 회사</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.compCd">
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
                        <span class="label-tit">- 위임자</span>
                    </div>
                    <div class="desc">
                        <div class="td-s-thumb search-area">
                            <input class="input input-bg" type="text" style="width:65px;" v-model="form.searchAdlgId"
                                   disabled>
                            <div class="ip-box ip-box-w02">
                                <input class="input" type="text" v-model="form.searchAdlgNm" @input="initSearchAdlgId"
                                       @keydown.enter="popSearchAdlgEmp">
                                <button class="icon is-right" @click="popSearchAdlgEmp(true)"><i
                                        class="fas fa-search"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="item desc-left">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 위임일자</span>
                    </div>
                    <div class="desc">
                        <div class="datepicker w-type-ymd02">
                            <dhx-calendar class="input ddate sDate" v-model="form.searchDtmFr" />
                        </div>
                        <span class="wave"> ~ </span>
                        <div class="datepicker w-type-ymd02">
                            <dhx-calendar class="input ddate sDate" v-model="form.searchDtmTo" />
                        </div>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 수임자</span>
                    </div>
                    <div class="desc">
                        <div class="td-s-thumb search-area">
                            <input class="input input-bg" type="text" style="width:65px;" v-model="form.searchActId"
                                   disabled>
                            <div class="ip-box ip-box-w02">
                                <input class="input" type="text" v-model="form.searchActNm" @input="initSearchActId"
                                       @keydown.enter="popSearchActEmp">
                                <button class="icon is-right" @click="popSearchActEmp(true)"><i
                                        class="fas fa-search"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="item desc-right">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 위임상태</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.adlgStatCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in adlgCds"
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
                        <h3 class="ico_table_name">결재 위임현황</h3>
                    </div>
                    <div class="btn-wrap btn-type1 clearfix">
                        <button class="btn-size btn-excel" @click="saveExcel">엑셀 저장</button>
                    </div>
                </div>

                <div class="grid-wrap">
                    <dhx-grid ref="grid" v-model="mndList" :config="config" @constructGridSuccessful="constructGridSuccessful"/>
                </div>
            </div>

        </div>
        <!-- //테이블 -->

        <!--팝업-->
        <b-modal :active.sync="showEmpModal" has-modal-card @receive="receiveSearchAdlgEmp">
            <emp :param="form.searchAdlgNm"></emp>
        </b-modal>
        <b-modal :active.sync="showEmpModal2" has-modal-card @receive="receiveSearchActEmp">
            <emp :param="form.searchActNm"></emp>
        </b-modal>

        <b-modal :active.sync="showVendorModal1" has-modal-card @receive="receiveMndPop">
            <appr-mnd-pop :adlgId="hiddenAdlgId"
                          :adlgNm="hiddenAdlgNm"
                          :actId="hiddenActId"
                          :actNm="hiddenActNm"
                          :adlgSeq="hiddenAdlgSeq"
                          :hiddenDtmFr="hiddenDtmFr"
                          :hiddenDtmTo="hiddenDtmTo"
                          :hiddenCheck="hiddenCheck">
            </appr-mnd-pop>
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
    import Emp from '@/components/Emp.vue';
    import ApprMndPop from '@/components/ApprMndPop.vue';

    export default {
        name: 'ApprMndSet',
        mixins: [mixin, mixinSlip],
        components: {Emp, ApprMndPop, DhxGrid, DhxCalendar},
        data() {
            return {
                config : {
                    columns: [
                        {id: 'rn', type: 'cntr', align: 'center', sort: 'na', value: 'No.', width: 35},
                        {id: 'adlgNm', type: 'ro', align: 'center', sort: 'na', value: '위임자', width: 300},
                        {id: 'actNm', type: 'ro', align: 'center', sort: 'na', value: '수임자', width: 300},
                        {id: 'adlgStrDt', type: 'ro', align: 'center', sort: 'na', value: '위임시작일', width: 120},
                        {id: 'adlgEndDt', type: 'ro', align: 'center', sort: 'na', value: '위임종료일', width: 120},
                        {id: 'adlgExeDtm', type: 'ro', align: 'center', sort: 'na', value: '위임실행일시', width: 120},
                        {id: 'adlgRvcDtm', type: 'ro', align: 'center', sort: 'na', value: '위임해제일시', width: 120},
                        {id: 'adlgStatNm', type: 'ro', align: 'center', sort: 'na', value: '위임상태', width: 150},
                        {id: 'adlgId', type: 'ro', align: 'center', sort: 'na', value: '위임자Id', width: 100},
                        {id: 'actId', type: 'ro', align: 'center', sort: 'na', value: '수임자Id', width: 100},
                        {id: 'adlgSeq', type: 'ro', align: 'center', sort: 'na', value: 'Seq', width: 100},
                        {id: 'adlgStatCd', type: 'ro', align: 'center', sort: 'na', value: '위임상태Cd', width: 100},
                    ],
                    height: 334,
                    enablePaging: true,
                    pagingSize: 8,
                    queryPage: (page) => {
                        page = page || 0
                        return new Promise((resolve, reject) => {
                            let data = {
                                contents: this.mndList,
                                page: page,
                                totalPages: parseInt(this.mndList.length / this.config.pagingSize) + (parseInt(this.mndList.length % this.config.pagingSize) > 0 ? 1 : 0),
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
                                let rId = index + 1
                                if (grid.cells(rId, 3).getValue()) grid.cells(rId, 3).setValue(this.$moment(grid.cells(rId, 3).getValue()).format('YYYY-MM-DD'));
                                if (grid.cells(rId, 4).getValue()) grid.cells(rId, 4).setValue(this.$moment(grid.cells(rId, 4).getValue()).format('YYYY-MM-DD'));
                                if (grid.cells(rId, 5).getValue()) grid.cells(rId, 5).setValue(this.$moment(grid.cells(rId, 5).getValue()).format('YYYY-MM-DD'));
                                if (grid.cells(rId, 6).getValue()) grid.cells(rId, 6).setValue(this.$moment(grid.cells(rId, 6).getValue()).format('YYYY-MM-DD'));
                            })
                        })
                    }
                },
                title: '결재 위임관리',
                docTypes: [],
                docStatuses: [],
                compCds: [],
                adlgCds: [],
                mndList: [],
                hiddenAdlgId: '',
                hiddenAdlgNm: '',
                hiddenActId: '',
                hiddenActNm: '',
                hiddenAdlgSeq: '',
                hiddenDtmFr: '',
                hiddenDtmTo: '',
                hiddenCheck: 'N',
                showEmpModal: false,
                showEmpModal2: false,
                showVendorModal1: false,
                form: {
                    compCd: '',
                    searchDtmFr: this.$moment().add(-2, 'month').startOf('month').format('YYYY-MM-DD'),
                    searchDtmTo: this.$moment().format('YYYY-MM-DD'),
                    searchAdlgId: '',
                    searchAdlgNm: '',
                    searchActId: '',
                    searchActNm: '',
                    adlgStatCd: '',
                },
            };
        },
        methods: {
            constructGridSuccessful(grid) {
                this.config.queryPage(0)
                grid.setColumnHidden(8,true)
                grid.setColumnHidden(9,true)
                grid.setColumnHidden(10,true)
                grid.setColumnHidden(11,true)

                grid.attachEvent('onRowDblClicked', (rId) => {
                    this.hiddenAdlgId = grid.cells(rId, 8).getValue();
                    this.hiddenAdlgNm = grid.cells(rId, 1).getValue();
                    this.hiddenActId = grid.cells(rId, 9).getValue();
                    this.hiddenActNm = grid.cells(rId, 2).getValue();
                    this.hiddenAdlgSeq = grid.cells(rId, 10).getValue();
                    this.hiddenDtmFr = grid.cells(rId, 3).getValue();
                    this.hiddenDtmTo = grid.cells(rId, 4).getValue();
                    this.hiddenCheck = 'Y';

                    if(grid.cells(rId, 11).getValue() !== '10'){
                        this.$swal({type: 'warning', text: '위임이 해제된 건입니다.'});
                        return false;
                    }
                    this.popVendor();
                });
            },
            getCompCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "COMP_CD"}})
                    .then(response => {
                        this.compCds = response.data;
                    });
            },
            getAdlgCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "ADLG_STAT_CD"}})
                    .then(response => {
                        this.adlgCds = response.data;
                    });
            },
            saveExcel() {
                this.downloadExcel(this.$refs.grid);
            },
            goSearch() {
                console.log("조회...")
                const param = JSON.parse(JSON.stringify(this.form));
                const stripFields = ['searchDtmFr', 'searchDtmTo'];
                _.forEach(stripFields, (name) => param[name] = this.toPure(param[name]));

                this.$store.commit('loading');
                this.$http.post(`/api/appr/delegating/list`, {
                        compCd: param.compCd,
                        adlgStrDt: param.searchDtmFr,
                        adlgEndDt: param.searchDtmTo,
                        adlgId: param.searchAdlgId,
                        actId: param.searchActId,
                        adlgStatCd: param.adlgStatCd
                    }
                )
                    .then(response => {
                        if (response.data) {
                            this.mndList = response.data;
                            this.config.queryPage(0)
                        }
                    });
            },
            popVendor(clear) {
                if (clear === true) {
                    this.hiddenAdlgId = '';
                    this.hiddenAdlgNm = '';
                    this.hiddenActId = '';
                    this.hiddenActNm = '';
                    this.hiddenAdlgSeq = '';
                    this.hiddenDtmFr = '';
                    this.hiddenDtmTo = '';
                    this.hiddenCheck = 'N'
                }
                this.showVendorModal1 = true;
            },
            popEmp(clear) {
                if (clear === true) {
                    this.form.draftUserId = '';
                    this.form.draftNm = '';
                }
                this.showEmpModal = true;
            },
            popSearchAdlgEmp(clear) {
                if (clear === true) {
                    this.form.serachAdlgId = '';
                    this.form.serachAdlgNm = '';
                }
                this.showEmpModal = true;
            },
            popSearchActEmp(clear) {
                if (clear === true) {
                    this.form.serachActId = '';
                    this.form.serachActNm = '';
                }
                this.showEmpModal2 = true;
            },
            receiveSearchAdlgEmp(obj) {
                this.form.searchAdlgId = obj.empNo;
                this.form.searchAdlgNm = obj.empNm;
            },
            receiveSearchActEmp(obj) {
                this.form.searchActId = obj.empNo;
                this.form.searchActNm = obj.empNm;
            },
            receiveMndPop(obj) {
                this.goSearch();
            },
            initEmp(force) {
                if (force === true) this.form.wrtNm = '';
                if (this.form.wrtNm === '') this.form.draftUserId = '';
            },
            initSearchAdlgId(force) {
                if (force === true) this.form.searchAdlgNm = '';
                if (this.form.searchAdlgNm === '') this.form.searchAdlgId = '';
            },
            initSearchActId(force) {
                if (force === true) this.form.searchActNm = '';
                if (this.form.searchActNm === '') this.form.searchActId = '';
            },
        },
        mounted() {
            if (this.$route.query) {
                for (let member in this.form) {
                    if (this.$route.query[member] !== undefined) {
                        this.form[member] = this.$route.query[member]
                    }
                }
            }
            this.getCompCdCombo();
            this.getAdlgCdCombo();
            this.goSearch();
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

    @media (max-width: 1580px) {
        .search-border .td-s-thumb.search-area .ip-box.ip-box-w02 {
            width: 50%;
        }
    }
</style>

