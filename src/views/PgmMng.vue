<template>
<div class="inner-box">
  <form @submit.prevent="query()">
    <div class="content-name">
      <h2 class="dp-ib">권한관리</h2>
      <div class="btn-wrap btn-type1 clearfix">
        <button type="submit" class="btn-size btn-gray fl_left">
          <span class="btn-icon"><i class="fas fa-search"></i></span>
          조회
        </button>
        <button type="button" class="btn-size btn-blue fl_left" @click="buttonClickEventSave()">
          <span class="btn-icon"><i class="fas fa-save"></i></span>
          저장
        </button>
      </div>
    </div>

    <div class="search-form">
      <div class="form-group">
        <label class="control-label">메뉴명</label>
        <div class="form-input">
          <input type="text" class="input" v-model="params.menuNm" />
        </div>
      </div>
    </div>
  </form>

  <!-- 데이터 영역 -->
  <div class="table-area">
    <div class="table-b">
      <div class="table-header">
        <div class="table-name">
          <h3 class="ico_table_name">권한 내역</h3>
        </div>
        <div class="btn-wrap btn-type2 clearfix">
          <button class="btn-size btn-w-gray" @click="buttonClickEventAddRow()">
            <span class="btn-icon">
              <i class="fas fa-plus"></i>
            </span>
            행추가
          </button>
          <button class="btn-size btn-w-gray" @click="buttonClickEventRemoveRow()">
            <span class="btn-icon">
              <i class="fas fa-trash-alt"></i>
            </span>
            행삭제
          </button>
          <button class="btn-size btn-excel">
            엑셀 저장
          </button>
        </div>
      </div>
      <!-- Grid -->
      <dhx-grid ref="grid" v-model="data" :config="config" style="margin-bottom: 40px;" @setRowDataComplete="setRowDataComplete" />
      <!-- //Grid -->
    </div>
  </div>
  <!-- //데이터 영역 -->
</div>
</template>

<script>
import Vue from 'vue'
import assert from '@/libs/assert'
import debug from '@/libs/debug'
import DhxGrid from '@/components/DhxGrid.vue'

const bus = new Vue()
const _debug = debug('PgmMng')

function _constructTreeData(array) {
  array = array.map(x => {
    delete x.children
    x.menuLv = 1
    return x
  })
  // Get root elements
  let idMap = array.filter(x => x.menuNo).map(x => x.menuNo)
  let root = array.filter((x, i) => {
    return idMap.indexOf(x.upperMenuNo) < 0 || !x.upperMenuNo
  })
  _constructTreeData_slave(root, array, 1)
  return _resort(root)
}

function _constructTreeData_slave(root, array, menuLv) {
  menuLv = (menuLv || 1) + 1
  if (root === undefined || !Array.isArray(root) || root.length < 1) {
    return
  }
  let arr = array.filter(x => root.indexOf(x) < 0).map(x => {
    x.menuLv = menuLv
    return x
  })
  for (var i = 0, node = root[i]; i < root.length; node = root[++i]) {
    node.children = arr.filter(x => x.upperMenuNo === node.menuNo)
    _constructTreeData_slave(node.children, arr, menuLv)
  }
  return true
}

function _resort(array, result) {
  result = result || []
  array = array.sort((a, b) => a.menuOrder - b.menuOrder)
  if (Array.isArray(array) && array.length > 0) {
    for (var i = 0, node = array[i]; i < array.length; node = array[++i]) {
      result.push(node)
      result = _resort(node.children, result)
    }
  }
  return result
}

