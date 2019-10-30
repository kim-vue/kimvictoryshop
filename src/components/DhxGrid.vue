<template>
<div class="grid-wrap">
  <!-- Grid div -->
  <div ref="grid" :id="gridId" class="grid-tbl-box"></div>
  <!-- //Grid div -->
  <!-- 아직 구현이 안됨...? -->
  <!-- Paging div -->
  <div ref="paging" :id="pageId" class="pagingbox" v-if="options.enablePaging"></div>
  <!-- //Paging div -->
</div>
</template>

<script>
/**
 * DhxGrid 공통 모듈
 *
 * @author jyyoon <jyyoon@skyware.co.kr>
 * @date   2019-07-15
 */
import Vue from 'vue'
import _ from 'lodash'
import $ from 'jquery'
// use uuid generator
import uuid from '@/libs/uuid'
import {
  setInterval
} from 'timers';
import debug from '@/libs/debug'

// 그리드 기본 옵션 설정
const defaultOptions = {
  // 그리드 컬럼 설정
  columns: [],
  // 이벤트 설정
  // *** 내부에 함수 목록을 구현한다. 자세한 내용은 dhtmlx의 그리드 이벤트 참조
  events: {},
  // 데이터 로딩 전 작업
  beforeRefreshData: undefined,
  // 데이터 로딩 후 작업
  afterRefreshData: undefined,
  /**************************************************************************/
  /** 그리드 설정 항목                                                     **/
  /** 계속 추가해 나가야함...                                              **/
  /**************************************************************************/
  editOnClick: true,
  editOnDoubleClick: true,
  editOnF2: true,
  // @see enableAutoWidth
  autoWidth: true,
  // @see enableAutoHeight
  autoHeight: false,
  // @see enableColSpan
  enableColSpan: false,
  // @see enableMultiselect
  enableMultiselect: false,
  enableBlockSelection: false,
  // enablePreRendering: 50,
  //// 그리드 설정 항목
  // 페이징 사용 여부
  enablePaging: false,
  // 페이지 당 행 수
  pagingSize: 50,
  // 보여줄 페이지 카운트
  pageCount: 10,
  enableVirtualPaging: true,
  /**
   * 페이징 핸들러
   * Spring JPA 의 Page 구조체를 상정하고 한다
   */
  pageHandler(response) {
    if (response !== undefined && response.data !== undefined && typeof response.data === 'object') {
      // 페이지 총 수를 가져온다
      this.totalPages = response.data.totalPages || 1
      // 행 수를 가져온다
      this.totalItems = response.data.totalElements || 0
      // 현재의 페이지...
      this.page = response.data.page || 0

      // Calculate page range
      var fp = this.page - Math.ceil(this.options.pageCount / 2) + 1
      fp = fp < 1 ? 1 : fp
      var ep = fp + this.options.pageCount - 1
      ep = ep >= this.totalPages ? this.totalPages : ep
      ep === this.totalPages ? fp = ep - this.options.pageCount + 1 : 0
      fp = fp < 1 ? 1 : fp

      this.pageStartPoint = fp // 페이지 전시 시작 포인트
      this.pageEndPoint = ep // 페이지 전시 종료 포인트

      if (this.instance !== undefined) {
        this.instance.changePage(this.page + 1)
      }
    }
    return response
  },
  // 페이지 업데이트 함수
  // *** 페이징 옵션 사용 시 필수 임!! 아니면 페이지가 넘어가지 않음!!!!!!
  // *** 그리고 queryPage는 반드시 Promise 형식이어야함
  queryPage() {
    return new Promise(resolve => {
      resolve()
    })
  }
}

const _debug = debug('DhxGrid')
let length = 0

