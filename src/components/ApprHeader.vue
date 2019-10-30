<template>
    <div>
        <div class="table-a">
            <div class="table-name">
                <h3 class="ico_table_name">문서정보</h3>
            </div>
            <table class="table">
                <colgroup>
                    <col width="10%">
                    <col width="20%">
                    <col width="10%">
                    <col width="20%">
                    <col width="10%">
                    <col width="20%">
                </colgroup>
                <tbody>
                    <tr>
                        <th>문서유형</th>
                        <td>{{form.docType}}</td>
                        <th>문서번호</th>
                        <td>{{form.apprNo}}</td>
                        <th>문서상태</th>
                        <td>{{form.docStatNm}}</td>
                    </tr>
                    <tr>
                        <th>제목</th>
                        <td colspan="5">{{ form.docTitleNm }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="table-b">
            <div class="table-name">
                <h3 class="ico_table_name">결재선</h3>
            </div>
            <table class="table">
                <colgroup>
                    <col width="3%">
                    <col width="7%">
                    <col width="20%">
                    <col width="20%">
                    <col width="10%">
                    <col width="10%">
                    <col width="30%">
                </colgroup>
                <thead>
                <tr>
                    <th class="no-radius">NO</th>
                    <th>결재유형</th>
                    <th>결재자</th>
                    <th>실제결재자</th>
                    <th>결재상태</th>
                    <th>결재일자</th>
                    <th style="border-right: 1px solid #adadad">의견</th>
                </tr>
                </thead>
                <tbody id="tbody">
                <tr v-for="(item, index) in form.apprDetailsData">
                    <td style="text-align: center;">{{index+1}}</td>
                    <td style="text-align: center;">{{item.apprType}}</td>
                    <td>{{item.aprverUser}}</td>
                    <td>{{item.aaprverUser}}</td>
                    <td style="text-align: center;">{{item.apprStatus}}</td>
                    <td style="text-align: center;">{{item.apprDtm}}</td>
                    <td style="border-right: 1px solid #adadad">{{item.apprDesc}}</td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
    /* eslint-disable */
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';

    export default {
        name: 'ApprHeader',
        props: {
            'value': {
                type: Object,
                required: true
            },
            'apprHeader': {
                type: Object,
                required: false,
                default() {
                    return {}
                }
            },
            'apprLine': {
                type: Array,
                required: true
            },
            docType: {
                type: String,
                required: false,
                default: 'SLIP'
            }
        }, //['apprHeader', 'apprLine', 'slipHeader'],
        mixins: [mixin, mixinSlip],
        data() {
            return {
                form: {
                    apprDetailsData: [],
                    //문서유형
                    docType: '',
                    //문서번호
                    apprNo: '',
                    //문서상태
                    docStatNm: '',
                    //문서제목
                    docTitleNm: '',
                    //NO
                    apprSeq: '',
                    //결재유형
                    apprType: '',
                    //결재자
                    aprverUser: '',
                    //실제결재자
                    aaprverUser: '',
                    //결재상태
                    apprStatus: '',
                    //결재일자
                    apprDtm: '',
                    //의견
                    apprDesc: '',
                    apprSubYn: 'Y',
                },
                docTypes: [],
            };
        },
        methods: {
            getDocTypeCombo() {
                this.$http.get(`/api/code/combo`, {params: {groupCd: "DOC_TYPE_CD"}})
                    .then(response => {
                        this.docTypes = response.data;
                    });
            },
            setApprHeader() {
                Object.assign(this.form, this.apprHeader[0]);
            },
            changeFormTitleEvent(value) {
                // 전표임
                if (this.docType === 'SLIP') {
                    this.form.docType = '전표'
                    this.form.docTitleNm = value.slipTypeNm + ' / ' + this.$filters.number(value.totAmt) + ' / ' + value.hdSgtxt
                } else if (this.docType === 'BDGT') {
                    this.form.docType = '예산'
                    this.form.docTitleNm = value.budFgNm + ' / ' + this.$filters.number(value.reqTotAmt) + ' / ' + value.reqRsn
                }
            }
        },
        mounted() {
            console.log('Appr Header Mounted!!')
            this.getDocTypeCombo()
        },
        watch: {
            apprHeader(value) {
                this.form = this.apprHeader || {}
                this.form.apprSubYn = 'N'
                this.setApprHeader()
                // 바뀌었으니 이것도 같이 바꾸어준다
                this.changeFormTitleEvent(this.value)
            },
            apprLine(value) {
                this.form.apprDetailsData = value.map(x => {
                    x.apprDtm = x.apprDtm ? this.$moment(x.apprDtm).format('YYYY-MM-DD') : undefined
                    return x
                })
            },
            'value': {
                immediate: true,
                deep: true,
                handler: 'changeFormTitleEvent'
            }
        }
    };
</script>

<style scoped>
    .table-a, .table-b {
        margin-bottom: 20px;
    }
    .table-a.fixed-th {
        margin-bottom: 10px;
    }
</style>

