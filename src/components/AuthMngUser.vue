<template>
<div class="modal-card">
  <header class="modal-card-head pop-header">
    <p class="modal-card-title tit">
      권한별 사용자 내역
      <button class="btn-pop-close delete" aria-label="close" @click="$parent.close()"></button>
    </p>
  </header>
  <section class="modal-card-body pop-content">
    <div class="inner-box">
      <div class="content-name">
        <div class="btn-wrap btn-type1 clearfix" style="float: right; margin-top: -25px;">
          <button class="btn-size btn-blue fl_left" @click="buttonClickEventSave()">
            <span class="btn-icon"><i class="fas fa-save"></i></span>
            저장
          </button>
        </div>
      </div>

      <div class="table-area">
        <div class="table-b">
          <dhx-grid ref="grid" v-model="data" :config="config" @constructGridSuccessful="constructGridSuccessful" />
        </div>
      </div>
    </div>
  </section>
</div>
</template>

<script>
import DhxGrid from '@/components/DhxGrid.vue'
import GridCheckbox from '@/components/grid/GridCheckbox.vue'
export default {
  props: {
    'roleCd': {
      type: String,
      required: true
    },
    'compCd': {
      type: String,
      required: true
    }
  },
  components: {
    DhxGrid
  },
  data() {
    return {
      data: [],
      config: {
        columns: [{
          value: 'No.',
          type: 'cntr',
          width: 50
        }, {
          id: 'roleChk',
          value: '권한부여',
          width: 80,
          type: 'ch'
          // component: GridCheckbox,
          // mixin: {
          //   data() {
          //     return {
          //       trueValue: '1',
          //       falseValue: '0'
          //     }
          //   }
          // }
        }, {
          id: 'crtRole',
          value: '현재권한'
        }, {
          id: 'empNo',
          value: '사번',
        }, {
          id: 'empNm',
          value: '성명',
        }, {
          id: 'dutNm',
          value: '직급',
        }, {
          id: 'deptNm',
          value: '부서',
          align: 'left',
          width: 150
        }]
      }
    }
  },
  methods: {
    constructGridSuccessful(grid) {},
    query() {
      this.$store.commit('loading')
      this.$http.get('/api/auth/user', {
        params: {
          roleCd: this.roleCd,
          compCd: this.compCd
        }
      }).then(response => {
        this.data = response.data.map(x => {
          x.roleChk = x.roleChk === '1' ? true : false
          x.compCd = this.compCd
          return x
        })
      }).finally(() => {
        this.$store.commit('finish')
      })
    },
    buttonClickEventSave() {
      let data = _.cloneDeep(this.data).map(x => {
        delete x.children
        x.roleChk = x.roleChk ? '1' : '0'
        x.roleCd = this.roleCd
        x.compCd = this.compCd
        return x
      }).filter(x => x.roleChk === '1')
      this.$http.put(`/api/auth/user/${this.roleCd}/${this.compCd}`, data)
        .then(response => {
          this.$emit('close')
        }).catch(response => {
          console.error(response)
        })
    }
  },
  created() {
    this.query()
  }
}
</script>
