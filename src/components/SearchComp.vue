<template>
<div class="desc-item" v-if="options.type === '01'">
  <div class="tit"><span class="label-tit">- {{ title }}</span></div>
  <div class="desc">
    <select class="input is-fullwidth" v-model="data.compCd" :disabled="lock()" v-show="show">
      <option v-for="{ key, value } in selectOptions" :key="key" :value="key">{{ format(key, value) }}</option>
    </select>
  </div>
</div>
<div class="form-group" v-else-if="options.type === '02'">
  <label class="control-label">{{ title }}</label>
  <div class="form-input">
    <select class="input is-fullwidth" v-model="data.compCd" :disabled="lock()" v-show="show">
      <option v-for="{ key, value } in selectOptions" :key="key" :value="key">{{ format(key, value) }}</option>
    </select>
  </div>
</div>
<div v-else></div>
</template>

<script>
const def_props = {
  type: '01',
  authorize: true,
  compCd: 'compCd'
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
      default: '회사'
    },
    options: {
      type: Object,
      required: false,
      default () {
        return {
          type: '01',
          authorize: true,
          compCd: 'compCd'
        }
      }
    }
  },
  data() {
    return {
      authority: undefined,
      data: {
        compCd: undefined
      },
      selectOptions: [],
      show: false
    }
  },
  methods: {
    format(key, value) {
      if (key === undefined) {
        return value
      } else {
        return '[' + key + '] ' + value
      }
    },
    lock() {
      if (this.options.authorize) {
        if (this.authority === '10')
          return false
        return true
      } else {
        return false
      }
    },
    initializeValues() {
      if (this.authority !== '10') {
        try {
          let loginInfo = this.$store.state.loginInfo
          this.data.compCd = loginInfo.compCd
          this.value[this.options.compCd] = this.data.compCd
          this.$emit('input', this.value)
        } catch (e) {
          // ...
        }
      }
    }
  },
  created() {
    this.$http.get('/api/code/combo', {
      params: {
        groupCd: 'COMP_CD'
      }
    }).then(response => {
      let selectOptions = response.data
      selectOptions.unshift({
        key: undefined,
        value: '==전체=='
      })
      this.selectOptions = selectOptions
      this.show = true
    })

    try {
      let authority = this.$store.state.loginInfo.authorities.map(x => x.roleSelectCd)[0]
      if (!authority) {
        authority = undefined
      }
      this.authority = authority
      this.initializeValues()
    } catch (e) {
      // this.authority = undefined
    }
  },
  watch: {
    'value': {
      immediate: true,
      deep: true,
      handler(value) {
        this.data = {
          compCd: value[this.options.compCd]
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
