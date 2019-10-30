// Common library
import _ from 'lodash'
import { url as _url } from '@/libs/join'
import assert from '@/libs/assert'

// mixins
import mixin_sc from '@/mixin/slip-common'

// Table components
import TableHeader from '@/components/slip/table/libs/TableHeader'
import TableInput from '@/components/slip/table/libs/TableInput'
import TableNumberInput from '@/components/slip/table/libs/TableNumberInput'
import TableRadio from '@/components/slip/table/libs/TableRadio'
import TableSelect from '@/components/slip/table/libs/TableSelect'
import TableCalendar from '@/components/slip/table/libs/TableCalendar'
import EvdCust from '@/components/slip/table/libs/EvdCust'
import AdvReq from '@/components/slip/table/libs/AdvReq'
import BaseDept from '@/components/slip/table/libs/BaseDept'

/**
 * Query options
 */
function queryOption(url, type, params) {
  return new Promise((resolve, reject) => {
    // Validate requirement
    assert(url !== undefined, 'URL is required')
    assert(type !== undefined, 'Type is required')

    if (!url.match(/^\/?api.*/g)) {
      url = _url('api', url)
    }

    this.$store.commit('loading')
    this.$http.get(url, { params })
      .then(response => {
        this.options[type] = response.data
        return resolve(response)
      }).catch(response => {
        return reject(response)
      }).finally(() => {
        this.$store.commit('finish')
      })
  })
}

