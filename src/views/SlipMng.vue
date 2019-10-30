<template>
<div class="inner-box">
  <form @submit.prevent="query">
    <div class="content-name">
      <h2 class="dp-ib">전표 관리</h2>
      <div class="btn-wrap btn-type1 clearfix">
        <button type="button" class="btn-size btn-gray fl_left" @click="approvalButtonClickEvent()">
          <span class="btn-icon"><i class="fas fa-thumbs-up"></i></span> 재경승인
        </button>
        <button type="button" class="btn-size btn-gray fl_left" @click="rejectButtonClickEvent()">
          <span class="btn-icon"><i class="fas fa-thumbs-down"></i></span> 재경반려
        </button>
        <button type="button" class="btn-size btn-orange fl_left" @click="reversalButtonClickEvent()">
          <span class="btn-icon"><i class="fas fa-undo"></i></span> 역분개
        </button>
        <button type="submit" class="btn-size btn-blue fl_left">
          <span class="btn-icon"><i class="fas fa-pen-alt"></i></span> 조회
        </button>
      </div>
    </div>

    <!-- Search -->
    <div class="search-form">
      <div class="form-group" style="width: 40%;">
        <label class="control-label">회계일자</label>
        <div class="form-input">
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input ddate sDate" v-model="params.postDtFrom" required="required" />
          </div>
          <span class="wave"> ~ </span>
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input ddate sDate" v-model="params.postDtTo" required="required" />
          </div>
        </div>
      </div>
      <div class="form-group" style="width: 30%;">
        <label class="control-label">전표유형</label>
        <div class="form-input">
          <select class="input" v-model="params.slipTypeCd">
            <option v-for="{ detailCd, detailNm } in options['SLIP_TYPE_CD']" :key="detailCd" :value="detailCd" v-text="detailNm" />
          </select>
        </div>
      </div>
      <div class="form-group" style="width: 30%;">
        <label class="control-label">전표상태</label>
        <div class="form-input">
          <select class="input" v-model="params.slipStatCd">
            <option v-for="{ detailCd, detailNm } in options['SLIP_STAT_CD']" :key="detailCd" :value="detailCd" v-text="detailNm" />
          </select>
        </div>
      </div>
      <div class="form-group" style="width: 40%;">
        <label class="control-label">증빙일자</label>
        <div class="form-input">
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input ddate sDate" v-model="params.evdDtFrom" />
          </div>
          <span class="wave"> ~ </span>
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input ddate sDate" v-model="params.evdDtTo" />
          </div>
        </div>
      </div>
      <div class="form-group" style="width: 30%;">
        <label class="control-label">거래처</label>
        <div class="form-input">
          <input type="text" class="input Rt-M" v-model="params.evdCustNm" />
        </div>
      </div>
      <div class="form-group" style="width: 30%;">
        <label class="control-label">지급처</label>
        <div class="form-input">
          <input type="text" class="input Rt-M" v-model="params.payCustNm" />
        </div>
      </div>
      <search-cctr title="작성부서" v-model="params" :options="{ type: '02', cctrCd: 'wrtDeptCd', cctrNm: 'wrtDeptNm', authorize: true }" style="width: 40%;" />
      <search-emp title="작성자" v-model="params" :options="{ type: '02', empNo: 'wrtId', empNm: 'wrtNm', dutNm: 'wrtDutNm', deptNm: 'wrtCctrNm' }" style="width: 50%;" />
      <div class="form-group" style="width: 30%; margin-right: 10%;">
        <label class="control-label">전표번호</label>
        <div class="form-input">
          <input type="text" class="input" v-model="params.eaSlipNo" />
        </div>
      </div>
      <div class="form-group" style="width: 30%;">
        <label class="control-label">ERP 전표번호</label>
        <div class="form-input">
          <input type="text" class="input Rt-M" v-model="params.erpSlipNo" />
        </div>
      </div>
    </div>
    <!-- //Search -->
  </form>

  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">결재의견</h3>
        </div>
      </div>
      <textarea v-model="apprRsn"></textarea>
    </div>
  </div>
  <!-- 데이터 영역 -->
  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">전표내역</h3>
        </div>
        <div class="btn-wrap btn-type1 clearfix">
          <button class="btn-size btn-excel" @click="toExcel">엑셀 저장</button>
        </div>
      </div>
      <!-- Grid -->
      <dhx-grid ref="grid" v-model="data" :config="config" style="margin-bottom: 40px;" @constructGridSuccessful="constructGridSuccessful_master" />
      <!-- //Grid -->
    </div>
  </div>
  <!-- //데이터 영역 -->
