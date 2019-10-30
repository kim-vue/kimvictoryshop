<template>
<dhx-calendar v-model="date" :config="config" @input="apply" />
</template>

<script>
import DhxCalendar from '@/components/DhxCalendar.vue'

export default {
  props: ['index', 'value', 'field'],
  components: {
    DhxCalendar
  },
  data() {
    return {
      date: undefined,
      config: {}
    }
  },
  methods: {
    apply() {
      this.value[this.field] = this.date
      if (this.onSubmit !== undefined && typeof this.onSubmit === 'function') {
        this.onSubmit.apply(this, [])
      }
    }
  },
  watch: {
    'value': {
      immediate: true,
      deep: true,
      handler(value) {
        this.date = value[this.field]
      }
    }
  }
}
</script>
