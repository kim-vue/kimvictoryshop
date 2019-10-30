<template>
    <div class="inner-box">
        <div class="content-name">
            <h2 class="dp-ib">{{title}}</h2>
            <div class="btn-wrap btn-type1 clearfix">
                <button class="btn-size btn-gray fl_left" @click="saveAll"><span class="btn-icon"><i class="fas fa-check"></i></span> 일괄저장</button>
                <button class="btn-size btn-orange fl_left" @click="doPrivateCost"><span class="btn-icon"><i class="fas fa-receipt"></i></span> 사적비용처리</button>
                <button class="btn-size btn-blue fl_left" @click="goSearch"><span class="btn-icon"><i class="fas fa-pen-alt"></i></span> 조회</button>
            </div>
        </div>

        <!-- 검색조건 영역 -->
        <div class="desc-content search-border">
            <div class="item desc-left">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 사용일자</span>
                    </div>
                    <div class="desc">
                        <div class="datepicker w-type-ymd02">
                            <input type="text" class="input date sDate" id="apprDateFrom" v-model="form.apprDateFrom"/>
                        </div>
                        <span class="wave"> ~ </span>
                        <div class="datepicker w-type-ymd02">
                            <input type="text" class="input date sDate" id="apprDateTo" v-model="form.apprDateTo"/>
                        </div>
                    </div>
                </div>
            </div>
            <div class="item desc-center">
                <div class="desc-item">
                    <div class="tit">
                        <span class="label-tit">- 카드번호</span>
                    </div>
                    <div class="desc">
                        <b-select class="select is-fullwidth" v-model="form.cardNo">
                            <option value=''>==전체==</option>
                            <option
                                    v-for="item in cardNos"
                                    :key="item.cardNo"
                                    :value="item.cardNo"
                                    v-text="`${item.maskedCardNo} (${item.crdPssrNm})`"/>
                        </b-select>
                    </div>
                </div>
            </div>
            <div class="item desc-right">
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
            </div>
        </div>
        <!-- //검색조건 영역 -->

        <!-- 테이블 -->
        <div class="table-area">

            <div class="table-b">
                <div class="table-header">
                    <div class="table-name">
                        <h3 class="ico_table_name">
                            {{title}}&nbsp;&nbsp;
                            (<input type="checkbox" id="checkAll" v-model="checkAll"/>
                            <label for="checkAll" style="font-size: 12pt;">전체내역</label>)
                        </h3>
                    </div>
                    <div class="btn-wrap btn-type1 clearfix">
                        <button class="btn-size btn-excel" @click="saveExcel">엑셀 저장</button>
                    </div>
                </div>

                <div class="grid-wrap">
                    <div id="gridbox" class="grid-tbl-box grid-check"></div>
                    <div id="pagingbox" class="pagingbox"></div>
                </div>
            </div>

        </div>
        <!-- //테이블 -->

        <popup-grid ref="pop" :slipTypeCd="form.slipTypeCd" @returnValue="setCellValue"></popup-grid>

    </div>
</template>