</div>
</template>

<script>
/**
 * 공통 라이브러리 Import
 */
import _ from 'lodash'
import moment from 'moment'
import {
  url as _url
} from '@/libs/join'
import assert from '@/libs/assert'

// mixins
import mixin from '@/mixin/common'

/**
 * 모달창
 */
import Emp from '@/components/Emp_new.vue'
import Cctr from '@/components/Cctr_new.vue'
import SlipModal from '@/components/SlipModal.vue'

/**
 * 사용되는 공통 컴포넌트 Import
 */
import DhxCalendar from '@/components/DhxCalendar.vue'
import DhxGrid from '@/components/DhxGrid.vue'

/**
 * 전표 관리 조회 - 초기 파라미터 값
 */
const defaultParams = {
  postDtFrom: moment().subtract(1, 'months').startOf('month').format('YYYYMMDD'),
  postDtTo: moment().format('YYYYMMDD'),
  evdDtFrom: moment().subtract(1, 'months').startOf('month').format('YYYYMMDD'),
  evdDtTo: moment().format('YYYYMMDD'),
  wrtDeptCd: undefined,
  wrtDeptNm: undefined,
  eaSlipNo: undefined,
  slipTypeCd: undefined,
  payCustNm: undefined,
  wrtId: undefined,
  wrtNm: undefined,
  wrtDutNm: undefined,
  wrtCctrNm: undefined,
  erpSlipNo: undefined,
  slipStatCd: undefined,
  evdCustNm: undefined,
  acctFlag: 'Y'
}

