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
            </div>
            <div class="item desc-center">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 문서유형</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.docTypeCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in docTypes"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </div>
                </div>
            </div>
            <div class="item desc-right">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 사용여부</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.useYn">
                            <option value=''>==전체==</option>
                            <option value='Y'>사용</option>
                            <option value='N'>미사용</option>
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
                        <h3 class="ico_table_name">전결 규정 내역</h3>
                    </div>
                    <div class="btn-wrap btn-type1 clearfix">
                        <button class="btn-size btn-excel" @click="saveExcel">엑셀 저장</button>
                    </div>
                </div>
                <div class="grid-wrap">
                    <dhx-grid ref="grid" v-model="ruleDetails" :config="config" @constructGridSuccessful="constructGridSuccessful"/>
                </div>
            </div>

        </div>
        <!-- //테이블 -->

        <b-modal :active.sync="showVendorModal1" has-modal-card @receive="receiveRulePop">
            <appr-rule-pop :docTypeNm="hiddenDocTypeNm"
                           :docTypeCd="hiddenDocTypeCd"
                           :dtlTypeNm="hiddenDtlTypeNm"
                           :dtlTypeCd="hiddenDtlTypeCd"
                           :useYn="hiddenUseYn"
                           :ruleSeq="hiddenRuleSeq"
                           :curNm="hiddenCurNm"
                           :curCd="hiddenCurCd"
                           :maxAmt="hiddenMaxAmt"
                           :apprTypeNm="hiddenApprTypeNm"
                           :apprTypeCd="hiddenApprTypeCd"
                           :fixYn="hiddenFixYn"
                           :aprverClassNm="hiddenAprverClassNm"
                           :aprverClassVal="hiddenAprverClassVal"
                           :aprverClassCd="hiddenAprverClassCd"
                           :remark="hiddenRemark"
                           :hiddenCheck="hiddenCheck">
            </appr-rule-pop>
        </b-modal>

    </div>
</template>

