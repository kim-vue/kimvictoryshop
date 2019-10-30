<template>
<layout>
  <span slot="header">
    {{ data.slipTypeNm }} - {{ data.eaSlipNo }}
    <button class="btn-pop-close delete" aria-label="close" @click="$parent.close()"></button>
  </span>
  <div slot="content" class="inner-box">
    <slip-base :ea-slip-no="eaSlipNo" v-model="data" />
  </div>
</layout>
</template>

<script>
import Layout from '@/components/ModalSlot.vue'
import SlipBase from '@/components/slip/SlipBase.vue'

export default {
  props: {
    eaSlipNo: {
      type: String,
      required: true
    }
  },
  components: {
    Layout,
    SlipBase
  },
  data() {
    return {
      data: {}
    }
  }
}
</script>

<style scoped>
.modal-card {
  width: auto;
}
</style>
