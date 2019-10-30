<template>
<input ref="box" type="text" class="input" v-model="string" @blur="apply" @keyup.enter="apply" />
</template>

<script>
export default {
  props: ['index', 'value', 'field'],
  data() {
    return {
      string: ''
    }
  },
  created() {
    this.string = this.value[this.field]
  },
  methods: {
    apply() {
      this.value[this.field] = this.string
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
        this.string = this.value[this.field]
      }
    }
  }
}
</script>