<script>
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import DhxGrid from '@/components/DhxGrid.vue'
    import DhxCalendar from '@/components/DhxCalendar.vue'
    import ApprRulePop from '@/components/ApprRulePop.vue'

    export default {
        name: 'ApprRuleSet',
        mixins: [mixin, mixinSlip],
        components: {DhxGrid, DhxCalendar, ApprRulePop},
        data() {
            return {
                config : {
                    columns: [
                        {id: 'rn', type: 'cntr', align: 'center', sort: 'na', value: 'No.', width: 35},
                        {id: 'docTypeNm', type: 'ro', align: 'center', sort: 'na', value: '문서유형', width: 100},
                        {id: 'dtlTypeNm', type: 'ro', align: 'center', sort: 'na', value: '상세유형', width: 200},
                        {id: 'useYn', type: 'ro', align: 'center', sort: 'na', value: '사용여부', width: 100},
                        {id: 'ruleSeq', type: 'ro', align: 'center', sort: 'na', value: '규정순번', width: 100},
                        {id: 'curNm', type: 'ro', align: 'center', sort: 'na', value: '통화코드', width: 100},
                        {id: 'maxAmt', type: 'ron', align: 'right', sort: 'na', value: '상한금액', width: 150},
                        {id: 'apprTypeNm', type: 'ron', align: 'center', sort: 'na', value: '결재유형', width: 120},
                        {id: 'fixYn', type: 'ro', align: 'center', sort: 'na', value: '고정여부', width: 100},
                        {id: 'aprverClassNm', type: 'ro', align: 'center', sort: 'na', value: '결재자구분', width: 180},
                        {id: 'aprverClassVal', type: 'ro', align: 'center', sort: 'na', value: '결재자구분값', width: 200},
                        {id: 'remark', type: 'ed', align: 'center', sort: 'na', value: '비고', width: 200},
                        {id: 'docTypeCd', type: 'ro', align: 'center', sort: 'na', value: '문서코드', width: 100},
                        {id: 'dtlTypeCd', type: 'ro', align: 'center', sort: 'na', value: '상세코드', width: 100},
                        {id: 'curCd', type: 'ro', align: 'center', sort: 'na', value: '통화Cd', width: 100},
                        {id: 'apprTypeCd', type: 'ro', align: 'center', sort: 'na', value: '결재코드', width: 100},
                        {id: 'aprverClassCd', type: 'ro', align: 'center', sort: 'na', value: '결재자구분코드', width: 100},
                    ],
                    height: 334,
                    enablePaging: true,
                    pagingSize: 8,
                    queryPage: (page) => {
                        page = page || 0
                        return new Promise((resolve, reject) => {
                            let data = {
                                contents: this.ruleDetails,
                                page: page,
                                totalPages: parseInt(this.ruleDetails.length / this.config.pagingSize) + (parseInt(this.ruleDetails.length % this.config.pagingSize) > 0 ? 1 : 0),
                                totalElements: 0
                            }
                            resolve({
                                data: data
                            })
                        })
                    },
                }
                ,
                hiddenDocTypeNm: '',
                hiddenDocTypeCd: '',
                hiddenDtlTypeNm: '',
                hiddenDtlTypeCd: '',
                hiddenUseYn: '',
                hiddenRuleSeq: '',
                hiddenCurNm: '',
                hiddenCurCd: '',
                hiddenMaxAmt: '',
                hiddenApprTypeNm: '',
                hiddenApprTypeCd: '',
                hiddenFixYn: '',
                hiddenAprverClassNm: '',
                hiddenAprverClassVal: '',
                hiddenAprverClassCd: '',
                hiddenRemark: '',
                hiddenCheck:'N',
                title: '전결 규정 관리',
                compCds: [],
                docTypes: [],
                ruleDetails: [],
                showVendorModal1: false,
                form: {
                    compCd: '',
                    docTypeCd: '',
                    useYn: '',
                },
            };
        },
        methods : {
            constructGridSuccessful(grid) {
                this.config.queryPage(0)
                grid.setColumnHidden(12,true)
                grid.setColumnHidden(13,true)
                grid.setColumnHidden(14,true)
                grid.setColumnHidden(15,true)
                grid.setColumnHidden(16,true)
                grid.setNumberFormat('0,000', 6, '.', ',')
                grid.attachEvent('onRowDblClicked', (rId) => {
                    this.hiddenDocTypeNm = grid.cells(rId, 1).getValue();
                    this.hiddenDocTypeCd = grid.cells(rId, 12).getValue();
                    this.hiddenDtlTypeNm = grid.cells(rId, 2).getValue();
                    this.hiddenDtlTypeCd = grid.cells(rId, 13).getValue();
                    this.hiddenUseYn = grid.cells(rId, 3).getValue();
                    this.hiddenRuleSeq = grid.cells(rId, 4).getValue();
                    this.hiddenCurNm = grid.cells(rId, 5).getValue();
                    this.hiddenCurCd = grid.cells(rId, 14).getValue();
                    this.hiddenMaxAmt = grid.cells(rId, 6).getValue();
                    this.hiddenApprTypeNm = grid.cells(rId, 7).getValue();
                    this.hiddenApprTypeCd = grid.cells(rId, 15).getValue();
                    this.hiddenFixYn = grid.cells(rId, 8).getValue();
                    this.hiddenAprverClassNm = grid.cells(rId, 9).getValue();
                    this.hiddenAprverClassVal = grid.cells(rId, 10).getValue();
                    this.hiddenAprverClassCd = grid.cells(rId, 16).getValue();
                    this.hiddenRemark = grid.cells(rId, 11).getValue();
                    this.hiddenCheck = 'Y';
                    this.popVendor();
                });
            },
            getCompCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "COMP_CD"}})
                    .then(response => {
                        this.compCds = response.data;
                    });
            },
            getDocTypeCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "DOC_TYPE_CD"}})
                    .then(response => {
                        this.docTypes = response.data;
                    });
            },
            saveExcel() {
                this.downloadExcel(this.$refs.grid);
            },
            goSearch() {
                this.$store.commit('loading');
                this.$http.post(`/api/appr/rule/list`, {
                        compCd: this.form.compCd,
                        docTypeCd: this.form.docTypeCd,
                        useYn: this.form.useYn,
                    }
                )
                    .then(response => {
                        if (response.data) {
                            this.ruleDetails = response.data;
                            this.config.queryPage(0)
                        }
                    });
            },
            popVendor(clear) {
                if (clear === true) {
                    this.hiddenDocTypeNm = ''
                    this.hiddenDocTypeCd = ''
                    this.hiddenDtlTypeNm = ''
                    this.hiddenDtlTypeCd = ''
                    this.hiddenUseYn = ''
                    this.hiddenRuleSeq = ''
                    this.hiddenCurNm = ''
                    this.hiddenCurCd = ''
                    this.hiddenMaxAmt = ''
                    this.hiddenApprTypeNm = ''
                    this.hiddenApprTypeCd = ''
                    this.hiddenFixYn = ''
                    this.hiddenAprverClassNm = ''
                    this.hiddenAprverClassVal = ''
                    this.hiddenAprverClassCd = ''
                    this.hiddenRemark = ''
                    this.hiddenCheck = 'N'
                }
                this.showVendorModal1 = true;
            },
            receiveRulePop(obj) {
                this.goSearch();
            },
        },
        mounted() {
            this.getCompCdCombo();
            this.getDocTypeCombo();
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

    .desc-content .item.desc-left .desc-item .td-s-thumb.search-area input{
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

    .search-border .td-s-thumb.search-area > input,
    .search-border .td-s-thumb.search-area > .ip-box
    .search-border .td-s-thumb.search-area > button {
        float: left;
    }

</style>

