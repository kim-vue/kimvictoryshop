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
                        <span class="label-tit">- 사용일자</span>
                    </div>
                    <div class="desc">
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
                <div class="desc-item" style="height: 25px">
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 처리상태</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.useDtlsStatCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in useDtlsStatCds"
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
                    <div id="gridbox" class="grid-tbl-box"></div>
                    <div id="pagingbox" class="pagingbox"></div>
                </div>

                <div class="grid-wrap">
                    <dhx-grid class="slip-grid" ref="grid" v-model="useDetails" :config="config" @constructGridSuccessful="constructGridSuccessful"/>
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
    import DhxCalendar from '@/components/DhxCalendar.vue'
    import DhxGrid from '@/components/DhxGrid.vue'
    import Emp from '@/components/Emp.vue';

    export default {
        name: 'CardUseLst',
        mixins: [mixin, mixinSlip],
        components: {Emp, DhxGrid, DhxCalendar},
        data() {
            return {
                config : {
                    columns: [
                        {id: 'rn', type: 'cntr', align: 'center', sort: 'na', value: 'No.', width: 35},
                        {id: 'cardNo', type: 'ro', align: 'center', sort: 'na', value: '카드번호', width: 170},
                        {id: 'crdCompNm', type: 'ro', align: 'center', sort: 'na', value: '카드사', width: 150},
                        {id: 'crdFgNm', type: 'ro', align: 'center', sort: 'na', value: '카드구분', width: 100},
                        {id: 'apprNo', type: 'ro', align: 'center', sort: 'na', value: '승인번호', width: 120},
                        {id: 'acqClassNm', type: 'ro', align: 'center', sort: 'na', value: '매입구분', width: 100},
                        {id: 'useDtlsStatNm', type: 'ro', align: 'center', sort: 'na', value: '처리상태', width: 110},
                        {
                            id: 'useDtlsCancel',
                            align: 'center',
                            value: '처리취소',
                            width: 60,
                            component: {
                                props: ['index', 'value', 'field'],
                                template: `<button type="button" class="icon" v-if="this.$parent.value[index].useDtlsStatCd ==='40'" @click="cancel()"><i class="fas fa-ban"></i></button>`,
                                methods: {
                                    cancel() {
                                        this.$swal({
                                            type: 'warning',
                                            text: `기존 처리를 취소 하시겠습니까?`,
                                            showCancelButton: true,
                                            confirmButtonText: '예',
                                            cancelButtonText: '아니오',
                                        }).then((result) => {
                                            if (result.value) {
                                                const value = this.$parent.value[this.index]
                                                console.log(value.useDtlsNo)
                                                this.$http.post(`/api/card/privateCost/Cancel`,
                                                    {
                                                        useDtlsNo: value.useDtlsNo,
                                                    }
                                                ).then(response => {
                                                    this.$parent.$parent.goSearch();
                                                });
                                            }
                                        });
                                    },
                                }
                            }
                        },
                        {id: 'apprDate', type: 'ro', align: 'center', sort: 'na', value: '사용일자', width: 120},
                        {id: 'apprTime', type: 'ro', align: 'center', sort: 'na', value: '사용시간', width: 120},
                        {id: 'purchTot', type: 'ron', align: 'right', sort: 'na', value: '사용금액', width: 150},
                        {id: 'apprAmt', type: 'ron', align: 'right', sort: 'na', value: '공급가액', width: 150},
                        {id: 'vat', type: 'ron', align: 'right', sort: 'na', value: '부가세', width: 150},
                        {id: 'tips', type: 'ron', align: 'right', sort: 'na', value: '봉사료', width: 150},
                        {id: 'merchNm', type: 'ro', align: 'center', sort: 'na', value: '가맹점명', width: 200},
                        {id: 'merchAddr', type: 'ro', align: 'center', sort: 'na', value: '가맹점주소', width: 300},
                        {id: 'mccNm', type: 'ro', align: 'center', sort: 'na', value: '업종명', width: 120},
                        {id: 'etcNm ', type: 'ro', align: 'center', sort: 'na', value: '과세구분', width: 100},
                        {id: 'eaSlipNo', type: 'ro', align: 'center', sort: 'na', value: '전표번호', width: 150},
                        {id: 'slipStatNm', type: 'ro', align: 'center', sort: 'na', value: '전표상태', width: 100},
                        {id: 'crdPssrNm', type: 'ro', align: 'center', sort: 'na', value: '카드사용자', width: 100},
                        {id: 'crdUseDutNm', type: 'ro', align: 'center', sort: 'na', value: '직급', width: 100},
                        {id: 'crdUseDeptNm', type: 'ro', align: 'center', sort: 'na', value: '부서명', width: 150},
                        {id: 'compNm', type: 'ro', align: 'center', sort: 'na', value: '회사', width: 150},
                        {id: 'procPeriod', type: 'ro', align: 'center', sort: 'na', value: '경비처리기한', width: 120},
                        {id: 'slipProcNm', type: 'ro', align: 'center', sort: 'na', value: '경비처리자', width: 100},
                        {id: 'erpSlipDtm', type: 'ro', align: 'center', sort: 'na', value: '전송일시', width: 150},
                    ],
                    height: 390,
                    enablePaging: true,
                    pagingSize: 8,
                    afterRefreshData(grid, data) {
                        this.$nextTick(() => {
                            _.forEach(data, (item, index) => {
                                var rId = index + 1
                                grid.cells(rId, 1).setValue(this.$parent.getFormattedCardNumber(grid.cells(rId, 1).getValue()));
                                grid.cells(rId, 8).setValue(this.$moment(grid.cells(rId, 8).getValue()).format('YYYY-MM-DD'));
                                if (grid.cells(rId, 9).getValue()) grid.cells(rId, 9).setValue(this.$moment(grid.cells(rId, 9).getValue(), 'HHmmss').format('HH:mm:ss'));
                                if (grid.cells(rId, 26).getValue()) grid.cells(rId, 26).setValue(this.$moment(grid.cells(rId, 26).getValue()).format('YYYY-MM-DD HH:mm:ss'));
                            })
                        })
                    }
                },
                title: '법인카드 사용현황',
                compCds: [],
                crdCompCds: [],
                useDtlsStatCds: [],
                crdFgCds: [],
                useDetails: [],
                showEmpModal: false,
                authority: '',
                form: {
                    compCd: '',
                    crdCompCd: '',
                    useDtlsStatCd: '',
                    crdFgCd: '',
                    crdNo: '',
                    crdPssrId: '',
                    crdPssrNm: '',
                    crdPssrTitle: '',
                    crdPssrDut: '',
                    crdPssrDept: '',
                    searchDtmFr: this.$moment().startOf('month').format('YYYY-MM-DD'),
                    searchDtmTo: this.$moment().format('YYYY-MM-DD'),
                },
            };
        },
        methods: {
            constructGridSuccessful(grid) {
                this.config.queryPage(0)
                var header_style = 'color:#222;text-align:center;'
                var stat_total_text = 'color:red;text-align:right;padding-right:10px !important;'

                grid.attachHeader(
                    ["합계", "#cspan", "#cspan", "#cspan", "#cspan", "#cspan", "#cspan", "#cspan", "#cspan", "#cspan", "#stat_total", "#stat_total", "#stat_total", "#stat_total","","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan"],
                    [header_style, '', '', '', '', '', '', '', '', '', stat_total_text, stat_total_text, stat_total_text, stat_total_text]
                )
                grid.setNumberFormat('0,000', 10, '.', ',')
                grid.setNumberFormat('0,000', 11, '.', ',')
                grid.setNumberFormat('0,000', 12, '.', ',')
                grid.setNumberFormat('0,000', 13, '.', ',')
            },
            getCompCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "COMP_CD"}})
                    .then(response => {
                        this.compCds = response.data;
                    });
            },
            getCardCompCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "CRD_COMP_CD"}})
                    .then(response => {
                        this.crdCompCds = response.data;
                    });
            },
            getUseStatCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "USE_DTLS_STAT_CD"}})
                    .then(response => {
                        this.useDtlsStatCds = response.data;
                    });
            },
            getCardFgCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "CRD_FG_CD"}})
                    .then(response => {
                        this.crdFgCds = response.data;
                    });
            },
            saveExcel() {
                this.downloadExcel(this.$refs.grid);
            },
            goSearch() {
                const param = JSON.parse(JSON.stringify(this.form));
                const stripFields = ['searchDtmFr', 'searchDtmTo','crdNo'];
                _.forEach(stripFields, (name) => param[name] = this.toPure(param[name]));

                this.$store.commit('loading');
                this.$http.post(`/api/card/useList`, {
                        compCd: param.compCd,
                        searchDtmFr: param.searchDtmFr,
                        searchDtmTo: param.searchDtmTo,
                        useDtlsStatCd: param.useDtlsStatCd,
                        cardNo: param.crdNo,
                        crdPssrId: param.crdPssrId,
                        crdCompCd: param.crdCompCd,
                        crdFgCd: param.crdFgCd
                    }
                )
                    .then(response => {
                        if (response.data) {
                            this.useDetails = response.data;
                            this.config.queryPage(0)
                        }
                    });
            },
            popEmp(clear) {
                if (clear === true) {
                    this.form.crdPssrId = '';
                    this.form.crdPssrNm = '';
                    this.form.crdPssrDut = '';
                    this.form.crdPssrDept = '';
                }
                this.showEmpModal = true;
            },
            receiveEmp(obj) {
                this.form.crdPssrId = obj.empNo;
                this.form.crdPssrNm = obj.empNm;
                this.form.crdPssrDut = obj.dutNm;
                this.form.crdPssrDept = obj.deptNm;
            },
            initEmp(force) {
                if (force === true) this.form.crdPssrNm = '';
                if (this.form.crdPssrNm === '') {
                    this.form.crdPssrId = '';
                    this.form.crdPssrDut = '';
                    this.form.crdPssrDept = '';
                }
            },
        },
        mounted() {
            this.form.compCd = this.$store.state.loginInfo.compCd;
            this.authority = this.$store.state.loginInfo.authorities[0].roleCd;
            this.getCompCdCombo();
            this.getCardCompCdCombo();
            this.getUseStatCdCombo();
            this.getCardFgCdCombo();
            this.goSearch();
        }
    };
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
