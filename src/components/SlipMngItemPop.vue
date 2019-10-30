<template>
<layout>
  <span slot="header">
    관리 항목
    <button class="btn-pop-close delete" aria-label="close" @click="$parent.close()"></button>
  </span>
  <div slot="content" class="inner-box">
    <div class="content-name" style="margin-top: 20px;" v-if="isInputState">
      <div class="btn-wrap btn-type1 clearfix" style="float: right; margin-top: -25px;">
        <button class="btn-size btn-blue fl_left" @click="$emit('close', rows[0])">
          <span class="btn-icon"><i class="fas fa-check"></i></span> 완료
        </button>
        <button class="btn-size btn-gray fl_left" @click="$parent.close()">
          <span class="btn-icon"><i class="fas fa-times"></i></span> 취소
        </button>
      </div>
    </div>

    <!-- Grid 영역 -->
    <div class="table-b" v-if="config !== undefined">
      <dhx-grid ref="grid" v-model="rows" :config="config" @constructGridSuccessful="constructGridSuccessful" />
    </div>
    <!-- //Grid 영역 -->
  </div>
</layout>
</template>

<script>
import _ from 'lodash'
import Vue from 'vue'

import Layout from '@/components/ModalSlot.vue'
import DhxGrid from '@/components/DhxGrid.vue'

import GridSelect from '@/components/grid/GridSelect.vue'

const bus = new Vue()

const defColumns = [{
  value: 'No.',
  width: 40,
  type: 'cntr'
}, {
  id: 'cctrNm',
  value: '계정과목',
  width: 150
}]

const options = {}
const mutex = {}

function queryOption(cd) {
  return new Promise((resolve, reject) => {
    if (mutex[cd] || (Array.isArray(options[cd]) && options[cd].length > 0)) {
      resolve({})
    } else {
      mutex[cd] = true
      this.$http.get('/api/code/combo', {
        params: {
          groupCd: cd
        }
      }).then(response => {
        options[cd] = response.data
        bus.$emit(cd, options[cd])
      }).finally(() => {
        delete mutex[cd]
      })
    }
  })
}

const DateRenderer = {
  template: `<span style="padding-left: 10px; padding-right: 10px;">{{ this.$moment(value[field]).format('YYYY-MM-DD') }}</span>`
}

const CodeRenderer = (code) => {
  return {
    template: `<span style="padding-left: 10px; padding-right: 10px;">{{ value[field] }}</span>`,
    data() {
      return {
        options: []
      }
    },
    methods: {
      format(value) {
        let f = this.options.filter(x => x.key === this.value[this.field])[0]
        return f === undefined ? value : f.value
      }
    },
    created() {
      if (!options[code]) {
        queryOption.apply(this, [code])
      } else {
        this.options = options[code]
      }

      bus.$on(code, () => {
        this.options = options[code]
      })
    }
  }
}

const CodeSelector = (code) => {
  return {
    template: `
      <select class="input is-fullwidth" v-model="data" @change="apply()">
        <option v-for="{ key, value } in options" :key="key" :value="key" v-text="value" />
      </select>
    `,
    data() {
      return {
        data: undefined,
        options: []
      }
    },
    methods: {
      apply() {
        this.value[this.field] = this.data
        this.$emit('input', this.value)
      }
    },
    created() {
      if (!options[code]) {
        queryOption.apply(this, [code])
      } else {
        this.options = options[code]
        let f = this.options.filter(x => x.key === this.data)[0]
        if (f === undefined) {
          f = this.options[0]
        }
        this.data = f.key
        this.value[this.field] = this.data
        this.$emit('input', this.value)
      }

      bus.$on(code, () => {
        this.options = options[code]
        let f = this.options.filter(x => x.key === this.data)[0]
        if (f === undefined) {
          f = this.options[0]
        }
        this.data = f.key
        this.value[this.field] = this.data
        this.$emit('input', this.value)
      })
    },
    watch: {
      value: {
        immediate: true,
        deep: true,
        handler(value) {
          this.data = value[this.field]
        }
      }
    }
  }
}

export default {
  props: {
    eaSlipNo: {
      type: String,
      required: false
    },
    orderSeq: {
      type: Number,
      required: false
    },
    acctCd: {
      type: String,
      required: true
    },
    data: {
      type: Object,
      required: true
    },
    readonly: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  components: {
    Layout,
    DhxGrid
  },
  data() {
    return {
      config: undefined,
      rows: []
    }
  },
  computed: {
    isInputState() {
      return !this.readonly
    }
  },
  methods: {
    queryGridConfig() {
      this.config = undefined
      this.$http.post('/api/slip/mngItemPop', {
        acctCd: this.acctCd
      }).then(response => {
        let config = {
          columns: defColumns,
          autoHeight: true
        }
        let datas = response.data.map(x => {
          x.mngItemTypeCd = String(x.mngItemTypeCd || 'text').toLowerCase()
          return x
        }).filter(x => x.useYn === 'Y')
        let append = []
        let row = _.clone(this.data)

        _.forEach(datas, x => {
          let id = ['ref', this.$numeral(x.mngItemCd.replace(/^.*(\d+)$/g, '$1')).value()].join('')
          let value = x.mngItemNm
          let width = this.$numeral(x.fixLen).value()
          let align = x.halignCd || 'center'
          let inputType = x.mngItemTypeCd
          let type = 'ro'
          let component = undefined

          switch (inputType) {
            case 'text':
              type = this.readonly ? 'ro' : 'ed'
              break
            case 'date':
              type = this.readonly ? 'ro' : 'dhxCalendarA'
              component = this.readonly ? DateRenderer : undefined
              break
            case 'code':
              type = 'ro'
              if (x.useCd) {
                component = this.readonly ? CodeRenderer(x.useCd) : CodeSelector(x.useCd)
              } else {
                type = this.readonly ? 'ro' : 'ed'
              }
              break
          }

          if (row[id] === undefined) {
            row[id] = x.defaultValue || undefined
          }

          append.push({
            id,
            value,
            width,
            align,
            type,
            component: component
          })
        })

        config.columns = config.columns.concat(append)

        this.config = config
        this.rows = [row]
      })
    },
    constructGridSuccessful(grid) {
      grid.setDateFormat('%Y-%m-%d', '%Y%m%d')
    }
  },
  created() {
    this.queryGridConfig()
  }
}
</script>

<style scoped>

</style>
