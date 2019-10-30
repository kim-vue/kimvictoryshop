<template>
    <div class="inner-box">
        <div class="content-name">
            <h2 class="dp-ib">{{title}}</h2>
            <div class="btn-wrap btn-type1 clearfix">
                <button class="btn-size btn-blue fl_left" @click="approval"><span class="btn-icon"><i class="fas fa-pen-alt"></i></span> 결재상신</button>
                <button class="btn-size btn-gray fl_left" @click="newPage"><span class="btn-icon"><i class="far fa-file"></i></span> 신규</button>
                <button class="btn-size btn-gray fl_left" @click="remove" v-if="showDeleteButton"><span class="btn-icon"><i class="far fa-trash-alt"></i></span> 삭제</button>
                <button class="btn-size btn-gray fl_left" @click="save"><span class="btn-icon"><i class="fas fa-check"></i></span> 저장</button>
            </div>
        </div>

        <!-- 테이블 -->
        <div class="table-area">
            <slip-basic ref="header" :slipTypeCd="slipTypeCd" :slipHeader="slipHeader" :slipDetails="slipDetails" @changeViewMode="toggleDeleteButton"/>
        </div>
        <!-- //테이블 -->
    </div>
</template>

<script>
    // eslint-disable-next-line
    import Vue from 'vue';
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import SlipBasic from '@/components/SlipBasic.vue';
    import ApprSubm from '@/views/ApprSubm.vue';
    import _ from 'lodash'

    export default {
        name: 'BillSlipReg',
        components: {SlipBasic, ApprSubm},
        props: ['eaSlipNo', 'copy'],
        mixins: [mixin, mixinSlip],
        data() {
            return {
                title: '수기세금계산서 전표',
                slipTypeCd: 'E3',
                slipHeader: {},
                slipDetails: [],
                showDeleteButton: false,
                copyMode: false,
                showVendorModal1: false,
            };
        },
        methods: {
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
                    // console.log(rowObj);
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

                console.log(header)

                this.$http.post(`/api/slip`, header)
                    .then((response) => {
                        // console.log(response.data);
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
            getSlip(eaSlipNo) {
                if (eaSlipNo != undefined && eaSlipNo != '0') {
                    let url;
                    if (this.copyMode === true) {
                        url = `/api/slip/copy/${eaSlipNo}`;
                    } else {
                        url = `/api/slip/${eaSlipNo}`;
                    }
                    this.$http.get(url)
                        .then(response => {
                            console.log(response.data)
                            if (response.data) {
                                this.slipHeader = response.data.slipHeader;
                                this.slipDetails = response.data.slipDetails;
                                console.log("slipHeader", this.slipHeader)
                            }
                        })
                        .catch(({message}) => {
                            console.error(message);
                            // this.$swal({ type: 'warning', text: '해당 전표가 존재하지 않습니다.' });
                        });
                } else {

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
                console.log('!!!!!!@@@@@@@@@@')
                console.log(JSON.stringify(this.slipHeader))
                console.log(JSON.stringify(this.slipDetails))

                if (this.slipHeader.eaSlipNo === undefined) {
                    this.$swal({type: 'warning', text: '저장 후 작업해주세요.'});
                    return false;
                }

                this.slipHeader.slipDetails = this.slipDetails

                this.$modal.open({
                    component: ApprSubm,
                    props: {
                        docType: 'SLIP',
                        value: this.slipHeader
                    },
                    parent: this,
                    fullScreen: true,
                    width: 1200,
                    events: {
                        close() {
                            console.log('닫힘 이벤트')
                        }
                    }
                })
            },
            init() {
                this.copyMode = this.copy;
                console.log("전표번호 수신", this.eaSlipNo)
                this.getSlip(this.eaSlipNo);
            }
        },
        mounted() {
            this.init();
        },
    };
</script>

<style>
    /* file-upload */
    .file.has-name {
        width: 265px;
    }

    .file.has-name .file-cta {
        position: relative;
        height: 46px;
        padding: 0 25px;
        border: 1px solid #adadad;
        font-family: 'NotoM';
        font-size: 15px;
        color: #222;
        vertical-align: middle;
        background: none;
        border-right: none;
    }

    .file.has-name .icon-bar {
        position: absolute;
        right: 0;
        top: 13px;
    }

    .file .file-name {
        height: 46px;
        border: 1px solid #adadad !important;
        border-left: none !important;
        font-family: 'RobotoM';
        font-size: 15px;
        color: #0065b3;
        vertical-align: middle;
        padding: 11px 0 11px 25px;
    }

    .file .file-name i {
        font-size: 18px;
        margin: 0 25px;
    }

    .popup {
        width: 680px;
    }

    .popup .pop-content {
        width: 630px;
    }

    .td-s-thumb.search-area .ip-box,
    .td-s-thumb.search-area .ip-box.ip-box-w02 {
        width: 60%;
    }

    @media (max-width: 1500px) {
        .rs-mt2 {
            margin-top: 2px;
            margin-bottom: 2px;
        }

        .td-s-thumb.search-area .ip-box,
        .td-s-thumb.search-area .ip-box.ip-box-w02 {
            width: 80%;
        }
    }
</style>

