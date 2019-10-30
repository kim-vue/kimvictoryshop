<template>
<div class="inner-box">
  <form @submit.prevent="query">
    <!-- 헤더 -->
    <div class="content-name">
      <h2 class="dp-ib">기초 예산 등록</h2>
      <div class="btn-wrap btn-type1 clearfix">
        <button type="button" class="btn-size btn-blue fl_left" @click="e => { enableUploadArea = true }">
          <span class="btn-icon"><i class="fas fa-upload"></i></span>
          신규 업로드
        </button>
        <button type="button" class="btn-size btn-blue fl_left" @click="save">
          <span class="btn-icon"><i class="fas fa-save"></i></span>
          저장
        </button>
        <button type="submit" class="btn-size btn-gray fl_left">
          <span class="btn-icon"><i class="fas fa-search"></i></span>
          조회
        </button>
      </div>
    </div>
    <!-- //헤더 -->

    <!-- 검색 폼 -->
    <div class="search-form">
      <div class="form-group">
        <label class="control-label">조회연도</label>
        <div class="form-input">
          <div class="datepicker w-type-ymd02">
            <dhx-calendar class="input" v-model="params.searchYear" :config="dateOptions" />
          </div>
        </div>
      </div>
      <search-cctr title="부서" v-model="params" :options="{ type: '02', cctrCd: 'budCctrCd', cctrNm: 'budCctrNm' }" @submit="query" />
      <search-account title="계정코드" v-model="params" :options="{ type: '02', acctCd: 'budAcctCd', acctNm: 'budAcctNm' }" @submit="query" />
    </div>
    <!-- //검색 폼 -->
  </form>

  <!-- 신규업로드 -->
  <div class="table-area" v-if="enableUploadArea">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">업로드 파일 선택</h3>
        </div>
      </div>
      <div class="upload-area">
        <div class="input-area">
          <input type="text" class="input" v-model="file.name" readonly="readonly" />
          <input ref="file" type="file" accept=".csv" @change="fileChangeEvent" />
        </div>
        <div class="btn-wrap btn-type1">
          <button type="button" class="btn-size btn-gray fl_left" @click="searchFile">
            파일찾기
          </button>
          <button type="button" class="btn-size btn-blue fl_left" @click="uploadFile">
            업로드
          </button>
        </div>
      </div>
    </div>
  </div>
  <!-- //신규업로드 -->

  <!-- 기초 예산 현황 -->
  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">기초 예산 현황</h3>
        </div>
        <div class="btn-wrap btn-type1 clearfix">
          <button class="btn-size btn-excel" @click="downloadExcel()">
            엑셀 저장
          </button>
        </div>
      </div>
      <dhx-grid ref="grid" v-model="data" :config="config" @constructGridSuccessful="constructGridSuccessful" />
    </div>
  </div>
  <!-- //기초 예산 현황 -->
</div>
</template>

<script>
/**
 * EA-03-08
 * 기초 예산 등록
 */

import moment from 'moment'
import { url as _url } from '@/libs/join'
import assert from '@/libs/assert'
import debug from '@/libs/debug'

import DhxCalendar from '@/components/DhxCalendar.vue'
import DhxGrid from '@/components/DhxGrid.vue'
import Account from '@/components/Account_new.vue'
import Cctr from '@/components/Cctr_new.vue'

const defParams = {
  searchYear: moment().format('YYYY'),
  budCctrCd: undefined,
  budCctrNm: undefined,
  budAcctCd: undefined,
  budAcctNm: undefined
}

const _debug = debug('BdgtReqReg')

