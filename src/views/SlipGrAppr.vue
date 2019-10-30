<template>
<div class="inner-box">
  <form @submit.prevent="query">
    <div class="content-name">
      <h2 class="dp-ib">법인카드 전표 그룹결재 상신</h2>
      <div class="btn-wrap btn-type1 clearfix">
        <button type="button" class="btn-size btn-blue fl_left" @click="submitGroupButtonClickEvent()">
          <span class="btn-icon"><i class="fas fa-pen-alt"></i></span> 그룹결재 상신
        </button>
        <button type="submit" class="btn-size btn-gray fl_left">
          <span class="btn-icon"><i class="fas fa-pen-alt"></i></span> 조회
        </button>
      </div>
    </div>

    <!-- 검색 영역 -->
    <div class="search-form">
      <div class="form-group" style="width: 50%;">
        <label class="control-label">회계일자</label>
        <div class="form-input">
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input ddate sDate" v-model="params.postDtFrom" />
          </div>
          <span class="wave"> ~ </span>
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input ddate sDate" v-model="params.postDtTo" />
          </div>
        </div>
      </div>
      <div class="form-group" style="width: 50%;">
        <label class="control-label">그룹기안일자</label>
        <div class="form-input">
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input ddate sDate" v-model="params.apprDtFrom" :config="{ outputFormat: 'YYYY-MM-DD' }" />
          </div>
          <span class="wave"> ~ </span>
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input ddate sDate" v-model="params.apprDtTo" :config="{ outputFormat: 'YYYY-MM-DD' }" />
          </div>
        </div>
      </div>
    </div>
    <!-- //검색 영역 -->
  </form>

  <!-- 데이터 영역 -->
  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">전표내역</h3>
        </div>
      </div>
      <!-- Grid -->
      <dhx-grid v-model="data_sg" :config="config_sg" style="margin-bottom: 40px;" @constructGridSuccessful="constructGridSuccessful_sg" />
      <!-- //Grid -->
    </div>
  </div>
  <!-- //데이터 영역 -->

  <!-- 그룹결재 영역 -->
  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">그룹결재 내역</h3>
        </div>
      </div>
      <!-- Grid -->
      <dhx-grid v-model="data_gr" :config="config_gr" @constructGridSuccessful="constructGridSuccessful_gr" />
      <!-- //Grid -->
    </div>
  </div>
  <!-- //그룹결재 영역 -->
</div>
</template>

<script>
/**
 * EA-02-03
 * 법인카드전표 – 그룹결재 상신
 */
import _ from 'lodash'
import moment from 'moment'
import Join from '@/libs/join'
import assert from '@/libs/assert'
import Vue from 'vue'

import DhxCalendar from '@/components/DhxCalendar.vue'
import DhxGrid from '@/components/DhxGrid.vue'
import GridCheckbox from '@/components/grid/GridCheckbox.vue'

import SlipModal from '@/components/SlipModal.vue'
import ApprSubm from '@/views/ApprSubm.vue'

const _url = Join.url

const defaultParams = {
  postDtFrom: moment().subtract(1, 'months').startOf('month').format('YYYYMMDD'),
  postDtTo: moment().format('YYYYMMDD'),
  apprDtFrom: moment().subtract(1, 'months').startOf('month').format('YYYY-MM-DD'),
  apprDtTo: moment().format('YYYY-MM-DD')
}

const bus = new Vue()

const options = {}
const status = {}

function queryGrApprStatCd() {
  if (options['GR_APPR_STAT_CD'] !== undefined || status['GR_APPR_STAT_CD']) {
    return
  }
  status['GR_APPR_STAT_CD'] = true
  this.$http.get('/api/code/detail', {
    params: {
      groupCd: 'GR_APPR_STAT_CD'
    }
  }).then(response => {
    options['GR_APPR_STAT_CD'] = response.data
    bus.$emit('GR_APPR_STAT_CD.updated', options['GR_APPR_STAT_CD'])
  }).finally(() => {
    delete status['GR_APPR_STAT_CD']
  })
}

