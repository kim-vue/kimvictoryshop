<template>
  <div class="modal-card">
    <header class="modal-card-head pop-header">
      <p class="modal-card-title tit">
        <slot name="header"></slot>
      </p>
    </header>

    <section class="modal-card-body pop-content">
      <slot name="content"></slot>
    </section>
  </div>
</template>
<script>
export default {
  name: "ModalSlot",
  data() {
    return {
    }
  },
  methods: {
  },
}
</script>

<style>
.modal-card-head {background: #0065b3;}
.modal-card-title {color:white; font-size:1.2em;}
.modal-close {top: 80px;}
</style>
