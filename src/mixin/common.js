import { url as _url } from '@/libs/join'

export default {
  methods: {
    findEmp(searchStr, callback, failed) {
      if (!searchStr) {
        callback.apply(this, [{}])
      } else {
        this.$http.get(_url('/api/emp', searchStr))
          .then(response => {
            let data = response.data
            if (Array.isArray(data) && data.length > 0 && typeof callback === 'function') {
              callback.apply(this, data)
            } else {
              failed.apply(this, [])
            }
          }).catch(() => {
            failed.apply(this, [])
          })
      }
    },
    findAccount(slipTypeCd, searchStr, callback, failed) {
      if (!searchStr) {
        callback.apply(this, [{}])
      } else {
        this.$http.get('/api/account', {
          params: {
            slipTypeCd: slipTypeCd,
            value: searchStr
          }
        }).then(response => {
          let data = response.data
          if (Array.isArray(data) && data.length > 0 && typeof callback === 'function') {
            callback.apply(this, data)
          } else {
            failed.apply(this, [])
          }
        }).catch(() => {
          failed.apply(this, [])
        })
      }
    },
    findCctr(searchStr, callback, failed) {
      if (!searchStr) {
        callback.apply(this, [{}])
      } else {
        this.$http.get(_url('/api/cctr', searchStr))
          .then(response => {
            let data = response.data
            if (Array.isArray(data) && data.length > 0 && typeof callback === 'function') {
              callback.apply(this, data)
            } else {
              failed.apply(this, [])
            }
          }).catch(() => {
            failed.apply(this, [])
          })
      }
    },
    findVendor(slipTypeCd, searchStr, callback, failed) {
      if (!searchStr) {
        callback.apply(this, [{}])
      } else {
        this.$http.get(_url('/api/vendor', slipTypeCd, searchStr))
          .then(response => {
            let data = response.data
            if (Array.isArray(data) && data.length > 0 && typeof callback === 'function') {
              callback.apply(this, data)
            } else {
              failed.apply(this, [])
            }
          }).catch(() => {
            failed.apply(this, [])
          })
      }
    }
  }
}