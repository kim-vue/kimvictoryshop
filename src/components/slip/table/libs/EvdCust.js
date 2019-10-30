import uuid from '@/libs/uuid'
import Vendor from '@/components/Vendor_new.vue'

const th = {
  props: {
    'title': {
      type: String,
      required: true
    },
    'readonly': {
      type: Boolean,
      required: false,
      default: false
    },
    'required': {
      type: Boolean,
      required: false,
      default: false
    }
  },
  template: `
  <th :class="{ 'tp-a': required && !readonly }">{{ title }}</th>
  `
}

const td = {
  props: {
    'title': {
      type: String,
      required: true
    },
    'value': {
      type: Object,
      required: true
    },
    'colspan': {
      type: Number,
      required: false,
      default: 1
    },
    'readonly': {
      type: Boolean,
      required: false,
      default: false
    }
  },
  template: `
  <td :colspan="colspan" v-if="readonly">{{ value.evdCustCd }} / {{ value.evdCustNm }}</td>
  <td :colspan="colspan" v-else>
    <div class="td-s-thumb search-area">
      <input class="input input-bg mr5 Rt-M rs-mt2" type="text" v-model="value.evdCustCd" style="width:66px;" disabled="disabled" />
      <div class="ip-box ip-box-w02 rs-mt2">
        <input type="text" class="input" v-model="value.evdCustNm" @keypress.enter="query(value.evdCustNm)" />
        <button class="icon is-right" @click="modal(value.evdCustNm)"><i class="fas fa-search"></i></button>
      </div>
      <button class="remove_text trash-input rs-mb2" @click="apply()">
        <i class="far fa-trash-alt"></i>
      </button>
    </div>
  </td>
  `,
  methods: {
    apply(data) {
      data = data || {}
      this.value.evdCustCd = data.vendCd
      this.value.evdCustNm = data.vendNm
      this.value.evdCustBizNo = data.bizNo
      this.$emit('input', this.value)
    },
    failure() {
      this.apply({})
    },
    modal(searchStr) {
      let vm = this
      this.$modal.open({
        component: Vendor,
        props: {
          searchStr,
          slipTypeCd: this.value.slipTypeCd
        },
        parent: this,
        events: {
          close(data) {
            vm.apply.apply(vm, [data])
          }
        }
      })
    },
    query(searchStr) {
      if (searchStr) {
        this.$store.commit('loading')
        this.$http.get(`/api/vendor/${this.value.slipTypeCd}/${searchStr}`)
          .then(response => {
            if (response.data.length === 1) {
              this.apply(response.data[0] || {})
            } else {
              this.modal(searchStr)
            }
          })
          .catch(() => {
            this.failure()
          })
          .finally(() => {
            this.$store.commit('finish')
          })
      } else {
        this.failure()
      }
    }
  }
}

const td_pay_chk = {
  props: {
    'value': {
      type: Object,
      required: true
    },
    'readonly': {
      type: Boolean,
      required: false,
      default: false
    }
  },
  template: `
  <td class="bd-l-none">
    <input type="checkbox" :id="id" v-model="value.usePayCust" :disabled="readonly" @input="checkInput" />
    <label :for="id">실지급처</label>
  </td>
  `,
  computed: {
    id() {
      return uuid()
    }
  },
  methods: {
    checkInput() {
      this.value.payCustCd = undefined
      this.value.payCustNm = undefined
      this.value.payCustBizNo = undefined
      this.$emit('input', this.value)
    }
  },
  created() {
    this.value.usePayCust = !!(this.value.payCustCd !== undefined)
  }
}

const td_pay = {
  props: {
    'title': {
      type: String,
      required: true
    },
    'value': {
      type: Object,
      required: true
    },
    'colspan': {
      type: Number,
      required: false,
      default: 1
    },
    'readonly': {
      type: Boolean,
      required: false,
      default: false
    }
  },
  template: `
  <td class="bd-l-none" v-if="readonly">{{ value.payCustCd }} / {{ value.payCustNm }}</td>
  <td class="bd-l-none" v-else>
    <div class="td-s-thumb search-area">
      <input class="input input-bg mr5 Rt-M rs-mt2" type="text" v-model="value.payCustCd" style="width:66px;" disabled="disabled" />
      <div class="ip-box ip-box-w02 rs-mt2">
        <input type="text" class="input" v-model="value.payCustNm" @keypress.enter="query" :disabled="!value.usePayCust" />
        <button class="icon is-right" @click="modal" :disabled="!value.usePayCust"><i class="fas fa-search"></i></button>
      </div>
      <button class="remove_text trash-input rs-mb2" @click="apply()" :disabled="!value.usePayCust">
        <i class="far fa-trash-alt"></i>
      </button>
    </div>
  </td>
  `,
  methods: {
    apply(data) {
      data = data || {}
      this.value.payCustCd = data.vendCd
      this.value.payCustNm = data.vendNm
      this.value.payCustBizNo = data.bizNo
      this.$emit('input', this.value)
    },
    failure() {
      this.$swal({
        type: 'error',
        text: `요청하신 실지급처를 찾을 수 없습니다.`
      }).then(() => {
        this.apply({})
      })
    },
    modal() {
      let vm = this
      this.$modal.open({
        component: Vendor,
        props: {
          slipTypeCd: this.value.slipTypeCd
        },
        parent: this,
        events: {
          close(data) {
            vm.apply.apply(vm, [data])
          }
        }
      })
    },
    query() {
      this.$store.commit('loading')
      this.$http.get(`/api/vendor/${this.value.slipTypeCd}/${this.value.payCustNm}`)
        .then(response => {
          if (response.data.length > 0) {
            this.apply(response.data[0] || {})
          } else {
            this.failure()
          }
        })
        .catch(() => {
          this.failure()
        })
        .finally(() => {
          this.$store.commit('finish')
        })
    }
  }
}

export default {
  functional: true,
  props: {
    'title': {
      type: String,
      required: true
    },
    'required': {
      type: Boolean,
      required: false,
      default: false
    },
    'value': {
      type: Object,
      required: true
    },
    'colspan': {
      type: Number,
      required: false,
      default: 1
    },
    'readonly': {
      type: Boolean,
      required: false,
      default: false
    },
    'usePayCust': {
      type: Boolean,
      required: false,
      default: false
    }
  },
  render(createElement, context) {
    // construct emit
    let on = {}
    for (var event in context.listeners) {
      on[event] = e => {
        if (Array.isArray(context.listeners[event]) && context.listeners[event].length > 0) {
          _.forEach(context.listeners[event], f => {
            if (typeof f === 'function')
              f.apply(this, [e])
          })
        } else if (typeof context.listeners[event] === 'function') {
          context.listeners[event].apply(this, [e])
        }
      }
    }

    const the = createElement(th, {
      props: context.props
    })
    const tde = createElement(td, {
      props: context.props,
      on: on
    })
    const tde_pay_1 = createElement(td_pay_chk, {
      props: context.props,
      on: on
    })
    const tde_pay_2 = createElement(td_pay, {
      props: context.props,
      on: on
    })
    return context.props.usePayCust ? [the, tde, tde_pay_1, tde_pay_2] : [the, tde]
  }
}