export default {
  components: {
    DhxCalendar,
    DhxGrid
  },
  data() {
    return {
      enableUploadArea: false,
      file: {
        name: undefined
      },
      fileLoaded: false,
      params: {},
      dateOptions: {
        outputFormat: 'YYYY',
        format: 'YYYY',
        dateFormat: '%Y'
      },
      memento: [],
      data: [],
      config: {
        columns: [{
          value: 'No.',
          type: 'cntr',
          width: 40
        }, {
          id: 'budCctrCd',
          value: '비용부서'
        }, {
          id: 'budCctrNm',
          value: '비용부서명',
          width: 150
        }, {
          id: 'budAcctCd',
          value: '계정코드'
        }, {
          id: 'budAcctNm',
          value: '계정코드명',
          width: 150
        }, {
          id: 'jan',
          value: '1월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'feb',
          value: '2월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'mar',
          value: '3월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'apr',
          value: '4월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'may',
          value: '5월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'jun',
          value: '6월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'jul',
          value: '7월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'aug',
          value: '8월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'sep',
          value: '9월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'oct',
          value: '10월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'nov',
          value: '11월',
          align: 'right',
          type: 'edn'
        }, {
          id: 'dec',
          value: '12월',
          align: 'right',
          type: 'edn'
        }],
        height: 600,
        events: {
          onEditCell(stage, rId, cInd, nValue, oValue) {
            let row = this.data[this.instance.getRowIndex(rId)]

            if (stage === 2 && nValue !== oValue) {
              row.chg = true
            }

            return true
          }
          // onEditCell(stage, rId, cInd, nValue, oValue) {
          //   // when editor closed
          //   if (stage === 2) {
          //     _debug.apply(this, ['Start change cell value for', rId, cInd, nValue, oValue])
          //     // and value has been changed
          //     if (nValue !== oValue) {
          //       let index = this.instance.getRowIndex(rId)
          //       let row = this.value[index]
          //       let colDef = this.options.columns[cInd]
          //       this.$http.get('/api/budget/remain', {
          //         params: {
          //           postDt: row.postDt,
          //           cctrCd: row.budCctrCd,
          //           acctCd: row.budAcctCd
          //         }
          //       }).then(response => {
          //         // Already used budget
          //         let lv = this.$numeral(response.data).value()
          //         // Changed value
          //         let rv = this.$numeral(nValue).value()
          //
          //         // used budget is greater than inputed
          //         if (lv > rv) {
          //           this.$swal({
          //             type: 'warning',
          //             text: `[${row.budCctrCd}/${row.budCctrNm}][${row.budAcctCd}/${row.budAcctNm}]: 기 사용 예산 ${this.$numeral(lv).format('0,0')}`
          //           }).then(() => {
          //             // restore value
          //             row[colDef.id] = oValue
          //             row.chg = false
          //           })
          //         } else {
          //           row.chg = true
          //           this.$parent.memento.push(_.clone(this.$parent.data))
          //         }
          //       }).catch(response => {
          //         row[colDef.id] = oValue
          //         row.chg = false
          //       })
          //     }
          //   }
          //   return true
          // }
        }
      }
    }
  },
  computed: {
    hasEdited() {
      return this.memento.length > 1
    }
  },
  methods: {
    constructGridSuccessful(grid) {
      grid.setNumberFormat('0,000', 5, '.', ',')
      grid.setNumberFormat('0,000', 6, '.', ',')
      grid.setNumberFormat('0,000', 7, '.', ',')
      grid.setNumberFormat('0,000', 8, '.', ',')
      grid.setNumberFormat('0,000', 9, '.', ',')
      grid.setNumberFormat('0,000', 10, '.', ',')
      grid.setNumberFormat('0,000', 11, '.', ',')
      grid.setNumberFormat('0,000', 12, '.', ',')
      grid.setNumberFormat('0,000', 13, '.', ',')
      grid.setNumberFormat('0,000', 14, '.', ',')
      grid.setNumberFormat('0,000', 15, '.', ',')
      grid.setNumberFormat('0,000', 16, '.', ',')
    },
    searchFile() {
      this.$refs.file.click()
    },
    fileChangeEvent() {
      this.file = this.$refs.file.files[0] || {
        name: undefined
      }
      this.fileLoaded = this.$refs.file.files[0] !== undefined
    },
    uploadFile() {
      if (this.fileLoaded) {
        let form = new FormData()
        form.append('file', this.file)
        this.$store.commit('loading')
        this.$http.post('/budget/base/upload', form, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }).then(response => {
          this.$swal({
            type: 'success',
            text: response.data
          })
          return response
        }).catch(response => {
          this.$swal({
            type: 'error',
            text: response.data
          })
          return response
        }).finally(() => {
          this.enableUploadArea = false
          this.$store.commit('finish')
        })
      } else {
        this.$swal({
          type: 'warning',
          text: '업로드할 파일을 선택해주세요.'
        })
      }
    },
    query() {
      try {
        assert.apply(this, [this.params.searchYear, '조회연도를 입력해주세요.'])

        this.$store.commit('loading')
        this.$http.post('/api/budget/base/list', this.params)
          .then(response => {
            this.data = response.data
            this.enableUploadArea = false
            this.memento = []
            return response
          })
          .finally(() => {
            this.$store.commit('finish')
          })
      } catch (e) {
        this.$swal({
          type: 'error',
          text: e
        })
      }
    },
    save() {
      try {
        let datas = this.data.filter(x => x.chg)

        // 저장할 내용이 없음
        assert(datas.length > 0, '변경된 행이 없습니다.')

        this.$store.commit('loading')
        this.$http.post('/api/budget/base/save', datas)
          .then(response => {
            this.$swal({
              type: 'success',
              text: '저장되었습니다.'
            }).then(this.query)
            return response
          })
          .catch(error => {
            if (error && error.response.data && error.response.data.message) {
              this.$swal({
                type: 'error',
                text: error.response.data.message
              })
            }
          })
          .finally(() => {
            this.$store.commit('finish')
          })
      } catch (e) {
        this.$swal({
          type: 'error',
          text: e
        })
      }
    },
    downloadExcel() {
      this.$refs.grid.instance.toExcel('http://dhtmlxgrid.appspot.com/export/excel')
    }
  },
  created() {
    // TODO::Query
    this.params = _.clone(defParams)
  },
  watch: {
    'data': {
      deep: true,
      handler(value) {
        let v = JSON.stringify(_.cloneDeep(value).map(x => {
          delete x.chg
          return x
        }))
        let exists = this.memento.indexOf(v)
        // If already hav same history
        if (exists >= 0) {
          // fallback
          this.memento.splice(exists, exists)
        } else {
          this.memento.unshift(v)
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.upload-area {
  position: relative;

  input[type="file"] {
    display: none;
  }

  * {
    float: left;
  }

  .input-area {
    min-width: 400px;
    margin-right: 15px;

    .input {
      height: 34px;
    }
  }
}

.upload-area:after {
  content: " ";
  display: table;
  clear: both;
}
</style>
