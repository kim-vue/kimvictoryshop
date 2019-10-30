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
                        <span class="label-tit">- 카드소유자</span>
                    </div>
                    <div class="desc">
                        <div class="td-s-thumb search-area">
                            <input class="input input-bg" type="text" style="width:65px;" v-model="form.searchCdlgId"
                                   disabled>
                            <div class="ip-box ip-box-w02">
                                <input class="input" type="text" v-model="form.searchCdlgNm" @input="initSearchCdlgId"
                                       @keydown.enter="popSearchCdlgEmp">
                                <button class="icon is-right" @click="popSearchCdlgEmp(true)"><i
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
                            <input class="input input-bg" type="text" style="width:65px;" v-model="form.searchNomnId"
                                   disabled>
                            <div class="ip-box ip-box-w02">
                                <input class="input" type="text" v-model="form.searchNomnNm" @input="initSearchNomnId"
                                       @keydown.enter="popSearchNomnEmp">
                                <button class="icon is-right" @click="popSearchNomnEmp(true)"><i
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
                        <b-select class="select is-fullwidth" v-model="form.cdlgStatCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in cdlgCds"
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
                        <h3 class="ico_table_name">법인카드 위임현황</h3>
                    </div>
                    <div class="btn-wrap btn-type1 clearfix">
                        <button class="btn-size btn-excel" @click="saveExcel">엑셀 저장</button>
                    </div>
                </div>

                <div class="grid-wrap">
                    <dhx-grid ref="grid" v-model="deleDetails" :config="config" @constructGridSuccessful="constructGridSuccessful"/>
                </div>
            </div>

        </div>
        <!-- //테이블 -->

        <!--팝업-->
        <b-modal :active.sync="showEmpModal" has-modal-card @receive="receiveSearchCdlgEmp">
            <emp :param="form.searchCdlgNm"></emp>
        </b-modal>
        <b-modal :active.sync="showEmpModal2" has-modal-card @receive="receiveSearchNomnEmp">
            <emp :param="form.searchNomnNm"></emp>
        </b-modal>

        <b-modal :active.sync="showVendorModal1" has-modal-card @receive="receiveMndPop">
            <card-mnd-pop :cdlgId="hiddenCdlgId"
                          :cdlgNm="hiddenCdlgNm"
                          :nomnId="hiddenNomnId"
                          :nomnNm="hiddenNomnNm"
                          :cdlgSeq="hiddenCdlgSeq"
                          :hiddenDtmFr="hiddenDtmFr"
                          :hiddenDtmTo="hiddenDtmTo"
                          :hiddenCrdNo="hiddenCrdNo"
                          :hiddenCheck="hiddenCheck"></card-mnd-pop>
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
    import CardMndPop from '@/components/CardMndPop.vue';

    export default {
        name: 'CardMndMng',
        mixins: [mixin, mixinSlip],
        components: {Emp, CardMndPop, DhxGrid, DhxCalendar},
        data() {
            return {
                config : {
                    columns: [
                        {id: 'rn', type: 'cntr', align: 'center', sort: 'na', value: 'No.', width: 35},
                        {id: 'crdNo', type: 'ro', align: 'center', sort: 'na', value: '카드번호', width: 220},
                        {id: 'cdlgNm', type: 'ro', align: 'center', sort: 'na', value: '카드소유자', width: 150},
                        {id: 'cdlgStrDt', type: 'ro', align: 'center', sort: 'na', value: '위임시작일', width: 120},
                        {id: 'cdlgEndDt', type: 'ro', align: 'center', sort: 'na', value: '위임종료일', width: 120},
                        {id: 'nomnNm', type: 'ro', align: 'center', sort: 'na', value: '수임자', width: 120},
                        {id: 'cdlgExeDtm', type: 'ro', align: 'center', sort: 'na', value: '위임실행일시', width: 150},
                        {id: 'cdlgRvcDtm', type: 'ro', align: 'center', sort: 'na', value: '위임해제일시', width: 120},
                        {id: 'cdlgStatNm', type: 'ro', align: 'center', sort: 'na', value: '위임상태', width: 120},
                        {id: 'cdlgId', type: 'ro', align: 'center', sort: 'na', value: '위임자Id', width: 100},
                        {id: 'nomnId', type: 'ro', align: 'center', sort: 'na', value: '수임자Id', width: 100},
                        {id: 'cdlgSeq', type: 'ro', align: 'center', sort: 'na', value: 'Seq', width: 100},
                        {id: 'cdlgStatCd', type: 'ro', align: 'center', sort: 'na', value: '위임상태Cd', width: 100},
                    ],
                    height: 334,
                    enablePaging: true,
                    pagingSize: 8,
                    queryPage: (page) => {
                        page = page || 0
                        return new Promise((resolve, reject) => {
                            let data = {
                                contents: this.deleDetails,
                                page: page,
                                totalPages: parseInt(this.deleDetails.length / this.config.pagingSize) + (parseInt(this.deleDetails.length % this.config.pagingSize) > 0 ? 1 : 0),
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

                                grid.cells(rId, 1).setValue(this.$parent.getFormattedPureCardNumber(grid.cells(rId, 1).getValue()));
                                grid.cells(rId, 3).setValue(this.$moment(grid.cells(rId, 3).getValue()).format('YYYY-MM-DD'));
                                grid.cells(rId, 4).setValue(this.$moment(grid.cells(rId, 4).getValue()).format('YYYY-MM-DD'));
                                if(grid.cells(rId, 6).getValue()) grid.cells(rId, 6).setValue(this.$moment(grid.cells(rId, 6).getValue()).format('YYYY-MM-DD'));
                                if(grid.cells(rId, 7).getValue()) grid.cells(rId, 7).setValue(this.$moment(grid.cells(rId, 7).getValue()).format('YYYY-MM-DD'));
                            })
                        })
                    }
                },
                title: '법인카드 위임관리',
                compCds: [],
                cdlgCds: [],
                deleDetails: [],
                hiddenCdlgId: '',
                hiddenCdlgNm: '',
                hiddenNomnId: '',
                hiddenNomnNm: '',
                hiddenCdlgSeq: '',
                hiddenDtmFr: '',
                hiddenDtmTo: '',
                hiddenCrdNo: '',
                hiddenCheck: 'N',
                form: {
                    compCd: '',
                    searchDtmFr: this.$moment().add(-2, 'month').startOf('month').format('YYYY-MM-DD'),
                    searchDtmTo: this.$moment().format('YYYY-MM-DD'),
                    searchCdlgId: '',
                    searchCdlgNm: '',
                    searchNomnId: '',
                    searchNomnNm: '',
                    cdlgStatCd: '',
                },
                showEmpModal: false,
                showEmpModal2: false,
                showVendorModal1: false,
            };
        },
        methods: {
            constructGridSuccessful(grid) {
                this.config.queryPage(0)
                grid.setColumnHidden(9,true)
                grid.setColumnHidden(10,true)
                grid.setColumnHidden(11,true)
                grid.setColumnHidden(12,true)
                grid.attachEvent('onRowDblClicked', (rId) => {
                    this.hiddenCdlgId = grid.cells(rId, 9).getValue();
                    this.hiddenCdlgNm = grid.cells(rId, 2).getValue();
                    this.hiddenNomnId = grid.cells(rId, 10).getValue();
                    this.hiddenNomnNm = grid.cells(rId, 5).getValue();
                    this.hiddenCdlgSeq = grid.cells(rId, 11).getValue();
                    this.hiddenDtmFr = grid.cells(rId, 3).getValue();
                    this.hiddenDtmTo = grid.cells(rId, 4).getValue();
                    this.hiddenCrdNo = grid.cells(rId, 1).getValue();
                    this.hiddenCheck = 'Y';

                    if(grid.cells(rId, 12).getValue() !== '10'){
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
            getCdlgCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "CDLG_STAT_CD"}})
                    .then(response => {
                        this.cdlgCds = response.data;
                    });
            },
            saveExcel() {
                this.downloadExcel(this.$refs.grid);
            },
            goSearch() {
                const param = JSON.parse(JSON.stringify(this.form));
                const stripFields = ['searchDtmFr', 'searchDtmTo'];
                _.forEach(stripFields, (name) => param[name] = this.toPure(param[name]));

                this.$store.commit('loading');
                this.$http.post(`/api/card/delegating/list`, {
                        compCd: param.compCd,
                        searchDtmFr: param.searchDtmFr,
                        searchDtmTo: param.searchDtmTo,
                        cdlgId: param.searchCdlgId,
                        nomnId: param.searchNomnId,
                        cdlgStatCd: param.cdlgStatCd
                    }
                )
                    .then(response => {
                        if (response.data) {
                            this.deleDetails = response.data;
                            this.config.queryPage(0)
                        }
                    });
            },
            popVendor(clear) {
                if (clear === true) {
                    this.hiddenCdlgId = '';
                    this.hiddenCdlgNm = '';
                    this.hiddenNomnId = '';
                    this.hiddenNomnNm = '';
                    this.hiddenCdlgSeq = '';
                    this.hiddenDtmFr = '';
                    this.hiddenDtmTo = '';
                    this.hiddenCheck = 'N'
                }
                this.showVendorModal1 = true;
            },
            popSearchCdlgEmp(clear) {
                if (clear === true) {
                    this.form.serachCdlgId = '';
                    this.form.serachCdlgNm = '';
                }
                this.showEmpModal = true;
            },
            popSearchNomnEmp(clear) {
                if (clear === true) {
                    this.form.serachNomnId = '';
                    this.form.serachNomnNm = '';
                }
                this.showEmpModal2 = true;
            },
            receiveSearchCdlgEmp(obj) {
                this.form.searchCdlgId = obj.empNo;
                this.form.searchCdlgNm = obj.empNm;
            },
            receiveSearchNomnEmp(obj) {
                this.form.searchNomnId = obj.empNo;
                this.form.searchNomnNm = obj.empNm;
            },
            receiveMndPop(obj) {
                this.goSearch();
            },
            initSearchCdlgId(force) {
                if (force === true) this.form.searchCdlgNm = '';
                if (this.form.searchCdlgNm === '') this.form.searchCdlgId = '';
            },
            initSearchNomnId(force) {
                if (force === true) this.form.searchNomnNm = '';
                if (this.form.searchNomnNm === '') this.form.searchNomnId = '';
            },
        },
        mounted() {
            this.getCompCdCombo();
            this.getCdlgCdCombo();
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

    @media (max-width: 1580px) {
        .search-border .td-s-thumb.search-area .ip-box.ip-box-w02 {
            width: 50%;
        }
    }
</style>

