<template>
    <layout style="width: 1000px;">
        <span slot="header">{{title}}<button class="btn-pop-close delete" aria-label="close"
                                             @click="closeModal"></button></span>
        <div slot="content">
            <div>
                <div v-if="hiddenCheck != 'Y'" class="btn-wrap btn-type1 clearfix">
                    <button class="btn-size btn-blue fl_right" @click="save"><span class="btn-icon"><i
                            class="fas fa-check"></i></span> 저장
                    </button>
                </div>
                <div v-else class="btn-wrap btn-type1 clearfix fl_right">
                    <button class="btn-size btn-blue" @click="save"><span class="btn-icon"><i
                            class="fas fa-check"></i></span> 저장
                    </button>
                    <button class="btn-size btn-gray" @click="cancel"><span class="btn-icon"><i
                            class="fas fa-check"></i></span> 삭제
                    </button>
                </div>
            </div>
            <div class="inner-box" style="height: 310px">

                <div class="table-area">
                    <div class="table-a">
                        <table id="basic" class="table">
                            <colgroup>
                                <col width="15%">
                                <col width="35%">
                                <col width="15%">
                                <col width="35%">
                            </colgroup>
                            <tbody>
                            <tr>
                                <th class="tp-a">문서유형</th>
                                <td>
                                    <div v-if="hiddenCheck !== 'Y'" class="td-s-thumb search-area" style="width: 200px">
                                        <b-select class="select is-fullwidth" v-model="form.docTypeCd">
                                            <option value=''>==선택==</option>
                                            <option
                                                    v-for="item in docTypes"
                                                    :key="item.key"
                                                    :value="item.key"
                                                    v-text="item.value"/>
                                        </b-select>
                                    </div>
                                    <div v-else class="td-s-thumb search-area" style="width: 200px">
                                        {{this.form.docTypeNm}}
                                    </div>
                                </td>

                                <th class="tp-a">상세유형</th>
                                <td v>
                                    <div v-if="hiddenCheck !== 'Y'" class="td-s-thumb search-area" style="width: 200px">
                                        <b-select  v-if="this.form.docTypeCd === 'SLIP'" class="select is-fullwidth" v-model="form.dtlTypeCd">
                                            <option value=''>==선택==</option>
                                            <option
                                                    v-for="item in slipTypes"
                                                    :key="item.key"
                                                    :value="item.key"
                                                    v-text="item.value"/>
                                        </b-select>
                                        <b-select  v-else-if="this.form.docTypeCd === 'BDGT'" class="select is-fullwidth" v-model="form.dtlTypeCd">
                                            <option value=''>==선택==</option>
                                            <option
                                                    v-for="item in brwTypes"
                                                    :key="item.key"
                                                    :value="item.key"
                                                    v-text="item.value"/>
                                        </b-select>
                                        <b-select  v-else class="select is-fullwidth" v-model="form.dtlTypeCd">
                                            <option value=''>==선택==</option>
                                        </b-select>
                                    </div>
                                    <div v-else class="td-s-thumb search-area" style="width: 200px">
                                        {{this.form.dtlTypeNm}}
                                    </div>
                                </td>
                            </tr>

                            <tr>
                                <th class="tp-a">사용여부</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 100px; float: left">
                                        <b-select v-model="form.useYn">
                                            <option value=''>==선택==</option>
                                            <option value='Y'>사용</option>
                                            <option value='N'>미사용</option>
                                        </b-select>
                                    </div>
                                    <div v-if="hiddenCheck == 'Y'" style="float: left; padding-top: 4px">
                                        규정순번 : {{this.form.ruleSeq}}
                                    </div>
                                </td>
                                <th class="tp-a">통화코드</th>
                                <td>
                                    <div v-if="hiddenCheck !== 'Y'" class="td-s-thumb search-area" style="width: 200px">
                                        <b-select class="select is-fullwidth" v-model="form.curCd">
                                            <option value=''>==선택==</option>
                                            <option
                                                    v-for="item in curTypes"
                                                    :key="item.key"
                                                    :value="item.key"
                                                    v-text="item.value"/>
                                        </b-select>
                                    </div>
                                    <div v-else class="td-s-thumb search-area" style="width: 200px">
                                        {{this.form.curNm}}
                                    </div>
                                </td>
                            </tr>

                            <tr>
                                <th>상한금액</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 200px">
                                        <input class="input Rt-M tar" type="text" v-model="form.maxAmt"/>
                                    </div>
                                </td>
                                <th class="tp-a">결재유형</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 200px">
                                        <b-select class="select is-fullwidth" v-model="form.apprTypeCd">
                                            <option value=''>==선택==</option>
                                            <option
                                                    v-for="item in apprTypes"
                                                    :key="item.key"
                                                    :value="item.key"
                                                    v-text="item.value"/>
                                        </b-select>
                                    </div>
                                </td>
                            </tr>

                            <tr>
                                <th class="tp-a">고정여부</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 200px">
                                        <b-select class="select is-fullwidth" v-model="form.fixYn">
                                            <option value=''>==선택==</option>
                                            <option value='Y'>고정</option>
                                            <option value='N'>비고정</option>
                                        </b-select>
                                    </div>
                                </td>
                                <th class="tp-a">결재자구분</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 200px">
                                        <b-select class="select is-fullwidth" v-model="form.aprverClassCd">
                                            <option value=''>==선택==</option>
                                            <option
                                                    v-for="item in aprverClassTypes"
                                                    :key="item.detailCd"
                                                    :value="item.detailCd"
                                                    v-text="item.detailNm"/>
                                        </b-select>
                                    </div>
                                </td>
                            </tr>

                            <tr>
                                <th>결재자구분값</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 200px">
                                        <input class="input" type="text" v-model="form.aprverClassVal"/>
                                    </div>
                                </td>
                                <th>비고</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 200px">
                                        <input class="input" type="text" v-model="form.remark"/>
                                    </div>
                                </td>
                            </tr>

                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

        </div>
    </layout>
