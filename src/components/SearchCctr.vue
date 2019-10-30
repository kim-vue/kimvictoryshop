<template>
<div class="desc-item" v-if="options.type === '01'">
  <div class="tit"><span class="label-tit">- {{ title }}</span></div>
  <div class="desc">
    <div class="td-s-thumb search-area">
      <input class="input input-bg" type="text" v-model="data.cctrCd" style="width:60px;" disabled="disabled">
      <div class="ip-box ip-box-w02">
        <input class="input" type="text" v-model="data.cctrNm" @keypress.enter.prevent="query(data.cctrNm)" />
        <button class="icon is-right modal-button" @click="openModal(data.cctrNm)">
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
        <input type="text" class="input" disabled="disabled" v-model="data.cctrCd" style="width: 80px;" />
        <input type="text" class="input search-input" v-model="data.cctrNm" style="max-width: calc(100% - 88px);" :disabled="lock()" @keypress.enter.prevent="query(data.cctrNm)" />
        <button type="button" class="btn-icon" @click="openModal(data.cctrNm)" v-if="!lock()">
          <span class="btn-icon"><i class="fas fa-search"></i></span>
        </button>
      </div>
    </div>
  </div>
</div>
<div v-else></div>
</template>

<script>
import Cctr from './Cctr_new.vue'

const def_props = {
  type: '01',
  authorize: true,
  cctrCd: 'cctrCd',
  cctrNm: 'cctrNm'
}

export default {
  props: {
    value: {
      type: Object,
      required: true
    },
    title: {
      type: String,
      required: false,
      default: '부서'
    },
    options: {
      type: Object,
      required: false,
      default () {
        return {
          type: '01',
          authorize: true,
          cctrCd: 'cctrCd',
          cctrNm: 'cctrNm'
        }
      }
    }
  },
  data() {
    return {
      data: {
        authority: undefined,
        cctrCd: undefined,
        cctrNm: undefined
      }
    }
  },
  methods: {
    lock() {
      if (this.options.authorize) {
        if (this.authority !== '10')
          return true
      }
      return false
    },
    submit(data) {
      data = data || {}
      // Apply data
      this.data.cctrCd = data.cctrCd
      this.data.cctrNm = data.cctrNm
      // Apply to parents
      this.value[this.options.cctrCd] = this.data.cctrCd
      this.value[this.options.cctrNm] = this.data.cctrNm
      this.$emit('input', this.value)
      this.$emit('submit')
    },
    query(searchStr) {
      if (searchStr) {
        this.$store.commit('loading')
        this.$http.get(`/api/cctr/${searchStr}`)
          .then(response => {
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
          })
          .catch(() => {
            this.submit()
          })
          .finally(response => {
            this.$store.commit('finish')
          })
      } else {
        this.submit()
      }
    },
    openModal(searchStr) {
      let vm = this
      this.$modal.open({
        component: Cctr,
        props: {
          title: this.title,
          searchStr: searchStr
        },
        parent: this,
        events: {
          close(data) {
            vm.submit.apply(vm, [data])
          }
        }
      })
    },
    initializeValues() {
      if (this.authority !== '10') {
        try {
          let loginInfo = this.$store.state.loginInfo
          this.data.cctrCd = loginInfo.loginDeptCd
          this.data.cctrNm = loginInfo.loginDeptNm
          this.value[this.options.cctrCd] = this.data.cctrCd
          this.value[this.options.cctrNm] = this.data.cctrNm
          this.$emit('input', this.value)
        } catch (e) {
          // ...
        }
      }
    }
  },
  created() {
    try {
      let authority = this.$store.state.loginInfo.authorities.map(x => x.roleSelectCd)[0]
      if (!authority) {
        authority = undefined
      }
      this.authority = authority
      this.initializeValues()
    } catch (e) {}
  },
  watch: {
    'value': {
      immediate: true,
      deep: true,
      handler(value) {
        this.data = {
          cctrCd: value[this.options.cctrCd],
          cctrNm: value[this.options.cctrNm]
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
        this.initializeValues()
      }
    }
  }
}
</script>