export default {
  props: {
    'value': {
      type: Object,
      required: true
    },
    'status': {
      type: Object,
      required: true
    }
  },
  mixins: [mixin_sc],
  /**
   * Import table essentials
   */
  components: {
    TableHeader,
    TableInput,
    TableNumberInput,
    TableRadio,
    TableSelect,
    TableCalendar,
    EvdCust,
    AdvReq,
    BaseDept
  },
  data() {
    return {
      options: {
        'EVD_TYPE_CD': [],
        'ACCOUNT': [],
        'PAY_TERM_CD': [],
        'USE_TYPE_CD': [],
        'BP_CD': [],
        'TAX_CD': [],
        'VENT_ACCTS': [],
        'FRGN_NAT_CD': [],
        'FRGN_CUR_CD': [],
        'STL_FG': [{
          value: 'N',
          label: '미정산'
        }, {
          value: 'Y',
          label: '선급금정산'
        }]
      }
    }
  },
  computed: {
    lastColspan() {
      return this.status.readonly ? 2 : 1
    },
    readonly() {
      return this.status.readonly
    },
    isNew() {
      // return this.value.eaSlipNo === undefined
      return this.status.new
    },
    showHeader() {
      return !this.status.new
    }
  },
  methods: {
    // ** queryOption
    // ------------------------------------------------------------------------
    /**
     * QUERY:EVD_TYPE_CD
     * 증빙유형 목록 조회
     */
    queryEvdTypeCd() {
      return queryOption.apply(this, ['/code/combo', 'EVD_TYPE_CD', { groupCd: 'EVD_TYPE_CD', remark1: this.value.slipTypeCd }])
    },
    /**
     * QUERY:ACCOUNT
     * 대변계좌 목록 조회
     */
    queryAccounts() {
      if (this.value.slipTYpeCd === 'E1') {
        return queryOption.apply(this, ['/account/card/credit', 'ACCOUNT'])
      } else {
        return queryOption.apply(this, [`/account/combo/${this.value.slipTypeCd}`, 'ACCOUNT'])
      }
    },
    /**
     * QUERY:USE_TYPE_CD
     * 사용유형 목록 조회
     */
    queryUseTypeCd() {
      return queryOption.apply(this, ['/code/combo', 'USE_TYPE_CD', { groupCd: 'USE_TYPE_CD' }])
        .then(() => {
          this.options['USE_TYPE_CD'] = this.options['USE_TYPE_CD'].map(x => {
            return { value: x.key, label: x.value }
          })
        })
    },
    /**
     * QUERY:FRGN_NAT_CD
     * 사용국가 목록 조회
     */
    queryFrgnNatCd() {
      return queryOption.apply(this, ['/code/combo', 'FRGN_NAT_CD', { groupCd: 'FRGN_NAT_CD' }])
    },
    /**
     * QUERY:FRGN_CUR_CD
     * 통화 목록 조회
     */
    queryFrgnCurCd() {
      return queryOption.apply(this, ['/code/combo', 'FRGN_CUR_CD', { groupCd: 'FRGN_CUR_CD' }])
    },
    /**
     * QUERY:VENT_ACCTS
     * 지급계좌 목록 조회
     */
    queryVentAccts() {
      return queryOption.apply(this, [`/vendor/account/${this.value.evdCustCd}`, 'VENT_ACCTS'])
        .then(() => {
          if (this.options['VENT_ACCTS'].length === 0) {
            this.options['VENT_ACCTS'].push({
              key: '_',
              value: '== 지급계좌 없음 =='
            })
          } else {
            this.options['VENT_ACCTS'] = this.options['VENT_ACCTS'].map(x => {
              x.key = [x.bnkCd, x.acctNo].join('_')
              x.value = x.acctNo
              return x
            })
          }
        })
    },
    /**
     * QUERY:BP_CD
     * 사업장 목록 조회
     */
    queryBpCd() {
      return queryOption.apply(this, ['/bp/combo', 'BP_CD'])
    },
    /**
     * QUERY:TAX_CD
     * 세금코드 조회
     */
    queryTaxCd() {
      return queryOption.apply(this, ['/taxes', 'TAX_CD', { evdTypeCd: this.value.evdTypeCd }])
    },
    /**
     * QUERY:PAY_TERM_CD
     * 지급조건 목록 조회
     */
    queryPayTermCd() {
      return queryOption.apply(this, ['/code/detail', 'PAY_TERM_CD', { groupCd: 'PAY_TERM_CD', remark3: this.value.evdTypeCd }])
    },
    /**
     * 부가세 항목 조회
     */
    queryVatAcct() {
      this.$http.get('/api/account/vat')
        .then(response => {
          this.value.vatAcctCd = response.data.acctCd
          this.value.vatAcctNm = response.data.acctNm
        })
    },
    // ------------------------------------------------------------------------
    // ** Event handler
    // ------------------------------------------------------------------------
    /**
     * 지급유형 갱신 이벤트
     */
    payTermCdChangeEvent() {
      let f = this.options['PAY_TERM_CD'].filter(x => x.detailCd === this.value.payTermCd)[0]

      // PAY_TERM_CD가 선택됨
      if (f !== undefined) {
        let am = this.$numeral(f.remark1).value()
        let fd = this.$numeral(f.remark2).value()

        if (am === 0) {
          this.value.payDueDt = undefined
        } else {
          let dt = this.$moment(this.value.evdDt || undefined).add('month', am + 1)
          dt = fd === 31 ? this.$moment(dt).endOf('month') : this.$moment(dt).date(fd)
          this.value.payDueDt = dt.format('YYYYMMDD')
        }
      }
    },
    /**
     * 증빙유형 갱신 이벤트
     */
    evdTypeChangeEvent() {
      // 세금 코드 갱신
      this.queryTaxCd()
        .then(() => {
          let f = this.options['TAX_CD'].filter(x => x.taxCd === this.value.taxCd)[0]
          if (this.value.taxCd === undefined || f === undefined) {
            f = this.options['TAX_CD'][0]
          }
          this.value.taxCd = f.taxCd
          this.value.taxRt = f.taxRt

          this.reset_rows()
        })

      this.queryPayTermCd()
        .then(() => {
          let f = this.options['PAY_TERM_CD'].filter(x => x.detailCd === this.value.payTermCd)[0]
          if (this.value.payTermCd === undefined || f === undefined) {
            f = this.options['PAY_TERM_CD'][0]
          }
          this.value.payTermCd = f.detailCd
          this.value.payTermNm = f.detailNm
        })

      _flush.apply(this, [])

      switch (this.value.evdTypeCd) {
        case '42':
          this.value.useTypeCd = this.options['USE_TYPE_CD'][0].value
          break
        case '43':
          this.value.frgnNatCd = this.options['FRGN_NAT_CD'][0].key
          this.value.frgnCurCd = this.options['FRGN_CUR_CD'][0].key
          break
      }

      function _flush() {
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
      }
    },
    /**
     * 증빙거래처 갱신 이벤트
     */
    evdCustCdChangeEvent() {
      // 기타증빙 및 교통비 전표는 임직원 거래처를 사용한다
      if (this.value.slipTypeCd === 'E4' || this.value.slipTypeCd === 'E6') {
        this.$http.get(`/api/emp/${this.value.evdCustBizNo}`)
          .then(response => {
            if (response.data.length > 0) {
              this.value.baseDeptCd = response.data[0].cctrCd
              this.value.baseDeptNm = response.data[0].cctrNm
            }
            this.baseDeptCdChangeEvent()
          })
      }

      this.queryVentAccts()
        .then(() => {
          let f = this.options['VENT_ACCTS'].filter(x => x.key === this.value.custAccount)[0]
          if (this.value.custAccount === undefined || this.value.custAccount === '_' || f === undefined) {
            f = this.options['VENT_ACCTS'][0]
          }
          this.value.custBnkCd = f.bnkCd
          this.value.custAcctNo = f.acctNo
          this.value.custAccount = f.key

          this.options['VENT_ACCTS'] = _.clone(this.options['VENT_ACCTS'])
        })
    },
    /**
     * 기준부서 변경 이벤트
     */
    baseDeptCdChangeEvent() {
      _.forEach(this.value.slipDetails, x => {
        x.bdptCd = x.cctrCd = this.value.baseDeptCd
        x.cctrNm = this.value.baseDeptNm
      })
    },
    /**
     * 증빙일자 변경 이벤트
     */
    evdDtChangeEvent() {
      if (this.value.slipTypeCd === 'E6') {
        _.forEach(this.value.slipDetails, x => {
          x.useDt = this.value.evdDt
        })
      }
    },
    /**
     * 대변계정 갱신 이벤트
     */
    apAcctCdChangeEvent() {
      let f = this.options['ACCOUNT'].filter(x => x.key === this.value.apAcctCd)[0]
      if (this.value.apAcctCd === undefined || f === undefined) {
        f = this.options['ACCOUNT'][0] || {}
      }
      this.value.apAcctCd = f.key
      this.value.apAcctNm = f.value
      let citems = this.value.slipDetails.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'C_ITEM')
      _.forEach(citems, x => {
        x.acctCd = this.value.apAcctCd
        x.acctNm = this.value.apAcctNm
      })
    },
    /**
     * 적요 변경 이벤트
     */
    hdSgtxtChangeEvent() {
      _.forEach(this.value.slipDetails, x => {
        x.lnSgtxt = this.value.hdSgtxt
      })
    }
  },
  created() {
    Promise.all([this.queryEvdTypeCd(), this.queryVentAccts(), this.queryVatAcct()])
      .then(() => {
        if (this.isNew && !this.$route.params.copyEaSlipNo) {
          this.evdTypeChangeEvent()
          this.evdCustCdChangeEvent()
        } else {
          this.queryTaxCd()
          this.queryPayTermCd()
        }
      })

    if (this.isNew && !this.$route.params.copyEaSlipNo) {
      this.evdCustCdChangeEvent()
    }

    this.queryAccounts()
      .then(() => {
        this.apAcctCdChangeEvent()
      })

    if (this.value.slipTypeCd === 'E4') {
      this.queryFrgnCurCd()
      this.queryFrgnNatCd()
      this.queryUseTypeCd()
    }
  }
}
