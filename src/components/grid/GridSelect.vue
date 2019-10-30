<template>
<select class="input is-fullwidth" v-model="data" @input="onInput()" :disabled="disable" v-show="showIf">
  <option v-for="option in options" :key="option[detailCd]" :value="option[detailCd]" v-text="option[detailNm]" />
</select>
</template>

<script>
export default {
  props: ['index', 'value', 'field'],
  data() {
    return {
      data: undefined,
      disable: false,
      showIf: true,
      options: [],
      detailCd: 'detailCd',
      detailNm: 'detailNm'
    }
  },
  mounted() {
    this.data = this.value[this.field]
  },
  methods: {
    onInput() {
      this.$nextTick(() => {
        this.value[this.field] = this.data
        if (this.onSubmit !== undefined && typeof this.onSubmit === 'function') {
          this.onSubmit.apply(this, [])
        }
      })
    }
  },
  watch: {
    'value': {
      immediate: true,
      deep: true,
      handler() {
        this.data = this.value[this.field]
        this.$forceUpdate()
      }
    },
    'options': {
      immediate: true,
      deep: true,
      handler() {
        this.data = this.value[this.field]
        this.$forceUpdate()
      }
    }
  }
}
</script>
