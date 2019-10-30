<template>
    <div>
        <div class="table-area" style="margin-top: 0px;">
            <appr-header :doc-type="docType" :apprHeader="apprHeader" :appr-line="apprLine" v-model="data"/>
        </div>
        <!-- //Appr Header area -->
        <component :is="docComponent" v-model="data" :budReqNo="budReqNo" :readonly="true" @input="queryApprLineRule"/>
    </div>
</template>

<script>
    import DhxGrid from '@/components/DhxGrid.vue'
    import ApprHeader from '@/components/ApprHeader.vue'
    import ApprLineSet from '@/components/ApprLineSet.vue'

    // Slip
    import SlipBase from '@/components/slip/SlipBase.vue'
    // BdgReq
    import BdgReq from '@/components/BdgReq.vue'
    // SlipGr
    import SlipGr from '@/components/SlipGr.vue'

    export default {
        props: {
            title: {
                type: String,
                required: false,
                default: '결재 상신'
            },
            docMngNo: {
                type: String,
                required: false
            },
            budReqNo: {
                type: String,
                required: false
            },
            value: {
                type: Object,
                required: false
            },
            docType: {
                type: String,
                required: false,
                default: 'SLIP'
            },
            approvalLine: {
                type: Array,
                required: true
            }
        },
        components: {
            DhxGrid,
            ApprHeader,
            ApprLineSet,
            SlipBase,
            BdgReq,
            SlipGr
        },
        data() {
            return {
                apprHeader: {},
                apprLine: [],
                apprNo: '',
                apprSeq: '',
                docTitleNm: '',
                docTypeCd: '',
                docStatus: '',
                draftUserId: '',
                thisApprUser: '',
                deleYn: 'N',
                loaded: false,
                data: {},
                deleInfo: {},
            }
        },
        computed: {
            docComponent() {
                console.log('this.docType : ' + this.docType)
                switch (this.docType) {
                    case 'SLIP':
                        return 'SlipBase'
                    case 'BDGT':
                        return 'BdgReq'
                    case 'GR':
                        return 'SlipGr'
                    default:
                        return undefined
                }
            }
        },
        methods: {
            /**
             * Query Approval line rule
             */
            queryApprLineRule() {
                console.log('queryApprLineRule !!')
                let docTypeCd = this.docType
                let dtlTypeCd = undefined
                let curCd = undefined
                let maxAmt = undefined

                switch (this.docType) {
                    case 'SLIP':
                        dtlTypeCd = this.data.slipTypeCd
                        curCd = this.data.curCd
                        maxAmt = this.data.totAmt
                        break
                    case 'BDGT':
                        dtlTypeCd = this.data.brwTypeCd
                        curCd = 'KRW'
                        maxAmt = this.data.reqTotAmt
                        break
                    case 'GR':
                        docTypeCd = 'SLIP'
                        dtlTypeCd = 'E1'
                        curCd = this.data.currCode
                        maxAmt = 0
                        break
                }

                this.$store.commit('loading')
                this.$http.get('/api/appr/rule', {
                    params: {
                        docTypeCd,
                        dtlTypeCd,
                        curCd,
                        maxAmt
                    }
                }).then(response => {
                    if (Array.isArray(response.data) && response.data.length > 0) {
                        this.apprLine = response.data.filter(x => x.aprverUser)
                    }
                }).finally(() => {
                    this.apprLine.unshift(
                        {
                            aprverUser: this.$store.state.loginInfo.userName,
                            jobNm: this.$store.state.loginInfo.loginJobNm,
                            aprverId: this.$store.state.loginInfo.loginId,
                            cctrNm: this.$store.state.loginInfo.loginDeptNm,
                            apprTypeCd: '10',
                            apprType: '기안'
                        }
                    );

                    this.$emit('approvalLine', this.apprLine)
                    this.$store.commit('finish')
                })
            },
            approval() {
            },
            getAppr(docMngNo) {
                console.log('Get Appr !!, docMngNo : '+docMngNo)
                this.$http.get(`/api/appr/detail/${docMngNo}`)
                    .then(response => {
                        if (response.data) {

                            this.apprSeq = ''
                            this.thisApprUser = ''
                            this.apprHeader = response.data.apprHeader[0];
                            this.apprLine = response.data.apprDetails;

                            if (this.docType === 'GR') {
                                let data = response.data.slipGroupHeader
                                data.slipGroupDetails = response.data.slipGroupDetails
                                this.data = data
                            } else {
                                let data = response.data.slipHeader
                                data.slipDetails = response.data.slipDetails
                                this.data = data
                            }

                            //this.slipHeader = response.data.slipHeader;
                            //this.slipDetails = response.data.slipDetails;

                            this.docTypeCd = response.data.apprHeader[0].docTypeCd;
                            this.docStatus = response.data.apprHeader[0].docStatCd;
                            this.draftUserId = response.data.apprHeader[0].draftUserId;
                            this.docTitleNm = response.data.apprHeader[0].docTitleNm;
                            this.apprNo = response.data.apprHeader[0].apprNo;

                            _.forEach(this.apprLine, v => {
                                if (v.apprFgCd === 'X') {
                                    this.apprSeq = v.apprSeq
                                    this.thisApprUser = v.aprverId
                                    return false
                                }
                            })

                            this.loaded = true

                            this.$emit('approvalLine', this.apprLine)
                        }
                    })
                    .catch(({message}) => {
                        console.error(message);
                    })
            },
            apprCheck() {
                this.$http.get(`/api/appr/delegatingCheck`, {
                    params: {
                        adlgId: this.thisApprUser,
                        actId: this.$store.state.loginInfo.loginId
                    }
                })
                    .then(response => {
                        console.log('ApprCheck!!')
                        this.deleYn = response.data;

                        this.apprInfo = {
                            "deleYn": this.deleYn,
                            "apprSeq": this.apprSeq,
                            "thisApprUser": this.thisApprUser,
                            "docStatus": this.docStatus,
                            "draftUserId": this.draftUserId,
                            "docTitleNm": this.docTitleNm,
                            "apprNo": this.apprNo
                        }
                        this.$emit('apprInfo', this.apprInfo)
                        this.loaded = false
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
                                        this.$swal({type: 'info', text: '상신 취소되었습니다.'});
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
            openVendorPopup() {
                let vm = this
                this.$modal.open({
                    component: ApprLineSet,
                    props: {
                        lineList: this.apprLine
                    },
                    parent: this,
                    events: {
                        close(data) {
                            // Close event handler
                            vm.apprLine = data.lineList || []
                        }
                    }
                })
            }
        },
        created() {
            if (this.docMngNo !== undefined) this.getAppr(this.docMngNo)
            if (this.docMngNo === undefined && this.budReqNo === undefined) this.queryApprLineRule()
        },
        mounted() {
            console.log('ApprDtl1 : '+this.docMngNo)
            console.log('ApprDtl2 : '+this.budReqNo)
        },
        watch: {
            value: {
                immediate: true,
                deep: true,
                handler(value) {
                    this.data = value
                }
            },
            approvalLine: {
                immediate: true,
                deep: true,
                handler(value) {
                    this.apprLine = value
                }
            },
            'loaded'() {
                if(this.loaded) this.apprCheck()
            },
        }
    }
</script>

<style scoped>
    .modal-card {
        width: auto;
    }
</style>