export default {
  props: {
    value: {
      type: Array,
      required: true
    },
    config: {
      type: Object,
      required: false
    },
    gridName: {
      type: String,
      required: false
    }
  },
  data() {
    return {
      // 그리드 div ID
      gridId: undefined,
      data: [],
      // 그리드 인스턴스
      instance: undefined,
      // 그리드 옵션
      options: defaultOptions,
      // 현재 페이지...는 0부터 시작한다
      page: 0,
      // 전체 페이지 수...?
      totalPages: 1,
      // 총총총 전체 행 수
      totalItems: 0,
      queue: [],
      isLoading: false,
      componentMap: {},
      pageStartPoint: 1,
      pageEndPoint: 1,
      gridHeight: 0,
      gridHeight_old: 0,
      xhdrHeight: 0,
      xhdrHeight_old: 0,
      objboxHeight: 0,
      objboxHeight_old: 0,
      unwatchGridHeight: undefined,
      unwatchXhdrHeight: undefined,
      unwatchObjboxHeight: undefined,
      cellMap: {}
    }
  },
  computed: {
    pageId() {
      return this.gridId + '-page'
    }
  },
  /**************************************************************************/
  /** 구현된 함수 목록                                                     **/
  /**************************************************************************/
  methods: {
    /**
     * Construct grid object
     */
    construct() {
      // Generate uuid for grid div
      this.gridId = uuid()
      // Wait until view is rendered
      this.$nextTick(() => {
        // eslint-disable-next-line
        const grid = new dhtmlXGridObject(this.gridId)

        // Start setting grid base settings
        if (this.options.columns !== undefined && Array.isArray(this.options.columns)) {
          // Set headers
          grid.setHeader(this.options.columns.map(x => (x.value || '')).join(','))
          grid.setColumnIds(this.options.columns.map(x => (x.id || '')).join(','))
          grid.setInitWidths(this.options.columns.map(x => (x.width === undefined ? '120' : String(x.width))).join(','))
          grid.setColAlign(this.options.columns.map(x => (x.align || 'center')).join(','))
          grid.setColSorting(this.options.columns.map(x => (x.sort || 'na')).join(','))
          // Not working...
          // grid.setColumnsVisibility(this.options.columns.map(x => (x.hide ? 'false' : 'true')).join(','))
          _.forEach(this.options.columns, (item, index) => {
            item.hide ? grid.setColumnHidden(index, true) : 0
          })
          // column type is disabled!!
          // grid.setColTypes(Array(this.options.columns.length).fill('ro').join(','))
          grid.setColTypes(this.options.columns.map(x => (x.type || 'ro')).join(','))
        }

        const components = this.options.columns.map((x, i) => {
          x.index = i
          return x
        }).filter(x => x.component !== undefined)

        function createComponent(new_id) {
          this.$nextTick(() => {
            try {
              var row = this.instance.getRowById(new_id)
              if (row && row._locked) return
              var rowNum = this.instance.getRowIndex(new_id)
              _.forEach(components, c => {
                if (!this.isCellLocked(new_id, c.index)) {
                  var cell_id = [this.gridId.replace(/\W/g, ''), new_id, c.id].join('_')
                  var parent = document.createElement('div')
                  parent.setAttribute('class', 'dhx-component')

                  var div = document.createElement('div')
                  div.setAttribute('id', cell_id)

                  parent.appendChild(div)

                  this.$nextTick(() => {
                    try {
                      var $el = $(this.instance.cells(new_id, c.index).cell)
                      $el.empty()
                      $el.append(parent)

                      this.$nextTick(() => {
                        let mixins = [{
                          props: ['index', 'value', 'field', 'cInd', 'colDef']
                        }]
                        c.mixin ? mixins.push(c.mixin) : 0
                        var Component = Vue.extend(c.component)
                        this.componentMap[cell_id] = new Component({
                          propsData: {
                            index: rowNum,
                            value: this.data[rowNum],
                            field: c.id,
                            cInd: c.index,
                            colDef: this.options.columns[c.index]
                          },
                          parent: this,
                          mixins
                        }).$mount($('#' + cell_id).get(0))
                      })
                    } catch (e) {
                      // TODO::Error
                    }
                  })
                }
              })
            } catch (e) {
              // ...?
            }
          })
        }

        let prevObject = undefined
        let ec_rId = null
        let ec_cInd = null

        function _onEditCancel(rowId, colInd, value) {
          try {
            let index = this.instance.getRowIndex(rowId)
            this.instance.setRowData(rowId, this.data[index])
            ec_rId = null
            ec_cInd = null
          } catch (e) {
            // DO?
          }
        }

        function _onPageChanged(ind, fInd, lInd) {
          try {
            let s = this.page * this.options.pagingSize
            let e = (this.page + 1) * this.options.pagingSize


            for (var i = s; i < e; i++) {
              let rId = this.instance.getRowId(i)
              createComponent.apply(this, [rId])
            }
          } catch (e) {
            // Create components failed
          }
        }

        function _onEditCell(...args) {
          if (args[0] === 1) {
            ec_rId = args[1]
            ec_cInd = args[2]
          } else {
            ec_rId = null
            ec_cInd = null
          }

          return _onEditCell_f.apply(this, args)

          function _onEditCell_f(...args) {
            let stage = args[0]
            let rId = args[1]
            let cInd = args[2]
            let nValue = stage === 2 ? args[3] : undefined
            let oValue = stage === 2 ? args[4] : undefined
            let retry = stage === 2 ? args[5] : args[3]

            try {
              if (stage === 0 && this.isCellLocked(rId, cInd)) {
                return false
              }

              let prevState = undefined;
              let event = this.options.events['onEditCell']

              if (event !== undefined && typeof event === 'function') {
                prevState = event.apply(this, args)
              }

              // Previous state is return false
              if (prevState === false) {
                this.instance.setRowData(rId, row)
                return false
              }

              let colDef = this.options.columns[cInd]
              let cell = this.instance.cells(rId, cInd)
              let row = this.data[rId - 1]

              if (stage === 1) {
                // 컴포넌트가 있는 경우
                if (grid.editor && grid.editor.obj) {
                  if (colDef.component !== undefined && cell) {
                    prevObject = $(grid.editor.obj).val()
                    $(grid.editor.obj).val(row[colDef.id])
                  }
                  grid.editor.obj.select()
                }
              } else if (stage === 2) {
                if (nValue === oValue) {
                  this.instance.setRowData(rId, row)
                  return false
                }
                try {
                  row[colDef.id] = String(nValue)
                  if (typeof oValue === 'number' || colDef.type === 'edn') {
                    row[colDef.id] = this.$numeral(row[colDef.id]).value()
                  }
                  // this.setRowData(this.value)
                  this.instance.setRowData(rId, row)
                } catch (e) {
                  // ERROR OCCURRED
                }
              }
              return true
            } catch (e) {
              retry = retry || 0
              stage === 2 ? args[5] = retry + 1 : args[3] = retry + 1
              return retry < 3 ? _onEditCell_f.apply(this, args) : false
            }
          }
        }

        function _onKeyPress(code, ctrl, shift, events) {
          if ((code === 9 || code === 13) && !ctrl && !shift) {
            let rId = ec_rId
            let cInd = ec_cInd
            grid.editStop(false)

            // If tab pressed
            if (code === 9 && rId !== null && cInd !== null) {
              let editableColumns = this.options.columns.map((x, cInd) => {
                return {
                  cInd,
                  type: x.type || 'ro'
                }
              }).filter(x => {
                let args = [0, rId, x.cInd]
                // check is valid
                return x.cInd > cInd && String(x.type).match(/ed.*/g) && _onEditCell.apply(this, args)
              })

              // if editable columns left
              if (Array.isArray(editableColumns) && editableColumns.length > 0) {
                // delay 100ms
                setTimeout(() => {
                  let rowIndex = this.instance.getRowIndex(rId)
                  this.instance.selectCell(rowIndex, editableColumns[0].cInd)
                  this.instance.editCell()
                }, 100)
              } else {}
            }
          } else if (code === 27 && !ctrl && !shift) {
            grid.editStop(true)
          } else if (code === 67 && ctrl && (ec_rId === null && ec_cInd === null)) {
            if (this.options.enableBlockSelection) {
              if (!grid._selectionArea) {
                // 선택된 내용이 없음
                return this.$swal({
                  type: 'warning',
                  text: '복사할 영역이 선택되지 않았습니다.'
                })
              }
              grid.copyBlockToClipboard()
            } else {
              _copy.apply(this, [0])

              function _copy(rtry) {
                try {
                  let rid = grid.getSelectedRowId()
                  let cid = grid.getSelectedCellIndex()

                  _debug.apply(this, ['copy', 'start copy cell at', rid, cid])

                  // has selected cell
                  if (rid !== null && cid !== -1) {
                    let c = this.options.columns[cid]
                    let r = this.data[grid.getRowIndex(rid)]
                    if (c.id !== undefined && r[c.id] !== undefined) {
                      let body = document.body
                      let t = document.createElement('input')
                      body.appendChild(t)
                      t.setAttribute('type', 'text')
                      t.setAttribute('value', r[c.id] || '')
                      t.select()
                      document.execCommand('copy')
                      body.removeChild(t)
                    }
                  }
                } catch (e) {
                  rtry = rtry || 0
                  rtry < 3 ? _copy.apply(this, [rtry + 1]) : console.error(e)
                }
              }
            }
          } else if (code === 86 && ctrl) {
            // Paste?
          }
        }

        function _onCheck(rId, cInd, state) {
          try {
            let row = this.value[this.instance.getRowIndex(rId)]
            let colDef = this.options.columns[cInd]

            row[colDef.id] = state
          } catch (e) {
            // No retry
          }
        }

        let onEditCell = false
        let onKeyPress = false
        let onCellChanged = false
        let onCheck = false

        // Bind events
        if (this.options.events !== undefined && typeof this.options.events === 'object') {
          for (var event in this.options.events) {
            // Only attach event when is function
            if (this.options.events[event] !== undefined && typeof this.options.events[event] === 'function') {
              grid.attachEvent(event, (...args) => {
                /**
                 * onRowDblClicked override
                 */
                if (event === 'onRowDblClicked' || event === 'onRowSelect') {
                  let rId = args[0]
                  let cInd = args[1]
                  let index = grid.getRowIndex(rId)
                  // Change rId value...
                  args[0] = index + 1
                  // push row data
                  args.push(this.data[index])
                  return this.options.events[event].apply(this, args)
                } else if (event === 'onKeyPress') {
                  _onKeyPress.apply(this, args)
                } else if (event === 'onCellChanged') {
                  this.options.events[event].apply(this, args)
                  return grid.callEvent('onGridReconstructed', [])
                } else if (event === 'onCheck') {
                  onCheck = true
                  this.options.events[event].apply(this, args)
                }
                return this.options.events[event].apply(this, args)
              })
            }
          }
        }

        // Edit cell event
        /**
         * 리턴값이 없어서 에디트 기능이 원활하게 돌아가지 않고 있었음
         */
        if (!onEditCell) {
          grid.attachEvent('onEditCell', (...args) => {
            return _onEditCell.apply(this, args)
          })
        }

        grid.attachEvent('onEditCancel', (...args) => {
          _onEditCancel.apply(this, args)
        })

        if (!onKeyPress) {
          grid.attachEvent('onKeyPress', (...args) => {
            return _onKeyPress.apply(this, args)
          })
        }

        if (!onCellChanged) {
          grid.attachEvent('onCellChanged', (rId, cInd, nValue) => {
            grid.callEvent('onGridReconstructed', [])
          })
        }

        if (!onCheck) {
          grid.attachEvent('onCheck', (...args) => {
            _onCheck.apply(this, args)
          })
        }

        grid.attachEvent('onPageChanged', (...args) => {
          _onPageChanged.apply(this, args)
        })

        // Paging related...
        if (this.options.enablePaging) {
          grid.enablePaging(true, this.options.pagingSize, this.options.pageCount, this.pageId, true)
          grid._pgn_custom = (page, start, end) => {
            var htmls = [
              '<button class="btn-page page-first"></button>',
              '<button class="btn-page page-prev"></button>',
              '<button class="btn-page page-next"></button>',
              '<button class="btn-page page-last"></button>'
            ]
            var pages = [2, 0]
            for (var p = this.pageStartPoint; p < this.pageEndPoint + 1; p++) {
              pages.push(`<button class="page-num">${p}</button>`)
            }
            htmls.splice.apply(htmls, pages)
            grid._pgn_parentObj.innerHTML = htmls.join('')
            $(grid._pgn_parentObj).find('button').each((i, el) => {
              var $el = $(el)
              if ($el.hasClass('page-first')) {
                $el.on('click', this.firstPage)
              } else if ($el.hasClass('page-prev')) {
                $el.on('click', this.prevPage)
              } else if ($el.hasClass('page-next')) {
                $el.on('click', this.nextPage)
              } else if ($el.hasClass('page-last')) {
                $el.on('click', this.lastPage)
              } else {
                var page = this.$numeral($el.text()).value() - 1
                if (page === this.page) {
                  $el.addClass('active')
                } else {
                  $el.removeClass('active')
                }
                $el.on('click', () => {
                  this.goPage(page)
                })
              }
            })
          }
          grid.setPagingSkin('custom')
        }

        // 페이징 가상화
        if (this.options.enablePaging && this.options.enableVirtualPaging) {
          this.config.queryPage = this.options.queryPage = (...args) => {
            return new Promise(resolve => {
              this.data = this.calculateVirtualPaging(this.value)
              return resolve()
            })
          }
        } else if (this.options.enablePaging) {
          /**
           * queryPage가 선언된 경우?
           */
          if (this.options.queryPage !== undefined && typeof this.options.queryPage === 'function') {
            /**
             * Page Handler를 붙인다
             */
            var queryPage = this.options.queryPage
            this.config.queryPage = this.options.queryPage = (...args) => {
              return queryPage.apply(this.$parent, args)
                .then(response => {
                  return this.options.pageHandler.apply(this, [response])
                })
            }
          }
        }

        // Initialize grid
        grid.init()
        // Set grid properties
        grid.enableAutoWidth(this.options.autoWidth)
        // grid.enableAutoHeight(this.options.autoHeight)
        grid.enableAutoHeight(this.options.autoHeight)
        // Disable all grid native events
        grid.enableEditEvents(this.options.editOnClick, this.options.editOnDoubleClick, this.options.editOnF2)
        // @see enableColSpan
        grid.enableColSpan(this.options.enableColSpan)
        // @see enableMultiselect
        grid.enableMultiselect(this.options.enableMultiselect)
        // Map grid instance to component variable
        if (this.options.enableBlockSelection)
          grid.enableBlockSelection()
        grid.enableKeyboardSupport(true)
        grid.enablePreRendering(20)
        grid.enablePreRendering(true)
        this.instance = grid

        if (components.length > 0) {
          var addRow = this.instance.addRow
          this.instance.addRow = (new_id, text, ind) => {
            addRow.apply(this.instance, [new_id, text, ind])
            this.$nextTick(() => {
              createComponent.apply(this, [new_id])
            })
          }
          var setRowData = this.instance.setRowData
          this.instance.setRowData = (rid, data) => {
            setRowData.apply(grid, [rid, data])

            const row = this.instance.getRowById(rid)
            if (row && row._locked) return
            var i = 0
            const size = components.length
            for (; i < size; ++i) {
              this.$nextTick(() => {
                createComponent.apply(this, [rid])
              })
            }
          }

          // override lock
          var lockRow = this.instance.lockRow
          this.instance.lockRow = (rid, lock) => {
            lockRow.apply(grid, [rid, lock])
            this.$nextTick(() => {
              for (var i = 0, v = components[i]; i < components.length; v = components[++i]) {
                var cell_id = [this.gridId.replace(/\W/g, ''), rid, v.id].join('_')
                var cell = this.instance.cellById(rid, v.index).cell
                // Lock row
                if (lock) {
                  this.componentMap[cell_id] ? this.componentMap[cell_id].$destroy() : 0
                  this.componentMap[cell_id] = undefined
                  $(cell).empty()
                }
                // Unlock
                else {
                  createComponent.apply(this, [rid])
                }
              }
              for (var i = 0, v = this.data[i]; i < this.data.length; v = this.data[++i]) {
                this.instance.setRowData(i + 1, v)
              }
            })
          }
        }

        // 사이즈를 조정해봅시다...
        let $el = $(this.$refs.grid)
        let height = '300px'
        if (this.options.height !== undefined && (typeof this.options.height === 'number' || typeof this.options.height === 'string')) {
          height = typeof this.options.height === 'number' ? (this.options.height + 'px') : this.options.height
        } else {
          this.options.height = height
        }
        $el.css('height', height)
        grid.setSizes()
        this.$emit('constructGridSuccessful', this.instance)
      })
    },
    /**
     * Destory grid object
     */
    destroy() {
      this.$emit('purgeGrid')
      /**
       * if instance is allocated, then destory it
       */
      if (this.instance !== undefined) {
        this.instance.destructor()
      }
      // Set all variable to undefined => refreshing!
      this.gridId = undefined
      this.instance = undefined
      this.columnMap = []

      for (var member in this.componentMap) {
        try {
          this.componentMap[member].$destroy()
        } catch (e) {
          // 에러 나써영
        }
      }
      this.componentMap = {}
    },
    /**
     * Reconstruct grid object
     */
    reconstruct() {
      // Destroy grid object first
      this.destroy()
      // On view refreshed...
      this.$nextTick(() => {
        // construct grid!
        this.construct()
      })
    },
    /**************************************************************************/
    /** 페이징 관련 함수                                                     **/
    /**************************************************************************/
    /**
     * 첫번째 페이지로 이동
     */
    firstPage() {
      if (this.page === 0) return
      return this.goPage(0)
    },
    /**
     * 마지막 페이지로 이동
     */
    lastPage() {
      if (this.page === this.totalPages - 1) return
      return this.goPage(this.totalPages - 1)
    },
    /**
     * 다음 페이지로 이동
     */
    nextPage() {
      var page = this.page + 1
      if (page > this.totalPages - 1) return
      return this.goPage(page)
    },
    /**
     * 이전 페이지로 이동
     */
    prevPage() {
      var page = this.page - 1
      if (page < 0) return
      return this.goPage(page)
    },
    /**
     * 지정한 페이지로 이동
     */
    goPage(page) {
      // 입력된 값이 범위에 있는지 확인한다
      if (page < 0 || page > this.totalPages - 1) {
        // 아니면...첫페이지로...
        page = 0
      }
      // 페이지 갱신 함수는 과연 Promise 형식인가...
      if (this.options.queryPage !== undefined) {
        // 현재 페이지 값을 업데이트 한다
        this.page = page
        this.options.queryPage.apply(this, [page])
      }
    },
    //// 페이징 관련 함수
    /**
     * 그리드 인스턴스를 받아온다
     */
    getInstance() {
      return this.instance
    },
    // 데이터 갱신
    setRowData(...args) {
      try {
        const vm = this
        const savedScrollPosition = $(this.$refs.grid).find('.objbox').scrollTop() || 0
        const data = args[0] || this.value
        const full = args[1] || false

        _debug.apply(this, ['setRowData', 'Start set row data, do full', !full])

        this.componentMap = {}
        this.cellMap = {}
        var i = 0
        const dataLength = data.length || 0

        const st_r = (new Date()).valueOf()

        this.instance.clearAll()
        this.instance.startFastOperations()
        // Fast looping
        for (; i < dataLength; ++i) {
          const id = String(i + 1)
          this.cellMap[id] = this.options.columns.map(x => {
            return {
              lock: false,
              colDef: x
            }
          })
          const row = this.options.columns.map(x => data[i][x.id])
          this.instance.addRow(id, row)
        }
        this.instance.stopFastOperations()

        _debug.apply(this, ['setRowData', 'setRowDatas complete', (new Date()).valueOf() - st_r, 'ms'])

        this.$nextTick(() => {
          // Run after row set event
          if (this.options.afterRefreshData !== undefined && typeof this.options.afterRefreshData === 'function') {
            setTimeout(() => {
              this.options.afterRefreshData.apply(this, [this.instance, data])
            }, 100)
          }

          // fix grid size
          $(this.$refs.grid).height(this.options.height)
          this.instance.setSizes()
          // if have previous scroll position then go
          $(this.$refs.grid).find('.objbox').scrollTop(savedScrollPosition)

          if (this.options.enablePaging) {
            this.goPage(this.page)
          }

          this.instance.callEvent('onGridReconstructed', [])
          this.$emit('setRowDataComplete')
        })
      } catch (e) {
        this.componentMap = {}
        this.cellMap = {}
      }
    },
    setColumnClassName(rId, cIns, className, remove) {
      if (this.instance !== undefined && cIns !== undefined) {
        if (Array.isArray(cIns)) {
          this.$nextTick(() => {
            var i = 0;
            const size = cIns.length
            for (; i < size; ++i) {
              try {
                var $el = $(this.instance.cells(rId, cIns[i]).cell)
                remove ? $el.removeClass(className) : $el.addClass(className)
              } catch (e) {

              }
            }
          })
        } else if (typeof cIns === 'number') {
          this.$nextTick(() => {
            try {
              var $el = $(this.instance.cells(rId, cIns).cell)
              remove ? $el.removeClass(className) : $el.addClass(className)
            } catch (e) {

            }
          })
        }
      }
    },
    // lock cell
    toggleCell(rId, cInd, status) {
      try {
        this.cellMap[rId][cInd].lock = status
      } catch (e) {
        // TODO::Nothing
      }
    },
    isCellLocked(rId, cInd) {
      return this.cellMap[rId][cInd].lock
    },
    lockCell(rId, cInd) {
      this.toggleCell(rId, cInd, true)
    },
    lockCells(rId, cInds) {
      _.forEach(cInds, cInd => {
        this.lockCell(rId, cInd)
      })
    },
    lockAllCells(rId) {
      try {
        this.cellMap[rId] = this.cellMap[rId].map(x => {
          x.lock = true
          return x
        })
      } catch (e) {

      }
    },
    unlockCell(rId, cInd) {
      this.toggleCell(rId, cInd, false)
    },
    unlockCells(rId, cInds) {
      _.forEach(cInds, cInd => {
        this.unlockCell(rId, cInd)
      })
    },
    unlockAllCells(rId) {
      try {
        this.cellMap[rId] = this.cellMap[rId].map(x => {
          x.lock = false
          return x
        })
      } catch (e) {
        // TODO::Nothing...
      }
    },
    toExcel() {
      if (this.instance !== undefined && typeof this.instance.toExcel === 'function') {
        this.instance.toExcel('http://dhtmlxgrid.appspot.com/export/excel')
      }
    },
    /**
     * Calculate paging area
     */
    calculateVirtualPaging(value) {
      // If value is array
      if (Array.isArray(value) && this.options) {
        let s = this.page * this.options.pagingSize
        let e = (this.page + 1) * this.options.pagingSize

        this.totalPages = Math.ceil(value.length / this.options.pagingSize) || 1
        this.totalItems = value.length

        var fp = this.page - Math.ceil(this.options.pageCount / 2) + 1
        fp = fp < 1 ? 1 : fp
        var ep = fp + this.options.pageCount - 1
        ep = ep >= this.totalPages ? this.totalPages : ep
        ep === this.totalPages ? fp = ep - this.options.pageCount + 1 : 0
        fp = fp < 1 ? 1 : fp

        this.pageStartPoint = fp // 페이지 전시 시작 포인트
        this.pageEndPoint = ep // 페이지 전시 종료 포인트

        if (this.instance !== undefined) {
          this.instance.changePage(this.page + 1)
        }

        this.data = value.slice(s, e)
        return this.data
      } else {
        return value
      }
    }
  },
  watch: {
    /**
     * 아아...이것은 모래
     * 이것은 함수
     * 이것은 watcher...
     * 그리드를 다시 만든다
     */
    'config': {
      immediate: true,
      handler(value) {
        // Extends options
        this.options = _.clone(defaultOptions)
        for (var member in value) {
          this.options[member] = value[member]
        }
        // Reconstruct
        this.reconstruct()
      }
    },
    /**
     * 그리드가 변경되었을 경우
     */
    'instance': {
      handler(value) {
        if (value !== undefined) {
          this.setRowData(this.value)
        }
      }
    },
    /**
     * v-model로 바인딩 되어있는 값 갱신 Watcher
     */
    'value': {
      immediate: true,
      deep: true,
      handler(value, old) {
        const o_l = length
        const n_l = Array.isArray(value) ? value.length : 0
        const full = (old === undefined || value !== old || o_l !== n_l)
        if (this.options && this.options.enablePaging && this.options.enableVirtualPaging) {
          this.data = this.calculateVirtualPaging(value)
        } else {
          this.data = value
        }
        this.setRowData(value, !full)
        length = n_l
      }
    }
  },
  beforeDestroy() {
    // Destroy grid instance before component destoried
    this.destroy()

    if (typeof this.unwatchGridHeight === 'function') {
      this.unwatchGridHeight()
    }

    if (typeof this.unwatchXhdrHeight === 'function') {
      this.unwatchXhdrHeight()
    }

    if (typeof this.unwatchObjboxHeight === 'function') {
      this.unwatchObjboxHeight()
    }
  }
}
</script>
<!-- DHX 그리드 추가 스타일 -->

