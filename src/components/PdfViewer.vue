<template>
<div ref="canvas" class="pdf-viewer" v-if="href !== undefined">
  <pdf v-for="i in numPages" :key="i" :src="href" :page="i" style="display: inline-block; width: 100%;"></pdf>
</div>
</template>

<script>
import _ from 'lodash'
import pdf from 'vue-pdf'

export default {
  props: {
    src: {
      type: String,
      required: true
    }
  },
  components: {
    pdf
  },
  data() {
    return {
      loading: false,
      numPages: undefined,
      href: undefined
    }
  },
  watch: {
    src: {
      immediate: true,
      handler(url) {
        if (url !== undefined) {
          this.loading = true
          this.href = url
          pdf.createLoadingTask(url)
            .then(pdf => {
              this.numPages = pdf.numPages
              this.$nextTick(() => {
                let canvas = this.$refs.canvas.getElementsByTagName('canvas')
                _.forEach(canvas, c => {
                  let ctx = c.getContext('2d')
                  this.$nextTick(() => {
                    ctx.fillStyle = '#757575'
                    ctx.fill()
                  })
                })
              })
            })
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.pdf-viewer {
  width: 100%;
  overflow-x: hidden;
  overflow-y: scroll;
  background-color: #757575;

  :global(span),
  :global(div) {
    background-color: transparent;
  }
}
</style>
