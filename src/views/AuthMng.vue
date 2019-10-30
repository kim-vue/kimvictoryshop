<template>
<div class="inner-box">
  <form @submit.prevent="buttonClickEventSearch()">
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
        <label class="control-label">회사</label>
        <div class="form-input">
          <select class="input" v-model="params.compCd">
            <option v-for="{ key, value } in options['COMP_CD']" :key="key" :value="key" v-text="value" />
          </select>
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
        </div>
      </div>
      <!-- Grid -->
      <dhx-grid ref="grid" v-model="data" :config="config" style="margin-bottom: 40px;" />
      <!-- //Grid -->
    </div>
  </div>
  <!-- //데이터 영역 -->
</div>
</template>

<script>
import Vue from 'vue'
import _ from 'lodash'
import assert from '@/libs/assert'
import DhxGrid from '@/components/DhxGrid.vue'
import GridSelect from '@/components/grid/GridSelect.vue'
import AuthMngMenu from '@/components/AuthMngMenu.vue'
import AuthMngUser from '@/components/AuthMngUser.vue'

const bus = new Vue()

const options = {
  'ROLE_SELECT_CD': []
}
const mutex = {
  'ROLE_SELECT_CD': false
}

function queryRoleSelectCd() {
  return new Promise((resolve, reject) => {
    if (mutex['ROLE_SELECT_CD'] && options['ROLE_SELECT_CD'].length > 0) {
      reject()
    } else {
      this.$store.commit('loading')
      this.$http.get('/api/code/combo', {
        params: {
          groupCd: 'ROLE_SELECT_CD'
        }
      }).then(response => {
        options['ROLE_SELECT_CD'] = response.data
        bus.$emit('OPTIONS.ROLE_SELECT_CD', options['ROLE_SELECT_CD'])
      }).finally(() => {
        this.$store.commit('finish')
      })
    }
  })
}