<style lang="scss" scoped>
.gridbox {
    background-color: #f3f5f9;
    :global(.objbox) {
        overflow-y: scroll !important;
        padding-right: 1px;
    }

    :global(.xhdr) {
        width: calc(100% - 17px) !important;
        border-right: 1px solid #dfdfdf;
        padding: 0;
        max-height: 100% !important;
    }

    :global(table tr td[align="left"]) {
        text-align: left !important;
        padding-left: 10px !important;
        :global(.dhx-component) {
            margin-left: -10px;
        }
    }

    :global(table tr td[align="right"]) {
        text-align: right !important;
        padding-right: 10px !important;
        :global(.dhx-component) {
            margin-right: -10px;
        }
    }

    :global(table tr td) {
        border: 1px solid #ededed !important;
    }

    :global(table tr td[align="center"]) {
        text-align: center !important;
    }

    :global(table tr td[excell="ch"] img[src="/dhtmlx/imgs/dhxgrid_material/item_chk0.gif"]) {
        content: url("/img/check_off.png");
    }

    :global(table tr td[excell="ch"] img[src="/dhtmlx/imgs/dhxgrid_material/item_chk1.gif"]) {
        content: url("/img/check_on.png");
    }

    :global(table tr td[excell="ch"] img:hover) {
        cursor: pointer;
    }

    :global(table) {
        border-collapse: collapse;
        margin: 0 !important;
        border: none;
    }

    :global(td[excell]) {
        position: relative;
        :global(img) {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
        }
    }

    :global(.objbox table tr td .align-right) {
        text-align: right !important;
    }

    :global(.objbox table tr td .align-right *) {
        text-align: right !important;
    }

    :global(.objbox table tr td .align-right span) {
        display: block;
        padding-right: 10px;
    }

    :global(.objbox table tr td .icon) {
        margin: 6px 0;
    }

    :global(.objbox table tr td .dhx-component) {
        display: block;
        height: 100%;
        padding: 1px;
    }

    :global(.objbox table tr td .dhx-component .input) {
        width: 100%;
        border-radius: 0;
        height: 34px;
        border: 0;
        display: block;
        padding: 5px 9px;
        margin: 0;
        background-color: transparent;
    }

    :global(.objbox table tr td .dhx-component .input:focus) {
        box-shadow: none;
    }

    :global(.objbox table tr td .dhx-component .number) {
        text-align: right !important;
    }

    :global(.dhx-component .btn-wrapper) {
        position: relative;
        height: 100%;
        margin: 0 10px;
        :global(.btn) {
            background: #646464;
            color: #fff;
            padding: 5px 15px;
            border-radius: 3px;
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            font-family: 'NotoM';
        }

        :global(.btn.btn-default) {
            background: #646464;
            color: #fff;
        }

        :global(.btn.btn-primary) {
            background: #4f9de1;
            color: #fff;
        }

        :global(.btn.btn-danger) {
            background: #f04c2b;
            color: #fff;
        }

        :global(.btn.btn-block) {
            width: 100%;
        }
    }
}
</style>
