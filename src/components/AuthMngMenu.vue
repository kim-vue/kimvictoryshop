<template>
<div class="modal-card">
  <header class="modal-card-head pop-header">
    <p class="modal-card-title tit">
      권한별 메뉴 내역
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
          id: 'roleCk',
          value: '권한',
          width: 40,
          type: 'ch'
        }, {
          id: 'menuNm',
          value: '메뉴',
          align: 'left',
          width: 150,
          component: {
            template: `
              <div :style="style">
                <i :class="{ 'far fa-folder-open': hasChildren, 'far fa-file': !hasChildren }"></i>
                {{ title() }}
              </div>
            `,
            computed: {
              hasChildren() {
                return Array.isArray(this.value.children) && this.value.children.length > 0
              },
              style() {
                return {
                  'margin-left': this.value.menuLv * 15 + 'px'
                }
              }
            },
            methods: {
              title() {
                return this.value[this.field]
              }
            }
          }
        }, {
          id: 'menuDc',
          value: '메뉴설명',
          align: 'left',
          width: 200
        }],
        events: {
          onCheck(rId, cInd, state) {
            const row = this.value[this.instance.getRowIndex(rId)]
            const column = this.options.columns[cInd]

            if (column.id === 'roleCk') {
              row[column.id] = state
              _setChildren.apply(this, [row.children, state])
              _setParents.apply(this, [row, state])

              function _setChildren(array, state) {
                if (Array.isArray(array) && array.length > 0) {
                  for (var i = 0, node = array[i], size = array.length; i < size; node = array[++i]) {
                    node.roleCk = state
                    _setChildren.apply(this, [node.children, state])
                  }
                }
              }

              function _setParents(row, state) {
                if (!state) {
                  return
                } else {
                  let array = this.value.filter(x => x.menuNo === row.upperMenuNo)
                  if (Array.isArray(array) && array.length > 0) {
                    for (var i = 0, node = array[i], size = array.length; i < size; node = array[++i]) {
                      node.roleCk = state
                      _setParents.apply(this, [node, state])
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  methods: {
    constructGridSuccessful(grid) {},
    query() {
      this.$store.commit('loading')
      this.$http.get('/api/auth/menu', {
        params: {
          roleCd: this.roleCd,
          compCd: this.compCd
        }
      }).then(response => {
        let root = []
        root = response.data.map(x => {
          x.roleCk = x.roleCk === '1' ? true : false
          return x
        }).filter(x => response.data.findIndex(y => y.menuNo === x.upperMenuNo) < 0)

        _.forEach(response.data, node => {
          _constructTreeData(root, node)
        })

        this.data = response.data

        function _constructTreeData(root, node) {
          let rst = false
          for (let i = 0, r = root[i]; i < root.length; r = root[++i]) {
            if (r.menuNo === node.upperMenuNo) {
              r.children = r.children || []
              r.children.push(node)
              return true
            } else if (Array.isArray(r.children)) {
              if (_constructTreeData(r.children, node)) {
                return true
              }
            }
          }
          return rst
        }
      }).finally(() => {
        this.$store.commit('finish')
      })
    },
    buttonClickEventSave() {
      let data = _cloneDeep(this.data).map(x => {
        delete x.children
        x.roleCk = this.roleCk ? '1' : '0'
        x.roleCd = this.roleCd
        x.compCd = this.compCd
        return x
      }).filter(x => x.roleCk === '1')
      this.$http.put(`/api/auth/menu/${this.roleCd}/${this.compCd}`, data)
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
