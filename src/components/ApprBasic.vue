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
                    <td>{{form.docStatus}}</td>
                </tr>
                <tr>
                    <th>제목</th>
                    <td colspan="5">{{form.docTitleNm}}</td>
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
                    <th>의견</th>
                </tr>
                </thead>
                <tbody id="tbody">
                <tr v-for="item in form.apprDetailsData">
                    <td style="text-align: center;">{{item.apprSeq}}</td>
                    <td style="text-align: center;">{{item.apprType}}</td>
                    <td>{{item.aprverUser}}</td>
                    <td>{{item.aaprverUser}}</td>
                    <td style="text-align: center;">{{item.apprStatus}}</td>
                    <td style="text-align: center;">{{item.apprDtm}}</td>
                    <td>{{item.apprDesc}}</td>
                </tr>
                </tbody>
            </table>
        </div>

        <div class="table-a fixed-th">
            <div class="table-name">
                <h3 class="ico_table_name">{{title}}</h3>
            </div>
            <table class="table">
                <tbody>
                <tr>
                    <th>전표번호</th>
                    <td>{{form.eaSlipNo}}</td>
                    <td></td>

                    <th>전표유형</th>
                    <td>{{form.slipTypeNm}}</td>

                    <th>전표상태</th>
                    <td><span class="color_table_org">{{form.slipStatNm}}</span></td>
                </tr>
                <tr>
                    <th>작성부서</th>
                    <td>{{form.wrtDeptCd}} / {{form.wrtDeptNm}}</td>
                    <td></td>

                    <th>작성자</th>
                    <td>{{form.wrtNm}}</td>

                    <th>작성일자</th>
                    <td class="Rt-M">{{this.$moment(form.wrtDtm).format('YYYY-MM-DD')}}</td>
                </tr>
                <tr>
                    <th>카드번호</th>
                    <td colspan="2">
                        {{form.evdTypeNm}}
                    </td>

                    <th>승인번호</th>
                    <td>
                        <div v-if="form.stlFgCd === 'Y'">선급금정산</div>
                        <div v-else>미정산</div>
                    </td>

                    <th>증빙일자</th>
                    <td>{{this.$moment(form.evdDt).format('YYYY-MM-DD')}}</td>
                </tr>
                <tr>
                    <th>카드소유자</th>
                    <td colspan="2">
                        [{{form.taxCd}}] {{form.taxNm}}
                    </td>

                    <th>카드구분</th>
                    <td class="clearfix">&nbsp;</td>

                    <th>회계일자</th>
                    <td>{{this.$moment(form.postDt).format('YYYY-MM-DD')}}</td>
                </tr>
                <tr>
                    <th>승인금액</th>
                    <td class="Rt-M tar" colspan="2">
                        {{form.supAmt | number}}
                    </td>

                    <th>가맹점명</th>
                    <td>
                        {{form.baseDeptCd}} / {{form.baseDeptNm}}
                    </td>

                    <th>승인시간</th>
                    <td>
                        {{this.$moment(form.payDueDt).format('YYYY-MM-DD')}}
                    </td>
                </tr>
                <tr>
                    <th>공급가액</th>
                    <td colspan="2">
                        {{form.payTermNm}}
                    </td>
                    <th>가맹점주소</th>
                    <td colspan="4">
                        {{form.evdCustCd}} / {{form.evdCustNm}}
                    </td>
                </tr>
                <tr>
                    <th>부가세액</th>
                    <td class="Rt-M tar" colspan="2">
                        {{form.supAmt | number}}
                    </td>

                    <th>과세유형/업종</th>
                    <td>
                        {{form.baseDeptCd}} / {{form.baseDeptNm}}
                    </td>

                    <th>경비처리기한</th>
                    <td>
                        {{this.$moment(form.payDueDt).format('YYYY-MM-DD')}}
                    </td>
                </tr>
                <tr>
                    <th>봉사료</th>
                    <td class="Rt-M tar" colspan="2">
                        {{form.supAmt | number}}
                    </td>

                    <th>공제구분</th>
                    <td>
                        {{form.baseDeptCd}} / {{form.baseDeptNm}}
                    </td>

                    <th>기준부서</th>
                    <td>
                        {{this.$moment(form.payDueDt).format('YYYY-MM-DD')}}
                    </td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>

</template>

