<template>
<input ref="ibox" type="text" class="Rt-M tar" />
</template>

<script>
import $ from 'jquery'

export default {
  replace: true,
  props: ['value', 'format'],
  data() {
    return {
      formatter: '0,0'
    }
  },
  created() {
    this.$nextTick(() => {
      var $el = $(this.$refs.ibox)
      this.formatter = this.format || '0,0'
      $el.val(this.$numeral(this.value || 0).format(this.formatter))
      $el.on('focus', () => {
        $el.select()
      })
      $el.on('input', () => {
        this.$nextTick(() => {
          var value = this.$numeral($el.val())
          $el.val(value.format(this.formatter))
          this.$emit('input', value.value())
          this.$forceUpdate()
        })
      })
      $el.on('blur', () => {
        this.$nextTick(() => {
          var value = this.$numeral($el.val())
          $el.val(value.format(this.formatter))
          this.$emit('update', value.value())
          this.$forceUpdate()
        })
      })
    })
  },
  beforeDestroy() {
    $(this.$refs.ibox).off('focus')
  },
  watch: {
    value: {
      immediate: true,
      handler(value) {
        this.$nextTick(() => {
          var $el = $(this.$refs.ibox)
          $el.val(this.$numeral(value).format(this.formatter))
        })
      }
    }
  }
}
</script>
