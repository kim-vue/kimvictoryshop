<template>
    <div class="modal-card">
        <header class="modal-card-head pop-header">
            <p class="modal-card-title tit">
                {{ title }}
                <button class="btn-pop-close delete" aria-label="close" @click="$parent.close()"></button>
            </p>
        </header>
        <section class="modal-card-body pop-content">
            <div class="inner-box">
                <div v-if="isNew" class="content-name" style="margin-top: 0px; margin-bottom: 0px;">
                    <div class="btn-wrap btn-type1 clearfix" style="float:right; margin-bottom: 0px;">
                        <button class="btn-size btn-blue" @click="approval()">
                            <span class="btn-icon"><i class="fas fa-pen-alt"></i></span> 상신
                        </button>
                        <button class="btn-size btn-blue" @click="openVendorPopup()">
                            <span class="btn-icon"><i class="fas fa-user-check"></i></span> 결재자 지정
                        </button>
                    </div>
                </div>
                <div v-if="!isNew" class="content-name" style="margin-top: 0px; margin-bottom: 0px;">
                    <div class="btn-wrap btn-type1 clearfix" style="float:right; margin-bottom: 0px;">
                        <button v-if="this.$store.state.loginInfo.loginId === this.apprInfo.thisApprUser || this.apprInfo.deleYn ==='Y'" class="btn-size btn-blue" @click="openApprPopup()"><span class="btn-icon"><i
                                class="fas fa-pen-alt"></i></span> 결재
                        </button>
                        <button v-if="this.$store.state.loginInfo.loginId == this.apprInfo.draftUserId && this.apprInfo.docStatus === 'REQ'"
                                class="btn-size btn-yellow" @click="cancel(docMngNo)"><span class="btn-icon"><i class="far fa-file"></i></span> 상신취소
                        </button>
                    </div>
                </div>

                <appr-dtl ref="apprDtl" v-if="isLoaded" v-model="data" :docType="docType" :approval-line.sync="apprLine" :docMngNo="docMngNo" :budReqNo="budReqNo" @input="$forceUpdate()" @approvalLine="changeApprovalLineEvent" @apprInfo="apprInfoCheck"/>
                <!-- Appr Header area -->
                <!--                <div class="table-area" style="margin-top: 0px;">
                                    <appr-header :doc-type="docType" :apprHeader="apprHeader" :appr-line="apprLine" v-model="data"/>
                                </div>-->
                <!-- //Appr Header area -->
                <!--            <component :is="docComponent" v-model="data" :readonly="true" @input="queryApprLineRule"/>-->
            </div>
        </section>
    </div>
</template>

