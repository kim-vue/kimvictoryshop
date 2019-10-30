export default (title) => {
  return function (...args) {
    if (this.debug) {
      console.log.apply(this, ['[' + this.$moment().format('YYYY-MM-DD HH:mm:ss.SSS') + ']', title].concat(args))
    }
  }
}
