import _ from 'lodash'

export default {
  methods: {
    // 전표 행추가 ===== 리뉴얼
    add_row(data, array) {
      array = array || this.value.slipDetails
      // 정의된 전표 상세
      let object = {
        eaSlipNo: data.eaSlipNo || this.value.eaSlipNo,
        itemSeq: data.itemSeq || (this.value.slipDetails.length + 1),
        compCd: data.compCd || this.value.compCd,
        lnTypeCd: data.lnTypeCd || 'ITEM',
        dcCd: data.dcCd || 'D',
        dcNm: data.dcCd === 'C' ? '대변' : '차변',
        taxCd: data.taxCd || this.value.taxCd,
        acctCd: data.acctCd,
        acctNm: data.acctNm,
        cctrCd: data.cctrCd || this.value.baseDeptCd,
        cctrNm: data.cctrNm || this.value.baseDeptNm,
        bdptCd: data.cctrCd || this.value.baseDeptCd,
        acctAmt: data.acctAmt,
        txbsAmt: data.txbsAmt,
        vatAmt: data.vatAmt,
        lnSgtxt: data.lnSgtxt || this.value.hdSgtxt,
        ioNo: data.ioNo,
        useDt: data.useDt,
        stptPlc: data.stptPlc,
        dstnPlc: data.dstnPlc,
        biztrpObj: data.biztrpObj,
        tpsTypeCd: data.tpsTypeCd,
        tpsDst: data.tpsDst,
        oilKindCd: data.oilKindCd,
        oilUpc: data.oilUpc,
        oilEff: data.oilEff,
        ref1: data.ref1,
        ref2: data.ref2,
        ref3: data.ref3,
        ref4: data.ref4,
        ref5: data.ref5,
        ref6: data.ref6,
        ref7: data.ref7,
        ref8: data.ref8,
        ref9: data.ref9,
        ref10: data.ref10
      }
      // 행을 추가한다
      array.push(object)
      this.$emit('input', this.value)
    },
    reset_rows() {
      let array = []
      let isE6 = this.value.slipTypeCd === 'E6'

      this.value.slipDetails.splice(0, this.value.slipDetails.length)

      // 미지급
      if (!isE6) { // E6 교통비 전표가 아닐때만 미지급 항목을 추가한다
        this.add_row.apply(this, [{
          lnTypeCd: 'ITEM',
          dcCd: 'C',
          useDt: isE6 ? this.value.evdDt : undefined,
          acctCd: this.value.apAcctCd,
          acctNm: this.value.apAcctNm,
        }])
      }

      let useTax = (this.$numeral(this.value.taxRt).value() > 0)
      // 부가세
      if (useTax) { // 부가세 항목은 부가세율이 0이 아닌 경우만 (0보다 큰 경우) 사용
        this.add_row.apply(this, [{
          lnTypeCd: 'TAX',
          dcCd: 'D',
          acctCd: this.value.vatAcctCd,
          acctNm: this.value.vatAcctNm
        }])
      }
      // 비용
      this.add_row.apply(this, [{
        lnTypeCd: 'ITEM',
        dcCd: 'D',
        useDt: isE6 ? this.value.evdDt : undefined,
        tpsTypeCd: isE6 ? '10' : undefined,
        oilKindCd: isE6 ? 'GSL' : undefined,
        acctAmt: this.value.supAmt
      }])

      // 전체 행을 갱신한다
      this.amountChangeEvent()

      this.$emit('input', this.value)
    },
    /**
     * 총 금액 갱신 이벤트
     */
    amountChangeEvent(field) {
      var taxRt = this.$numeral(this.value.taxRt).value()
      var supAmt = this.$numeral(this.value.supAmt).value()
      var etcAmt = this.$numeral(this.value.etcAmt).value()

      let useTax = (taxRt > 0)
      if (field !== 'vatAmt' && useTax) {
        this.value.vatAmt = Math.floor(supAmt * taxRt / 100.0)
      }

      var vatAmt = this.$numeral(this.value.vatAmt).value()
      // 총 금액 계산
      this.value.totAmt = supAmt + etcAmt + vatAmt

      _.forEach(this.value.slipDetails, (x, i) => {
        let id = [x.dcCd, x.lnTypeCd].join('_')

        x.itemSeq = i + 1

        // 전표 DT의 미지급 내용을 수정한다
        if (id === 'C_ITEM') {
          x.acctAmt = x.creditAmt = this.value.totAmt
          x.txbsAmt = supAmt + etcAmt
          x.vatAmt = vatAmt
        }
        // 전표 DT의 세금 내역을 수정한다
        else if (id === 'D_TAX') {
          x.acctAmt = x.debitAmt = vatAmt
        }
      })

      // 비용항목 수정 >_<
      let dItem = this.value.slipDetails.filter(x => [x.dcCd, x.lnTypeCd].join('_') === 'D_ITEM')[0]
      if (dItem !== undefined) {
        dItem.acctAmt = dItem.debitAmt = supAmt
      }
    }
  }
}
