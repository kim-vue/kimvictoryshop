<template>
  <div class="desc-item" v-if="options.type === '01'">
    <div class="tit"><span class="label-tit">- {{ title }}</span></div>
    <div class="desc">
      <div class="td-s-thumb search-area">
        <input class="input input-bg" type="text" v-model="data.empNo" style="width:80px;" disabled="disabled">
        <div class="ip-box ip-box-w02">
          <input class="input" type="text" v-model="data.empNm" @keypress.enter.prevent="query(data.empNm)" :disabled="lock()" />
          <button class="icon is-right modal-button" @click="openModal(data.empNm)" v-if="!lock()">
            <i class="fas fa-search"></i>
          </button>
        </div>
      </div>
      <div class="td-s-thumb search-area" v-if="options.showDept">
        <input class="input input-bg" type="text" v-model="data.dutNm" style="width:60px;" disabled="disabled" />
        <div class="ip-box ip-box-w02">
          <input class="input" type="text" v-model="data.deptNm" disabled="disabled" />
        </div>
      </div>
    </div>
  </div>
  <div class="form-group" v-else-if="options.type === '02'">
    <label class="control-label">{{ title }}</label>
    <div class="form-input">
      <div class="search-box">
        <div class="input-group">
          <input type="text" class="input" disabled="disabled" v-model="data.empNo" style="width: 80px;" />
          <input type="text" class="input search-input" v-model="data.empNm" style="max-width: calc(100% - 88px);" @keypress.enter.prevent="query(data.empNm)" :disabled="lock()" />
          <button type="button" class="btn-icon" @click="openModal(data.empNm)" v-if="!lock()">
            <span class="btn-icon"><i class="fas fa-search"></i></span>
          </button>
        </div>
        <div class="input-group" v-if="options.showDept">
          <input type="text" class="input" disabled="disabled" v-model="data.dutNm" style="width: 80px;" />
          <input type="text" class="input" disabled="disabled" v-model="data.deptNm" style="max-width: calc(100% - 88px);" />
        </div>
      </div>
    </div>
  </div>
  <div v-else></div>
</template>

<script>
import Emp from './Emp_new.vue'

const def_props = {
  type: '01',
  authorize: true,
  showDept: true,
  empNo: 'empNo',
  empNm: 'empNm',
  deptNm: 'deptNm',
  dutNm: 'dutNm'
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
      default() {
        return {
          type: '01',
          authorize: false,
          showDept: true,
          empNo: 'empNo',
          empNm: 'empNm',
          deptNm: 'deptNm',
          dutNm: 'dutNm'
        }
      }
    }
  },
  data() {
    return {
      data: {
        empNo: undefined,
        empNm: undefined,
        deptNm: undefined,
        dutNm: undefined
      }
    }
  },
  methods: {
    lock() {
      if (this.options.authorize) {
        if (this.authority === '10')
          return false
        return true
      } else {
        return false
      }
    },
    submit(data) {
      data = data || {}
      // Apply data
      this.data.empNo = data.empNo
      this.data.empNm = data.empNm
      this.data.deptNm = data.deptNm
      this.data.dutNm = data.dutNm
      // Apply to parents
      this.value[this.options.empNo] = this.data.empNo
      this.value[this.options.empNm] = this.data.empNm
      this.value[this.options.deptNm] = this.data.deptNm
      this.value[this.options.dutNm] = this.data.dutNm
      this.$emit('input', this.value)
      this.$emit('submit')
    },
    query(searchStr) {
      if (searchStr) {
        this.$store.commit('loading')
        this.$http.get(`/api/emp/${searchStr}`)
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
        component: Emp,
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
          // Apply data
          this.data.empNo = loginInfo.loginId
          this.data.empNm = loginInfo.userName
          this.data.deptNm = loginInfo.loginDeptNm
          this.data.dutNm = loginInfo.loginDutNm
          // Apply to parents
          this.value[this.options.empNo] = this.data.empNo
          this.value[this.options.empNm] = this.data.empNm
          this.value[this.options.deptNm] = this.data.deptNm
          this.value[this.options.dutNm] = this.data.dutNm
          this.$emit('input', this.value)
        } catch (e) {
          // ...
        }
      }
    }
  },
  watch: {
    'value': {
      immediate: true,
      deep: true,
      handler(value) {
        this.data = {
          empNo: value[this.options.empNo],
          empNm: value[this.options.empNm],
          deptNm: value[this.options.deptNm],
          dutNm: value[this.options.dutNm]
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
