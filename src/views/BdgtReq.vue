<template>
<div class="inner-box">
  <div class="content-name">
    <h2 class="dp-ib">예산 신청서</h2>
    <div class="btn-wrap btn-type1 clearfix" v-if="(!manage && isReadonly) || (manage && ['20', '30', '40', '60', '70'].indexOf(data.budStatCd) >= 0)">
      <button class="btn-size btn-gray fl_left" @click="buttonClickEvent_View">
        <span class="btn-icon"><i class="fas fa-check"></i></span>
        결재보기
      </button>
    </div>
    <div class="btn-wrap btn-type1 clearfix" v-else-if="manage && ['50', '60', '70'].indexOf(data.budStatCd) >= 0">
      <button class="btn-size btn-orange fl_left" @click="buttonClickEvent_Reject">
        <span class="btn-icon"><i class="fas fa-redo"></i></span>
        기획반려
      </button>
      <button class="btn-size btn-blue fl_left" @click="buttonClickEvent_Approve">
        <span class="btn-icon"><i class="fas fa-check"></i></span>
        기획확정
      </button>
    </div>
    <div class="btn-wrap btn-type1 clearfix" v-else-if="manage && ['50'].indexOf(data.budStatCd) < 0">
    </div>
    <div class="btn-wrap btn-type1 clearfix" v-else>
      <button class="btn-size btn-blue fl_left" @click="buttonClickEvent_Submit">
        <span class="btn-icon"><i class="fas fa-check"></i></span>
        결재상신
      </button>
      <button class="btn-size btn-gray fl_left" @click="buttonClickEvent_New">
        <span class="btn-icon"><i class="fas fa-file"></i></span>
        신규
      </button>
      <button class="btn-size btn-orange fl_left" @click="buttonClickEvent_Delete" v-if="isSaved">
        <span class="btn-icon"><i class="fas fa-trash-alt"></i></span>
        전체 삭제
      </button>
      <button class="btn-size btn-blue fl_left" @click="buttonClickEvent_Save">
        <span class="btn-icon"><i class="fas fa-save"></i></span>
        저장
      </button>
    </div>
  </div>

  <bdg-req :budReqNo="budReqNo" :manage="manage" :status="status" v-model="data" />
</div>
</template>

<script>
/**
 * EA-03-01 / EA-03-02
 * 예산 신청
 */
import assert from '@/libs/assert'

import BdgReq from '@/components/BdgReq.vue'
import ApprSubm from '@/views/ApprSubm.vue'

function _openApprModal(budReqNo, callback) {
  let vm = this

  this.$modal.open({
    component: ApprSubm,
    props: {
      docType: 'BDGT',
      budReqNo: this.budReqNo,
      value: this.data
    },
    parent: this,
    width: 1200,
    events: {
      close(data) {
        if (callback !== undefined && typeof callback === 'function') {
          callback.apply(this, [data])
        }
      }
    }
  })
}

function _openApprViewModal(budReqNo, callback) {
  let vm = this

  this.$modal.open({
    component: ApprSubm,
    props: {
      docType: 'BDGT',
      budReqNo: this.budReqNo,
      docMngNo : this.data.elecApprId,
      value: this.data
    },
    parent: this,
    width: 1200,
    events: {
      close(data) {
        if (callback !== undefined && typeof callback === 'function') {
          callback.apply(this, [data])
        }
      }
    }
  })
}

