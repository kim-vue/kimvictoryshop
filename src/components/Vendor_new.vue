<template>
<layout>
  <span slot="header">
    {{ title }} 조회
    <button class="btn-pop-close delete" aria-label="close" @click="$dismiss"></button>
  </span>
  <div slot="content">
    <div class="btn-type1">
      <button class="btn-size btn-gray" @click="query">
        <span class="btn-icon"><i class="fas fa-search"></i></span> 조회
      </button>
    </div>

    <!-- 검색영역 -->
    <div class="pop-content-search">
      <div class="field has-addons ">
        <div class="mr20 ">
          <span class="pop-c-name">- {{ title }} 코드/명/사업자번호</span>
        </div>
        <div class="control is-expanded">
          <input class="input" type="text" v-model="search" @keypress.enter="goSearch" />
        </div>
      </div>
    </div>
    <!-- //검색영역 -->

    <!-- DHX 그리드 영역 -->
    <dhx-grid class="gridbox" v-model="data" :config="config" />
    <!-- //DHX 그리드 영역 -->
  </div>
</layout>
</template>

<script>
import { url as _url } from '@/libs/join'

import Layout from '@/components/ModalSlot.vue'
import DhxGrid from '@/components/DhxGrid.vue'

export default {
  props: {
    slipTypeCd: {
      type: String,
      required: true
    },
    searchStr: {
      type: String,
      required: false
    },
    title: {
      type: String,
      required: false,
      default: '거래처'
    }
  },
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
          value: 'No.',
        }, {
          id: 'vendGrNm',
          type: 'ro',
          align: 'center',
          sort: 'str',
          value: '거래처그룹'
        }, {
          id: 'vendCd',
          type: 'ro',
          align: 'center',
          sort: 'str',
          value: '거래처코드'
        }, {
          id: 'vendNm',
          type: 'ro',
          align: 'left',
          sort: 'str',
          value: '거래처명'
        }, {
          id: 'bizNo',
          type: 'ro',
          align: 'center',
          sort: 'str',
          value: '사업자등록번호'
        }],
        events: {
          onRowDblClicked(rid) {
            var index = rid - 1
            var vm = this.$parent.$parent
            vm.$emit('close', vm.data[index])
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
    query() {
      this.$store.commit('loading')
      this.data = []
      this.$http.get(_url('/api/vendor', this.slipTypeCd, this.search))
        .then(response => {
          this.data = response.data
          if (!slow && this.data.length === 1)
            this.$emit('close', this.data[0])
          return response
        })
        .catch(response => {
          return response
        })
        .finally(() => {
          this.$store.commit('finish')
        })
    }
  },
  created() {
    this.search = this.searchStr
    if (this.search) {
      this.query()
    }
  }
}
</script>
