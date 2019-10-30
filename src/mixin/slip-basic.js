// Import components
import _ from 'lodash'
import {
  url as _url
} from '@/libs/join'
import assert from '@/libs/assert'
import debug from '@/libs/debug'

const _debug = debug('slip-basic')

import SlipBase from '@/components/slip/SlipBase.vue'
import ApprSubm from '@/views/ApprSubm.vue';
import ApprDtlQryPop from '@/views/ApprDtlQryPop.vue';

function queryBudget(postDt, cctrCd, acctCd) {
  return this.$http.get('/api/budget/remain', {
    params: {
      postDt,
      cctrCd,
      acctCd
    }
  })
}

export default {
  props: {
    eaSlipNo: {
      type: String,
      required: false
    },
    copyEaSlipNo: {
      type: String,
      required: false
    }
  },
  components: {
    SlipBase,
    ApprSubm,
    ApprDtlQryPop
  },
  data() {
    return {
      status: {
        new: true,
        loaded: false,
        readonly: false,
        change: false,
        memento: []
      }
    }
  },
  computed: {
    /**
     * 신규 전표 여부
     */
    isNew() {
      return this.eaSlipNo === undefined
    },
    isReadOnly() {
      return this.status.readonly
    },
    /**
     * 결재상신 가능 여부
     */
    isSubmitable() {
      return this.isNew || !this.status.readonly
    },
    /**
     * 신규작성 가능 여부
     */
    isCreateable() {
      return this.isNew || !this.status.readonly
    },
    /**
     * 삭제 가능 여부
     */
    isDeleteable() {
      return !this.isNew && !this.status.readonly
    },
    /**
     * 저장 가능 여부
     */
    isSaveable() {
      return this.isNew || !this.status.readonly
    }
  },
  methods: {
    /**
     * 데이터 검증
     */
    validate() {
      return new Promise(async (resolve, reject) => {

        _debug.apply(this, ['validate', 'Begin validate'])

        var data = this.data
        var messages = {
          evdCustCd: {
            E4: '지급처를 선택해주세요.',
            E6: '지급처를 선택해주세요.'
          }
        }

        try {
          /**
           * 헤더에 대한 Validation
           */
          assert.apply(this, [data.evdTypeCd, '증빙유형을 선택해 주세요.'])
          assert.apply(this, [data.stlFgCd, '정산구분을 선택해 주세요.'])
          assert.apply(this, [data.postDt, '회계일자를 선택해 주세요.'])
          assert.apply(this, [data.evdCustCd, messages['evdCustCd'][data.slipTypeCd] ? messages['evdCustCd'][data.slipTypeCd] : '거래처를 선택해 주세요.'])
          if (data.slipTypeCd !== 'E6') {
            assert.apply(this, [this.$numeral(data.supAmt).value(), '공급가액을 입력해 주세요.'])
          }
          assert.apply(this, [data.payDueDt, '지급예정일을 선택해 주세요.'])
          assert.apply(this, [data.baseDeptCd, '기준부서를 선택해 주세요.'])
          assert.apply(this, [data.custAccount, '지급계좌를 선택해 주세요.'])
          assert.apply(this, [data.hdSgtxt, '적요를 입력해 주세요.'])

          switch (data.evdTypeCd) {
            case '40':
              assert.apply(this, [data.crcptMerchNm, '상호명을 입력해 주세요.'])
              assert.apply(this, [data.crcptBizNo, '사업자번호를 입력해 주세요.'])
              assert.apply(this, [data.crcptNo, '승인번호를 입력해 주세요.'])
              break
          }

          /**
           * Detail에 대한 Validation
           */
          // 교통비만 아니면 차변/대변 일치여부 검증
          if (data.slipTypeCd !== 'E6') {
            // 차변금액 & 대변금액 일치 여부 확인
            var creditAmt = data.slipDetails.map(x => x.creditAmt || 0).reduce((acc, cur) => acc + cur)
            var debitAmt = data.slipDetails.map(x => x.debitAmt || 0).reduce((acc, cur) => acc + cur)
            assert.apply(this, [creditAmt === debitAmt, '차변금액과 대변금액이 일치하지 않습니다.'])
          }

          // 교통비인경우
          if (data.slipTypeCd === 'E6') {
            var a = data.slipDetails.map(x => this.$moment(x.useDt).format('YYYYMM')).filter((x, i, arr) => arr.indexOf(x) === i)
            assert.apply(this, [a.length === 1, '사용일자가 다른 월에 있습니다.'])
          }

          // 디테일한 검증
          data.slipDetails.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'D_ITEM').forEach(v => {
            // 공통 체크 부분
            assert.apply(this, [v.acctCd, `No.${v.itemSeq}의 계정과목을 선택해 주세요.`])

            switch (data.slipTypeCd) {
              case 'E6':
                assert.apply(this, [v.stptPlc, `No.${v.itemSeq}의 출발지를 입력해 주세요.`])
                assert.apply(this, [v.dstnPlc, `No.${v.itemSeq}의 도착지를 입력해 주세요.`])
                assert.apply(this, [v.biztrpObj, `No.${v.itemSeq}의 출장목적을 입력해 주세요.`])
                if (v.tpsTypeCd === '10') {
                  assert.apply(this, [v.tpsDst, `No.${v.itemSeq}의 거리를 입력해 주세요.`])
                  assert.apply(this, [v.oilKindCd, `No.${v.itemSeq}의 유종을 입력해 주세요.`])
                  assert.apply(this, [v.oilUpc && v.oilEff, `${this.$moment(v.useDt).format('YYYY-MM')}의 유류단가/연비가 없습니다.`])
                }
                assert.apply(this, [v.acctAmt, `No.${v.itemSeq}의 사용금액이 0원입니다.`])
                break
              default:
                assert.apply(this, [v.cctrCd, `No.${v.itemSeq}의 귀속부서를 선택해 주세요.`])
                break
            }
          })

          // 예산 검증
          let budget = data.slipDetails.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'D_ITEM').map(x => {
            return {
              id: [data.postDt, x.cctrCd, x.acctCd].join('_'),
              postDt: data.postDt,
              cctrCd: x.cctrCd,
              cctrNm: x.cctrNm,
              acctCd: x.acctCd,
              acctNm: x.acctNm,
              ctrlYn: x.ctrlYn
            }
          }).filter((x, i, arr) => x.ctrlYn === 'Y' && arr.findIndex(y => y.id === x.id) === i)

          await new Promise(resolve => {
            let cnt = budget.length
            if (cnt < 1) {
              resolve()
            } else {
              _.forEach(budget, x => {
                queryBudget.apply(this, [x.postDt, x.cctrCd, x.acctCd])
                  .then(response => {
                    x.bdgAmt = this.$numeral(response.data).value()
                    if (--cnt === 0) {
                      resolve()
                    }
                  })
              })
            }
          })

          _.forEach(budget, b => {
            let amount = data.slipDetails.filter(x => x.cctrCd === b.cctrCd && x.acctCd === b.acctCd).map(x => x.acctAmt).reduce((ac, val) => ac + val)
            let fn = b.bdgAmt - amount
            assert.apply(this, [fn >= 0, `[${b.cctrCd}/${b.cctrNm}][${b.acctCd}/${b.acctNm}]의 예산이 부족합니다.`])
          })

          _debug.apply(this, ['validate', 'Validate cmpl'])

          resolve()
        } catch (e) {
          this.$swal({
            type: 'error',
            text: e
          }).then(reject)
        }
      })
    },
    /**
     * ==========================================
     * 이벤트 처리 함수
     * ==========================================
     */
    /**
     * 출력 버튼 클릭 이벤트
     */
    buttonEventPrint() {
      // TODO::전표출력
    },
    /**
     * 결재보기 버튼 클릭 이벤트
     */
    buttonEventViewSubmit() {
      if (this.data.grSlipNo) {
        this.$modal.open({
          component: ApprSubm,
          props: {
            docType: 'GR',
            docMngNo: this.data.elecApprId
          },
          parent: this,
          width: 1200
        })
      } else {
        this.$modal.open({
          component: ApprSubm,
          props: {
            docType: 'SLIP',
            value: this.data,
            docMngNo: this.data.elecApprId
          },
          parent: this,
          width: 1200
        })
      }
    },
    /**
     * 전표복사 버튼 클릭 이벤트
     */
    buttonEventCopy() {
      let name = undefined
      switch (this.data.slipTypeCd) {
        case 'E1':
          name = 'cardSlipReg'
          break
        case 'E2':
          name = 'ebillSlipReg'
          break
        case 'E3':
          name = 'billSlipReg'
          break
        case 'E4':
          name = 'evidSlipNew'
          break
        case 'E6':
          name = 'whtSlipNew'
          break
      }
      this.$router.push({
        name: name,
        params: {
          eaSlipNo: (this.data.slipTypeCd === 'E1' || this.data.slipTypeCd === 'E2') ? this.data.eaSlipNo : undefined,
          copyEaSlipNo: this.data.eaSlipNo,
          copy: true
        }
      })
    },
    /**
     * 결재 상신 버튼 클릭 이벤트
     */
    buttonEventSubmit() {
      if (this.isNew) {
        this.buttonEventSave(__proceed)
      } else {
        __proceed.apply(this, [this.eaSlipNo])
      }

      function __proceed(eaSlipNo) {
        const vm = this
        this.$modal.open({
          component: ApprSubm,
          props: {
            docType: 'SLIP',
            value: this.data
          },
          parent: this,
          width: 1200,
          events: {
            close() {
              if (vm.$route.eaSlipNo !== undefined) {
                location.reload()
              } else {
                vm.$router.push({
                  name: vm.name,
                  params: {
                    eaSlipNo
                  }
                })
              }
            }
          }
        })
      }
    },
    /**
     * 신규 작성 버튼 클릭 이벤트
     */
    buttonEventCreate() {
      if (this.status.memento.length > 1) {
        this.$swal({
          type: 'warning',
          text: '변경된 데이터가 있습니다. 계속 하시겠습니까?',
          showCancelButton: true
        }).then(val => {
          val.value ? this.create() : 0
        })
      } else {
        this.create()
      }
    },
    /**
     * 삭제 버튼 클릭 이벤트
     */
    buttonEventDelete() {
      this.$swal({
        type: 'question',
        text: '삭제하시겠습니까?',
        showCancelButton: true
      }).then(val => {
        if (val.value) {
          this.$http.delete(_url('/api/slip', this.data.eaSlipNo))
            .then(response => {
              this.$swal({
                type: 'success',
                text: '삭제되었습니다.'
              }).then(() => {
                this.$router.push({
                  name: 'slipLst'
                })
              })
              return response
            })
            .catch(response => {
              return response
            })
        }
      })
    },
    /**
     * 저장 버튼 클릭 이벤트
     */
    buttonEventSave(callback) {
      this.validate()
        .then(() => {
          // TODO::데이터 저장
          var slipHeader = _.clone(this.data)
          // 작성일자를 지운다
          delete slipHeader.wrtDtm
          delete slipHeader.regDtm
          delete slipHeader.fnlApprDtm
          delete slipHeader.fnlAprverId
          delete slipHeader.elecApprId
          delete slipHeader.elecApprDtm
          for (var member in slipHeader) {
            if (slipHeader[member] != null) {
              if (member.match(/.*Amt$/g)) {
                slipHeader[member] = this.$numeral(slipHeader[member]).value()
              } else if (member.match(/.*(Dt)$/g)) {
                slipHeader[member] = this.$moment(slipHeader[member]).format('YYYYMMDD')
              }
            }
          }

          slipHeader.slipDetails = slipHeader.slipDetails.map(x => {
            delete x.regDtm
            delete x.chgDtm
            for (var member in x) {
              if (x[member] != null) {
                if (member.match(/^.*Amt$/g)) {
                  x[member] = this.$numeral(x[member]).value()
                } else if (member.match(/^.*Dt$/g)) {
                  x[member] = this.$moment(x[member]).format('YYYYMMDD')
                }
              }
            }
            return x
          })

          if (slipHeader.slipTypeCd === 'E6') {
            slipHeader.supAmt = slipHeader.totAmt
          }

          // 대표계정코드
          slipHeader.stnAcctCd = slipHeader.slipDetails.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'D_ITEM')[0].acctCd

          this.$http.post('/api/slip', slipHeader)
            .then(response => {
              if (callback !== undefined && typeof callback === 'function') {
                callback.apply(this, [response.data.eaSlipNo])
              } else {
                this.$swal({
                  type: 'success',
                  text: '저장되었습니다.'
                }).then(() => {
                  this.reroute(response.data.eaSlipNo)
                })
              }
              return response
            })
            .catch(response => {
              return response
            })
        })
    },
    /**
     * 일반 이벤트 함수
     */
    reroute(eaSlipNo) {
      //    if (this.eaSlipNo === undefined || this.eaSlipNo !== eaSlipNo) {
      this.$router.push({
        name: this.name + 'Edit',
        params: {
          eaSlipNo
        }
      })
      /*      } else {
              window.location.reload()
            }*/
    },
    create() {
      if (this.$route.params.eaSlipNo) {
        this.$router.push({
          name: this.name + 'New'
        })
      } else {
        window.location.reload()
      }
    },
    setGridStatus(isLoaded, isNew, isReadonly) {
      this.status.loaded = isLoaded
      this.status.new = isNew
      this.status.readonly = isReadonly
      this.gridType = isReadonly ? 'GridRO' : 'GridED'
      this.$forceUpdate()
    },
    uploadFile() {
      this.$modal.open({
        component: EvidAtchPop,
        parent: this,
        width: 1200
      })
    }
  },
  created() {
    this.status.memento = []
  }
}