export default {
  components: {
    DhxGrid
  },
  data() {
    return {
      compCd: undefined,
      memento: [],
      deleteList: [],
      queue: [],
      data: [],
      params: {
        menuNm: undefined
      },
      // DhxGrid Config
      config: {
        columns: [{
          value: 'No.',
          type: 'cntr',
          width: 50
        }, {
          id: 'menuNo',
          value: '메뉴번호',
          type: 'ed',
          width: 150,
          align: 'left',
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
          id: 'upperMenuNo',
          value: '상위메뉴번호',
          align: 'left',
          type: 'ed'
        }, {
          id: 'menuNm',
          value: '메뉴명',
          align: 'left',
          type: 'ed'
        }, {
          id: 'programFileNm',
          value: '프로그램',
          align: 'left',
          type: 'ed'
        }, {
          id: 'menuOrder',
          value: '순번',
          width: 80,
          type: 'ed'
        }, {
          id: 'relateImageNm',
          value: '관련이미지',
          align: 'left',
          type: 'ed',
          width: 150
        }, {
          id: 'relateImagePath',
          value: '관련이미지경로',
          align: 'left',
          type: 'ed',
          width: 150
        }, {
          id: 'menuDc',
          value: '메뉴설명',
          align: 'left',
          type: 'ed',
          width: 150
        }],
        height: '50vh',
        events: {
          onEditCell(stage, rId, cInd, nValue, oValue) {
            let row = this.data[rId - 1]
            let colDef = this.options.columns[cInd]
            if (cInd === 1 && !row.new) {
              _debug.apply(this, ['onEditCell', 'cell is locked'])
              return false
            }
            // If changed
            else if (stage === 2 && nValue !== oValue) {
              if (cInd === 1 && String(nValue || '')) {
                let index = this.value.indexOf(row)
                if (index >= 0) {
                  let menuNumbers = this.value.filter((x, i) => i !== index).map(x => x.menuNo)
                  // Duplicate found
                  if (menuNumbers.indexOf(String(nValue)) >= 0) {
                    bus.$emit('ERROR.MENU_NO.DUPLICATE', 200)
                    bus.$emit('REQUEST.RECONSTRUCT_TREE')
                    return false
                  }
                }
              }
              row.chg = true
              bus.$emit('REQUEST.RECONSTRUCT_TREE')
            }
            return true
          }
        },
        afterRefreshData(grid, data) {
          if (grid !== undefined && Array.isArray(data)) {
            this.$nextTick(() => {
              for (var index = 0, row = data[index]; index < data.length; row = data[++index]) {
                let rId = grid.getRowId(index)
                this.setColumnClassName(rId, 1, 'bg-grey', true)
                this.setColumnClassName(rId, 1, 'bg-lightpink', true)
                if (row.new) {
                  this.setColumnClassName(rId, 1, 'bg-lightpink')
                } else {
                  this.setColumnClassName(rId, 1, 'bg-grey')
                }
              }
            })
          }
        }
      }
    }
  },
  methods: {
    query() {
      this.$store.commit('loading')
      return this.$http.post('/api/prg/list', this.params)
        .then(response => {
          if (Array.isArray(response.data)) {
            this.data = _constructTreeData(response.data)
          } else {
            this.data = []
          }
          this.memento = []
          this.deleteList = []
        }).finally(() => {
          this.$store.commit('finish')
        })
    },
    buttonClickEventSave() {
      try {
        _debug.apply(this, ['Memento', this.memento.length])
        if (this.memento.length <= 1) {
          throw {
            type: 'warning',
            text: '저장할 내용이 없습니다.'
          }
        }
        let data = this.data.filter(x => x.chg)

        let emptyMenuNo = data.filter(x => !x.menuNo)
        assert.apply(this, [emptyMenuNo.length === 0, '메뉴번호는 빈 값일 수 없습니다.'])

        data = data.map(x => {
          delete x.children
          x.compCd = this.compCd
          x.upperMenuNo = !x.upperMenuNo ? null : x.upperMenuNo
          return x
        })

        if (this.deleteList.length > 0) {
          let work = []
          _.forEach(this.deleteList, menuNo => {
            work.push(this.$http.delete('/api/prg', {
              params: {
                menuNo
              }
            }))
          })
          Promise.all(work)
            .then(() => {
              _proceed.apply(this, [data])
            })
        } else {
          _proceed.apply(this, [data])
        }
      } catch (e) {
        if (typeof e === 'object' && e.type && e.text) {
          this.$swal(e)
        } else {
          this.$swal({
            type: 'error',
            text: e
          })
        }
      }

      function _proceed(data) {
        this.$store.commit('loading')
        this.$http.post('/api/prg/save', data)
          .then(response => {
            this.$swal({
              type: 'success',
              text: '저장되었습니다.'
            }).then(this.query)
          }).finally(() => {
            this.$store.commit('finish')
          })
      }
    },
    buttonClickEventAddRow() {
      let rId = this.$refs.grid.instance.getSelectedRowId()
      let upperMenuNo = null
      if (rId !== null) {
        upperMenuNo = this.data[this.$refs.grid.instance.getRowIndex(rId)].menuNo
      }
      this.data.unshift({
        menuNo: null,
        upperMenuNo,
        menuNm: null,
        programFileNm: null,
        menuOrder: 0,
        relateImageNm: '/',
        relateImagePath: '/',
        menuDc: undefined,
        menuLv: 1,
        children: [],
        new: true
      })
      bus.$emit('REQUEST.RECONSTRUCT_TREE')
    },
    buttonClickEventRemoveRow() {
      let rowId = this.$refs.grid.instance.getSelectedRowId()
      if (rowId === null) {
        this.$swal({
          type: 'error',
          text: '삭제할 메뉴를 선택해주세요.'
        })
      } else {
        let rowIndex = this.$refs.grid.instance.getRowIndex(rowId)
        if (!this.data[rowIndex].new) {
          this.deleteList.push(this.data[rowIndex].menuNo)
        }
        // Delete children
        _deleteAll(this.data[rowIndex], this.data)
        bus.$emit('REQUEST.RECONSTRUCT_TREE')
      }

      function _deleteAll(root, array) {
        if (root !== undefined && Array.isArray(root.children) && root.children.length > 0 && Array.isArray(array)) {
          for (var i = 0, node = root.children[i]; i < root.children.length; node = root.children[++i]) {
            _deleteAll(node, array)
          }
        }
        array.splice(array.indexOf(root), 1)
      }
    },
    buttonClickEventExcelExport() {
      this.$refs.grid.instance.toExcel()
    },
    setRowDataComplete() {
      if (this.queue.length > 0) {
        let f = this.queue.shift()
        this.$nextTick(() => {
          if (f !== undefined && typeof f === 'function') {
            f.apply(this, [])
          }
        })
      }
    }
  },
  created() {
    try {
      this.compCd = this.$store.state.loginInfo.compCd
    } catch (e) {
      // DO NOTHING...may be there is no session to get
    } finally {
      this.query()
    }

    bus.$on('REQUEST.RECONSTRUCT_TREE', delay => {
      delay = delay || 100
      setTimeout(() => {
        this.data = _constructTreeData(this.data)
      }, delay)
    })

    bus.$on('ERROR.MENU_NO.DUPLICATE', delay => {
      delay = delay || 200
      setTimeout(() => {
        this.$swal({
          type: 'error',
          text: '메뉴번호는 중복될 수 없습니다.'
        })
      }, delay)
    })
  },
  watch: {
    'data': {
      deep: true,
      handler(value) {
        let c = _.cloneDeep(value)
        let v = JSON.stringify(c.map(x => {
          delete x.children
          delete x.menuLv
          delete x.chg
          return x
        }))
        var exists = this.memento.indexOf(v)
        // Has similar history
        if (exists >= 0) {
          // fall back to restore point
          this.memento.splice(0, exists)
        } else {
          this.memento.unshift(v)
        }
      }
    }
  }
}
</script>
