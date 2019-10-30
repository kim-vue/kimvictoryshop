<template>
    <layout>
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
                            class="fas fa-check"></i></span> 해제
                    </button>
                </div>
            </div>
            <div v-if="hiddenCheck != 'Y'" class="inner-box" style="height: 290px">

                <div class="table-area">
                    <div class="table-a">
                        <table id="basic" class="table">
                            <colgroup>
                                <col width="20%">
                                <col width="80%">
                            </colgroup>
                            <tbody>
                            <tr>
                                <th class="tp-a">위임자</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 200px">
                                        <input class="input input-bg" type="text" style="width:65px;"
                                               v-model="form.adlgId"
                                               disabled>
                                        <div class="ip-box ip-box-w02">
                                            <input class="input" type="text" v-model="form.adlgNm" @input="initAdlgEmp"
                                                   @keydown.enter="popAdlgEmp">
                                            <button class="icon is-right" @click="popAdlgEmp(true)"><i
                                                    class="fas fa-search"></i>
                                            </button>
                                        </div>
                                    </div>
                                </td>
                            </tr>

                            <tr>
                                <th class="tp-a">수임자</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 200px">
                                        <input class="input input-bg" type="text" style="width:65px;"
                                               v-model="form.actId"
                                               disabled>
                                        <div class="ip-box ip-box-w02">
                                            <input class="input" type="text" v-model="form.actNm" @input="initActEmp"
                                                   @keydown.enter="popActEmp">
                                            <button class="icon is-right" @click="popActEmp(true)"><i
                                                    class="fas fa-search"></i>
                                            </button>
                                        </div>
                                    </div>
                                </td>
                            </tr>

                            <tr>
                                <th class="tp-a"> 위임기간</th>
                                <td>
                                    <div class="datepicker w-type-ymd02" style="float: left;">
                                        <dhx-calendar class="input ddate sDate" v-model="form.adlgStrDt" />
                                    </div>
                                    <span style="float: left; padding: 5px 6px;">~</span>
                                    <div class="datepicker w-type-ymd02" style="float: left;">
                                        <dhx-calendar class="input ddate sDate" v-model="form.adlgEndDt" />
                                    </div>
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div v-else class="inner-box" style="height: 290px">
                <div class="table-area">
                    <div class="table-a">
                        <table id="basic" class="table">
                            <colgroup>
                                <col width="20%">
                                <col width="80%">
                            </colgroup>
                            <tbody>
                            <tr>
                                <th class="tp-a">위임자</th>
                                <td>
                                    {{this.adlgNm}}
                                </td>
                            </tr>

                            <tr>
                                <th class="tp-a">수임자</th>
                                <td>
                                    {{this.actNm}}
                                </td>
                            </tr>

                            <tr>
                                <th class="tp-a"> 위임기간</th>
                                <td>
                                    <div class="datepicker w-type-ymd02" style="float: left;">
                                        <dhx-calendar class="input ddate sDate" v-model="form.adlgStrDt" />
                                    </div>
                                    <span style="float: left; padding: 5px 6px;">~</span>
                                    <div class="datepicker w-type-ymd02" style="float: left;">
                                        <dhx-calendar class="input ddate sDate" v-model="form.adlgEndDt" />
                                    </div>
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <b-modal parent:this :active.sync="showEmpModal1" has-modal-card @receive="receiveAdlgEmp">
                <emp :param="form.adlgNm"></emp>
            </b-modal>
            <b-modal parent:this :active.sync="showEmpModal2" has-modal-card @receive="receiveActEmp">
                <emp :param="form.actNm"></emp>
            </b-modal>
        </div>
    </layout>
</template>

