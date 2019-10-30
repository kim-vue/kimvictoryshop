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
                                <th class="tp-a">카드소유자</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 200px">
                                        <input class="input input-bg" type="text" style="width:65px;"
                                               v-model="form.cdlgId"
                                               disabled>
                                        <div class="ip-box ip-box-w02">
                                            <input class="input" type="text" v-model="form.cdlgNm" @input="initCdlgEmp"
                                                   @keydown.enter="popCdlgEmp">
                                            <button class="icon is-right" @click="popCdlgEmp(true)"><i
                                                    class="fas fa-search"></i>
                                            </button>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <th class="tp-a">카드번호</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 250px">
                                        <b-select class="select is-fullwidth" v-model="form.crdNo">
                                            <option value=''>==선택==</option>
                                            <option
                                                    v-for="item in crdList"
                                                    :key="item.crdNo"
                                                    :value="item.crdNo"
                                                    v-text="item.maskedCrdNo"/>
                                        </b-select>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <th class="tp-a">수임자</th>
                                <td>
                                    <div class="td-s-thumb search-area" style="width: 200px">
                                        <input class="input input-bg" type="text" style="width:65px;"
                                               v-model="form.nomnId"
                                               disabled>
                                        <div class="ip-box ip-box-w02">
                                            <input class="input" type="text" v-model="form.nomnNm" @input="initNomnEmp"
                                                   @keydown.enter="popNomnEmp">
                                            <button class="icon is-right" @click="popNomnEmp(true)"><i
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
                                        <dhx-calendar class="input ddate sDate" v-model="form.cdlgStrDt" />
                                    </div>
                                    <span style="float: left; padding: 5px 6px;">~</span>
                                    <div class="datepicker w-type-ymd02" style="float: left;">
                                        <dhx-calendar class="input ddate sDate" v-model="form.cdlgEndDt" />
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
                                <th class="tp-a">카드소유자</th>
                                <td>
                                    {{this.form.cdlgNm}}
                                </td>
                            </tr>
                            <tr>
                                <th class="tp-a">카드번호</th>
                                <td>
                                    {{this.form.crdNo}}
                                </td>
                            </tr>
                            <tr>
                                <th class="tp-a">수임자</th>
                                <td>
                                    {{this.form.nomnNm}}
                                </td>
                            </tr>
                            <tr>
                                <th class="tp-a"> 위임기간</th>
                                <td>
                                    <div class="datepicker w-type-ymd02" style="float: left;">
                                        <dhx-calendar class="input ddate sDate" v-model="form.cdlgStrDt" />
                                    </div>
                                    <span style="float: left; padding: 5px 6px;">~</span>
                                    <div class="datepicker w-type-ymd02" style="float: left;">
                                        <dhx-calendar class="input ddate sDate" v-model="form.cdlgEndDt" />
                                    </div>
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <b-modal parent:this :active.sync="showEmpModal1" has-modal-card @receive="receiveCdlgEmp">
                <emp :param="form.cdlgNm"></emp>
            </b-modal>
            <b-modal parent:this :active.sync="showEmpModal2" has-modal-card @receive="receiveNomnEmp">
                <emp :param="form.nomnNm"></emp>
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
    import _ from 'lodash'

    export default {
        name: 'CardMndPop',
        props: ['cdlgId','cdlgNm','nomnId','nomnNm','cdlgSeq','hiddenDtmFr','hiddenDtmTo','hiddenCrdNo','hiddenCheck'],
        mixins: [mixin, mixinSlip],
        components: {Layout, Emp, DhxCalendar},
        data() {
            return {
                title: '위임 처리',
                crdList: [],
                form: {
                    crdNo: '',
                    cdlgId: '',
                    cdlgNm: '',
                    nomnId: '',
                    nomnNm: '',
                    cdlgSeq: '',
                    cdlgStrDt: this.$moment().format('YYYY-MM-DD'),
                    cdlgEndDt: this.$moment().format('YYYY-MM-DD'),
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
                    if (!this.form.cdlgId) {
                        this.$swal({type: 'warning', text: '카드소유자를 지정해 주세요.'});
                        return false;
                    }
                    if (!this.form.crdNo) {
                        this.$swal({type: 'warning', text: '카드를 선택해 주세요.'});
                        return false;
                    }
                    if (!this.form.nomnId) {
                        this.$swal({type: 'warning', text: '수임자를 지정해 주세요.'});
                        return false;
                    }
                    if (this.form.cdlgId===this.form.nomnId) {
                        this.$swal({type: 'warning', text: '카드소유자와 동일한 수임자를 지정할 수 없습니다.'});
                        return false;
                    }
                    if (this.form.cdlgStrDt > this.form.cdlgEndDt) {
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
                            this.$http.post(`/api/card/delegating/save`, {
                                cdlgStrDt: this.toPure(this.form.cdlgStrDt),
                                cdlgEndDt: this.toPure(this.form.cdlgEndDt),
                                crdNo: this.toPure(this.form.crdNo),
                                cdlgId: this.form.cdlgId,
                                nomnId: this.form.nomnId,
                                cdlgSeq: this.form.cdlgSeq
                            }).then((response) => {
                                if(response.data==='위임기간이 중복되는 건이 존재합니다.'){
                                    this.$swal({type: 'warning', text: response.data});
                                    return;
                                }
                                this.doReturnObject();
                            }).catch((e) => {
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
                            this.$http.post(`/api/card/delegating/cancel`, {
                                cdlgId: this.form.cdlgId,
                                nomnId: this.form.nomnId,
                                crdNo: this.toPure(this.form.crdNo),
                                cdlgSeq: this.form.cdlgSeq
                            }).then((response) => {
                                this.doReturnObject()
                            }).catch((e) => {
                                console.error(e)
                            });
                        }
                    });
                },
                doReturnObject() {
                    this.returnObject.name = '';
                    this.$parent.$emit('receive', this.returnObject);
                    this.closeModal();
                },
                closeModal() {
                    this.$parent.close();
                },
                popCdlgEmp(clear) {
                    if (clear === true) {
                        this.form.cdlgId = '';
                        this.form.cdlgNm = '';
                    }
                    this.showEmpModal1 = true;
                },
                popNomnEmp(clear) {
                    if (clear === true) {
                        this.form.nomnId = '';
                        this.form.nomnNm = '';
                    }
                    this.showEmpModal2 = true;
                },
                initCdlgEmp(force) {
                    if (force === true) this.form.cdlgNm = '';
                    if (this.form.cdlgNm === '') this.form.cdlgId = '';
                },
                initNomnEmp(force) {
                    if (force === true) this.form.nomnNm = '';
                    if (this.form.nomnNm === '') this.form.nomnId = '';
                },
                receiveCdlgEmp(obj) {
                    this.form.cdlgId = obj.empNo;
                    this.form.cdlgNm = obj.empNm;
                },
                receiveNomnEmp(obj) {
                    this.form.nomnId = obj.empNo;
                    this.form.nomnNm = obj.empNm;
                },
                getCardListCombo(cdlgId) {
                    this.$http.post(`/api/card/list`, {
                            crdPssrId: cdlgId
                        }
                    )
                        .then(response => {
                            if (response.data) {
                                this.crdList = response.data;
                                _.forEach(this.crdList, (o) => {
                                    o.maskedCrdNo = this.getFormattedPureCardNumber(o.crdNo) + ' ' + o.crdCompNm;
                                });
                            }
                        });
                },
            }
        ,
        mounted() {
            if(this.hiddenCheck ==='Y'){
                this.form.crdNo = this.hiddenCrdNo;
                this.form.cdlgStrDt = this.hiddenDtmFr;
                this.form.cdlgEndDt = this.hiddenDtmTo;
                this.form.cdlgId = this.cdlgId;
                this.form.cdlgNm = this.cdlgNm;
                this.form.nomnId = this.nomnId;
                this.form.nomnNm = this.nomnNm;
                this.form.cdlgSeq = this.cdlgSeq;
                this.form.hiddenCheck = this.hiddenCheck;
            }
        },
        watch: {
            'form.cdlgId'(value) {
                this.getCardListCombo(value);
            },
        }
    }
</script>

<style scoped>
    .btn-wrap {
        margin-bottom: 20px;
    }

    .desc-content .item.desc-left .desc-item .td-s-thumb.search-area input,{
        float: left;
    }

    .desc-content .item.desc-left .desc-item .desc.select select {
        width: 70%;
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

    .search-border .td-s-thumb.search-area > input,
    .search-border .td-s-thumb.search-area > .ip-box
    .search-border .td-s-thumb.search-area > button {
        float: left;
    }
</style>
