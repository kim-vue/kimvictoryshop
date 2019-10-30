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
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 기안일자</span>
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
            </div>
            <div class="item desc-center">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 문서상태</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.docStatCd">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in docStatuses"
                                    :key="item.key"
                                    :value="item.key"
                                    v-text="item.value"/>
                        </b-select>
                    </div>
                </div>
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 기안자</span>
                    </div>
                    <div class="desc">
                        <div class="td-s-thumb search-area" style="width: 450px">
                            <input class="input input-bg" type="text" style="width:65px;" v-model="form.draftUserId" disabled>
                            <div class="ip-box ip-box-w02" style="width:120px;">
                                <input class="input" type="text" v-model="form.draftNm" @input="initEmp" @keydown.enter="popEmp">
                                <button class="icon is-right" @click="popEmp(true)"><i class="fas fa-search"></i>
                                </button>
                            </div>
                            <div class="ip-box ip-box-w02" style="width:200px;">
                                <input class="input input-bg" type="text" style="width:80px;" v-model="form.draftUserDut" disabled>
                                <input class="input input-bg" type="text" style="width:120px;" v-model="form.draftUserDept" disabled>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="item desc-right">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 제목</span>
                    </div>
                    <div class="desc">
                        <input class="input Rt-M tal" type="text" v-model="form.docTitleNm">
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
                        <h3 class="ico_table_name">결재한 목록</h3>
                    </div>
                    <div class="btn-wrap btn-type1 clearfix">
                        <button class="btn-size btn-excel" @click="saveExcel">엑셀 저장</button>
                    </div>
                </div>

                <div class="grid-wrap">
                    <dhx-grid ref="grid" v-model="compList" :config="config" @constructGridSuccessful="constructGridSuccessful"/>
                </div>
            </div>

        </div>
        <!-- //테이블 -->

        <!--팝업-->
        <b-modal :active.sync="showEmpModal" has-modal-card @receive="receiveEmp">
            <emp :param="form.draftNm"></emp>
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
        name: 'ApprCompLst',
        mixins: [mixin, mixinSlip],
        components: {Emp, DhxGrid, DhxCalendar},
        data() {
            return {
                config : {
                    columns: [
                        {id: 'rn', type: 'cntr', align: 'center', sort: 'na', value: 'No.', width: 35},
                        {id: 'docType', type: 'ro', align: 'center', sort: 'na', value: '문서유형'},
                        {id: 'docStatNm', type: 'ro', align: 'center', sort: 'na', value: '문서상태'},
                        {id: 'docTitleNm', type: 'ro', align: 'left', sort: 'na', value: '제목', width: 250},
                        {id: 'apprType', type: 'ro', align: 'center', sort: 'na', value: '결재유형'},
                        {id: 'apprStatus', type: 'ron', align: 'center', sort: 'na', value: '결재구분'},
                        {id: 'apprNo', type: 'ron', align: 'center', sort: 'na', value: '결재번호'},
                        {id: 'docMngNo', type: 'ron', align: 'center', sort: 'na', value: '문서번호'},
                        {id: 'draftUserId', type: 'ro', align: 'center', sort: 'na', value: '기안자사번'},
                        {id: 'draftUserName', type: 'ro', align: 'center', sort: 'na', value: '기안자'},
                        {id: 'draftUserJob', type: 'ro', align: 'center', sort: 'na', value: '직급'},
                        {id: 'draftDtm', type: 'ro', align: 'center', sort: 'na', value: '기안일자'},
                    ],
                    height: 334,
                    enablePaging: true,
                    pagingSize: 8,
                    queryPage: (page) => {
                        page = page || 0
                        return new Promise((resolve, reject) => {
                            let data = {
                                contents: this.compList,
                                page: page,
                                totalPages: parseInt(this.compList.length / this.config.pagingSize) + (parseInt(this.compList.length % this.config.pagingSize) > 0 ? 1 : 0),
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
                                grid.cells(rId, 11).setValue(this.$moment(grid.cells(rId, 11).getValue()).format('YYYY-MM-DD'));
                            })
                        })
                    }
                },
                title: '결재한 문서',
                docTypes: [],
                docStatuses: [],
                compList: [],
                showEmpModal: false,
                form: {
                    docTypeCd: '',
                    docStatCd: '',
                    searchDtmFr: this.$moment().add(-1, 'month').format('YYYY-MM-DD'),
                    searchDtmTo: this.$moment().format('YYYY-MM-DD'),
                    draftUserId: '',
                    draftUserDut: '',
                    draftUserDept: '',
                    docTitleNm: '',
                },
            };
        },
        methods: {
            constructGridSuccessful(grid) {
                this.config.queryPage(0)

                grid.attachEvent('onRowDblClicked', (rId) => {
                    let docMngNo = grid.cells(rId, 6).getValue();
                    this.$router.push({path: `/apprDtlQry/${docMngNo}`});
                });
            },
            getDocTypeCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "DOC_TYPE_CD"}})
                    .then(response => {
                        this.docTypes = response.data;
                    });
            },
            getStatusTypeCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "DOC_STAT_CD"}})
                    .then(response => {
                        this.docStatuses = response.data;
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

                if (param.searchDtmFr > param.searchDtmTo) {
                    this.$swal({type: 'warning', text: '조회 시작일자와 종료일자 지정이 잘못되었습니다.'});
                    return false
                }

                this.$store.commit('loading');
                this.$http.post(`/api/appr/done/list`, {
                            docTypeCd: param.docTypeCd,
                            searchDtmFr: this.toPure(param.searchDtmFr),
                            searchDtmTo: this.toPure(param.searchDtmTo),
                            docStatCd: param.docStatCd,
                            draftUserId: param.draftUserId,
                            docTitleNm: param.docTitleNm
                    }
                )
                    .then(response => {
                        if (response.data) {
                            this.compList = response.data;
                            this.config.queryPage(0)
                        }
                    });
            },
            popEmp(clear) {
                if (clear === true) {
                    this.form.draftUserId = '';
                    this.form.draftNm = '';
                    this.form.draftUserDut = '';
                    this.form.draftUserDept = '';
                }
                this.showEmpModal = true;
            },
            receiveEmp(obj) {
                this.form.draftUserId = obj.empNo;
                this.form.draftNm = obj.empNm;
                this.form.draftUserDut = obj.dutNm;
                this.form.draftUserDept = obj.deptNm;
            },
            initEmp(force) {
                if (force === true) this.form.draftNm = '';
                if (this.form.draftNm === '') {
                    this.form.draftUserId = '';
                    this.form.draftUserDut = '';
                    this.form.draftUserDept = '';
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
            this.setCallPageByParam()
            this.getDocTypeCombo()
            this.getStatusTypeCombo()
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

