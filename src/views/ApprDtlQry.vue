<template>
    <div class="inner-box" v-if="$route.path.substr(0,7)=='/mobile'" style="zoom: 65%;">
        <!-- Appr Header area -->
        <appr-dtl v-if="isLoaded" v-model="data" :docMngNo="docMngNo" :budReqNo="budReqNo" :docType="docType" :approval-line.sync="apprLine" @input="$forceUpdate()"/>
    </div>
    <div class="inner-box" v-else>
        <div class="content-name">
            <h2 class="dp-ib" style="height: 33px">{{title}}</h2>
            <div class="btn-wrap btn-type1 clearfix" style="margin-bottom: 0">
                <button v-if="this.$store.state.loginInfo.loginId === this.thisApprUser || this.deleYn ==='Y'" class="btn-size btn-blue" @click="openApprPopup()"><span class="btn-icon"><i
                        class="fas fa-pen-alt"></i></span> 결재
                </button>
                <button v-if="this.$store.state.loginInfo.loginId == draftUserId && docStatus === 'REQ'"
                        class="btn-size btn-yellow" @click="cancel(docMngNo)"><span class="btn-icon"><i class="far fa-file"></i></span> 상신취소
                </button>
            </div>
        </div>

        <appr-dtl v-if="isLoaded" v-model="data" :docMngNo="docMngNo" :budReqNo="budReqNo" :docType="docType" :approval-line.sync="apprLine" @input="$forceUpdate()"/>

        <b-modal :active.sync="showVendorModal1" has-modal-card @receive="getAppr">
            <appr-act-pop :docTitleNm="docTitleNm" :apprNo="apprNo" :apprSeq="apprSeq"></appr-act-pop>
        </b-modal>
    </div>
</template>

<script>
    /* eslint-disable */
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import _ from 'lodash'

    import ApprDtl from '@/components/ApprDtl.vue'
    import ApprHeader from '@/components/ApprHeader.vue'
    import ApprActPop from '@/components/ApprActPop.vue'

    export default {
        name: 'ApprDtlQry',
        props: {
            docMngNo: {
                type: String,
                required: false
            },
            value: {
                type: Object,
                required: false
            }
        },
        mixins: [mixin, mixinSlip],
        components: {ApprHeader, ApprActPop, ApprDtl},
        data() {
            return {
                data: {},
                title: '결재 상세',
                apprHeader: {},
                apprLine: [],
                budReqNo: undefined,
                apprNo: '',
                apprSeq: '',
                docTitleNm: '',
                docTypeCd: '',
                docType: 'SLIP',
                docStatus: '',
                draftUserId: '',
                thisApprUser: '',
                deleYn: 'N',
                loaded: false,
                showVendorModal1: false,
            };
        },
        methods: {
            getAppr(docMngNo) {
                this.loaded = false

                if (docMngNo != undefined) {
                    this.$http.get(`/api/appr/detail/${docMngNo}`)
                        .then(response => {
                            if (response.data) {
                                this.apprSeq = ''
                                this.thisApprUser = ''

                                console.log(JSON.stringify(response.data))
                                if(response.data.budgetHeader) {
                                    this.apprHeader = response.data.apprHeader;
                                    this.apprLine = response.data.apprDetails;

                                    this.docTypeCd = response.data.apprHeader[0].docTypeCd;
                                    this.docStatus = response.data.apprHeader[0].docStatCd;
                                    this.draftUserId = response.data.apprHeader[0].draftUserId;
                                    this.docTitleNm = response.data.apprHeader[0].docTitleNm;
                                    this.apprNo = response.data.apprHeader[0].apprNo;

                                    this.docType = 'BDGT'
                                    this.budReqNo = response.data.budgetHeader.budReqNo
                                } else if(response.data.slipGroupHeader){
                                    this.data = response.data.slipGroupHeader
                                    this.data.slipDetails = response.data.slipGroupDetails

                                    this.apprHeader = response.data.apprHeader;
                                    this.apprLine = response.data.apprDetails;

                                    this.docTypeCd = response.data.apprHeader[0].docTypeCd;
                                    this.docStatus = response.data.apprHeader[0].docStatCd;
                                    this.draftUserId = response.data.apprHeader[0].draftUserId;
                                    this.docTitleNm = response.data.apprHeader[0].docTitleNm;
                                    this.apprNo = response.data.apprHeader[0].apprNo;
                                    this.docType = 'GR'
                                } else {
                                    this.data = response.data.slipHeader
                                    this.data.slipDetails = response.data.slipDetails

                                    this.apprHeader = response.data.apprHeader;
                                    this.apprLine = response.data.apprDetails;

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
                                }


                                _.forEach(this.apprLine, v => {
                                    if (v.apprFgCd ==='X') {
                                        this.apprSeq = v.apprSeq
                                        this.thisApprUser = v.aprverId
                                        return false
                                    }
                                })

                                this.loaded = true
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
            cancel(docMngNo) {
                this.$swal({
                    type: 'info',
                    text: `상신을 취소합니다. 계속 하시겠습니까?`,
                    showCancelButton: true,
                    confirmButtonText: '예',
                    cancelButtonText: '아니오',
                }).then((result) => {
                    if (result.value) {
                        if (docMngNo != undefined) {
                            this.$http.get(`/api/appr/detail/cancel/${docMngNo}`)
                                .then(response => {
                                    if (response.data) {
                                        this.$router.push({path: `/apprReqLst`});
                                    }
                                })
                                .catch(({message}) => {
                                    console.error(message);
                                });
                        }
                    }
                })
            },
            openApprPopup() {
                let vm = this
                this.$modal.open({
                    component: ApprActPop,
                    props: {
                        docTitleNm: this.docTitleNm,
                        apprNo: this.apprNo,
                        apprSeq: this.apprSeq
                    },
                    parent: this,
                    events: {
                        close(data) {
                            // Close event handler
                            console.log('Appr Popup Close Event!!'+ data)
                            vm.getAppr(data)
                        }
                    }
                })
            },
            popVendor1(clear) {
                this.showVendorModal1 = true;
            },
            receiveVendor1(obj) {
                this.docTitleNm = obj.docTitleNm;
            },
        },
        created() {
            this.getAppr(this.docMngNo);
        },
        computed: {
            isLoaded() {
                return this.loaded
            },
        },
        watch: {
            'loaded'() {
                this.deleCheck()
            },
        }
    };
</script>

<style>
</style>

