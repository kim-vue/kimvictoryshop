<template>
  <div class="inner-box">  
      <div class="content-name">
          <h2 class="dp-ib">{{title}}</h2>
        <div class="btn-wrap btn-type1 clearfix">
            <button class="btn-size btn-gray fl_left"><span class="btn-icon"><i class="fas fa-print"></i></span> 출력</button>
            <button class="btn-size btn-blue fl_left" @click="showApproval=true"><span class="btn-icon"><i class="fas fa-vote-yea"></i></span> 결재보기</button>
            <button class="btn-size btn-orange fl_left" @click="copySlip"><span class="btn-icon"><i class="far fa-clone"></i></span> 전표복사</button>
        </div>
      </div>

      <!-- 테이블 -->
      <div class="table-area">
          <slip-basic ref="header" :slipHeader="slipHeader" :slipDetails="slipDetails" />
      </div>
      <!-- //테이블 -->

      <!--팝업-->
<!--      <b-modal :active.sync="showApproval" has-modal-card>
          <appr-dtl-qry></appr-dtl-qry>
      </b-modal>-->
      <!--//팝업 -->
  </div>
</template>

<script>
// eslint-disable-next-line
import Vue from 'vue';
import mixin from '@/mixin';
import SlipBasic from '@/components/CardSlipBasicRO.vue';
import _ from 'lodash'

export default {
  name: 'CardSlipQry',
  props: ['eaSlipNo'],
  components: { SlipBasic },
  mixins: [ mixin ],
  data() {
    return {
      title: '법인카드 전표',
      // slipTypeCd: 'E3',
      // bus: new Vue(),
      slipHeader: {},
      slipDetails: [],
      showApproval: false,
    };
  },
  methods: {
    getSlip(eaSlipNo) {
      if(eaSlipNo != undefined) {
        this.$http.get(`/api/slip/${this.eaSlipNo}`)
            .then(response => {
              if(response.data) {
                this.slipHeader = response.data.slipHeader;
                this.slipDetails = response.data.slipDetails;
                // console.log(this.slipHeader)
              }
            })
            .catch(({message}) => {
              console.error(message);
              // this.$swal({ type: 'warning', text: '해당 전표가 존재하지 않습니다.' });
            });
      }
    },
    copySlip() {
      this.$router.push({ name: 'cardSlipReg', params: { eaSlipNo: this.eaSlipNo, copy: true } });
    },
  },
  mounted() {
    this.getSlip(this.eaSlipNo);
  }
};
</script>

<style>
</style>

