<template>
    <layout>
        <span slot="header">{{title}}<button class="btn-pop-close delete" aria-label="close"
                                             @click="closeModal"></button></span>
        <div slot="content">
            <div class="btn-type1">
                <button class="btn-size btn-gray" @click="save"><span class="btn-icon"><i
                        class="fas fa-check"></i></span> 확인
                </button>
            </div>

            <div class="inner-box">
                <table id="basic">
                    <colgroup>
                        <col width="120px">
                        <col width="480px">
                    </colgroup>
                    <tbody>
                    <tr style="">
                        <th class="tp-a" style="border-top: 1px solid #d7d7d7"> 제목</th>
                        <td style="border-top: 1px solid #d7d7d7"><span>{{form.docTitleNm}}</span></td>
                    </tr>
                    <tr>
                        <th class="tp-a">결재구분</th>
                        <td>
                            <div class="control">
                                <div class="dp-ib fl_left">
                                    <input type="radio" id="radio01" v-model="form.apprFgCd" value="A"/>
                                    <label for="radio01" class="NotoM">승인</label>
                                </div>
                                <div class="dp-ib fl_left">
                                    <input type="radio" id="radio02" v-model="form.apprFgCd" value="R"/>
                                    <label for="radio02" class="NotoM">반려</label>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <th class="tp-a"> 의견</th>
                        <td><textarea v-model="form.apprDesc"></textarea></td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </layout>
</template>

<script>
    import Layout from '@/components/ModalSlot.vue'
    import mixin from '@/mixin';

    export default {
        name: 'ApprActPop',
        props: ['docTitleNm', 'apprNo', 'apprSeq'],
        mixins: [mixin],
        data() {
            return {
                title: '결재 처리',
                form: {
                    apprFgCd: 'A',
                    docTitleNm: '',
                    apprNo: '',
                    apprSeq: '',
                    apprDesc: '',
                },
                returnObject: {},
            }
        },
        methods:
            {
                save() {
                    this.$http.post(`/api/appr/detail/doApproval`, {
                        apprNo: this.form.apprNo,
                        apprSeq: this.form.apprSeq,
                        apprFgCd: this.form.apprFgCd,
                        apprDesc: this.form.apprDesc
                    })
                        .then((response) => {
                            console.log(response.data);
                            this.$parent.close();
                            this.$swal({ type: 'info', text: '결재가 완료되었습니다.' });
                            //this.$parent.$emit('close', this.form.apprNo);

                            this.$emit('close', this.form.apprNo)
                        })
                        .catch((e) => {
                            console.error(e);
                        });
                },
                closeModal() {
                    this.$parent.close();
                }
            }
        ,
        mounted() {
            console.log("팝업 마운트 : " + this.docTitleNm + ", "+ this.apprNo + ", "+ this.apprSeq);
            this.form.docTitleNm = this.docTitleNm;
            this.form.apprNo = this.apprNo;
            this.form.apprSeq = this.apprSeq;
        }
        ,
        components: {
            Layout
        }
    };
</script>

<style scoped>
    div#gridbox {
        width: 100%;
        height: 100%;
        min-height: 300px;
    }

</style>