<script>
    /* eslint-disable */
    import moment from 'moment'
    import mixin from '@/mixin';
    import mixinSlip from '@/mixin/slip';
    import _ from 'lodash'

    import SlipGrid from '@/components/SlipGridRO.vue';

    export default {
        name: 'ApprBasic',
        props: ['apprHeader', 'apprDetails'],
        mixins: [mixin, mixinSlip],
        components: {SlipGrid},
        data() {
            return {
                title: '기본정보',
                form: {
                    apprDetailsData: [],
                    //문서유형
                    docType: '',
                    //문서번호
                    apprNo: '',
                    //문서상태
                    docStatus: '',
                    //문서제목
                    docTitleNm: '',
                    //NO
                    apprSeq: '',
                    //결재유형
                    apprType: '',
                    //결재자
                    aprverUser: '',
                    //실제결재자
                    aAprverUser: '',
                    //결재상태
                    apprStatus: '',
                    //결재일자
                    apprDtm: '',
                    //의견
                    apprDesc: '',


                    // 전표번호
                    eaSlipNo: '',
                    // 전표유형
                    slipTypeNm: '',
                    // 전표상태코드
                    slipStatCd: '10',
                    // 카드번호
                    crdNo: '',
                    // 카드승인번호
                    crdApprNo: '10',
                    // 카드소유자ID
                    crdPssrId: '',
                    // 증빙유형코드
                    evdTypeCd: '',
                    // 정산구분코드
                    stlFgCd: 'N',
                    // 시스템구분코드WM
                    sysFgCd: 'W',
                    // 세금코드
                    taxCd: '',
                    // 증빙일자
                    evdDt: this.$moment().format('YYYY-MM-DD'),
                    // 회계일자
                    postDt: this.$moment().format('YYYY-MM-DD'),
                    // 증빙거래처코드
                    evdCustCd: '',
                    // 가맹점명
                    merchName: '',
                    // 가맹점주소1
                    merchAddr1: '',
                    // 가맹점주소2
                    merchAddr2: '',
                    // 과세유형
                    etc3: '',
                    // 가맹점 업종명
                    mccName: '',
                    // 경비처리 기한
                    dueDt: this.$moment().format('YYYY-MM-DD'),
                    // 공제구분
                    crdDdctCd: '',
                    // 증빙거래처명
                    evdCustNm: '',
                    // 증빙거래처사업자번호
                    evdCustBizNo: '',
                    // 지급거래처코드
                    payCustCd: '',
                    // 지급거래처명
                    payCustNm: '',
                    // 지급거래처사업자번호
                    payCustBizNo: '',
                    // 지급방법
                    payMthdCd: '',
                    // 지급조건
                    payTermCd: '',
                    // 지급만기일(지급예정일)
                    payDueDt: '',
                    // 거래처계좌번호
                    custAcctNo: '',
                    // 거래처계좌은행코드
                    custBnkCd: '',
                    // 승인시각
                    orginTransTime: '',
                    // 작성일시
                    wrtDtm: '',
                    // 작성자
                    wrtId: '',
                    // 작성부서코드
                    wrtDeptCd: '',
                    // 기준부서코드
                    baseDeptCd: 'O000000023',
                    // 기준부서명
                    baseDeptNm: '연구개발팀',
                    // 미지급계정코드
                    apAcctCd: '',
                    // 대표계정코드
                    stnAcctCd: '',
                    // 승인금액
                    billTot: '',
                    // 공급가액
                    supAmt: '',
                    // 부가세액
                    vatAmt: '',
                    // 기타금액
                    etcAmt: '',
                    // 봉사료
                    tips: '',
                    // 총금액
                    totAmt: '',
                    // 통화코드
                    curCd: 'KRW',
                    // 사업장코드
                    bpCd: '',
                    // 전표적요
                    hdSgtxt: '',
                },
            };
        },
        methods: {
            setApprHeader() {
                console.log("헤더정보 SET!!" + this.apprHeader);
                Object.assign(this.form, this.apprHeader[0]);

            },
            setApprDetails() {
                console.log("디테일정보 SET!!" + this.apprDetails);
                Object.assign(this.form.apprDetailsData, this.apprDetails);

                console.log("결재자 : " + this.form.apprDetailsData[0].aprverUser);
                // format date
                if (this.form.apprDtm) this.form.apprDtm = this.$moment(this.form.apprDtm).format('YYYY-MM-DD');
                this.$forceUpdate();

            },
        },
        computed: {
            columnTitle() {
                return this.form.slipTypeCd === 'E2' ? '전자승인번호' : '통화';
            }
        },
        mounted() {
            /*this.form = this.apprHeader;
            this.goSearch();*/

        },
        watch: {
            apprHeader() {
                this.setApprHeader();
            },
            apprDetails() {
                this.setApprDetails();
            },
        }
    };
</script>

<style>
</style>

