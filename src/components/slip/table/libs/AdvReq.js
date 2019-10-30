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
      required: false
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
  <td v-if="readonly"></td>
  <td class="clearfix" v-else>
    <div class="control is-expanded search-area">
      <div class="ip-box rs-mt2" style="width:80%;">
        <input class="input input-bg" type="text" value="" disabled="disabled" />
        <button class="icon is-right" disabled="disabled">
          <i class="fas fa-search"></i>
        </button>
      </div>
      <button class="remove_text rs-mt2 rs-mb2" disabled="disabled">
        <i class="far fa-trash-alt"></i>
      </button>
    </div>
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
      required: false
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