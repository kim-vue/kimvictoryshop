<template>
<input ref="box" type="text" class="input number" v-model="number" @input="number = $numeral(number).format('0,0')" @blur="apply" @keyup.enter="apply" :disabled="disable" v-show="showIf" />
</template>

<script>
export default {
  props: ['index', 'value', 'field'],
  data() {
    return {
      number: '0',
      disable: false,
      showIf: true
    }
  },
  mounted() {
    $(this.$refs.box).on('focus', () => {
      $(this.$refs.box).select()
    })
  },
  methods: {
    apply() {
      this.value[this.field] = this.$numeral(this.number).value()
      if (this.onSubmit !== undefined && typeof this.onSubmit === 'function') {
        this.onSubmit.apply(this, [])
      }
    }
  },
  watch: {
    'value': {
      immediate: true,
      deep: true,
      handler() {
        this.number = this.$numeral(this.value[this.field]).format('0,0')
      }
    }
  }
}
</script>
