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
    'code': {
      type: String,
      required: false,
      default: 'detailCd'
    },
    'text': {
      type: String,
      required: false,
      default: 'detailNm'
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
  <td :colspan="colspan" v-if="readonly">{{ getCodeName(value[field]) }}</td>
  <td :colspan="colspan" v-else>
    <b-select class="select is-fullwidth" v-model="value[field]" @input="$emit('input', value)" :disabled="disabled">
      <option v-for="option in options" :key="option[code]" :value="option[code]" v-text="option[text]" />
    </b-select>
  </td>
  `,
  methods: {
    getCodeName(value) {
      let f = this.options.filter(x => x[this.code] === value)[0]
      return f !== undefined ? f[this.text] : value
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
    'code': {
      type: String,
      required: false,
      default: 'detailCd'
    },
    'text': {
      type: String,
      required: false,
      default: 'detailNm'
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
