<template>
    <layout>
        <span slot="header">
            {{title}}
            <button class="btn-pop-close delete" aria-label="close" @click="closeModal"></button>
        </span>
        <div slot="content">
            <div class="inner-box">
                <div class="content-name" style="margin-top: 0px; margin-bottom: 0px;">
                    <div class="btn-wrap btn-type1 clearfix" style="float:right; margin-bottom: 0px;">
                        <button v-if="this.$store.state.loginInfo.loginId === this.thisApprUser || this.deleYn ==='Y'" class="btn-size btn-blue" @click="popVendor1(true)">
                            <span class="btn-icon"><i class="fas fa-pen-alt"></i></span> 결재
                        </button>
                        <button v-if="this.$store.state.loginInfo.loginId == draftUserId && docStatus === 'REQ'" class="btn-size btn-yellow" @click="cancel(docNo)">
                            <span class="btn-icon"><i class="far fa-file"></i></span> 상신취소
                        </button>
                    </div>
                </div>

                <!-- Appr Header area -->
                <div class="table-area" style="margin-top: 0px;">
                    <appr-header ref="header" :apprHeader="apprHeader" :apprDetails="apprDetails" />
                </div>
                <!-- //Appr Header area -->

                <!-- Table area -->
                <slip-table v-if="isLoaded" :slipType="data.slipTypeCd" v-model="data" :status="status" @input="$forceUpdate()" />
                <!-- //Table area -->

                <!-- Grid area -->
                <grid-r-o :slipType="data.slipTypeCd" v-model="data" :status="status" @input="$forceUpdate()" />
                <!-- //Grid area -->
            </div>

            <b-modal :active.sync="showVendorModal1" has-modal-card @receive="getAppr">
                <appr-act-pop :docTitleNm="docTitleNm" :apprNo="apprNo" :apprSeq="apprSeq"></appr-act-pop>
            </b-modal>
        </div>
    </layout>
</template>

<script>
    /* eslint-disable */
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import _ from 'lodash'
    import Layout from '@/components/ModalSlot.vue'

    import ApprHeader from '@/components/ApprHeader.vue'
    import ApprActPop from '@/components/ApprActPop.vue'
    import SlipTable from '@/components/slip/SlipTable.vue'
    import GridRO from '@/components/slip/GridRO.vue'

    export default {
        name: 'ApprDtlQry',
        props: {
            docNo: {
                type: String,
                required: false
            },
            value: {
                type: Object,
                required: false
            },
            status: {
                type: Object,
                required: false,
                default() {
                    return {
                        new: false,
                        loaded: false,
                        readonly: true,
                        change: false,
                        memento: []
                    }
                }
            },
        },
        mixins: [mixin, mixinSlip],
        components: {ApprHeader, ApprActPop, SlipTable, GridRO, Layout},
        data() {
            return {
                data: {},
                title: '결재 상세',
                apprHeader: {},
                apprDetails: [],
                apprNo: '',
                apprSeq: '',
                docTitleNm: '',
                docTypeCd: '',
                docStatus: '',
                draftUserId: '',
                thisApprUser: '',
                deleYn: 'N',
                showVendorModal1: false,
            };
        },
        methods: {
            getAppr(docNo) {
                this.status.loaded = false

                if (docNo != undefined) {
                    this.$http.get(`/api/appr/detail/${docNo}`)
                        .then(response => {
                            if (response.data) {
                                this.apprSeq = ''
                                this.thisApprUser = ''

                                this.data = response.data.slipHeader
                                this.data.slipDetails = response.data.slipDetails

                                this.apprHeader = response.data.apprHeader;
                                this.apprDetails = response.data.apprDetails;

                                this.docTypeCd = response.data.apprHeader[0].docTypeCd;
                                this.docStatus = response.data.apprHeader[0].docStatCd;
                                this.draftUserId = response.data.apprHeader[0].draftUserId;
                                this.docTitleNm = response.data.apprHeader[0].docTitleNm;
                                this.apprNo = response.data.apprHeader[0].apprNo;

                                this.data.custAccount = [this.data.custBnkCd, this.data.custAcctNo].join('_')

                                _.forEach(this.data.slipDetails, item => {
                                    switch (item.dcCd) {
                                        case 'C':
                                            item.creditAmt = item.acctAmt
                                            break
                                        case 'D':
                                            item.debitAmt = item.acctAmt
                                            break
                                    }
                                })

                                this.$emit('input', this.data)
                                this.status.loaded = true

                                setTimeout(() => {
                                    this.status.memento = [_.clone(this.data)]
                                }, 1500)

                                _.forEach(this.apprDetails, v => {
                                    if (v.apprFgCd ==='X') {
                                        this.apprSeq = v.apprSeq
                                        this.thisApprUser = v.aprverId
                                        return false
                                    }
                                })
                            }
                        })
                        .catch(({message}) => {
                            console.error(message);
                        })
                }
            },
            deleCheck() {
                this.$http.get(`/api/appr/delegatingCheck`, {
                    params: {
                        adlgId: this.thisApprUser,
                        actId: this.$store.state.loginInfo.loginId
                    }
                })
                    .then(response => {
                        this.deleYn = response.data;
                    });
            },
            cancel(docNo) {
                this.$swal({
                    type: 'info',
                    text: `상신을 취소합니다. 계속 하시겠습니까?`,
                    showCancelButton: true,
                    confirmButtonText: '예',
                    cancelButtonText: '아니오',
                }).then((result) => {
                    if (result.value) {
                        if (docNo != undefined) {
                            this.$http.get(`/api/appr/detail/cancel/${docNo}`)
                                .then(response => {
                                    if (response.data) {
                                        this.$parent.close()
                                        this.$swal({type: 'info', text: '상신이 취소되었습니다.'});
                                        this.$parent.$parent.status.readonly = false
                                    }
                                })
                                .catch(({message}) => {
                                    console.error(message);
                                });
                        }
                    }
                })
            },
            closeModal() {
                this.$emit('close')
                this.$parent.close();
            },
            popVendor1(clear) {
                this.showVendorModal1 = true;
            },
            receiveVendor1(obj) {
                this.docTitleNm = obj.docTitleNm;
            },
        },
        created() {
            this.getAppr(this.docNo);
        },
        computed: {
            isLoaded() {
                return this.status.loaded
            },
        },
        watch: {
            'status.loaded'() {
                this.deleCheck()
            },
        }
    };
</script>

<style scoped>
    .modal-card {
        width: auto;
    }
</style>

