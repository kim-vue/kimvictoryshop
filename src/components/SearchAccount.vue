<template>
  <div class="desc-item" v-if="options.type === '01'">
    <div class="tit"><span class="label-tit">- {{ title }}</span></div>
    <div class="desc">
      <div class="td-s-thumb search-area">
        <input class="input input-bg" type="text" v-model="data.acctCd" style="width:60px;" disabled="disabled">
        <div class="ip-box ip-box-w02">
          <input class="input" type="text" v-model="data.acctNm" @keypress.enter.prevent="query(data.acctNm)" />
          <button class="icon is-right modal-button" @click="openModal(data.acctNm)">
            <i class="fas fa-search"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
  <div class="form-group" v-else-if="options.type === '02'">
    <label class="control-label">{{ title }}</label>
    <div class="form-input">
      <div class="search-box">
        <div class="input-group">
          <input type="text" class="input" disabled="disabled" v-model="data.acctCd" style="width: 80px;" />
          <input type="text" class="input search-input" v-model="data.acctNm" style="max-width: calc(100% - 88px);" @keypress.enter.prevent="query(data.acctNm)" />
          <button type="button" class="btn-icon" @click="openModal(data.acctNm)">
            <span class="btn-icon"><i class="fas fa-search"></i></span>
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-else></div>
</template>

<script>
import Account from './Account_new.vue'

const def_props = {
  type: '01',
  authorize: true,
  acctCd: 'acctCd',
  acctNm: 'acctNm',
  slipTypeCd: undefined,
  queryFunction: undefined
}

function _successHandler(response, searchStr) {
  if (Array.isArray(response.data)) {
    if (response.data.length === 1) {
      this.submit(response.data[0])
    } else {
      this.openModal(searchStr)
    }
  } else {
    this.submit()
  }
  return response
}

function _defQueryFunction(searchStr) {
  this.$store.commit('loading')
  this.$http.get('/api/account', {
    params: {
      slipTypeCd: this.options.slipTypeCd,
      value: searchStr
    }
  }).then(response => {
    return _successHandler.apply(this, [response, searchStr])
  })
  .catch(() => {
    this.submit()
  })
  .finally(response => {
    this.$store.commit('finish')
  })
}

export default {
  props: {
    title: {
      type: String,
      required: false,
      default: '계정코드'
    },
    value: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      required: false,
      default() {
        return {
          type: '01',
          authorize: false,
          acctCd: 'acctCd',
          acctNm: 'acctNm',
          slipTypeCd: undefined,
          queryFunction: undefined
        }
      }
    }
  },
  data() {
    return {
      data: {
        acctCd: undefined,
        acctNm: undefined
      }
    }
  },
  methods: {
    submit(data) {
      data = data || {}
      // Apply data
      this.data.acctCd = data.acctCd
      this.data.acctNm = data.acctNm
      // Apply to parents
      this.value[this.options.acctCd] = this.data.acctCd
      this.value[this.options.acctNm] = this.data.acctNm
      this.$emit('input', this.value)
      this.$emit('submit')
    },
    query(searchStr) {
      if (searchStr) {
        if (typeof this.options.queryFunction === 'function') {
          this.options.queryFunction.apply(this, [searchStr])
            .then(response => {
              return _successHandler.apply(this, [response, searchStr])
            })
        } else {
          _defQueryFunction.apply(this, [searchStr])
        }
      } else {
        this.submit()
      }
    },
    openModal(searchStr) {
      let vm = this
      this.$modal.open({
        component: Account,
        props: {
          title: this.title,
          searchStr: searchStr,
          slipTypeCd: this.options.slipTypeCd,
          queryFunction: this.options.queryFunction
        },
        parent: this,
        events: {
          close(data) {
            vm.submit.apply(vm, [data])
          }
        }
      })
    }
  },
  watch: {
    'value': {
      immediate: true,
      deep: true,
      handler(value) {
        this.data = {
          acctCd: value[this.options.acctCd],
          acctNm: value[this.options.acctNm]
        }
      }
    },
    'options': {
      immediate: true,
      deep: true,
      handler(value) {
        for (var member in def_props) {
          if (value[member] === undefined) {
            value[member] = def_props[member]
          }
        }
      }
    }
  }
}
</script>