export default {
  components: {
    DhxCalendar,
    DhxGrid
  },
  mixins: [mixin],
  data() {
    return {
      params: {},
      options: {
        'SLIP_TYPE_CD': [],
        'SLIP_STAT_CD': []
      },
      data: [],
      data_slave: [],
      apprRsn: undefined
    }
  },
  computed: {
    config() {
      let cfg = {
        columns: [{
          id: 'chk',
          value: '#',
          width: 40,
          type: 'ch'
          // component: {
          //   props: ['index', 'value', 'field'],
          //   template: `
          //     <div style="position: relative;" @click="onclick">
          //       <input :id="id" type="checkbox" v-model="value[field]" />
          //       <label :for="id" style="padding: 12px;position: absolute;left: 50%;top: 50%;transform: translate(-50%, -50%);"></label>
          //     </div>
          //   `,
          //   methods: {
          //     onclick(e) {
          //       this.value.chk = !this.value.chk
          //       e.preventDefault()
          //     }
          //   },
          //   computed: {
          //     id() {
          //       return ['checkbox', this.$parent.gridId, this.index].join('-')
          //     }
          //   }
          // }
        }, {
          id: 'itemSeq',
          value: 'No.',
          width: 50
        }, {
          id: 'eaSlipNo',
          value: '전표번호',
          width: 150
        }, {
          id: 'slipStatNm',
          value: '전표상태'
        }, {
          id: 'slipTypeNm',
          value: '전표유형'
        }, {
          id: 'postDt',
          value: '회계일자',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span>{{ $moment(value[field]).format('YYYY-MM-DD') }}</span>`
          }
        }, {
          id: 'evdDt',
          value: '증빙일자',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span>{{ $moment(value[field]).format('YYYY-MM-DD') }}</span>`
          }
        }, {
          id: 'supAmt',
          value: '공급가',
          type: 'ron',
          align: 'right',
          width: 120
        }, {
          id: 'vatAmt',
          value: '부가세액',
          type: 'ron',
          align: 'right',
          width: 120
        }, {
          id: 'totAmt',
          value: '총금액',
          type: 'ron',
          align: 'right',
          width: 120
        }, {
          id: 'stnAcctCd',
          value: '계정코드'
        }, {
          id: 'stnAcctNm',
          value: '계정명',
          align: 'left',
          width: 200
        }, {
          id: 'expItemCnt',
          value: '계정라인',
          type: 'ron',
          align: 'right'
        }, {
          id: 'erpSlipNo',
          value: 'ERP 전표번호',
          width: 150
        }, {
          id: 'evdCustCd',
          value: '거래처코드'
        }, {
          id: 'evdCustNm',
          value: '거래처명',
          align: 'left',
          width: 200
        }, {
          id: 'payCustCd',
          value: '지급처코드'
        }, {
          id: 'payCustNm',
          value: '지급처명',
          align: 'left',
          width: 200
        }, {
          id: 'wrtDeptNm',
          value: '작성부서명'
        }, {
          id: 'wrtNm',
          value: '작성자'
        }, {
          id: 'hdSgtxt',
          value: '전표내용',
          align: 'left',
          width: 150
        }],
        height: 500,
        autoWidth: false,
        events: {
          // onRowSelect(...args) {},
          onRowDblClicked(...args) {
            let row = args[3] || args[2]
            this.$modal.open({
              component: SlipModal,
              props: {
                eaSlipNo: row.eaSlipNo
              },
              parent: this,
              width: 1200
            })
            // if (this.rowDblClicked === undefined && this.fireRowDblClicked === undefined) {
            //   this.rowDblClicked = (args[3] || args[2]).eaSlipNo
            //   window.setTimeout(() => {
            //     delete this.rowDblClicked
            //     if (this.fireRowDblClicked) {
            //       let row = args[3] || args[2]
            //       this.$modal.open({
            //         component: SlipModal,
            //         props: {
            //           eaSlipNo: row.eaSlipNo
            //         },
            //         parent: this,
            //         width: 1200
            //       })
            //       delete this.fireRowDblClicked
            //     } else {
            //       let cid = args[1]
            //       if (cid > 0) {
            //         args[2].chk = !args[2].chk
            //       }
            //     }
            //   }, 50)
            // } else {
            //   delete this.rowDblClicked
            //   this.fireRowDblClicked = true
            //   if (typeof args[2].preventDefault === 'function') {
            //     args[2].preventDefault()
            //   }
            // }
          }
        },
        beforeRefreshData(grid, data) {
          _.forEach(data, (x, i) => {
            x.itemSeq = i + 1
          })
        }
      }
      if (this.params.slipTypeCd === 'E1') {
        cfg.columns = cfg.columns.concat([{
          id: 'merchNm',
          value: '가맹점명'
        }, {
          id: 'merchAddr',
          value: '가맹점주소',
          align: 'left',
          width: 200
        }, {
          id: 'mccName',
          value: '업종명'
        }, {
          id: 'apprDate',
          value: '승인일자',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span>{{ format(value[field]) }}</span>`,
            methods: {
              format(value) {
                if (value !== undefined && String(value || '').match(/^\d{8}/g)) {
                  return value.replace(/(\d{4})(\d{2})(\d{2})/g, '$1-$2-$3')
                } else {
                  return ''
                }
              }
            }
          }
        }, {
          id: 'apprTime',
          value: '승인시각',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span>{{ format(value[field]) }}</span>`,
            methods: {
              format(value) {
                if (value !== undefined && String(value || '').match(/^\d{6}/g)) {
                  return value.replace(/(\d{2})(\d{2})(\d{2})/g, '$1:$2:$3')
                } else {
                  return ''
                }
              }
            }
          }
        }])
      }
      return cfg
    }
  },
  methods: {
    constructGridSuccessful_master(grid) {
      grid.setNumberFormat('0,000', 7, '.', ',')
      grid.setNumberFormat('0,000', 8, '.', ',')
      grid.setNumberFormat('0,000', 9, '.', ',')
      // grid.setNumberFormat('0,000', 11, '.', ',')
    },
    approvalButtonClickEvent() {
      try {
        let data = this.data.filter(x => x.chk)
        let submitted = data.filter(x => x.slipStatCd === '60' || x.slipStatCd === '70')

        assert.apply(this, [data, '재경승인할 전표를 선택해주세요.'])
        assert.apply(this, [submitted.length === 0, '재경반려 또는 재경승인된 전표는 다시 재경승인할 수 없습니다.'])
        assert.apply(this, [this.apprRsn, '결재의견을 작성하셔야 재경승인을 할 수 있습니다.'])

        this.$swal({
          type: 'question',
          text: '승인 후 취소 되지 않습니다. 승인 작업을 계속하시겠습니까?',
          showCancelButton: true,
          confirmButtonText: 'Yes'
        }).then(response => {
          if (response.value) {
            this.$store.commit('loading')
            this.$http.post('/api/slip/mnt/acctAccept', data, {
              params: {
                apprRsn: this.apprRsn
              }
            }).then(response => {
              this.$swal({
                type: 'success',
                text: '승인되었습니다.'
              }).then(this.query)
              return response
            }).catch(response => {
              // TODO::Error Handling
              return response
            }).finally(() => {
              this.$store.commit('finish')
            })
          }
        })
      } catch (e) {
        this.$swal({
          type: 'error',
          text: e
        })
      }
    },
    rejectButtonClickEvent() {
      try {
        let data = this.data.filter(x => x.chk)
        let submitted = data.filter(x => x.slipStatCd === '60' || x.slipStatCd === '70')

        assert.apply(this, [data, '재경반려할 전표를 선택해주세요.'])
        assert.apply(this, [submitted.length === 0, '재경반려 또는 재경승인된 전표는 다시 재경반려할 수 없습니다.'])
        assert.apply(this, [this.apprRsn, '결재의견을 작성하셔야 재경반려를 할 수 있습니다.'])

        this.$swal({
          type: 'question',
          text: '반려 후 취소 되지 않습니다. 반려 작업을 계속하시겠습니까?',
          showCancelButton: true,
          confirmButtonText: 'Yes'
        }).then(response => {
          if (response.value) {
            this.$store.commit('loading')
            this.$http.post('/api/slip/mnt/acctReject', data, {
              params: {
                apprRsn: this.apprRsn
              }
            }).then(response => {
              this.$swal({
                type: 'success',
                text: '반려되었습니다.'
              }).then(this.query)
              return response
            }).catch(response => {
              // TODO::Error Handling
              return response
            }).finally(() => {
              this.$store.commit('finish')
            })
          }
        })
      } catch (e) {
        this.$swal({
          type: 'error',
          text: e
        })
      }
    },
    reversalButtonClickEvent() {
      try {
        let data = this.data.filter(x => x.chk)

        assert.apply(this, [data, '역분개할 전표를 선택해주세요.'])

        this.$swal({
          type: 'warning',
          text: 'ERP와 연계되지 않았습니다.'
        })
      } catch (e) {
        this.$swal({
          type: 'error',
          text: e
        })
      }
    },
    query() {
      this.$store.commit('loading')
      return this.$http.post('/api/slip/history', this.params)
        .then(response => {
          this.apprRsn = undefined
          this.data = response.data.map(x => {
            x.chk = false
            return x
          })
          return response
        })
        .finally(() => {
          this.$store.commit('finish')
        })
    },
    toExcel() {
      this.$refs.grid.toExcel()
    }
  },
  created() {
    this.params = _.clone(defaultParams)

    /**
     * Query SLIP_TYPE_CD
     */
    this.$http.get('/api/code/detail', {
      params: {
        groupCd: 'SLIP_TYPE_CD'
      }
    }).then(response => {
      this.options['SLIP_TYPE_CD'] = response.data
      this.options['SLIP_TYPE_CD'].unshift({
        detailCd: undefined,
        detailNm: '==전체=='
      })
    })

    /**
     * Query SLIP_STAT_CD
     */
    this.$http.get('/api/code/detail', {
      params: {
        groupCd: 'SLIP_STAT_CD'
      }
    }).then(response => {
      this.options['SLIP_STAT_CD'] = response.data.filter(x => x.remark1 === 'Y' && x.detailCd >= '50')
      this.options['SLIP_STAT_CD'].unshift({
        detailCd: undefined,
        detailNm: '==전체=='
      })
    })

    this.query()
  }
}
</script>

