<template>
    <div class="inner-box">
        <div class="content-name">
            <h2 class="dp-ib">{{title}}</h2>
            <div class="btn-wrap btn-type1 clearfix" v-if="this.status.readonly">
                <button class="btn-size btn-gray fl_left"><span class="btn-icon"><i class="fas fa-print"></i></span> 출력</button>
                <button class="btn-size btn-blue fl_left" @click="showApproval"><span class="btn-icon"><i class="fas fa-vote-yea"></i></span> 결재보기</button>
                <button class="btn-size btn-orange fl_left" @click="copySlip"><span class="btn-icon"><i class="far fa-clone"></i></span> 전표복사</button>
            </div>
            <div class="btn-wrap btn-type1 clearfix" v-else>
                <button class="btn-size btn-blue fl_left" @click="approval"><span class="btn-icon"><i class="fas fa-pen-alt"></i></span> 결재상신</button>
                <button class="btn-size btn-gray fl_left" @click="newPage"><span class="btn-icon"><i class="far fa-file"></i></span> 신규</button>
                <button class="btn-size btn-gray fl_left" @click="remove" v-if="showDeleteButton"><span class="btn-icon"><i class="far fa-trash-alt"></i></span> 삭제</button>
                <button class="btn-size btn-gray fl_left" @click="save"><span class="btn-icon"><i class="fas fa-check"></i></span> 저장</button>
            </div>
        </div>

        <!-- Table area -->
        <slip-table v-if="isLoaded" :slipType="data.slipTypeCd" v-model="data" :status="status" @input="$forceUpdate()"/>
        <!-- //Table area -->

        <!-- Grid area -->
        <component :is="gridComponentName" :slipType="data.slipTypeCd" v-model="data" :status="status" @input="$forceUpdate()"/>
        <!-- //Grid area -->
    </div>
</template>