<script>
    import Layout from '@/components/ModalSlot.vue';
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';

    import DhxCalendar from '@/components/DhxCalendar.vue'
    import Emp from '@/components/Emp.vue';

    export default {
        name: 'ApprMndPop',
        props: ['adlgId', 'adlgNm', 'actId', 'actNm', 'adlgSeq', 'hiddenDtmFr', 'hiddenDtmTo', 'hiddenCheck'],
        mixins: [mixin, mixinSlip],
        components: {Layout, Emp, DhxCalendar},
        data() {
            return {
                title: '위임 처리',
                form: {
                    adlgId: '',
                    adlgNm: '',
                    actId: '',
                    actNm: '',
                    adlgSeq: '',
                    adlgStrDt: this.$moment().format('YYYY-MM-DD'),
                    adlgEndDt: this.$moment().format('YYYY-MM-DD'),
                    hiddenCheck: '',
                },
                returnObject: {},
                showEmpModal1: false,
                showEmpModal2: false,
            }
        },
        methods:
            {
                save() {
                    if (!this.form.adlgId) {
                        this.$swal({type: 'warning', text: '위임자를 지정해 주세요.'});
                        return false;
                    }
                    if (!this.form.actId) {
                        this.$swal({type: 'warning', text: '수임자를 지정해 주세요.'});
                        return false;
                    }
                    if (this.form.adlgId===this.form.actId) {
                        this.$swal({type: 'warning', text: '위임자와 동일한 수임자는 지정할 수 없습니다.'});
                        return false;
                    }
                    if (this.form.adlgStrDt > this.form.adlgEndDt) {
                        this.$swal({type: 'warning', text: '위임시작일자와 위임종료일자의 지정이 잘못되었습니다.'});
                        return false;
                    }

                    this.$swal({
                        type: 'info',
                        text: `위임설정을 저장합니다. 계속 하시겠습니까?`,
                        showCancelButton: true,
                        confirmButtonText: '예',
                        cancelButtonText: '아니오',
                    }).then((result) => {
                        if (result.value) {
                            this.$http.post(`/api/appr/delegating/save`, {
                                adlgStrDt: this.toPure(this.form.adlgStrDt),
                                adlgEndDt: this.toPure(this.form.adlgEndDt),
                                adlgId: this.form.adlgId,
                                actId: this.form.actId,
                                adlgSeq: this.form.adlgSeq
                            }).then((response) => {
                                this.$swal({type: 'info', text: '저장되었습니다.'});
                                this.doReturnObject(1);
                            }).catch((e) => {
                                this.$swal({type: 'error', text: e.response.data.message});
                                console.error(e);
                            });
                        }
                    });
                },
                cancel() {
                    this.$swal({
                        type: 'warning',
                        text: `위임을 해제합니다. 계속 하시겠습니까?`,
                        showCancelButton: true,
                        confirmButtonText: '예',
                        cancelButtonText: '아니오',
                    }).then((result) => {
                        if (result.value) {
                            this.$http.post(`/api/appr/delegating/cancel`, {
                                adlgId: this.form.adlgId,
                                actId: this.form.actId,
                                adlgSeq: this.form.adlgSeq
                            }).then((response) => {
                                console.log(response.data);
                                this.doReturnObject(1);
                            }).catch((e) => {
                                console.error(e);
                            });
                        }
                    });
                },
                doReturnObject(rId) {
                    this.returnObject.name = '';
                    this.$parent.$emit('receive', this.returnObject);
                    this.closeModal();
                },
                closeModal() {
                    this.$parent.close();
                },
                popAdlgEmp(clear) {
                    console.log('직원팝업');
                    if (clear === true) {
                        this.form.adlgId = '';
                        this.form.adlgNm = '';
                    }
                    this.showEmpModal1 = true;
                },
                popActEmp(clear) {
                    console.log('직원팝업');
                    if (clear === true) {
                        this.form.actId = '';
                        this.form.actNm = '';
                    }
                    this.showEmpModal2 = true;
                },
                initAdlgEmp(force) {
                    if (force === true) this.form.adlgNm = '';
                    if (this.form.adlgNm === '') this.form.adlgId = '';
                },
                initActEmp(force) {
                    if (force === true) this.form.actNm = '';
                    if (this.form.actNm === '') this.form.actId = '';
                },
                receiveAdlgEmp(obj) {
                    this.form.adlgId = obj.empNo;
                    this.form.adlgNm = obj.empNm;
                },
                receiveActEmp(obj) {
                    this.form.actId = obj.empNo;
                    this.form.actNm = obj.empNm;
                },
            }
        ,
        mounted() {
            if(this.hiddenCheck =='Y'){
                this.form.adlgStrDt = this.hiddenDtmFr;
                this.form.adlgEndDt = this.hiddenDtmTo;
                this.form.adlgId = this.adlgId;
                this.form.adlgNm = this.adlgNm;
                this.form.actId = this.actId;
                this.form.actNm = this.actNm;
                this.form.adlgSeq = this.adlgSeq;
                this.form.hiddenCheck = this.hiddenCheck;
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
