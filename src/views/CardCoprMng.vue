<template>
    <div class="inner-box">
        <div class="content-name">
            <h2 class="dp-ib">{{title}}</h2>
            <div class="btn-wrap btn-type1 clearfix">
                <button class="btn-size btn-gray fl_left" @click="compare"><span class="btn-icon"><i class="fas fa-check"></i></span> 대사실행</button>
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
                        <span class="label-tit">- 결제연월</span>
                    </div>
                    <div class="desc">
                        <div class="datepicker w-type-ymd02">
                            <input type="text" class="input date sDate" id="reqYm" v-model="form.reqYm" readonly/>
                        </div>
                    </div>
                </div>
            </div>
            <div class="item desc-center">
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

        <div class="table-area">
        <div class="table-b">
            <div class="table-name">
                <h3 class="ico_table_name">법인카드 대사내역</h3>
            </div>
            <table class="table">
                <colgroup>
                    <col width="10%">
                    <col width="18%">
                    <col width="18%">
                    <col width="18%">
                    <col width="18%">
                    <col width="18%">
                </colgroup>
                <thead>
                <tr>
                    <th class="no-radius">구분</th>
                    <th>청구내역</th>
                    <th>대사내역</th>
                    <th>차이내역</th>
                    <th>경비처리내역</th>
                    <th style="border-right: 1px solid #adadad">미처리내역</th>
                </tr>
                </thead>
                <tbody id="tbody">
                <tr>
                    <td style="text-align: center;">건수</td>
                    <td style="text-align: right;"><span @click=goDetail(10)><font color="#1e90ff"><b><u>{{this.cardCompare.billCnt}}</u></b></font></span>건</td>
                    <td style="text-align: right;"><span @click=goDetail(20)><font color="#1e90ff"><b><u>{{this.cardCompare.cmprCnt}}</u></b></font></span>건</td>
                    <td style="text-align: right;"><span @click=goDetail(30)><font color="#1e90ff"><b><u>{{this.cardCompare.diffCnt}}</u></b></font></span>건</td>
                    <td style="text-align: right;"><span @click=goDetail(40)><font color="#1e90ff"><b><u>{{this.cardCompare.dealCnt}}</u></b></font></span>건</td>
                    <td style="text-align: right; border-right: 1px solid #adadad;"><span @click=goDetail(50)><font color="#1e90ff"><b><u>{{this.cardCompare.untrCnt}}</u></b></font></span>건</td>
                </tr>
                <tr>
                    <td style="text-align: center;">금액</td>
                    <td style="text-align: right;">{{this.cardCompare.billTotSum}}원</td>
                    <td style="text-align: right;">{{this.cardCompare.cmprTotSum}}원</td>
                    <td style="text-align: right;">{{this.cardCompare.diffTotSum}}원</td>
                    <td style="text-align: right;">{{this.cardCompare.dealTotSum}}원</td>
                    <td style="text-align: right; border-right: 1px solid #adadad;">{{this.cardCompare.untrTotSum}}원</td>
                </tr>
                </tbody>
            </table>
        </div>
        </div>

        <!-- 테이블 -->
        <div class="table-area">
            <div class="table-b">
                <div class="table-header">
                    <div class="table-name">
                        <h3 class="ico_table_name">법인카드 사용내역</h3>
                    </div>
                    <div class="btn-wrap btn-type1 clearfix">
<!--                        <button class="btn-size btn-excel" @click="saveExcel">엑셀 저장</button>-->
                        <button type="button" class="btn-size btn-excel" @click="saveExcel()">엑셀 저장</button>
                    </div>
                </div>

                <div class="grid-wrap">
                    <dhx-grid ref="grid" class="slip-grid" v-model="useDetails" :config="config" @constructGridSuccessful="constructGridSuccessful"/>
                </div>
            </div>
        </div>
        <!-- //테이블 -->
    </div>
</template>

