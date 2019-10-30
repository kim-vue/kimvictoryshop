<template>
<div v-if="isLoaded">
  <!-- Table area -->
  <slip-table :slipType="data.slipTypeCd" v-model="data" :status="status" @input="$forceUpdate()" v-if="status.loaded" />
  <!-- //Table area -->

  <!-- Grid area -->
  <component :is="gridComponentName" :slipType="data.slipTypeCd" v-model="data" :status="status" @input="$forceUpdate()" v-if="status.loaded" />
  <!-- //Grid area -->

  <!--파일업로드-->
  <div class="file-upload" v-if="showEvidAtchPop">
    <div class="table-name">
      <h3 class="ico_table_name">증빙첨부</h3>
    </div>
    <!-- 20190520 퍼블수정 -->
    <div class="file has-name">
      <div class="file-label" @click="openUploadEvidencePopup()">
        <span class="file-cta">
          <span class="file-label"> Files Count</span>
          <span class="icon-bar"><img src="/img/bar.png" alt="" /></span>
        </span>
        <span class="file-name">{{ this.$numeral(evidFileSize).format('00') }}<i class="far fa-file-alt"></i></span>
      </div>
    </div>
    <!-- //20190520 퍼블수정 -->
  </div>
  <!--//파일업로드-->
</div>
<div v-else></div>
</template>

<script>
import _ from 'lodash'
import assert from '@/libs/assert'
import {
  url as _url
} from '@/libs/join'
import debug from '@/libs/debug'

const _debug = debug('SlipBase')

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
    this.$http.get(url, {
        params
      })
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

import SlipTable from '@/components/slip/SlipTable.vue'
import GridED from '@/components/slip/GridED.vue'
import GridRO from '@/components/slip/GridRO.vue'

import EvidAtchPop from '@/components/EvidAtchPop.vue'