export default {
  components: {
    DhxCalendar,
    DhxGrid
  },
  data() {
    return {
      params: {},
      data_sg: [],
      data_gr: [],
      /**
       * Grid config :::: 전표내역 (Master)
       */
      config_sg: {
        columns: [{
          value: 'No.',
          type: 'cntr',
          width: 50
        }, {
          id: 'chk',
          value: '#',
          width: 50,
          type: 'ch'
          // component: GridCheckbox
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
          id: 'evdDt',
          value: '증빙일자',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span>{{ $moment(value[field]).format('YYYY-MM-DD') }}</span>`
          }
        }, {
          id: 'postDt',
          value: '회계일자',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span>{{ $moment(value[field]).format('YYYY-MM-DD') }}</span>`
          }
        }, {
          id: 'supAmt',
          value: '공급가',
          type: 'ron',
          align: 'right'
        }, {
          id: 'vatAmt',
          value: '부가세액',
          type: 'ron',
          align: 'right'
        }, {
          id: 'totAmt',
          value: '총금액',
          type: 'ron',
          align: 'right'
        }, {
          id: 'stnAcctCd',
          value: '계정코드'
        }, {
          id: 'stnAcctNm',
          value: '계정명',
          align: 'left',
          width: 150
        }, {
          id: 'expItemCnt',
          value: '계정라인'
        }, {
          id: 'evdCustCd',
          value: '거래처코드'
        }, {
          id: 'evdCustNm',
          value: '거래처명'
        }, {
          id: 'payCustCd',
          value: '지급처코드'
        }, {
          id: 'payCustNm',
          value: '지급처명'
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
        }, {
          id: 'merchNm',
          value: '가맹점명',
          align: 'left',
          width: 120
        }, {
          id: 'merchAddr',
          value: '가맹점주소',
          align: 'left',
          width: 250
        }, {
          id: 'mccName',
          value: '업종명',
          align: 'left',
          width: 120
        }, {
          id: 'apprDate',
          value: '승인일자',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span>{{ format(value[field]) }}</span>`,
            methods: {
              format(value) {
                if (value !== undefined && value.match(/^\d{8}/g)) {
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
                if (value !== undefined && value.match(/^\d{6}/g)) {
                  return value.replace(/(\d{2})(\d{2})(\d{2})/g, '$1:$2:$3')
                } else {
                  return ''
                }
              }
            }
          }
        }],
        height: 300,
        autoWidth: false
      },
      /**
       * Grid config 그룹결재 내역
       */
      config_gr: {
        columns: [{
          value: 'No.',
          type: 'cntr',
          width: 50
        }, {
          id: 'grSlipNo',
          value: '그룹전표번호'
        }, {
          id: 'grApprStatCd',
          value: '상태',
          component: {
            props: ['index', 'value', 'field'],
            template: `<span>{{ getCode(value[field]) }}</span>`,
            data() {
              return {
                options: []
              }
            },
            methods: {
              getCode(value) {
                let found = this.options.filter(x => x.detailCd === value)[0]
                return found !== undefined ? found.detailNm : value
              }
            },
            created() {
              this.options = options['GR_APPR_STAT_CD']
              bus.$on('GR_APPR_STAT_CD.updated', () => {
                this.options = options['GR_APPR_STAT_CD']
              })
            }
          }
        }, {
          id: 'totAmt',
          value: '총 금액',
          align: 'right',
          type: 'ron'
        }, {
          id: 'slipCnt',
          value: '전표 수',
          align: 'right',
          type: 'ron'
        }, {
          id: 'elecApprDtm',
          value: '기안일자'
        }, {
          id: 'apprReqEmpNm',
          value: '기안자'
        }, {
          id: 'elecApprId',
          value: '결재번호'
        }],
        events: {
          onRowDblClicked(rid) {
            let row = this.value[rid - 1]
            this.$modal.open({
              component: ApprSubm,
              props: {
                title: '법인카드 전표 그룹결재 상세',
                docMngNo: row.elecApprId,
                docType: 'GR',
              },
              parent: this,
              width: 1200
            })
          }
        },
        height: 300,
        autoWidth: false
      }
    }
  },
  methods: {
    /**
     * 그룹결재 상신 버튼 클릭 이벤트
     */
    submitGroupButtonClickEvent() {
      try {
        let datas = _.cloneDeep(this.data_sg.filter(x => x.chk))

        assert.apply(this, [datas.length > 0, '결재상신할 전표를 선택해주세요.'])

        this.$modal.open({
          component: ApprSubm,
          props: {
            title: '법인카드 전표 그룹결재 상신',
            docType: 'GR',
            value: {
              slipTypeNm: datas[0].slipTypeNm,
              currCode: 'KRW',
              slipGroupDetails: datas
            }
          },
          width: 1200,
          parent: this
        })
      } catch (e) {
        this.$swal({
          type: 'error',
          text: e
        })
      }
    },
    /**
     * 조회 버튼 클릭 이벤트
     */
    query() {
      return new Promise((resolve, reject) => {
        try {
          assert.apply(this, [this.params.postDtFrom, '회계일자를 입력해주세요.'])
          assert.apply(this, [this.params.postDtTo, '회계일자를 입력해주세요.'])
          assert.apply(this, [this.params.apprDtFrom, '그룹기안일자를 입력해주세요.'])
          assert.apply(this, [this.params.apprDtTo, '그룹기안일자를 입력해주세요.'])

          this.$store.commit('loading')
          this.$http.post('/api/slip/groupAppr/list', this.params)
            .then(response => {
              let data_sg = response.data[0]
              let data_gr = response.data[1]
              data_sg.map(x => {
                x.chk = false
                return x
              })
              this.data_sg = data_sg

              this.$http.get('/api/emp')
                .then(response => {
                  let emps = response.data
                  data_gr.map(x => {
                    let found = emps.filter(y => y.empNo === x.apprReqEmp)[0]
                    if (found !== undefined) {
                      x.apprReqEmpNm = found.empNm
                    }
                    return x
                  })

                  this.data_gr = data_gr
                  return resolve(response)
                })
            })
            .catch(reject)
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
    /**
     * Grid 초기화
     */
    constructGridSuccessful_sg(grid) {
      grid.setNumberFormat('0,000', 7, '.', ',')
      grid.setNumberFormat('0,000', 8, '.', ',')
      grid.setNumberFormat('0,000', 9, '.', ',')
    },
    constructGridSuccessful_gr(grid) {
      grid.setNumberFormat('0,000', 3, '.', ',')
      grid.setNumberFormat('0,000', 4, '.', ',')
      grid.setColumnHidden(7,true)
    }
  },
  created() {
    this.params = _.clone(defaultParams)
    this.query()

    queryGrApprStatCd.apply(this, [])
  }
}
</script>
