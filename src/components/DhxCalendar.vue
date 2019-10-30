<template>
<input ref="ibox" :id="calendarId" v-model="date" @blur="apply()" @keypress.enter="apply()" :disabled="disabled" />
</template>

<script>
import uuid from '@/libs/uuid'

const defaultOptions = {
  hideTime: true,
  format: 'YYYY-MM-DD',
  outputFormat: 'YYYYMMDD',
  dateFormat: '%Y-%m-%d'
}

export default {
  replace: true,
  props: ['value', 'config', 'disabled'],
  data() {
    return {
      date: undefined,
      calendarId: undefined,
      instance: undefined,
      options: {
        hideTime: true,
        format: 'YYYY-MM-DD',
        outputFormat: 'YYYYMMDD',
        dateFormat: '%Y-%m-%d'
      }
    }
  },
  methods: {
    construct() {
      this.destroy()
      // Copy options
      this.cloneOptions()

      this.$nextTick(() => {
        this.calendarId = uuid()

        this.$nextTick(() => {
          var $el = $(this.$refs.ibox)

          // eslint-disable-next-line
          const c = new dhtmlXCalendarObject(this.calendarId)

          var date = this.$moment(this.value, this.options.outputFormat)
          if (!date.isValid()) {
            date = this.$moment()
          }

          c.setDateFormat(this.options.dateFormat)
          c.setDate(date.toDate())

          if (this.options.hideTime) {
            c.hideTime()
          }

          // c.attachEvent('onClick', d => {
          //   var date = this.$moment(d, this.options.format)
          //   if (date.isValid()) {
          //     this.date = date.format(this.options.format)
          //     this.$emit('input', date.format(this.options.outputFormat))
          //   }
          // })

          c.attachEvent('onChange', d => {
            let date = this.$moment(d)
            if (date.isValid()) {
              this.date = date.format(this.options.format)
              this.$emit('input', date.format(this.options.outputFormat))
            }
          })

          this.instance = c
        })
      })
    },
    apply() {
      if (this.date) {
        let dateStr = String(this.date || '').replace(/\D/g, '')
        let formats = [this.options.format, this.options.outputFormat, 'YYYY', 'YMD', 'YYYYMD']
        let date = this.$moment(dateStr, formats)
        if (date !== undefined && date.isValid()) {
          this.date = date.format(this.options.format)
          this.$emit('input', date.format(this.options.outputFormat))
        } else {
          this.date = undefined
          this.$emit('input', undefined)
        }
      } else {
        this.$emit('input', undefined)
      }
    },
    cloneOptions() {
      this.options = _.clone(defaultOptions)
      for (var member in this.config || {}) {
        this.options[member] = this.config[member]
      }
    },
    destroy() {
      if (this.instance !== undefined) {
        this.instance.unload()
      }
      this.instance = undefined
      this.calendarId = undefined
    }
  },
  created() {
    this.construct()
  },
  beforeDestroy() {
    this.destroy()
  },
  watch: {
    'config': {
      handler(value) {
        if (value !== undefined && typeof value === 'object') {
          this.construct()
        }
      }
    },
    'value': {
      immediate: true,
      handler(value) {
        var dt = this.$moment(value, this.options.outputFormat)
        if (value !== undefined && dt.isValid()) {
          this.date = dt.format(this.options.format)
        } else {
          this.date = undefined
        }
      }
    }
  }
}
</script>