export default {
  /**
   * Properties include
   */
  props: {
    id: {
      type: String,
      required: false
    },
    eaSlipNo: {
      type: String,
      required: false
    },
    value: {
      type: Object,
      required: false
    },
    status: {
      type: Object,
      required: false,
      default () {
        return {
          new: false,
          loaded: false,
          readonly: false,
          change: false,
          memento: []
        }
      }
    },
    readonly: {
      type: Boolean,
      required: false,
      default: false
    },
    showEvidAtchPop: {
      type: Boolean,
      required: false,
      default: true
    }
  },
  components: {
    SlipTable,
    GridED,
    GridRO
  },
  data() {
    return {
      data: {},
      options: {
        'SLIP_TYPE_CD': [],
        'VENDOR': [],
        'EMP': []
      },
      evidFileSize: 0
    }
  },
  computed: {
    isNew() {
      return this.getId === undefined && this.data.eaSlipNo === undefined
    },
    isLoaded() {
      return this.status.loaded
    },
    gridComponentName() {
      return 'Grid' + (this.isReadonly ? 'RO' : 'ED')
    },
    getId() {
      return this.eaSlipNo || this.id
    },
    isReadonly() {
      return this.status.readonly || this.readonly
    }
  },
  methods: {
    querySlipData() {
      return new Promise((resolve, reject) => {

        if (this.getId === undefined) {
          this.status.loaded = true
          this.status.readonly = true
          return resolve({})
        }

        this.status.loaded = false

        this.$store.commit('loading')
        this.$http.get(`/api/slip/${this.getId}`)
          .then(response => {
            let data = response.data.slipHeader
            data.slipDetails = response.data.slipDetails
            data.title = response.data.slipHeader.slipTypeNm + ' 전표'

            data.custAccount = [data.custBnkCd, data.custAcctNo].join('_')

            _.forEach(data.slipDetails, item => {
              switch (item.dcCd) {
                case 'C':
                  item.creditAmt = item.acctAmt
                  break
                case 'D':
                  item.debitAmt = item.acctAmt
                  break
              }
            })

            // 교통비 전표인 경우, 미지급 항목을 제외한다
            if (data.slipTypeCd === 'E6') {
              data.slipDetails = data.slipDetails.filter(x => [x.dcCd, x.lnTypeCd].join('_') !== 'C_ITEM')
            }

            this.status.readonly = data.slipStatCd !== '10'

            this.data = data
            this.$emit('input', this.data)

            this.status.change = false
            this.status.loaded = true
            setTimeout(() => {
              this.status.memento = [_.clone(this.data)]
            }, 1500)

            return resolve(response)
          })
          .catch(response => {
            return reject(response)
          })
          .finally(() => {
              this.$emit('slipTypeSend', this.data.slipTypeCd)
            this.$store.commit('finish')
          })
      })
    },
    querySlipTypeCd() {
      return queryOption.apply(this, ['/code/detail', 'SLIP_TYPE_CD', {
        groupCd: 'SLIP_TYPE_CD'
      }])
    },
    queryVendor(searchStr) {
      return queryOption.apply(this, [_url(`/vendor/${this.data.slipTypeCd}`, searchStr), 'VENDOR'])
    },
    queryEmp() {
      return queryOption.apply(this, ['/emp', 'EMP'])
    },
    queryEvidFile() {
      /**
       * 증빙파일이 얼마나 첨부되었는지 확인해보자
       */
      this.$http.get(`/api/evid/fileList/${this.getId}`)
        .then(response => {
          this.evidFileSize = ((response.data || {}).aFiles || []).length
        })
    },
    openUploadEvidencePopup() {
      let vm = this
      this.$modal.open({
        component: EvidAtchPop,
        props: {
          docMngNo: this.data.eaSlipNo,
          readonly: this.isReadonly // Check readonly
        },
        parent: this,
        width: 1200,
        events: {
          close(value) {
            vm.evidFileSize = value.length
          }
        }
      })
    }
  },
  created() {

    // Get login info
    let l = {}
    try {
      l = this.$store.state.loginInfo
    } catch (e) {
      l = {}
    }

    // Check is new
    if (this.getId || this.data.eaSlipNo !== undefined) {
      this.status.new = false
    } else {
      this.status.new = true
    }

    // if has copy code
    if (this.$route.params.copyEaSlipNo !== undefined) {
      this.$http.get(_url('/api/slip/copy', this.$route.params.copyEaSlipNo))
        .then(response => {
          let data = response.data.slipHeader
          data.slipDetails = response.data.slipDetails
          data.title = response.data.slipHeader.slipTypeNm + ' 전표'

          data.custAccount = [data.custBnkCd, data.custAcctNo].join('_')

          _.forEach(data.slipDetails, item => {
            switch (item.dcCd) {
              case 'C':
                item.creditAmt = item.acctAmt
                break
              case 'D':
                item.debitAmt = item.acctAmt
                break
            }
          })

          // 교통비 전표인 경우, 미지급 항목을 제외한다
          if (data.slipTypeCd === 'E6') {
            data.slipDetails = data.slipDetails.filter(x => [x.dcCd, x.lnTypeCd].join('_') !== 'C_ITEM')
          }

          // 임시번호 채번
          this.$http.get('/api/tmp/documentMngNo')
            .then(response => {
              data.eaSlipNo = response.data

              this.data = data

              this.$emit('input', this.data)

              this.queryEvidFile(this.data.eaSlipNo)

              this.status.change = false
              this.status.loaded = true
              this.status.readonly = false

              setTimeout(() => {
                this.status.memento = [_.clone(this.data)]
              }, 1500)
            })
        })
    }
    // if is new
    else if (this.isNew) {
      this.status.readonly = this.readonly || false

      // 임시번호 채번
      this.$http.get('/api/tmp/documentMngNo')
        .then(response => {
          this.data.eaSlipNo = response.data
          this.queryEvidFile(response.data)
        })

      // 기타전표 또는 교통비전표일때
      if (this.data.slipTypeCd === 'E4' || this.data.slipTypeCd === 'E6') {
        Promise.all([this.querySlipTypeCd(), this.queryVendor(l.loginId), this.queryEmp()])
          .then(() => {
            let slip = this.options['SLIP_TYPE_CD'].filter(x => x.detailCd === this.data.slipTypeCd)[0]
            // Has found
            if (slip !== undefined) {
              this.data.bpCd = slip.remark1
            }

            // has found vendor info
            if (this.options['VENDOR'].length === 1) {
              let vendor = this.options['VENDOR'][0]

              this.data.evdCustCd = vendor.vendCd
              this.data.evdCustNm = vendor.vendNm
              this.data.evdCustBizNo = vendor.bizNo

              let emp = this.options['EMP'].filter(x => x.empNo === vendor.bizNo)[0]
              if (emp !== undefined) {
                this.data.baseDeptCd = emp.cctrCd
                this.data.baseDeptNm = emp.cctrNm
              }
            }

            this.status.loaded = true
            setTimeout(() => {
              this.status.memento = [_.clone(this.data)]
            }, 1500)
          })
      }
    }
    // if isEditable and data is not set
    else if (this.data.eaSlipNo === undefined) {
      this.querySlipData()
      this.queryEvidFile(this.getId)
    }
    // else
    else {
      this.querySlipData()
      this.queryEvidFile(this.data.eaSlipNo)
    }
  },
  watch: {
    'value': {
      immediate: true,
      deep: true,
      handler(value) {
        this.data = value || {}
      }
    },
    'data': {
      deep: true,
      handler(value) {
        if (this.status.memento.length === 0) {
          this.status.memento.unshift(_.clone(value))
        } else {
          let c = JSON.stringify(this.status.memento[0])
          let v = JSON.stringify(v)
          if (c !== v) {
            this.status.memento.unshift(_.clone(value))
          }
        }
      }
    },
    'status.readonly'() {
      this.querySlipData()
    },
  }
}
</script>

<style lang="scss" scoped>

</style>
