import _ from 'lodash'

// 모달창
import Cctr from '@/components/Cctr_new.vue'
import Vendor from '@/components/Vendor_new.vue'
import Emp from '@/components/Emp_new.vue'

export default {
  components: {
    Cctr,
    Emp,
    Vendor
  },
  computed: {
    /**
     * 디테일을 변경해야하는지 여부를 판단하기 위해,
     * 변조된 값을 만든다
     */
    forSlipDetails() {
      return [String(this.value.evdTypeCd || ''), String(this.value.totAmt || ''), String(this.value.vatAmt || ''), String(this.value.taxCd || ''), String(this.value.apAcctCd || ''), String(this.value.hdSgtxt || ''), String(this.value.baseDeptCd || '')].join('_')
    }
  },
  data() {
    return {
      options: {
        evdTypeCd: [],
        payTermCd: [],
        accounts: [],
        useTypeCd: [],
        taxCd: [],
        ventAccts: [],
        frgnCurCd: [],
        frgnNatCd: []
      }
    }
  },
  methods: {
    /**
     * 증빙유형 코드 목록 조회
     */
    queryEvdTypeCd(slipTypeCd, options) {
      return new Promise((resolve, reject) => {
        options = options || {}
        this.$http
          .get('/api/code/combo', {
            params: {
              groupCd: 'EVD_TYPE_CD',
              remark1: slipTypeCd
            }
          })
          .then(response => {
            options['evdTypeCd'] = response.data
            return resolve(response)
          })
          .catch(response => {
            options['evdTypeCd'] = []
            return reject(response)
          })
      })
    },
    /**
     * 대변계좌 갱신
     */
    queryAccounts(slipTypeCd, options) {
      return new Promise((resolve, reject) => {
        options = options || {}
        return this.$http
          .get(`/api/account/combo/${slipTypeCd}`)
          .then(response => {
            options['accounts'] = response.data
            return resolve(response)
          })
          .catch(response => {
            options['accounts'] = []
            return reject(response)
          })
      })
    },
    /**
     * 이건 뭥미?
     */
    queryUseTypeCd(options) {
      return new Promise((resolve, reject) => {
        options = options || {}
        this.$http
          .get('/api/code/combo', {
            params: {
              groupCd: 'USE_TYPE_CD'
            }
          })
          .then(response => {
            options['useTypeCd'] = response.data
            return resolve(response)
          })
          .catch(response => {
            options['useTypeCd'] = []
            return reject(response)
          })
      })
    },
    /**
     * 사용 국가 갱신
     */
    queryFrgnNatCd(options) {
      return new Promise((resolve, reject) => {
        options = options || {}
        this.$http
          .get('/api/code/combo', {
            params: {
              groupCd: 'FRGN_NAT_CD'
            }
          })
          .then(response => {
            options['frgnNatCd'] = response.data
            return resolve(response)
          })
          .catch(response => {
            options['frgnNatCd'] = []
            return reject(response)
          })
      })
    },
    /**
     * 통화 코드 갱신
     */
    queryFrgnCurCd(options) {
      return new Promise((resolve, reject) => {
        options = options || {}
        this.$http
          .get('/api/code/combo', {
            params: {
              groupCd: 'FRGN_CUR_CD'
            }
          })
          .then(response => {
            options['frgnCurCd'] = response.data
            return resolve(response)
          })
          .catch(response => {
            options['frgnCurCd'] = []
            return reject(response)
          })
      })
    },
    queryVentAccts(apAcctCd, options) {
      return new Promise((resolve, reject) => {
        options = options || {}
        this.$http
          .get(`/api/vendor/account/${apAcctCd}`)
          .then(response => {
            options['ventAccts'] = response.data
            return resolve(response)
          })
          .catch(response => {
            options['ventAccts'] = []
            return reject(response)
          })
      })
    },
    /**
     * 사업장 조회
     */
    queryBpCd(options) {
      return new Promise((resolve, reject) => {
        options = options || {}
        this.$http
          .get('/api/bp/combo')
          .then(response => {
            options['bpCd'] = response.data
            return resolve(response)
          })
          .catch(response => {
            options['bpCd'] = []
            return reject(response)
          })
      })
    },
    /**
     * 세금코드 조회
     */
    queryTaxCd(evdTypeCd) {
      return new Promise((resolve, reject) => {
        this.options['taxCd'] = []
        this.$http
          .get(`/api/taxes`, {
            params: {
              evdTypeCd: evdTypeCd
            }
          })
          .then(response => {
            this.options['taxCd'] = response.data
            this.value.taxCd = response.data[0].taxCd
            this.value.taxRt = response.data[0].taxRt

            if (this.id === 'ED' && this.value.slipDetails.length < 1) {
              this.resetSlipDetail(response.data[0].taxRt !== 0)
              this.changeApAcctCd()
            }

            return resolve(response)
          })
          .catch(response => {
            this.value.taxCd = undefined
            this.value.taxRt = 0
            return reject(response)
          })
      })
    },
    /**
     * 총 금액 계산기
     */
    totalAmountCalculator(field) {
      // 공급가액
      var supAmt = this.$numeral(this.value.supAmt).value()
      // 기타금액
      var etcAmt = this.$numeral(this.value.etcAmt).value()
      // 부가세액
      var vatAmt = this.$numeral(this.value.vatAmt).value()

      if (field === 'vatAmt') {
        // TODO::
      } else {
        var tax = this.options['taxCd'].filter(x => x.taxCd === this.value.taxCd)[0]
        if (tax) {
          vatAmt = Math.floor((tax.taxRt * supAmt) / 100.0)
          this.value.vatAmt = this.$numeral(vatAmt).format('0,0')
        }
      }

      // 총 금액
      this.value.totAmt = this.$numeral(supAmt + etcAmt + vatAmt).format('0,0')
    },
    /**
     * 지급일자 재계산
     */
    resetPayDueDt(value) {
      var payTerm = this.options['payTermCd'].filter(x => x.detailCd === value)[0]

      // TODO::오류처리
      if (!payTerm) {
        throw 'Failed to find pay term from payTermCd options'
      }

      // 추가월
      var additionalMonth = this.$numeral(payTerm.remark1).value()
      // 증빙월
      var fixedDate = this.$numeral(payTerm.remark2).value()

      // 사용자 선택
      if (additionalMonth === 0) {
        this.value.payDueDt = undefined
      }
      // 자동 계산
      else {
        var dt = this.$moment(this.value.evdDt || undefined).add('month', additionalMonth + 1)

        if (fixedDate === 31) dt = this.$moment(dt).endOf('month')
        else dt = this.$moment(dt).date(fixedDate)

        this.value.payDueDt = dt.format('YYYY-MM-DD')
      }
    },
    /**
     * 증빙유형 변경 이벤트 핸들러
     * 유형이 변경될 때 데이터를 해당 유형에 맞게 초기화 한다
     */
    evdTypeCdHandler() {
      switch (this.value.evdTypeCd) {
        case '40':
          this.evdTypeCd40Handler()
          break
        case '41':
          this.evdTypeCd41Handler()
          break
        case '42':
          this.evdTypeCd42Handler()
          break
        case '43':
          this.evdTypeCd43Handler()
          break
      }
    },
    /**
     * 증빙유형 40 - 현금영수증 이벤트 핸들러
     */
    evdTypeCd40Handler() {
      this.evdTypeCdFlushData()
    },
    /**
     * 증빙유형 41 - 간이영수증 이벤트 핸들러
     */
    evdTypeCd41Handler() {
      this.evdTypeCdFlushData()
    },
    /**
     * 증빙유형 42 - 사내증빙 이벤트 핸들러
     */
    evdTypeCd42Handler() {
      this.evdTypeCdFlushData()

      this.queryUseTypeCd(this.options).then(response => {
        this.value.useTypeCd = response.data[0].key
      })
    },
    /**
     * 증빙유형 43 - 해외사용 이벤트 핸들러
     */
    evdTypeCd43Handler() {
      this.evdTypeCdFlushData()

      this.queryFrgnNatCd(this.options).then(response => {
        this.value.frgnNatCd = response.data[0].key
      })

      this.queryFrgnCurCd(this.options).then(response => {
        this.value.frgnCurCd = response.data[0].key
      })
    },
    /**
     * 증빙유형 변경 시, 데이터를 리셋시킨다
     */
    evdTypeCdFlushData() {
      this.value.useTypeCd = undefined
      this.value.taxCd = undefined
      this.value.curCd = 'KRW'
      this.value.crcptNo = undefined
      this.value.crcptBizNo = undefined
      this.value.crcptMerchNm = undefined
      this.value.frgnNatCd = undefined
      this.value.frgnCurCd = undefined
      this.value.frgnAmt = undefined
      this.value.frgnNatCd = undefined
      this.value.frgnCurCd = undefined
      this.value.frgnAmt = 0
      this.value.supAmt = 0
      this.value.etcAmt = 0
      this.value.vatAmt = 0
      this.value.slipDetails = []
    },
    /**
     * 라디오 버튼 ID 생성을 위한 아이
     */
    getRadioId(name, index) {
      return [name, index].join('-')
    },
    /**
     * ======================================================
     * 모달 관련 함수들
     * ======================================================
     */
    /**
     * 부서 모달창
     */
    openCctr(map, callback) {
      const self = this
      this.$modal.open({
        component: Cctr,
        parent: this,
        props: {
          slipTypeCd: this.value.slipTypeCd
        },
        width: 700,
        events: {
          close(object) {
            map = map || {}
            for (var member in map) {
              self.value[map[member]] = object[member]
            }
            self.$forceUpdate()
            if (typeof callback === 'function') {
              callback.apply(self, [object])
            }
          }
        }
      })
    },
    /**
     * Vendor modal
     */
    openVendor(map, callback) {
      const self = this
      this.$modal.open({
        component: Vendor,
        parent: this,
        props: {
          slipTypeCd: this.value.slipTypeCd
        },
        width: 700,
        events: {
          close(object) {
            map = map || {
              'vendCd': 'evdCustCd',
              'vendNm': 'evdCustNm',
              'bizNo': 'evdCustBizNo',
              'compCd': 'compCd'
            }
            for (var member in map) {
              self.value[map[member]] = object[member]
            }
            switch (self.value.slipTypeCd) {
              case 'E4':
              case 'E6':
                self.$http.get(_url('/api/emp', object.bizNo))
                  .then(response => {
                    if (response.data.length > 0) {
                      self.value.baseDeptCd = response.data[0].deptCd
                      self.value.baseDeptNm = response.data[0].deptNm
                    }
                    return response
                  })
                break
            }
            self.$forceUpdate()
            if (typeof callback === 'function') {
              callback.apply(self, [object])
            }
          }
        }
      })
    },
    /**
     * 직원 모달 창
     */
    openEmp(map, evdCustCd, callback) {
      const self = this
      this.$modal.open({
        component: Emp,
        parent: this,
        props: {
          slipTypeCd: this.value.slipTypeCd,
          param: evdCustCd
        },
        width: 700,
        events: {
          close(object) {
            map = map || {
              'empNo': 'evdCustCd',
              'empNm': 'evdCustNm',
              'cctrCd': 'baseDeptCd',
              'cctrNm': 'baseDeptNm',
              'compCd': 'compCd'
            }
            for (var member in map) {
              self.value[map[member]] = object[member]
            }
            self.$forceUpdate()
            if (typeof callback === 'function') {
              callback.apply(self, [object])
            }
          }
        }
      })
    },
    /**
     * ======================================================
     * 전표 상세 조작 함수
     * ======================================================
     */
    changeHdSgtxt() {
      let hdSgtxt = this.value.hdSgtxt
      _.forEach(this.value.slipDetails, item => {
        item.lnSgtxt = hdSgtxt
      })
    },
    /**
     * 대변 계정 변경 이벤트
     */
    changeApAcctCd() {
      var f = this.options['accounts'].filter(x => this.value.apAcctCd === x.key)
      this.value.apAcctNm = f.length > 0 ? f[0].value : undefined

      _.forEach(this.value.slipDetails, v => {
        var id = [v.dcCd, v.lnTypeCd].join('_')
        if (id === 'C_ITEM') {
          v.acctCd = this.value.apAcctCd
          v.acctNm = this.value.apAcctNm
        }
      })

      this.$emit('input', this.value)
    },
    updateSlipDetails(value, old) {
      // forSlipDetails 참조
      // 감시하는 값이 늘어날 경우 여기도 수정해야함
      // TODO::FIX_forSlipDetails
      var values = String(value || '_______').split('_')
      var olds = String(old || '_______').split('_')

      // 증빙유형코드
      let evdTypeCd = values[0],
        evdTypeCd_old = olds[0]
      // 총 금액
      let totAmt = this.$numeral(values[1] || '0').value(),
        totAmt_old = this.$numeral(olds[1] || '0').value()
      // 부가세액
      let vatAmt = this.$numeral(values[2] || '0').value(),
        vatAmt_old = this.$numeral(olds[2] || '0').value()
      // 세금코드
      let taxCd = values[3],
        taxCd_old = olds[3]
      // 미지급계정코드
      let apAcctCd = values[4],
        apAcctCd_old = olds[4]
      // 전표적요
      let hdSgtxt = values[5],
        hdSgtxt_old = olds[5]

      let baseDeptCd = values[6],
        baseDeptCd_old = olds[6]

      // 증빙유형코드가 바뀐 경우는 다른 방식으로 처리하기 때문에 여기서는 처리하지 않고 넘어감
      if (evdTypeCd_old && evdTypeCd !== evdTypeCd_old) return

      if (this.id === 'ED') {
        // 수정 가능인 경우만
        // 루핑을 돌면서 처리한다
        _.forEach(this.value.slipDetails, item => {
          var id = [item.dcCd, item.lnTypeCd].join('_')
          switch (id) {
            case 'C_ITEM':
              item.acctAmt = totAmt
              item.creditAmt = totAmt
              break
            case 'D_TAX':
              item.acctAmt = vatAmt
              item.debitAmt = vatAmt
              break
          }

          if (baseDeptCd !== baseDeptCd_old) {
            item.cctrCd = this.value.baseDeptCd
            item.cctrNm = this.value.baseDeptNm
          }
        })
      }

      this.$emit('input', this.value)
    },
    updateSubDepartment() {
      if (this.id === 'ED') {
        _.forEach(this.value.slipDetails, v => {
          v.cctrCd = this.value.baseDeptCd
          v.cctrNm = this.value.baseDeptNm
        })
        this.$emit('input', this.value)
      }
    },
    updateUseDt() {
      if (this.id === 'ED') {
        _.forEach(this.value.slipDetails, v => {
          v.useDt = this.value.evdDt
        })
      }
    }
  },
  watch: {
    value: {
      deep: true,
      handler(value) {
        this.$forceUpdate()
      }
    },
    /**
     * 증빙유형 변경 이벤트
     */
    'value.evdTypeCd': {
      immediate: true,
      handler(value) {
        if (value) {
          this.$nextTick(() => {
            var fnd = this.options['evdTypeCd'].filter(x => x.key === value)
            if (fnd.length > 0) {
              this.value.evdTypeNm = fnd[0].value
            }

            /**
             * 세금코드 변경
             */
            this.$http
              .get(`/api/taxes`, {
                params: {
                  evdTypeCd: value
                }
              })
              .then(response => {
                this.options['taxCd'] = response.data
                this.value.taxCd = response.data[0].taxCd
                this.value.taxRt = response.data[0].taxRt

                if (this.id === 'ED' && this.value.slipDetails.length < 1) {
                  this.resetSlipDetail(response.data[0].taxRt !== 0)
                  this.changeApAcctCd()
                }
              })

            /**
             * 지급조건 변경
             */
            this.$http
              .get('/api/code/detail', {
                params: {
                  groupCd: 'PAY_TERM_CD',
                  remark3: value
                }
              })
              .then(response => {
                this.options['payTermCd'] = response.data
                if (!this.value.payTermCd || this.options['payTermCd'].map(x => x.detailCd).indexOf(this.value.payTermCd) < 0) this.value.payTermCd = this.options['payTermCd'][0].detailCd
              })
          })
        }
      }
    },
    /**
     * 전표 디테일을 변경한다 핫!
     */
    forSlipDetails: {
      handler: 'updateSlipDetails'
    }
  },
  created() {
    if (this.isNew) {
      this.updateSlipDetails(this.forSlipDetails)
    }
    /**
     * 증빙유형 코드를 갱신한다
     */
    this.queryEvdTypeCd(this.value.slipTypeCd, this.options).then(response => {
      if (!this.value.evdTypeCd) {
        this.value.evdTypeCd = this.options['evdTypeCd'][0].key
        this.value.evdTypeNm = this.options['evdTypeCd'][0].value
      } else {
        var fnd = this.options['evdTypeCd'].filter(x => x.key === this.value.evdTypeCd)
        if (fnd.length > 0) {
          this.value.evdTypeNm = fnd[0].value
        }
      }
      return response
    })
    /**
     * 대변계좌 코드를 갱신한다
     */
    this.queryAccounts(this.value.slipTypeCd, this.options).then(response => {
      if (!this.value.apAcctCd) this.value.apAcctCd = this.options['accounts'][0].key
      if (this.id !== 'RO') {
        this.changeApAcctCd()
      }
      return response
    })
    if (this.value.slipTypeCd === 'E4') {
      /**
       * E4인 경우에만 해당 옵션 로딩
       */
      this.queryUseTypeCd(this.options)
      this.queryFrgnNatCd(this.options)
      this.queryFrgnCurCd(this.options)
    }
    /**
     * 사업장 정보를 가져와서 설정한다
     * ...없으면
     */
    this.queryBpCd(this.options).then(response => {
      if (this.value.bpCd === undefined) this.value.bpCd = this.options['bpCd'][0].key
      return response
    })

    // this.$watch(() => {
    //   switch (this.value.slipTypeCd) {
    //     case 'E4':
    //     case 'E6':
    //       return this.value.evdCustCd
    //     default:
    //       return this.value.apAcctCd
    //   }
    // }, (nValue, oValue) => {
    //   if (this.id === 'RO') return nValue
    //   if (nValue !== oValue && nValue !== undefined) {
    //     /**
    //      * 지급 계좌 정보를 불러온다
    //      */
    //     this.queryVentAccts.apply(this, [nValue, this.options]).then(response => {
    //       var found = this.options['ventAccts'].filter(x => [x.custBnkCd, x.custAcctNo].join('|') === this.value.custAccount)
    //       if ((this.value.custAccount === undefined || found.length < 1) && this.options['ventAccts'].length > 0) {
    //         this.value.custBnkCd = this.options['ventAccts'][0].bnkCd
    //         this.value.custAcctNo = this.options['ventAccts'][0].acctNo
    //         this.value.custAcctNo = this.options['ventAccts'][0].acctNo
    //         this.value.custAccount = [this.value.custBnkCd, this.value.custAcctNo].join('|')
    //       }
    //       if (this.options['ventAccts'].length < 1) {
    //         this.value.custBnkCd = undefined
    //         this.value.custAcctNo = undefined
    //         this.value.custAcctNo = undefined
    //         this.value.custAccount = undefined
    //       }
    //       return response
    //     })
    //   }
    // }, {
    //   immediate: true
    // })
  }
}

function _url(...args) {
  args = args.map(x => String(x || '').trim().replace(/^\/*|\/*$/g, ''))
  args = args.filter(x => x)
  return args.join('/')
}