<script>
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import _ from 'lodash'
    import DhxGrid from '@/components/DhxGrid.vue'
    import Emp from '@/components/Emp.vue';

    export default {
        name: 'CardCoprMng',
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
                        {id: 'acqClassNm', type: 'ro', align: 'center', sort: 'na', value: '매입구분', width: 100},
                        {id: 'useDtlsStatNm', type: 'ro', align: 'center', sort: 'na', value: '처리상태', width: 110},
                        {id: 'apprDate', type: 'ro', align: 'center', sort: 'na', value: '사용일자', width: 120},
                        {id: 'apprTime', type: 'ro', align: 'center', sort: 'na', value: '사용시각', width: 120},
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
                        {id: 'erpSlipDtm', type: 'ro', align: 'right', sort: 'na', value: '전송일시', width: 150},
                    ],
                    height: 300,
                    enablePaging: true,
                    pagingSize: 5,
                    // afterRefreshData(grid, data) {
                    //     this.$nextTick(() => {
                    //         _.forEach(data, (item, index) => {
                    //             var rId = index + 1
                    //             grid.cells(rId, 1).setValue(this.$parent.getFormattedCardNumber(grid.cells(rId, 1).getValue()));
                    //             grid.cells(rId, 7).setValue(this.$moment(grid.cells(rId, 7).getValue()).format('YYYY-MM-DD'));
                    //             if(grid.cells(rId, 8).getValue()) grid.cells(rId, 8).setValue(this.$moment(grid.cells(rId, 8).getValue(),'HHmmss').format('HH:mm:ss'));
                    //
                    //             if(grid.cells(rId, 23).getValue()) grid.cells(rId, 23).setValue(this.$moment(grid.cells(rId, 23).getValue()).format('YYYY-MM-DD HH:mm:ss'));
                    //
                    //         })
                    //     })
                    // }
                },
                title: '법인카드 대사현황',
                compCds: [],
                crdCompCds: [],
                crdFgCds: [],
                cardCompare: [],
                searchCond: [],
                useDetails: [],
                authority: '',
                form: {
                    compCd: '',
                    crdCompCd: '',
                    crdFgCd: '',
                    reqYm: this.$moment().format('YYYY-MM'),
                },
            }
        },
        methods: {
            constructGridSuccessful(grid) {
                // this.config.queryPage(0)
                let header_style = 'color:#222;text-align:center;'
                let stat_total_text = 'color:red;text-align:right;padding-right:10px !important;'

                grid.attachHeader(
                    ['합계', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#stat_total', '#stat_total', '#stat_total', '#stat_total','', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan', '#cspan'],
                    [header_style, '', '', '', '', '', '', '', '', stat_total_text, stat_total_text, stat_total_text, stat_total_text]
                )

                grid.setNumberFormat('0,000', 9, '.', ',')
                grid.setNumberFormat('0,000', 10, '.', ',')
                grid.setNumberFormat('0,000', 11, '.', ',')
                grid.setNumberFormat('0,000', 12, '.', ',')
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
            getCardFgCdCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "CRD_FG_CD"}})
                    .then(response => {
                        this.crdFgCds = response.data
                    })
            },
            saveExcel() {
                // this.downloadExcel(this.$refs.grid.instance)
                // console.log(this.$refs.grid)
                this.$refs.grid.toExcel()
            },
            calendarLoad() {
                const iljinCalendar1 = new dhtmlXCalendarObject('reqYm')
                iljinCalendar1.hideTime();
                iljinCalendar1.setPosition('bottom')
                iljinCalendar1.setDate(new Date())
                iljinCalendar1.setDateFormat('%Y-%m')
                iljinCalendar1.attachEvent('onChange', (v) => {
                    this.form.reqYm = this.$refs.reqYm.getFormatedDate()
                })
                iljinCalendar1.attachEvent("onButtonClick", (d) => {
                    if (d === null) {
                        this.form.reqYm = this.$refs.reqYm.getFormatedDate()
                    }
                })
                this.$refs.reqYm = iljinCalendar1
            },
            goSearch() {
                const param = JSON.parse(JSON.stringify(this.form))
                const stripFields = ['reqYm']
                _.forEach(stripFields, (name) => param[name] = this.toPure(param[name]))

                this.$store.commit('loading')
                this.$http.post(`/api/card/compare/state`, {
                        reqYm: this.$moment(param.reqYm, 'YYYYMM').format('YYYYMM'),
                        compCd: param.compCd,
                        crdCompCd: param.crdCompCd,
                        crdFgCd: param.crdFgCd
                    }
                )
                    .then(response => {
                        if (response.data) {
                            this.cardCompare = response.data.cardCompare
                            this.searchCond = response.data.searchCond
                        }
                    })
            },
            goDetail(gubun){
                this.$store.commit('loading')
                this.$http.post(`/api/card/compare/state/list`, {
                        reqYm: this.searchCond.reqYm,
                        compCd: this.searchCond.compCd,
                        crdCompCd: this.searchCond.crdCompCd,
                        crdFgCd: this.searchCond.crdFgCd,
                        cmprFgCd: gubun
                    }
                )
                    .then(response => {
                        if (response.data) {
                            this.useDetails = response.data.map(x => {
                                x.cardNo = String(x.cardNo || '').replace(/(\d{4})(\d{4})(\d{4})(\d{4})$/g, '$1-xxxx-$3-$4')
                                x.apprDate = this.$moment(x.apprDate).format('YYYY-MM-DD')
                                return x
                            })
                            this.config.queryPage(0)
                        }
                    })

            },
            compare() {
                this.$swal({
                    type: 'warning',
                    text: `대사작업을 실행합니다. 계속 하시겠습니까?`,
                    showCancelButton: true,
                    confirmButtonText: '예',
                    cancelButtonText: '아니오',
                }).then((result) => {
                    if (result.value) {
                        const param = JSON.parse(JSON.stringify(this.form))
                        const stripFields = ['reqYm']
                        _.forEach(stripFields, (name) => param[name] = this.toPure(param[name]))

                        this.$store.commit('loading')
                        this.$http.post(`/api/card/comparing`, {
                                reqYm: this.$moment(param.reqYm, 'YYYYMM').format('YYYYMM'),
                                compCd: param.compCd,
                                crdCompCd: param.crdCompCd,
                                crdFgCd: param.crdFgCd
                            }
                        )
                            .then(response => {
                                if (response.data) {
                                    this.$swal({type: 'info', text: '대사작업이 완료되었습니다.'});
                                    this.goSearch()
                                }
                            })
                    }
                })
            },
        },
        mounted() {
            this.form.compCd = this.$store.state.loginInfo.compCd
            this.authority = this.$store.state.loginInfo.authorities[0].roleCd
            this.calendarLoad()
            this.getCompCdCombo()
            this.getCardCompCdCombo()
            this.getCardFgCdCombo()
            this.goSearch()
        }
        ,
        watch: {
            'cardCompare.billCnt'(value) {
                this.cardCompare.billCnt = this.$filters.number(value);
            },
            'cardCompare.cmprCnt'(value) {
                this.cardCompare.cmprCnt = this.$filters.number(value);
            },
            'cardCompare.diffCnt'(value) {
                this.cardCompare.diffCnt = this.$filters.number(value);
            },
            'cardCompare.dealCnt'(value) {
                this.cardCompare.dealCnt = this.$filters.number(value);
            },
            'cardCompare.untrCnt'(value) {
                this.cardCompare.untrCnt = this.$filters.number(value);
            },
            'cardCompare.billTotSum'(value) {
                this.cardCompare.billTotSum = this.$filters.number(value);
            },
            'cardCompare.cmprTotSum'(value) {
                this.cardCompare.cmprTotSum = this.$filters.number(value);
            },
            'cardCompare.diffTotSum'(value) {
                this.cardCompare.diffTotSum = this.$filters.number(value);
            },
            'cardCompare.dealTotSum'(value) {
                this.cardCompare.dealTotSum = this.$filters.number(value);
            },
            'cardCompare.untrTotSum'(value) {
                this.cardCompare.untrTotSum = this.$filters.number(value);
            },
        }
    }
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

    .desc-content .item.desc-left .desc-item .td-s-thumb.search-area input {
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