<style scoped>
.desc-content:after {
  clear: both;
  content: '';
  display: block;
}

.btn-wrap {
  margin-bottom: 20px;
}

.desc-content {
  border: 2px solid #9db6c9;
  background: #f9fafc;
  margin: 0 0 20px 0;
  border-radius: 4px;
  padding: 15px 2%;
  clear: both;
}

.desc-content .item {
  float: left;
}

.desc-content .item .desc-item {
  position: relative;
  padding-left: 82px;
  margin-bottom: 8px;
}

.desc-content .item.desc-center .desc-item {
  padding-left: 120px;
}

.desc-content .item .desc-item:last-child {
  margin-bottom: 0;
  height: 25px;
}

.desc-content .item .desc-item .tit {
  position: absolute;
  left: 0;
}

.desc-content .item .desc-item .label-tit {
  font-family: 'NotoM';
  color: #222;
  font-size: 15px;
}

.desc-content .item.desc-left .desc-item {
  padding-left: 90px;
}

.desc-content .item.desc-left .desc-item .desc:after {
  clear: both;
  content: '';
  display: block;
}

.desc-content .item.desc-left .desc-item .desc .datepicker {
  float: left;
}

.desc-content .item.desc-left .desc-item .desc span.wave {
  float: left;
  padding: 0 6px;
}

