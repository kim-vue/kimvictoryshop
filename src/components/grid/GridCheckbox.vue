<template>
<div class="bd-l-none checkbox-wrapper">
  <input :id="id" type="checkbox" v-model="data" @change="apply" />
  <label :for="id">&nbsp;</label>
</div>
</template>

<script>
import uuid from '@/libs/uuid'

export default {
  props: ['index', 'value', 'field'],
  data() {
    return {
      id: undefined,
      data: false
    }
  },
  created() {
    this.id = uuid()
  },
  methods: {
    apply() {
      this.value[this.field] = this.data ? (this.trueValue || 'Y') : (this.falseValue || 'N')
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
        this.$nextTick(() => {
          this.data = this.value[this.field] === (this.trueValue || 'Y') ? true : false
        })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.checkbox-wrapper {
  position: relative;

  :global(label) {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    padding: 0 12px;
  }
}
</style>
