<template>
<div>
  <!-- 전표정보 -->
  <div class="table-area">
    <div class="table-a fixed-th">
      <div class="table-name">
        <h3 class="ico_table_name">전표정보</h3>
      </div>
      <table class="table" v-if="isNew">
        <tbody>
          <tr>
            <th style="width: 15%;">전표유형</th>
            <td style="width: 35%;"></td>

            <th style="width: 15%;">통화</th>
            <td style="width: 35%;"></td>
          </tr>
        </tbody>
      </table>
      <table class="table" v-else>
        <tbody>
          <tr>
            <th style="width: 10.33%;">그룹전표번호</th>
            <td style="width: 13%;"></td>

            <th style="width: 10.33%;">전표유형</th>
            <td style="width: 13%;"></td>

            <th style="width: 10.33%;">통화</th>
            <td style="width: 13%;"></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <!-- //전표정보 -->
  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">그룹결재 내역</h3>
        </div>
      </div>
      <!-- Grid -->
      <dhx-grid v-model="data_gr" :config="config_gr" @constructGridSuccessful="constructGridSuccessful_gr" />
      <!-- //Grid -->
    </div>
  </div>
</div>
</template>

<script>
export default {
  props: {
    grSlipNo: {
      type: String,
      required: false
    },
    value: {
      type: Object,
      required: true,
      default() {
        return {

        }
      }
    }
  },
  data() {
    return {
      data: [],
      config: {}
    }
  },
  computed: {
    isNew() {
      return this.grSlipNo === undefined
    }
  }
}
</script>
