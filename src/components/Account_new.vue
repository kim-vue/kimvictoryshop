<template>
<layout>
  <span slot="header">
    {{ title }} 조회
    <button class="btn-pop-close delete" aria-label="close" @click="$dismiss"></button>
  </span>
  <div slot="content">
    <form @submit.prevent="query()">
      <div class="btn-type1">
        <button type="submit" class="btn-size btn-gray">
          <span class="btn-icon"><i class="fas fa-search"></i></span>
          조회
        </button>
      </div>
      <div class="pop-content-search">
        <div class="field has-addons ">
          <div class="mr20 ">
            <span class="pop-c-name">- {{ title }} 코드/명</span>
          </div>
          <div class="control is-expanded">
            <input class="input" type="text" v-model="search" />
          </div>
        </div>
      </div>
    </form>

    <!-- DHX 그리드 영역 -->
    <dhx-grid class="gridbox" v-model="data" :config="config" />
    <!-- //DHX 그리드 영역 -->
  </div>
</layout>
</template>

<script>
import Layout from '@/components/ModalSlot.vue'
import DhxGrid from '@/components/DhxGrid.vue'

export default {
  props: {
    title: {
      type: String,
      required: false,
      default: '계정과목'
    },
    slipTypeCd: {
      type: String,
      required: false
    },
    searchStr: {
      type: String,
      required: false
    },
    queryFunction: {
      type: Function,
      required: false
    }
  },
  components: {
    Layout,
    DhxGrid
  },
  mixins: ['mixin'],
  data() {
    return {
      search: undefined,
      config: {
        columns: [{
          id: 'no',
          type: 'cntr',
          align: 'center',
          sort: 'int',
          value: 'No.'
        }, {
          id: 'acctCd',
          type: 'ro',
          align: 'center',
          sort: 'str',
          value: '계정코드'
        }, {
          id: 'acctNm',
          type: 'ro',
          align: 'left',
          sort: 'str',
          value: '계정명'
        }],
        events: {
          onRowDblClicked(rid) {
            var index = rid - 1
            var self = this.$parent.$parent
            self.$emit('close', self.data[index])
          }
        },
        height: 300
      },
      data: []
    }
  },
  methods: {
    $dismiss() {
      this.$emit('dismiss')
      this.$parent.close()
    },
    query(searchStr) {
      searchStr = searchStr || this.search
      this.$store.commit('loading')
      this.data = []
      return this.$http.get('/api/account', {
        params: {
          slipTypeCd: this.slipTypeCd,
          value: searchStr
        }
      }).then(response => {
        this.data = response.data
        return response
      }).finally(() => {
        this.$store.commit('finish')
      })
    }
  },
  created() {
    this.search = this.searchStr
    if (this.queryFunction !== undefined && typeof this.queryFunction === 'function') {
      this.query = () => {
        this.queryFunction.apply(this, [])
      }
    }

    if (this.search) {
      this.query()
    }
  }
}
</script>
