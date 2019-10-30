<template>
<layout>
  <span slot="header">
    IO 조회
    <button class="btn-pop-close delete" aria-label="close" @click="$dismiss"></button>
  </span>
  <div slot="content">
    <div class="btn-type1">
      <button class="btn-size btn-gray" @click="goSearch(true)">
        <span class="btn-icon">
          <i class="fas fa-search"></i>
        </span>
        조회
      </button>
    </div>

    <div class="pop-content-search">
      <div class="field has-addons ">
        <div class="mr20 ">
          <span class="pop-c-name">- IO 코드/명</span>
        </div>
        <div class="control is-expanded">
          <input class="input" type="text" v-model="search" @keydown.enter="goSearch" />
        </div>
      </div>
    </div>

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
  props: ['param'],
  components: {
    Layout,
    DhxGrid
  },
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
          id: 'ioCd',
          type: 'ro',
          align: 'center',
          sort: 'str',
          value: 'IO코드'
        }, {
          id: 'ioNm',
          type: 'ro',
          align: 'center',
          sort: 'str',
          value: 'IO명칭'
        }, {
          id: 'cctrCd',
          type: 'ro',
          align: 'center',
          sort: 'str',
          value: '비용부서코드'
        }, {
          id: 'cctrNm',
          type: 'ro',
          align: 'left',
          sort: 'str',
          value: '비용부서'
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
    goSearch(slow) {
      this.$store.commit('loading')
      this.data = []
      this.$http.get(_url('/api/io', this.search))
        .then(response => {
          this.data = response.data
          if (!slow && this.data.length === 1)
            this.$emit('close', this.data[0])
          return response
        })
        .finally(() => {
          this.$store.commit('finish')
        })
    }
  },
  created() {
    this.search = this.param
  }
}

function _url(...args) {
  return args.map(x => String(x || '').trim().replace(/^\/*|\/*$/g, '')).filter(x => x).join('/')
}
</script>
