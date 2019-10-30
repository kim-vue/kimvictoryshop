import NumberInput from '@/components/NumberInput.vue'

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
    'format': {
      type: String,
      required: false,
      default: '0,0'
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
  components: { NumberInput },
  template: `
  <td :colspan="colspan" style="text-align: right !important" v-if="readonly">{{ this.$numeral(value[field]).format(format) }}</td>
  <td :colspan="colspan" v-else>
    <number-input class="input" v-model="value[field]" @input="$emit('input', value)" :format="format" :disabled="disabled" />
  </td>
  `
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