export default {
  props: {
    budReqNo: {
      type: String,
      required: false
    },
    manage: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  components: {
    BdgReq,
    ApprSubm
  },
  data() {
    return {
      data: {
        //예산신청번호
        budReqNo: undefined,
        budgetDetails: [],
        //회사코드
        compCd: undefined,
        //신청상태코드
        budStatCd: '10',
        //예산구분코드
        budFgCd: '10',
        budFgNm: undefined,
        //전용유형코드
        brwTypeCd: undefined,
        //신청총금액
        reqTotAmt: 0,
        //신청사유
        reqRsn: '',
        //ERP관리번호
        erpMngNo: undefined,
        //최종결재일시
        fnlApprDtm: undefined,
        //최종결재자ID
        fnlAprverId: undefined,
        //전자결재ID
        elecApprId: undefined,
        //전자결재기안일시
        elecApprDtm: undefined,
        //반려사유
        rejRsn: undefined,
        //작성자ID
        wrtId: undefined,
        //작성부서코드
        wrtDeptCd: undefined,
        //작성일자
        wrtDt: undefined,
        //증빙관리번호
        evdMngNo: undefined,
        //문서고유값
        docInVal: undefined
      },
      status: {
        memento: [],
        readonly: false
      }
    }
  },
  computed: {
    isNew() {
      return this.budReqNo === undefined
    },
    isSaved() {
      return this.budReqNo !== undefined
    },
    isReadonly() {
      return this.status.readonly
    }
  },
  methods: {
    buttonClickEvent_View() {
      console.log(JSON.stringify(this.data))
      _openApprViewModal.apply(this, [this.budReqNo])
    },
    buttonClickEvent_Submit() {
      if (this.isNew || this.status.memento.length > 1) {
        // 먼저 저장을 수행한다
        this.buttonClickEvent_Save(true)
          .then(response => {
            let budReqNo = response.data.budReqNo
            _openApprModal.apply(this, [budReqNo])
          })
      } else {
        _openApprModal.apply(this, [this.budReqNo])
      }
    },
    buttonClickEvent_New() {
      if (this.memento.length > 1) {
        this.$swal({
          type: 'warning',
          text: '수정내용이 있습니다. 신규 작성을 계속하시겠습니까?',
          showCancelButton: true
        }).then(r => {
          r.value ? _proceed.apply(this, []) : 0
        })
      } else {
        // DO Nothing...Because u don't need create new again
        _proceed.apply(this, [])
      }

      function _proceed() {
        if (this.$route.name === 'bdgtReqNew') {
          window.location.reload()
        } else {
          this.$router.push({
            name: 'bdgtReqNew'
          })
        }
      }
    },
    buttonClickEvent_Delete() {
      this.$swal({
        type: 'question',
        text: '삭제하시겠습니까?',
        showCancelButton: true
      }).then(r => {
        if (r.value) {
          this.$http.delete(`/api/budget/${this.data.budReqNo}`)
            .then(response => {
              this.$swal({
                type: 'success',
                text: '삭제되었습니다.'
              }).then(() => {
                this.$router.push({
                  name: 'bdgtReqNew'
                })
              })
            })
        }
      })
    },
    buttonClickEvent_Save(s) {
      return new Promise((resolve, reject) => {
        try {
          let data = _.clone(this.data)

          assert.apply(this, [data.reqRsn, '신청사유는 필수 값입니다.'])

          data.reqTotAmt = data.budgetDetails.map(x => x.reqAmt).reduce((a, v) => a + v)
          assert.apply(this, [data.reqTotAmt > 0, '신청 금액은 0원일 수 없습니다.'])

          _.forEach(data.budgetDetails, (r, i) => {
            r.budSeq = i + 1
            r.reqAmt = this.$numeral(r.reqAmt).value()

            switch (r.brwTypeCd) {
              case '10':
                assert.apply(this, [r.rcvYm, '받는 대상의 연월을 입력해주세요.'])
                assert.apply(this, [r.rcvCctrCd, '받는 대상의 부서를 선택해주세요.'])
                assert.apply(this, [r.rcvAcctCd, '받는 대상의 계정을 선택해주세요.'])
                break
              case '20':
                assert.apply(this, [r.sndYm, '주는 대상의 연월을 입력해주세요.'])
                assert.apply(this, [r.sndCctrCd, '주는 대상의 부서를 선택해주세요.'])
                assert.apply(this, [r.sndAcctCd, '주는 대상의 계정을 선택해주세요.'])
                assert.apply(this, [r.rcvYm, '받는 대상의 연월을 입력해주세요.'])
                assert.apply(this, [r.sndYm !== r.rcvYm, '주는 대상의 연월과 받는 대상의 연월이 같습니다.'])
                break
              case '30':
                assert.apply(this, [r.sndYm, '주는 대상의 연월을 입력해주세요.'])
                assert.apply(this, [r.sndCctrCd, '주는 대상의 부서를 선택해주세요.'])
                assert.apply(this, [r.sndAcctCd, '주는 대상의 계정을 선택해주세요.'])
                assert.apply(this, [r.rcvAcctCd, '받는 대상의 계정을 선택해주세요.'])
                break
              case '40':
                assert.apply(this, [r.sndYm, '주는 대상의 연월을 입력해주세요.'])
                assert.apply(this, [r.sndCctrCd, '주는 대상의 부서를 선택해주세요.'])
                assert.apply(this, [r.sndAcctCd, '주는 대상의 계정을 선택해주세요.'])
                assert.apply(this, [r.rcvCctrCd, '받는 대상의 부서를 선택해주세요.'])
                break
            }

            switch (r.brwTypeCd) {
              case '20':
              case '30':
              case '40':
                assert.apply(this, [r.rmdAmt >= r.reqAmt, '주는 대상의 예산 잔액이 부족합니다.'])
                break
            }
          })

          this.$store.commit('loading')
          this.$http.post('/api/budget', data)
            .then(response => {
              if (s !== true) {
                this.$swal({
                  type: 'success',
                  text: '저장되었습니다.'
                }).then(() => {
                  if (this.$route.name === 'bdgtReqNew') {
                    this.$router.push({
                      name: 'bdgtReqEdit',
                      params: {
                        budReqNo: response.data.budReqNo
                      }
                    })
                  } else {
                    this.queryBdgtReq()
                  }
                })
              }
              return resolve(response)
            })
            .catch(response => {
              return reject(response)
            })
            .finally(() => {
              this.$store.commit('finish')
            })
        } catch (e) {
          this.$swal({
            type: 'error',
            text: e
          }).then(reject)
        }
      })
    },
    buttonClickEvent_Approve() {
      // TODO::기획 확정 URL
      const url = '/api/budget'

      try {
        assert.apply(this, [this.data.budStatCd !== '60' && this.data.budStatCd !== '70', '기획 확정 또는 반려된 예산은 다시 확정 또는 반려 작업을 할 수 없습니다.'])

        this.$swal({
          type: 'question',
          text: '확정 후 취소 되지 않습니다. 확정작업을 계속 하시겠습니까?',
          showCancelButton: true
        }).then(r => {
          if (r.value) {
            this.$http.post(url, this.data)
              .then(response => {
                this.$swal({
                  type: 'success',
                  text: '확정되었습니다.'
                }).then(() => {
                  window.location.reload()
                })
                return response
              })
          }
        })
      } catch (e) {
        // error handling
        this.$swal({
          type: 'error',
          text: e
        })
      }
    },
    buttonClickEvent_Reject() {
      // TODO::기획 반려 URL
      const url = '/api/budget'

      try {
        assert.apply(this, [this.data.budStatCd !== '60' && this.data.budStatCd !== '70', '기획 확정 또는 반려된 예산은 다시 확정 또는 반려 작업을 할 수 없습니다.'])
        assert.apply(this, [this.data.rejRsn, '기획 반려 시 반려사유를 반드시 작성해 주십시오.'])

        this.$swal({
          type: 'question',
          text: '반려 후 취소 되지 않습니다. 반려작업을 계속 하시겠습니까?',
          showCancelButton: true
        }).then(r => {
          if (r.value) {
            this.$http.post(url, this.data)
              .then(response => {
                this.$swal({
                  type: 'success',
                  text: '반려되었습니다.'
                }).then(() => {
                  window.location.reload()
                })
                return response
              })
          }
        })
      } catch (e) {
        // error handling
        this.$swal({
          type: 'error',
          text: e
        })
      }
    }
  },
  mounted() {
    console.log('Mounted this.budReqNo : ' + this.budReqNo)
  }
}
</script>