<script>
    // eslint-disable-next-line
    import mixin from '@/mixin';

    import ApprSubm from '@/views/ApprSubm.vue';
    import ApprDtlQryPop from '@/views/ApprDtlQryPop.vue';
    import SlipTable from '@/components/slip/SlipTable.vue'
    import GridED from '@/components/slip/GridED.vue'
    import GridRO from '@/components/slip/GridRO.vue'
    import _ from 'lodash'

    export default {
        name: 'BillSlipQry',
        props: {
            eaSlipNo: {
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
                        readonly: false,
                        change: false,
                        memento: []
                    }
                }
            },
            readonly: {
                type: Boolean,
                required: false,
                default: false
            }
        },
        components: {
            SlipTable,
            GridED,
            GridRO,
            ApprSubm,
            ApprDtlQryPop
        },
        mixins: [mixin],
        data() {
            return {
                data: {},
                title: '',
                // slipTypeCd: 'E3',
                // bus: new Vue(),
                slipHeader: {},
                slipDetails: [],
                showDeleteButton: false,
            };
        },
        computed: {
            isNew() {
                return this.eaSlipNo === undefined
            },
            isLoaded() {
                return this.status.loaded
            },
            gridComponentName() {
                return 'Grid' + (this.status.readonly ? 'RO' : 'ED')
            }
        },
        methods: {
            querySlipData() {
                return new Promise((resolve, reject) => {

                    this.status.loaded = false

                    this.$store.commit('loading')
                    this.$http.get(`/api/slip/${this.eaSlipNo}`)
                        .then(response => {
                            this.data = response.data.slipHeader
                            this.data.slipDetails = response.data.slipDetails
                            this.title = response.data.slipHeader.slipTypeNm + ' 전표'

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

                            this.status.readonly = (this.data.slipStatCd !== '10' || this.readonly)

                            this.$emit('input', this.data)

                            this.status.change = false
                            this.status.loaded = true
                            setTimeout(() => {
                                this.status.memento = [_.clone(this.data)]
                            }, 1500)

                            return resolve(response)
                        })
                        .catch(response => {
                            return reject(response)
                        })
                        .finally(() => {
                            this.$store.commit('finish')
                        })
                })
            },
            copySlip() {
                let prgNm = this.slipHeader.slipTypeCd === 'E2' ? 'ebillSlipReg' : 'billSlipReg';
                this.$router.push({name: prgNm, params: {eaSlipNo: this.eaSlipNo, copy: true}});
            },
            save() {
                console.log("저장해 봅시다.")

                // form validation
                if (!this.$refs.header.validation()) return;
                // if(!this.$refs.detail.validation()) return;

                const header = JSON.parse(JSON.stringify(this.$refs.header.form));
                const stripFields = ['evdDt', 'postDt', 'payDueDt', 'supAmt', 'vatAmt', 'etcAmt', 'totAmt'];
                _.forEach(stripFields, (name) => header[name] = this.toPure(header[name]));
                // 전표유형
                header.slipTypeCd = this.slipTypeCd;
                // 작성일자 삭제
                header.wrtDtm = '';

                const grid = this.$refs.header.$refs.detail.$refs.grid;

                var details = [];
                var rowIds = [];
                var once = false;

                for (var i = 0; i < grid.getRowsNum(); i++) {
                    let rowId = grid.getRowId(i);
                    let rowObj = grid.getRowData(rowId);
                    rowObj.acctAmt = _.toInteger(rowObj.creditAmt) + _.toInteger(rowObj.debitAmt);
                    details.push(rowObj);
                    rowIds.push(rowId);

                    var dcCd = grid.cells2(i, 14).getValue();
                    var lnTypeCd = grid.cells2(i, 15).getValue();

                    // 대표계정
                    if (!once && dcCd === 'D' && lnTypeCd === 'ITEM') {
                        header.stnAcctCd = grid.cells2(i, 7).getValue();
                        once = true;
                    }
                }
                header.slipDetails = details;

                this.$http.post(`/api/slip`, header)
                    .then((response) => {
                        this.copyMode = false;
                        this.getSlip(response.data.eaSlipNo);
                    })
                    .catch((e) => {
                        console.error(e);
                    });
            },
            remove() {
                const eaSlipNo = this.$refs.header.form.eaSlipNo;
                console.log("삭제...", eaSlipNo)
                if (eaSlipNo != undefined) {
                    this.$http.delete(`/api/slip/${eaSlipNo}`)
                        .then(response => {
                            if (response.status === 200) {
                                this.$swal({type: 'warning', text: response.data});
                                console.log("삭제 후 페이지 이동 필요")
                            }
                        });
                }
            },
            toggleDeleteButton(value) {
                this.showDeleteButton = value;
                console.log("showDeleteButton", this.showDeleteButton)
            },
            newPage() {
                this.$swal({
                    type: 'warning',
                    text: `변경된 데이터가 있습니다. 계속 하시겠습니까?`,
                    showCancelButton: true,
                    confirmButtonText: '예',
                    cancelButtonText: '아니오',
                }).then((result) => {
                    if (result.value) {
                        this.$router.replace({name: 'billSlipReg', params: {eaSlipNo: 0}});
                        this.$router.go(this.$router.currentRoute);
                    }
                });
            },
            approval() {
                this.$modal.open({
                    component: ApprSubm,
                    props: {
                        slipTypeCd: this.data.slipTypeCd,
                        slipHeader: this.data,
                        slipDetailsProp: this.data.slipDetails
                    },
                    parent: this,
                    fullScreen: true,
                    width: 1200,
                    events: {
                        close() {
                            //this.querySlipData()
                            console.log('닫힘 이벤트')
                        }
                    }
                })
            },
            showApproval() {
                this.$modal.open({
                    component: ApprDtlQryPop,
                    props: {
                        docNo: this.data.elecApprId,
                        popYn: 'Y'
                    },
                    parent: this,
                    fullScreen: true,
                    width: 1200,
                    events: {
                        close() {
                            //this.querySlipData()
                            console.log('닫힘 이벤트')
                        }
                    }
                })
            },
        },
        mounted() {
            this.querySlipData()
        },
        watch: {
            'value': {
                immediate: true,
                deep: true,
                handler(value) {
                    this.data = value || {}
                }
            },
            'data': {
                deep: true,
                handler(value) {
                    if (this.status.memento.length === 0) {
                        this.status.memento.unshift(_.clone(value))
                    } else {
                        let c = JSON.stringify(this.status.memento[0])
                        let v = JSON.stringify(v)
                        if (c !== v) {
                            this.status.memento.unshift(_.clone(value))
                        }
                    }
                }
            }
        }
    }
</script>

<style>
</style>

