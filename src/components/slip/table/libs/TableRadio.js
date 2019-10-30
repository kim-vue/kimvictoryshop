import uuid from '@/libs/uuid'

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
    'value': {
      type: Object,
      required: true
    },
    'field': {
      type: String,
      required: true
    },
    'options': {
      type: Array,
      required: true
    },
    'colspan': {
      type: Number,
      required: false,
      default: 1
    },
    'disabled': {
      type: Boolean,
      required: false,
      default: false
    },
    'readonly': {
      type: Boolean,
      required: false,
      default: false
    }
  },
  template: `
  <td :colspan="colspan" v-if="readonly">{{ getCodeName(data) }}</td>
  <td :colspan="colspan" v-else>
    <div class="control">
      <div class="db-ib fl_left" v-for="(option, index) in options">
        <input type="radio" :id="getRadioId(index)" v-model="data" :disabled="disabled" :value="option.value" @change="apply" />
        <label :for="getRadioId(index)" class="NotoM">{{ option.label }}</label>
      </div>
    </div>
  </td>
  `,
  data() {
    return {
      id: undefined,
      data: undefined
    }
  },
  methods: {
    getCodeName(value) {
      let f = this.options.filter(x => x.value === value)[0]
      return f !== undefined ? f.label : value
    },
    getRadioId(index) {
      return [this.id, index].join('_')
    },
    apply() {
      this.value[this.field] = this.data
      this.$emit('input', this.value)
    }
  },
  created() {
    this.id = String(uuid()).replace(/\W/g, '')
  },
  watch: {
    'value': {
      immediate: true,
      deep: true,
      handler(value) {
        this.data = value[this.field]
      }
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
    'field': {
      type: String,
      required: true
    },
    'options': {
      type: Array,
      required: true
    },
    'colspan': {
      type: Number,
      required: false,
      default: 1
    },
    'disabled': {
      type: Boolean,
      required: false,
      default: false
    },
    'readonly': {
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

    const the = createElement(th, { props: context.props })
    const tde = createElement(td, {
      props: context.props,
      on: on
    })
    return [the, tde]
  }
}