<script>
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import _ from 'lodash'

    import PopupGrid from '@/components/PopupGrid.vue';

    export default {
        name: 'SlipList',
        components: { PopupGrid },
        mixins: [ mixin, mixinSlip ],
        data() {
            return {
                title: '법인카드 이용내역',
                cardNos: [],
                useDtlsStatCds: [],
                checkAll: false,
                form: {
                    slipTypeCd: 'E1',
                    // apprDateFrom: this.$moment().add(-1, 'month').startOf('month').format('YYYY-MM-DD'),
                    apprDateFrom: this.$moment().add(-2, 'year').startOf('month').format('YYYY-MM-DD'),
                    apprDateTo: this.$moment().format('YYYY-MM-DD'),
                    cardNo: '',
                    useDtlsStatCd: '',
                },
                popup: {
                    rId: -1,
                    cInd: -1,
                },
                grid: {
                    head: [
                        {id: 'no', type: 'ch', align: 'center', sort: 'na', value: '선택', width: 35 },
                        {id: 'postDt', type: 'dhxCalendar', align: 'center', sort: 'na', value: '회계일자', width: 90, hidden:true},
                        {id: 'baseDeptCd', type: 'ro', align: 'center', sort: 'na', value: '기준부서', width: 100, hidden:true},
                        {id: 'baseDeptNm', type: 'ed', align: 'center', sort: 'na', value: '기준부서명', width: 120, hidden:true},
                        {id: 'deptSrch', type: 'ro', align: 'center', sort: 'na', value: '#cspan', width: 40, hidden:true},
                        {id: 'stnAcctCd', type: 'ro', align: 'center', sort: 'na', value: '계정코드', width: 100, hidden:true},
                        {id: 'stnAcctNm', type: 'ed', align: 'center', sort: 'na', value: '계정명', width: 150, hidden:true},
                        {id: 'acctSrch', type: 'ro', align: 'center', sort: 'na', value: '#cspan', width: 40, hidden:true},
                        {id: 'hdSgtxt', type: 'ed', align: 'center', sort: 'na', value: '적요', width: 220, hidden:true},
                        {id: 'useDtlsStatNm', type: 'ro', align: 'center', sort: 'na', value: '진행상태', width: 90},
                        {id: 'slipStatNm', type: 'ro', align: 'center', sort: 'na', value: '전표상태', width: 80},
                        {id: 'cardNo', type: 'ro', align: 'center', sort: 'na', value: '카드번호', width: 150},
                        {id: 'crdPssrNm', type: 'ro', align: 'center', sort: 'na', value: '소유자', width: 90},
                        {id: 'apprDate', type: 'ro', align: 'center', sort: 'na', value: '사용일자', width: 90},
                        {id: 'apprTime', type: 'ro', align: 'center', sort: 'na', value: '시각', width: 70},
                        {id: 'merchNm', type: 'ro', align: 'center', sort: 'na', value: '가맹점명', width: 150},
                        {id: 'purchTot', type: 'ron', align: 'right', sort: 'na', value: '금액', width: 120},
                        {id: 'apprAmt', type: 'ron', align: 'right', sort: 'na', value: '공급가액', width: 120},
                        {id: 'vat', type: 'ron', align: 'right', sort: 'na', value: '부가세액', width: 120},
                        {id: 'mccName', type: 'ro', align: 'center', sort: 'na', value: '업종', width: 120},
                        {id: 'etc3', type: 'ro', align: 'center', sort: 'na', value: '과세유형', width: 100},
                        {id: 'apprNo', type: 'ro', align: 'center', sort: 'na', value: '승인번호', width: 90},
                        {id: 'merchAddr', type: 'ro', align: 'center', sort: 'na', value: '가맹점주소', width: 300},
                        {id: 'procPeriod', type: 'ro', align: 'center', sort: 'na', value: '경비처리기한', width: 90},
                        {id: 'eaSlipNo', type: 'ro', align: 'center', sort: 'na', value: '전표번호', width: 120},
                        {id: 'useDtlsNo', type: 'ro', align: 'center', sort: 'na', value: '', hidden:true},
                        {id: 'crdPssrDeptCd', type: 'ro', align: 'center', sort: 'na', value: '', hidden:true},
                        {id: 'crdPssrDeptNm', type: 'ro', align: 'center', sort: 'na', value: '', hidden:true},
                        {id: 'slipStatCd', type: 'ro', align: 'center', sort: 'na', value: '', hidden:true},
                        {id: 'slipProcId', type: 'ro', align: 'center', sort: 'na', value: ''},
                    ],
                    data: [],
                },
            };
        },
        methods: {
            // 카드번호
            getCardNoCombo() {
                this.$http.get(`/api/card/combo`)
                    .then(response => {
                        this.cardNos = response.data;
                        _.forEach(this.cardNos, (o) => {
                            o.maskedCardNo = this.getFormattedCardNumber(o.cardNo);
                        });
                    });
            },
            // 처리상태
            getUseDtlsStatCombo() {
                this.$http.get(`/api/code/combo`, { params: {groupCd: "USE_DTLS_STAT_CD"} })
                    .then(response => {
                        this.useDtlsStatCds = response.data;
                    });
            },
            saveAll() {
                console.log("일괄저장")
                let targetList = [];
                let checkedRowIds = this.$refs.grid.getCheckedRows(0);
                if(checkedRowIds) {
                    _.forEach(checkedRowIds.split(","), (rId) => {
                        let eaSlipNo = this.$refs.grid.cells(rId,24).getValue();
                        // 신규인 경우에만 저장 허용!
                        if(eaSlipNo === '') {
                            targetList.push({
                                postDt: this.$refs.grid.cells(rId,1).getValue().toString().replace(/[-]/g, ''),
                                baseDeptCd: this.$refs.grid.cells(rId,2).getValue(),
                                stnAcctCd: this.$refs.grid.cells(rId,5).getValue(),
                                hdSgtxt: this.$refs.grid.cells(rId,8).getValue(),
                                useDtlsNo: this.$refs.grid.cells(rId,25).getValue()
                            });
                        }
                    });
                    this.$http.post(`/api/card/all`, targetList)
                        .then((response) => {
                            this.goSearch();
                        })
                        .catch((e) => {
                            console.error(e);
                        });
                } else {
                    this.$swal({ type: 'info', text: '일괄저장 대상을 선택해 주세요.' });
                }
            },
            doPrivateCost() {
                console.log("사적비용처리")
                let checkedRowIds = this.$refs.grid.getCheckedRows(0);
                let checkedUseDtlsNos = [];
                if(checkedRowIds) {
                    _.forEach(checkedRowIds.split(","), (rId) => checkedUseDtlsNos.push(this.$refs.grid.cells(rId,25).getValue()));
                    console.log(checkedUseDtlsNos)
                    this.$http.post(`/api/card/private`, checkedUseDtlsNos)
                        .then(response => {
                            this.goSearch();
                        });
                }
            },
            saveExcel() {
                this.downloadExcel(this.$refs.grid);
            },
            drawGrid() {
                const iljinGrid = new dhtmlXGridObject('gridbox');
                iljinGrid.setNumberFormat("0,000",16,'.',',');
                iljinGrid.setNumberFormat("0,000",17,'.',',');
                iljinGrid.setNumberFormat("0,000",18,'.',',');
                iljinGrid.enableAutoWidth(false);
                iljinGrid.enableAutoHeight(false);
                iljinGrid.enableAlterCss('even', 'uneven');
                iljinGrid.setDateFormat('%Y-%m-%d','%Y%m%d');
                iljinGrid.enableEditEvents(true,false,true);  // click, dblclick, F2key
                // iljinGrid.setEditable(false);
                iljinGrid.init();
                iljinGrid.parse(this.grid, 'js');
                iljinGrid.attachEvent('onRowDblClicked', (rId, cInd) => {
                    if(cInd > 8) {
                        let eaSlipNo = this.$refs.grid.cells(rId,24).getValue();
                        let useDtlsNo = this.$refs.grid.cells(rId,25).getValue();
                        let slipStatCd = this.$refs.grid.cells(rId,28).getValue();
                        if(eaSlipNo) {
                            this.goPage({ eaSlipNo, slipStatCd });
                        } else {
                            this.goPage({ useDtlsNo });
                        }
                    }
                });
                iljinGrid.attachEvent("onRowSelect", (rId, cInd) => {
                    console.log("셀위치 [", rId, cInd, "]", this.$refs.grid.cells(rId,25).getValue())
                    this.popup.rId = rId;
                    this.popup.cInd = cInd;
                });
                iljinGrid.attachEvent("onCheck", (rId, cInd, state) => {
                    console.log("체크 [", rId, cInd, state, "]")
                    // 수정모드 활성
                    this.setDisabled(this.$refs.grid, rId, [1, 3, 6, 8], !state);
                    // 검색버튼
                    if(state) {
                        this.checkAll = true;
                        this.setCellClassName(this.$refs.grid, rId, [1,3,4,6,7,8], 'bg-lightpink');
                        this.$refs.grid.cells(rId,4).setValue("<button class='icon fl_right' onclick='popCctr();'><i class='fas fa-search'></i></button>");
                        this.$refs.grid.cells(rId,7).setValue("<button class='icon fl_right' onclick='popAccount();'><i class='fas fa-search'></i></button>");
                        // 신규일 경우, 오늘날짜 기본셋팅
                        if(this.$refs.grid.cells(rId,1).getValue() === '') {
                            this.$refs.grid.cells(rId,1).setValue(this.$moment().format('YYYYMMDD'));
                        }
                        // 신규일 경우, 카드소유자부서로 기본셋팅
                        if(this.$refs.grid.cells(rId,2).getValue() === '') {
                            this.$refs.grid.cells(rId,2).setValue(this.$refs.grid.cells(rId,26).getValue());
                            this.$refs.grid.cells(rId,3).setValue(this.$refs.grid.cells(rId,27).getValue());
                        }
                    } else {
                        this.setCellClassName(this.$refs.grid, rId, [1,3,4,6,7,8], 'bg-lightpink', true);
                        this.$refs.grid.cells(rId,4).setValue("");
                        this.$refs.grid.cells(rId,7).setValue("");
                    }
                });
                this.$refs.grid = iljinGrid;
            },
            goPage(params) {
                console.log("페이지이동", params)
                let targetName = (params.eaSlipNo === undefined || params.slipStatCd === '10') ? 'cardSlipReg' : 'billSlipMng';
                this.$router.push({ name: targetName, params: params });
            },
            refreshGrid() {
                this.$refs.grid.callEvent('ongridreconstructed',[]);
            },
            calendarLoad() {
                // 사용일자
                const iljinCalendar1 = new dhtmlXCalendarObject('apprDateFrom');
                iljinCalendar1.setDate(new Date());
                iljinCalendar1.hideTime();
                iljinCalendar1.attachEvent('onChange', (v) => this.form.apprDateFrom = this.$refs.apprDateFrom.getFormatedDate());
                iljinCalendar1.attachEvent("onButtonClick", (d) => { if (d === null) { this.form.apprDateFrom = this.$refs.apprDateFrom.getFormatedDate() } });
                this.$refs.apprDateFrom = iljinCalendar1;
                // 사용일자
                const iljinCalendar2 = new dhtmlXCalendarObject('apprDateTo');
                iljinCalendar2.setDate(new Date());
                iljinCalendar2.hideTime();
                iljinCalendar2.attachEvent('onChange', (v) => this.form.apprDateTo = this.$refs.apprDateTo.getFormatedDate());
                iljinCalendar2.attachEvent("onButtonClick", (d) => { if (d === null) { this.form.apprDateTo = this.$refs.apprDateTo.getFormatedDate() } });
                this.$refs.apprDateTo = iljinCalendar2;
            },
            goSearch() {
                console.log("조회...")
                const param = JSON.parse(JSON.stringify(this.form));
                const stripFields = ['apprDateFrom','apprDateTo'];
                _.forEach(stripFields, (name) => param[name] = this.toPure(param[name]));

                if(!this.validation(param)) return;

                this.$refs.grid.clearAll();
                this.$store.commit('loading');
                this.$http.get(`/api/card/list`, { params: param })
                    .then(response => {
                        // this.$set(this.grid.data, 0, response.data);
                        if(response.data) {
                            this.grid.data = response.data;
                            // set data
                            this.setGridPaging(this.$refs.grid, response.data);
                            this.$refs.grid.parse(this.grid,"js");
                            this.toggleHiddenColumn(!this.checkAll);
                            this.$refs.grid.attachHeader(["합계","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan","#cspan"
                                ,"#stat_total","#stat_total","#stat_total"
                                ,"","#cspan","#cspan","#cspan","#cspan","#cspan","","",""]);
                            this.setGridStyle();
                            this.refreshGrid();
                        }
                        // this.$store.commit('finish');
                    });
            },
            toggleHiddenColumn(hide) {
                this.setColumnHidden(this.$refs.grid, [1,2,3,4,5,6,7,8], hide);
            },
            validation(param) {
                if(!param.apprDateFrom || !param.apprDateTo)    { this.$swal({ type: 'warning', text: '사용일자를 입력해 주세요.' }); return false; }

                return true;
            },
            setGridStyle() {
                this.doLineAction(this.$refs.grid, {
                    all: (grid,rId) => {
                        // 날짜
                        this.setDateFormat(grid, rId, [13, 23]);
                        this.setTimeFormat(grid, rId, 14);
                        // 정렬
                        this.setCellClassName(grid, rId, [8, 15, 22], 'tal');
                        this.setCellClassName(grid, rId, [16, 17, 18], 'tar');
                        // 수정모드 비활성
                        this.setDisabled(this.$refs.grid, rId, [1, 3, 6, 8], true);
                        // 카드번호
                        const cardNo = this.getFormattedCardNumber(grid.cells(rId,11).getValue());
                        grid.cells(rId,11).setValue(cardNo);
                    }
                });

            },
            setCellValue(data) {
                console.log(data)
                if(this.$refs.grid) {
                    if(data.name === 'account') {
                        this.$refs.grid.cells(this.popup.rId,5).setValue(data.acctCd);
                        this.$refs.grid.cells(this.popup.rId,6).setValue(data.acctNm);
                    } else if(data.name === 'cctr') {
                        this.$refs.grid.cells(this.popup.rId,2).setValue(data.cctrCd);
                        this.$refs.grid.cells(this.popup.rId,3).setValue(data.cctrNm);
                    }
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
        watch: {
            checkAll(value) {
                console.log("checkAll", value)
                this.toggleHiddenColumn(!value);
            }
        },
        mounted() {
            window.popCctr = () => this.$refs.pop.popCctr(this.popup.rId, this.popup.cInd);
            window.popAccount = () => this.$refs.pop.popAccount(this.popup.rId, this.popup.cInd);
            this.setCallPageByParam()
            this.calendarLoad()
            this.getCardNoCombo()
            this.getUseDtlsStatCombo()
            this.drawGrid()
            this.goSearch()
        }
    };
</script>

<style scoped>
    .gridbox{height: 465px!important;}
    .gridbox .objbox{height:400px!important;}

    .desc-content:after{clear: both; content:''; display: block;}
    .btn-wrap{margin-bottom:20px;}
    .desc-content{border:2px solid #9db6c9; background:#f9fafc; margin:0 0 20px 0; border-radius:4px; padding:15px 2%; clear: both;}
    .desc-content .item{float:left;}
    .desc-content .item .desc-item{position: relative; padding-left:82px; margin-bottom:8px;}
    .desc-content .item .desc-item:last-child{margin-bottom:0; height:25px;}
    .desc-content .item .desc-item .tit{position: absolute; left:0; }
    .desc-content .item .desc-item .label-tit{font-family:'NotoM'; color:#222; font-size:15px; }
    .desc-content .item.desc-left .desc-item{padding-left:90px;}
    .desc-content .item.desc-left .desc-item .desc:after{clear:both; content:''; display:block;}
    .desc-content .item.desc-left .desc-item .desc .datepicker{float:left;}
    .desc-content .item.desc-left .desc-item .desc span.wave{float:left; padding:0 6px;}
    .desc-content .item.desc-left .desc-item .td-s-thumb.search-area:after{clear:both; content:''; display:block;}
    .desc-content .item.desc-left .desc-item .td-s-thumb.search-area input,
    .desc-content .item.desc-left .desc-item .td-s-thumb.search-area .ip-box{float:left;}
    .desc-content .item.desc-left .desc-item .desc.select select{width:70%;}
    .desc-content .item.desc-left{width:35%; padding-right:40px;}
    .desc-content .item.desc-center{width:35%; padding-right:40px;}
    .desc-content .item.desc-right{width:30%; }
    .search-area input{position:relative;}
    .search-area .icon{position:absolute; right:8px; top:1px; z-index:100; cursor:pointer; font-size:16px; color:#555;}
    .search-border .td-s-thumb{position:relative; display:inline-block; }
    .search-border .td-s-thumb.search-area > input,
    .search-border .td-s-thumb.search-area > .ip-box
    .search-border .td-s-thumb.search-area > button{float:left;}
    .search-border .td-s-thumb.search-area .ip-box.ip-box-w02{width:60%; margin-left:6px;}
    .remove_text{margin-left: 0;}
    .contents div.gridbox_material.gridbox .xhdr{border-bottom:1px solid #dfdfdf;}

    @media (max-width:1580px) {
        .search-border .td-s-thumb.search-area .ip-box.ip-box-w02{width:50%;}
    }
</style>