export default {
  components: {
    DhxGrid
  },
  data() {
    return {
      data: [],
      deleteList: [],
      memento: [],
      params: {
        compCd: undefined
      },
      options: {
        'COMP_CD': []
      },
      // Grid config
      config: {
        columns: [{
          value: 'No.',
          type: 'cntr',
          width: 50
        }, {
          id: 'roleCd',
          value: '권한코드',
          type: 'ed',
          align: 'left'
        }, {
          id: 'roleNm',
          value: '권한명',
          type: 'ed',
          align: 'left'
        }, {
          id: 'roleSelectCd',
          value: '조회권한',
          component: GridSelect,
          mixin: {
            data() {
              return {
                detailCd: 'key',
                detailNm: 'value'
              }
            },
            methods: {
              initializeRoleSelectCd() {
                this.options = options['ROLE_SELECT_CD']
                if (Array.isArray(this.options) && this.options.length > 0) {
                  let found = this.options.filter(x => x[this.detailCd] === this.data)[0]
                  if (found === undefined) {
                    this.data = this.options[0][this.detailCd]
                    this.value[this.field] = this.data
                    this.$emit('input', this.value)
                  }
                }
                return function() {}
              }
            },
            created() {
              this.initializeRoleSelectCd()
              bus.$on('OPTIONS.ROLE_SELECT_CD', () => {
                this.initializeRoleSelectCd()
              })
            }
          }
        }, {
          value: '권한별 메뉴',
          component: {
            template: `<div class="btn-wrapper" v-if="!value.new"><button type="button" class="btn btn-primary btn-block" @click="openModal()">선택</button></div>`,
            methods: {
              openModal() {
                this.$modal.open({
                  component: AuthMngMenu,
                  parent: this,
                  width: 800,
                  props: {
                    roleCd: this.value.roleCd,
                    compCd: this.value.compCd
                  }
                })
              }
            }
          }
        }, {
          value: '권한별 사용자',
          component: {
            template: `<div class="btn-wrapper" v-if="!value.new"><button type="button" class="btn btn-primary btn-block" @click="openModal()">선택</button></div>`,
            methods: {
              openModal() {
                this.$modal.open({
                  component: AuthMngUser,
                  parent: this,
                  width: 800,
                  props: {
                    roleCd: this.value.roleCd,
                    compCd: this.value.compCd
                  }
                })
              }
            }
          }
        }],
        height: '40vh',
        events: {
          onEditCell(stage, rId, cInd, nValue, oValue) {
            // 권한코드인 경우
            if (stage === 2 && cInd === 1) {
              if (nValue !== oValue) {
                this.value[rId - 1].roleCd = String(nValue || '').toUpperCase()
                this.setRowData(this.value)
                return false
              }
            }
            return true
          }
        },
        afterRefreshData(grid, data) {
          if (grid !== undefined && Array.isArray(data)) {
            this.$nextTick(() => {
              _.forEach(data, (row, index) => {
                let rId = grid.getRowId(index)
                this.unlockCell(rId, 1)
                this.setColumnClassName(rId, 1, 'bg-grey', true)
                this.setColumnClassName(rId, [1, 2], 'bg-lightpink', true)
                if (row.new) {
                  this.setColumnClassName(rId, [1, 2], 'bg-lightpink')
                } else {
                  this.lockCell(rId, 1)
                  this.setColumnClassName(rId, 1, 'bg-grey')
                  this.setColumnClassName(rId, 2, 'bg-lightpink')
                }
              })
            })
          }
        }
      }
    }
  },
  methods: {
    query() {
      this.$store.commit('loading')
      this.$http.get('/api/auth', {
        params: this.params
      }).then(response => {
        this.data = response.data
        this.deleteList = []
        this.memento = []
      }).finally(() => {
        this.$store.commit('finish')
      })
    },
    queryCompCd() {
      this.$store.commit('loading')
      this.$http.get('/api/code/combo', {
        params: {
          groupCd: 'COMP_CD'
        }
      }).then(response => {
        this.options['COMP_CD'] = response.data
      }).catch(response => {
        return response
      }).finally(() => {
        this.$store.commit('finish')
      })
    },
    save(callback) {
      try {
        // 권한코드 중복 체크
        let dupRoleCd = this.data.map(x => x.roleCd).filter((x, i, arr) => arr.indexOf(x) === i)
        assert.apply(this, [dupRoleCd.length === this.data.length, '중복된 권한코드는 허용되지 않습니다.'])

        // 빈 권한코드 체크
        let emptyRoleCd = this.data.filter(x => !x.roleCd)
        assert.apply(this, [(emptyRoleCd.length === 0), '권한코드는 빈 값일 수 없습니다.'])

        // 빈 권한명 체크
        let emptyRoleNm = this.data.filter(x => !x.roleNm)
        assert.apply(this, [(emptyRoleNm.length === 0), '권한명은 빈 값일 수 없습니다.'])

        // 삭제할 것이 있음
        if (this.deleteList.length > 0) {
          this.$store.commit('loading')
          let work = []
          _.forEach(this.deleteList, x => {
            work.push(this.$http.delete('/api/auth', {
              params: x
            }))
          })
          Promise.all(work)
            .then(response => {
              _proceed.apply(this, [callback])
            }).catch(response => {
              console.error('Failed to remove authority')
            })
        } else {
          _proceed.apply(this, [callback])
        }
      } catch (e) {
        this.$swal({
          type: 'error',
          text: e
        })
      }

      function _proceed(callback) {
        this.$store.commit('loading')
        this.$http.put('/api/auth', this.data)
          .then(response => {
            if (callback !== undefined && typeof callback === 'function') {
              callback.apply(this, [])
            } else {
              this.$swal({
                type: 'success',
                text: '저장되었습니다.'
              }).then(this.query)
            }
          }).finally(() => {
            this.$store.commit('finish')
          })
      }
    },
    buttonClickEventSearch() {
      this.query()
    },
    buttonClickEventSave() {
      if (this.memento.length === 1) {
        this.$swal({
          type: 'warning',
          text: '저장할 내용이 없습니다.'
        })
      } else {
        this.save()
      }
    },
    buttonClickEventAddRow() {
      this.data.push({
        new: true
      })
    },
    buttonClickEventRemoveRow() {
      // 삭제할 행을 찾는다
      let rowId = this.$refs.grid.instance.getSelectedRowId()
      // 선택된 행이 없음
      if (rowId === null) {
        this.$swal({
          type: 'error',
          text: '삭제할 행을 선택해주세요.'
        })
      } else {
        let i = this.$refs.grid.instance.getRowIndex(rowId)
        let row = this.data[i]
        if (!this.data[i].new) {
          this.deleteList.push({
            roleCd: this.data[i].roleCd,
            compCd: this.data[i].compCd
          })
        }
        this.data.splice(i, 1)
      }
    }
  },
  created() {
    try {
      this.queryCompCd()

      let compCd = this.$store.state.loginInfo.compCd
      this.params.compCd = compCd
    } catch (e) {
      // ERROR::Failed to get login info (Maybe login info is not exists)
    } finally {
      this.query()

      queryRoleSelectCd.apply(this, [])
    }
  },
  watch: {
    'data': {
      deep: true,
      handler(value) {
        let exists = this.memento.indexOf(JSON.stringify(value))
        // Has history?
        if (exists >= 0) {
          // fallback
          this.memento.splice(exists, this.memento.length - exists + 1)
        } else {
          this.memento.unshift(JSON.stringify(value))
        }
      }
    }
  }
}
</script>