</template>

<script>
    import Layout from '@/components/ModalSlot.vue';
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';

    export default {
        name: 'ApprRulePop',
        props: ['docTypeNm',
                'docTypeCd',
                'dtlTypeNm',
                'dtlTypeCd',
                'useYn',
                'ruleSeq',
                'curNm',
                'curCd',
                'maxAmt',
                'apprTypeNm',
                'apprTypeCd',
                'fixYn',
                'aprverClassNm',
                'aprverClassVal',
                'aprverClassCd',
                'remark',
                'hiddenCheck'],
        mixins: [mixin, mixinSlip],
        components: {Layout},
        data() {
            return {
                title: '규정 관리',
                docTypes: [],
                slipTypes: [],
                brwTypes: [],
                curTypes: [],
                apprTypes: [],
                aprverClassTypes: [],
                form: {
                    docTypeNm: '',
                    docTypeCd: 'SLIP',
                    dtlTypeNm: '',
                    dtlTypeCd: '',
                    useYn: 'Y',
                    ruleSeq: '',
                    curNm: '',
                    curCd: 'KRW',
                    maxAmt: '',
                    apprTypeNm: '',
                    apprTypeCd: '20',
                    fixYn: 'Y',
                    aprverClassNm: '',
                    aprverClassVal: '',
                    aprverClassCd: 'P',
                    remark: '',
                },
                returnObject: {},
                showEmpModal1: false,
                showEmpModal2: false,
            }
        },
        methods:
            {
                getDocTypeCombo() {
                    this.$http.get(`/api/code/combo`, {params: {groupCd: "DOC_TYPE_CD"}})
                        .then(response => {
                            this.docTypes = response.data;
                        });
                },
                getSlipTypeCombo() {
                    this.$http.get(`/api/code/combo`, {params: {groupCd: "SLIP_TYPE_CD"}})
                        .then(response => {
                            this.slipTypes = response.data;
                        });
                },
                getBrwTypeCombo() {
                    this.$http.get(`/api/code/combo`, {params: {groupCd: "BRW_TYPE_CD"}})
                        .then(response => {
                            this.brwTypes = response.data;
                        });
                },
                getCurTypeCombo() {
                    this.$http.get(`/api/code/combo`, {params: {groupCd: "CUR_CD"}})
                        .then(response => {
                            this.curTypes = response.data;
                        });
                },
                getApprTypeCombo() {
                    this.$http.get(`/api/code/combo`, {params: {groupCd: "APPR_TYPE_CD", remark1: "Y"}})
                        .then(response => {
                            this.apprTypes = response.data;
                        });
                },
                geAprverClassTypeCombo() {
                    this.$http.get(`/api/code/detail`, {params: {groupCd: "APRVER_CLASS_CD"}})
                        .then(response => {
                            this.aprverClassTypes = response.data;
                            console.log(this.aprverClassTypes)
                        });
                },
                save() {
                    if (!this.validation()) return;
                    this.$swal({
                        type: 'warning',
                        text: `전결규정을 저장합니다. 계속 하시겠습니까?`,
                        showCancelButton: true,
                        confirmButtonText: '예',
                        cancelButtonText: '아니오',
                    }).then((result) => {
                        if (result.value) {
                            const param = JSON.parse(JSON.stringify(this.form));
                            const stripFields = ['maxAmt'];
                            _.forEach(stripFields, (name) => param[name] = this.toPure(param[name]));

                            //if(!this.validation(param)) return;

                            this.$http.post(`/api/appr/rule`, [param
                            ]).then((response) => {
                                console.log(response.data);
                                this.doReturnObject(1);
                            }).catch((e) => {
                                console.error(e);
                            });
                        }
                    });
                },
                cancel() {
                    this.$swal({
                        type: 'warning',
                        text: `전결규정을 삭제합니다. 계속 하시겠습니까?`,
                        showCancelButton: true,
                        confirmButtonText: '예',
                        cancelButtonText: '아니오',
                    }).then((result) => {
                        if (result.value) {
                            const param = JSON.parse(JSON.stringify(this.form));

                            this.$http.post(`/api/appr/deleteRules`, [param
                            ]).then((response) => {
                                console.log(response.data);
                                this.doReturnObject(1);
                            }).catch((e) => {
                                console.error(e);
                            });
                        }
                    });
                },
                validation() {
                    const ruleInfo = JSON.parse(JSON.stringify(this.form));
                    const stripFields = ['maxAmt'];
                    _.forEach(stripFields, (name) => ruleInfo[name] = this.toPure(ruleInfo[name]));

                    if (!ruleInfo.docTypeCd) {
                        this.$swal({type: 'warning', text: '문서유형을 선택해 주세요.'});
                        return false;
                    }
                    if (!ruleInfo.dtlTypeCd) {
                        this.$swal({type: 'warning', text: '상세유형을 선택해 주세요.'});
                        return false;
                    }
                    if (!ruleInfo.useYn) {
                        this.$swal({type: 'warning', text: '사용여부를 선택해 주세요.'});
                        return false;
                    }
                    if (!ruleInfo.curCd) {
                        this.$swal({type: 'warning', text: '통화코드을 선택해 주세요.'});
                        return false;
                    }
                    if (_.toInteger(ruleInfo.maxAmt)<0) {
                        this.$swal({type: 'warning', text: '상한금액에 0보다 큰 금액을 넣어주세요.'});
                        return false;
                    }
                    if (!ruleInfo.apprTypeCd) {
                        this.$swal({type: 'warning', text: '결재유형을 선택해 주세요.'});
                        return false;
                    }
                    if (!ruleInfo.fixYn) {
                        this.$swal({type: 'warning', text: '고정여부를 선택해 주세요.'});
                        return false;
                    }

                    const obj = this.aprverClassTypes.find(x => x.detailCd === ruleInfo.aprverClassCd);
                    if(obj) {
                        if (obj.remark1==='C') {
                            if (!ruleInfo.aprverClassVal) {
                                this.$swal({type: 'warning', text: '결재자구분값을 입력해 주세요.'});
                                return false;
                            }
                        }
                    }
                    return true;
                },
                doReturnObject(rId) {
                    this.returnObject.name = '';
                    this.$parent.$emit('receive', this.returnObject);
                    this.closeModal();
                },
                closeModal() {
                    this.$parent.close();
                },
            }
        ,
        mounted() {
            console.log("팝업 마운트 : " + this.docTypeCd);
            this.getDocTypeCombo();
            this.getSlipTypeCombo();
            this.getBrwTypeCombo();
            this.getCurTypeCombo();
            this.getApprTypeCombo();
            this.geAprverClassTypeCombo();

            if(this.hiddenCheck === 'Y') {
                this.form.docTypeNm = this.docTypeNm;
                this.form.docTypeCd = this.docTypeCd;
                this.form.dtlTypeNm = this.dtlTypeNm;
                this.form.dtlTypeCd = this.dtlTypeCd;
                this.form.useYn = this.useYn;
                this.form.ruleSeq = this.ruleSeq;
                this.form.curNm = this.curNm;
                this.form.curCd = this.curCd;
                this.form.maxAmt = this.maxAmt;
                this.form.apprTypeNm = this.apprTypeNm;
                this.form.apprTypeCd = this.apprTypeCd;
                this.form.fixYn = this.fixYn;
                this.form.aprverClassNm = this.aprverClassNm;
                this.form.aprverClassVal = this.aprverClassVal;
                this.form.aprverClassCd = this.aprverClassCd;
                this.form.remark = this.remark;
            }
        }
        ,
        watch: {
            'form.maxAmt'(value) {
                this.form.maxAmt = this.$filters.number(value);
            },
            'form.docTypeCd'(){
                if(this.hiddenCheck !== 'Y')
                    this.form.dtlTypeCd=''
            }
        }
    }
</script>

<style scoped>
    div#gridbox {
        width: 100%;
        height: 100%;
        min-height: 300px;
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