.desc-content .desc-item .td-s-thumb.search-area:after {
  clear: both;
  content: '';
  display: block;
}

.desc-content .desc-item .td-s-thumb.search-area input,
.desc-content .desc-item .td-s-thumb.search-area .ip-box {
  float: left;
}

.desc-content .item.desc-left .desc-item .desc.select select {
  width: 70%;
}

.desc-content .item.desc-left {
  width: 40%;
}

.desc-content .item.desc-center {
  width: 40%;
  padding-right: 40px;
}

.desc-content .item.desc-right {
  width: 20%;
}

.desc-content .item .desc-item .select select,
.desc-content .item .desc-item .input-box input {
  width: 70%;
}

.desc-content .item.desc-right .desc-item .select select,
.desc-content .item.desc-right .desc-item .input-box input {
  width: 100%;
}

.search-area input {
  position: relative;
}

.search-area .icon {
  position: absolute;
  right: 8px;
  top: 1px;
  z-index: 100;
  cursor: pointer;
  font-size: 16px;
  color: #555;
}

.search-border .td-s-thumb {
  position: relative;
  display: inline-block;
  width: 48%;
}

.search-border .td-s-thumb.search-area>input,
.search-border .td-s-thumb.search-area>.ip-box .search-border .td-s-thumb.search-area>button {
  float: left;
}

.search-border .td-s-thumb.search-area .ip-box.ip-box-w02 {
  width: 65%;
  margin-left: 6px;
}

.remove_text {
  margin-left: 0;
}

.contents div.gridbox_material.gridbox .xhdr {
  border-bottom: 1px solid #dfdfdf;
}

@media (max-width:1580px) {
  .search-border .td-s-thumb.search-area .ip-box.ip-box-w02 {
    width: 50%;
  }
}

textarea {
  height: 80px;
}
</style>
