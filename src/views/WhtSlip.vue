<template>
<div class="inner-box">
  <div class="content-name">
    <h2 class="dp-ib">교통비전표</h2>
    <div class="btn-wrap btn-type1 clearfix">
      <button class="btn-size btn-gray fl_left" @click="buttonEventPrint" v-if="isReadOnly">
        <span class="btn-icon"><i class="fas fa-print"></i></span>
        출력
      </button>
      <button class="btn-size btn-blue fl_left" @click="buttonEventViewSubmit" v-if="isReadOnly">
        <span class="btn-icon"><i class="fas fa-vote-yea"></i></span>
        결재보기
      </button>
      <button class="btn-size btn-orange fl_left" @click="buttonEventCopy" v-if="isReadOnly">
        <span class="btn-icon"><i class="far fa-clone"></i></span>
        전표복사
      </button>
      <button class="btn-size btn-blue fl_left" @click="buttonEventSubmit" v-if="isSubmitable">
        <span class="btn-icon">
          <i class="fas fa-pen-alt"></i>
        </span>
        결재상신
      </button>
      <button class="btn-size btn-gray fl_left" @click="buttonEventCreate" v-if="isCreateable">
        <span class="btn-icon">
          <i class="far fa-file"></i>
        </span>
        신규
      </button>
      <button class="btn-size btn-gray fl_left" @click="buttonEventDelete" v-if="isDeleteable">
        <span class="btn-icon">
          <i class="far fa-trash-alt"></i>
        </span>
        삭제
      </button>
      <button class="btn-size btn-gray fl_left" @click="buttonEventSave" v-if="isSaveable">
        <span class="btn-icon">
          <i class="fas fa-check"></i>
        </span>
        저장
      </button>
    </div>
  </div>

  <slip-base :eaSlipNo="eaSlipNo" v-model="data" :status="status" />
</div>
</template>

<script>
import slip from '@/mixin/slip-basic'

export default {
  mixins: [slip],
  data() {
    return {
      name: 'whtSlip',
      data: {
        eaSlipNo: undefined,
        compCd: undefined,
        slipTypeCd: 'E6',
        evdDt: this.$moment().format('YYYYMMDD'),
        postDt: this.$moment().format('YYYYMMDD'),
        slipStatCd: '10',
        evdTypeCd: '60',
        stlFgCd: 'N',
        useTypeCd: undefined,
        sysFgCd: 'W',
        bpCd: undefined,
        taxCd: undefined,
        evdCustCd: undefined,
        evdCustNm: undefined,
        evdCustBizNo: undefined,
        custAcctNo: undefined,
        custBnkCd: undefined,
        totAmt: 0,
        supAmt: 0,
        curCd: 'KRW',
        payDueDt: undefined,
        payTermCd: undefined,
        wrtDtm: undefined,
        wrtId: undefined,
        wrtDeptCd: undefined,
        baseDeptCd: undefined,
        apAcctCd: undefined,
        stnAcctCd: undefined,
        expItemCnt: undefined,
        hdSgtxt: undefined,
        fnlApprDtm: undefined,
        fnlAprverId: undefined,
        elecApprId: undefined,
        elecApprDtm: undefined,
        apprRsn: undefined,
        evdMngNo: undefined,
        regId: undefined,
        regDtm: undefined,
        chgId: undefined,
        chgDtm: undefined,
        expItemCnt: 1,
        slipDetails: []
      }
    }
  }
}
</script>
