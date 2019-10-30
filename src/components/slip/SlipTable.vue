<template>
  <div class="table-area">
    <div class="table-a fixed-th">
      <div class="table-name">
        <h3 class="ico_table_name">기본정보</h3>
      </div>
      <component :is="tableId" v-model="value" :status="status" />
    </div>
  </div>
</template>

<script>
import TableE1 from '@/components/slip/E1/TableRO.vue'
import TableE2 from '@/components/slip/E2/TableRO.vue'
import TableE3 from '@/components/slip/E3/TableRO.vue'
// E4 - 기타증빙
import TableE4 from '@/components/slip/table/TableE4.vue'
// E6 - 교통비
import TableE6 from '@/components/slip/table/TableE6.vue'

export default {
  props: ['slipType', 'value', 'status'],
  components: {
    TableE1,
    TableE2,
    TableE3,
    TableE4,
    TableE6
  },
  data() {
    return {
      options: {}
    }
  },
  computed: {
    tableId() {
      return 'Table' + this.slipType
    }
  }
}
</script>