<script>
    import DhxGrid from '@/components/DhxGrid.vue'

    import ApprLineSet from '@/components/ApprLineSet.vue'
    import ApprActPop from '@/components/ApprActPop.vue'
    import ApprDtl from '@/components/ApprDtl.vue'

    export default {
        props: {
            docMngNo: {
                type: String,
                required: false
            },
            budReqNo: {
                type: String,
                required: false
            },
            docType: {
                type: String,
                required: false,
                default: 'SLIP'
            },
            value: {
                type: Object,
                required: false,
                default() {
                  return {}
                }
            }
        },
        components: {
            ApprDtl,
            DhxGrid,
            ApprLineSet,
        },
        data() {
            return {
                title: '결재상신',
                data: {},
                dataProp: {},
                apprHeader: {},
                apprLine: [],
                apprNo: '',
                apprSeq: '',
                docTitleNm: '',
                //docTypeCd: '',
                docStatus: '',
                draftUserId: '',
                thisApprUser: '',
                deleYn: 'N',
                apprInfo: [],
                loaded: false,
                isNew: false,
            }
        },
        methods: {
            approval() {
                if (this.apprLine.length < 2) {
                    this.$swal({type: 'warning', text: '결재선을 지정해주세요.'});
                    return false;
                }

                this.$swal({
                    type: 'info',
                    text: `결재내역을 상신합니다. 계속 하시겠습니까?`,
                    showCancelButton: true,
                    confirmButtonText: '예',
                    cancelButtonText: '아니오',
                }).then((result) => {
                    if (result.value) {
                        let docTypeCd = ''
                        let docMngNo = ''
                        let docTitle = ''

                        console.log('this.docType : '+ this.docType)
                        console.log(JSON.stringify(this.data))
                        //if(this.data.eaSlipNo !== undefined) {
                        if(this.docType === 'SLIP'){
                            if (this.data.eaSlipNo.substr(0, 2) === 'GR' || this.data.eaSlipNo.substr(0, 2) === 'EA') {
                                //docTypeCd = 'SLIP'
                                docMngNo = this.data.eaSlipNo
                                docTitle = this.data.slipTypeNm + ' / ' + this.$filters.number(this.data.totAmt) + ' / ' + this.data.hdSgtxt
                            }
                        }
                        else if(this.docType === 'BDGT'){
                            if (this.budReqNo.substr(0, 2) === 'BD') {
                                //docTypeCd = 'BDGT'
                                docMngNo = this.budReqNo
                                docTitle = this.data.budFgNm + ' / ' + this.$filters.number(this.data.reqTotAmt) + ' / ' + this.data.reqRsn
                            }
                        }

                        _.forEach(this.apprLine, (v, index) => {
                            v.apprSeq = index + 1
                        })

                        /*
                        this.$http.put(`/api/appr/detail/req`, {
                            docTypeCd: this.docType,
                            docMngNo: docMngNo,
                            docTitleNm: docTitle,
                            approvalDetails: this.apprLine
                        })
                            .then((response) => {
                                this.$parent.close();
                                this.$swal({type: 'info', text: '상신이 완료되었습니다.'});
                                this.$parent.$parent.status.readonly = true
                                this.$parent.$parent.$forceUpdate()
                            })
                            .catch((e) => {
                                this.$swal({type: 'error', text: e.response.data.message});
                            })*/

                        if(this.docType === 'SLIP' || this.docType === 'BDGT') {
                            this.$http.put(`/api/appr/detail/req`, {
                                docTypeCd: this.docType,
                                docMngNo: docMngNo,
                                docTitleNm: docTitle,
                                approvalDetails: this.apprLine
                            })
                                .then((response) => {
                                    this.$parent.close();
                                    this.$swal({type: 'info', text: '상신이 완료되었습니다.'});
                                    this.$parent.$parent.status.readonly = true
                                })
                                .catch((e) => {
                                    this.$swal({type: 'error', text: e.response.data.message});
                                })
                        } else {
                            console.log('그룹상신 !!')
                            this.$http.post('/api/slip/groupAppr', {
                                approvalHeader: {
                                    docTypeCd: 'SLIP',
                                    approvalDetails: this.apprLine
                                },
                                slipHistoryDtos:  this.data.slipGroupDetails
                            }).then(response => {
                                this.$parent.close();
                                this.$swal({type: 'info', text: '상신이 완료되었습니다.'});
                                this.$parent.$parent.status.readonly = true
                            }).catch((e) => {
                                  this.$swal({type: 'error', text: e.response.data.message});
                            })
                        }

                    }
                })
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
                                    this.$parent.close();
                                    this.$swal({type: 'info', text: '상신 취소되었습니다.'});
                                    this.$parent.$parent.status.readonly = false
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
            },
            openApprPopup() {
                let vm = this
                this.$modal.open({
                    component: ApprActPop,
                    props: {
                        docTitleNm: this.apprInfo.docTitleNm,
                        apprNo: this.apprInfo.apprNo,
                        apprSeq: this.apprInfo.apprSeq
                    },
                    parent: this,
                    events: {
                        close(data) {
                            // Close event handler
                            console.log('Appr Popup Close Event!!')
                            vm.$refs.apprDtl.getAppr(data)
                        }
                    }
                })
            },
            changeApprovalLineEvent(data) {
                this.apprLine = data
            },
            apprInfoCheck(data) {
                console.log('Appr Info Check!!')
                this.apprInfo = data
                console.log(JSON.stringify(this.apprInfo))
                console.log(this.apprInfo.thisApprUser +', '+this.apprInfo.deleYn)
            },
        },
        computed: {
            isLoaded() {
                return this.loaded
            }
        },
        created() {
            if(this.docMngNo === undefined) {
                this.isNew = true
            }
            else{
                this.isNew = false
                this.title = '결재보기'
            }
            console.log(this.docMngNo)
        },
        watch: {
            value: {
                immediate: true,
                deep: true,
                handler(value) {
                    this.data = value
                    this.loaded = true
                }
            }
        }
    }
</script>

<style scoped>
    .modal-card {
        width: auto;
    }
</style>
