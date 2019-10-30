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
          <slip-basic ref="header" :slipTypeCd="slipTypeCd" :slipHeader="slipHeader" :slipDetails="slipDetails" @changeViewMode="toggleDeleteButton" />
      </div>
      <!-- //테이블 -->

  </div>
</template>

<script>
// eslint-disable-next-line
import Vue from 'vue';
import mixin from '@/mixin';
import mixinSlip from '@/mixin/slip';
import SlipBasic from '@/components/CardSlipBasic.vue';
import ApprSubm from '@/views/ApprSubm.vue';
import _ from 'lodash'

export default {
  name: 'CardSlipReg',
  components: { SlipBasic, ApprSubm },
  props: ['eaSlipNo','useDtlsNo','copy'],
  mixins: [ mixin, mixinSlip ],
  data() {
    return {
      title: '법인카드 전표',
      slipTypeCd: 'E1',
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
      if(!this.$refs.header.validation()) return;
      // if(!this.$refs.detail.validation()) return;

      const header = JSON.parse(JSON.stringify(this.$refs.header.form));
      const stripFields = ['cardNo','evdDt','postDt','payDueDt','totAmt','supAmt','vatAmt','tips'];
      _.forEach(stripFields, (name) => header[name] = this.toPure(header[name]));
      // 전표유형
      header.slipTypeCd = this.slipTypeCd;
      // 작성일자 삭제
      header.wrtDtm = '';

      console.log("저장 직전 slipHeader", header)

      const grid = this.$refs.header.$refs.detail.$refs.grid;

      var details = [];
      var rowIds = [];
      var once = false;

      this.doLineAction(grid, {
        credit: (grid,rId) => {
          header.apAcctCd = grid.cells(rId,7).getValue();
        },
        cost: (grid,rId) => {
          if(!once) {
            // header.apAcctCd = grid.cells(rId,7).getValue();
            header.stnAcctCd = grid.cells(rId,7).getValue();
            once = true;
          }
        },
        all: (grid,rId) => {
          let rowObj = grid.getRowData(rId);
          rowObj.acctAmt = _.toInteger(rowObj.creditAmt) + _.toInteger(rowObj.debitAmt);
          details.push(rowObj);
        }
      });

      header.slipDetails = details;

      console.log(header)

      this.$http.post(`/api/slip`, header)
        .then((response) => {
          // console.log(response.data);
          this.$swal({
            type: 'success',
            text: '저장되었습니다.'
          }).then(() => {
            this.copyMode = false;
            this.getSlip(response.data.eaSlipNo);
          })
        })
        .catch((e) => {
          console.error(e);
        });
    },
    remove() {
      const eaSlipNo = this.$refs.header.form.eaSlipNo;
      console.log("삭제...", eaSlipNo)
      if(eaSlipNo != undefined) {
        this.$http.delete(`/api/slip/${eaSlipNo}`)
            .then(response => {
              if(response.status === 200) {
                this.$swal({ type: 'warning', text: response.data });
                console.log("삭제 후 페이지 이동 필요")
                this.$router.push({ path: `/cardSlipUseLst` });
              }
            });
      }
    },
    getSlip(eaSlipNo) {
      if(eaSlipNo != undefined && eaSlipNo != '0') {
        let url;
        if(this.copyMode === true) {
          url = `/api/slip/copy/${eaSlipNo}`;
        } else {
          url = `/api/slip/${eaSlipNo}`;
        }
        this.$http.get(url)
            .then(response => {
              if(response.data) {
                this.slipHeader = response.data.slipHeader;
                this.slipDetails = response.data.slipDetails;
                console.log("slipHeader", this.slipHeader)
              }
            })
            .catch(({message}) => {
              console.error(message);
              // this.$swal({ type: 'warning', text: '해당 전표가 존재하지 않습니다.' });
            });
      }
    },
    getCardUseList() {
      this.$http.get(`/api/card/${this.useDtlsNo}`)
        .then(({data}) => {
          if(data) {
            data.slipTypeCd = 'E1';
            data.evdDt = data.apprDate;
            data.custAcctNo = data.acctNo;
            data.custBnkCd = data.bnkCd;
            data.baseDeptCd = data.crdPssrDeptCd;
            data.baseDeptNm = data.crdPssrDeptNm;
            data.taxCd = data.taxCd||'C9';
            data.totAmt = data.purchTot;
            data.supAmt = data.apprAmt;
            data.vatAmt = data.vat;
            data.useDtlsNo = this.useDtlsNo;
            data.crdNo = data.cardNo;
            data.crdApprNo = data.apprNo;
            data.crdMerchNm = data.merchNm;

            console.log("slipHeader전달", data)
            this.slipHeader = data;
          }
        })
        .catch(({message}) => {
          console.error(message);
        });
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
        if(result.value) {
          // this.init();
          this.$router.push({ path: '/cardSlipUseLst' });
        }
      });
    },
    approval() {
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
      // console.log("결재상신 처리")
      //   if (!this.slipHeader.eaSlipNo) {
      //       this.$swal({type: 'warning', text: '저장 후 상신해주세요.'});
      //       return false;
      //   }
      //   console.log('슬립헤더 내용확인 : '+this.slipHeader.crdNo);
      //   this.showVendorModal1 = true;
    },
    init() {
      this.copyMode = this.copy;
      console.log("전표번호 수신", this.eaSlipNo)
      if(this.eaSlipNo) {
        this.getSlip(this.eaSlipNo);
      } else if(this.useDtlsNo) {
        this.getCardUseList()
      }
    },
  },
  mounted() {
    this.init();
  },
};
</script>

<style>
/* file-upload */
.file.has-name{width:265px;}
.file.has-name .file-cta{position:relative; height:46px; padding:0 25px; border:1px solid #adadad; font-family:'NotoM';  font-size:15px; color:#222; vertical-align:middle; background:none; border-right:none;}
.file.has-name .icon-bar{position:absolute; right:0; top:13px;}
.file .file-name{height:46px; border:1px solid #adadad!important; border-left:none!important; font-family:'RobotoM'; font-size:15px; color:#0065b3; vertical-align:middle; padding:11px 0 11px 25px;}
.file .file-name i{font-size:18px; margin:0 25px;}

.popup{width:680px;}
.popup .pop-content{width:630px;}

.td-s-thumb.search-area .ip-box,
.td-s-thumb.search-area .ip-box.ip-box-w02{width:60%;}

@media (max-width:1500px) {
    .rs-mt2{margin-top:2px; margin-bottom:2px;}
    .td-s-thumb.search-area .ip-box,
    .td-s-thumb.search-area .ip-box.ip-box-w02{width:80%;}
}
</style>
