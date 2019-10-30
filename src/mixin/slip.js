import debug from '@/libs/debug'

const _debug = debug('slip')

/* eslint-disable */
export default {
    data() {
        return {};
    },
    methods: {
        changeRowId(grid) {
            if (grid) {
                const rowsNum = grid.getRowsNum();
                for (var i = 0; i < rowsNum; i++) {
                    grid.changeRowId(grid.getRowId(i), i + 1);
                    grid.cells2(i, 0).setValue(i);
                }
            }
        },
        toPure(v) {
            if (v == null || v == undefined) v = '0';
            return v.toString().replace(/[,-]/g, '');
        },
        setColumnHidden(grid, cInds, hide) {
            if (grid) {
                for (var i = 0; i < cInds.length; i++) {
                    grid.setColumnHidden(cInds[i], hide);
                }
            }
        },
        setDisabled(grid, rId, cInds, disabled) {
            if (grid) {
                for (var i = 0; i < cInds.length; i++) {
                    grid.cells(rId, cInds[i]).setDisabled(disabled);
                }
            }
        },
        setCellClassName(grid, rId, cInds, className, remove) {
            if (grid) {
                for (var i = 0; i < cInds.length; i++) {
                    let $cell = $(grid.cells(rId, cInds[i]).cell);
                    if (remove) {
                        $cell.removeClass(className);
                    } else {
                        $cell.addClass(className);
                    }
                }
            }
        },
        setDateFormat(grid, rId, cInds) {
            if (grid) {
                for (var i = 0; i < cInds.length; i++) {
                    let value = grid.cells(rId, cInds[i]).getValue();
                    if (value) grid.cells(rId, cInds[i]).setValue(this.$moment(value).format('YYYY-MM-DD'));
                }
            }
        },
        setTimeFormat(grid, rId, cInd) {
            if (grid) {
                let value = grid.cells(rId, cInd).getValue();
                if (value) grid.cells(rId, cInd).setValue(this.$moment(value, 'HHmmss').format('HH:mm:ss'));
            }
        },
        getFormattedCardNumber(cardNo) {
            let count = 0;
            return (cardNo.length === 16) ? _.reduce(cardNo, (no, c) => {
                if (no.replace(/-/gi, '').length % 4 === 0) {
                    count++;
                    return no + '-' + (count == 2 ? 'x' : c);
                } else {
                    return no + (count == 2 ? 'x' : c);
                }
            }) : cardNo;
        },
        getFormattedPureCardNumber(cardNo) {
            let count = 0;
            return (cardNo.length === 16) ? _.reduce(cardNo, (no, c) => {
                if (no.replace(/-/gi, '').length % 4 === 0) {
                    count++;
                    return no + '-' + c;
                } else {
                    return no + c;
                }
            }) : cardNo;
        },
        // grid: grid object
        // callback.credit: 미지급금 계정
        // callback.vat: 부가세 계정
        // callback.cost: 비용 계정
        // callback.all: 전체 처리
        doLineAction(grid, callback) {
            if (grid) {
                let hasCredit = (callback.credit != undefined) ? true : false;
                let hasVat = (callback.vat != undefined) ? true : false;
                let hasCost = (callback.cost != undefined) ? true : false;
                let hasAll = (callback.all != undefined) ? true : false;

                // console.log(hasCredit, hasVat, hasCost, hasAll)

                grid.forEachRow((rId) => {
                    let rowData = grid.getRowData(rId);
                    if (rowData.dcCd === 'C' && rowData.lnTypeCd === 'ITEM') {
                        if (hasCredit) callback.credit(grid, rId);
                    } else if (rowData.dcCd === 'D' && rowData.lnTypeCd === 'TAX') {
                        if (hasVat) callback.vat(grid, rId);
                    } else if (rowData.dcCd === 'D' && rowData.lnTypeCd === 'ITEM') {
                        if (hasCost) callback.cost(grid, rId);
                    }
                    if (hasAll) callback.all(grid, rId);
                });
                grid.callEvent('ongridreconstructed', []);
            }
        },
        setGridPaging(iljinGrid, data, options = { pageSize: 10, pageUnit: 10 }) {
            // const totalPages = parseInt(totalSize / options.pageSize) + (totalSize % options.pageSize > 0 ? 1 : 0);
            // console.log(totalSize, totalPages)
            const totalSize = data.length;
            const totalPages = Math.ceil(totalSize / options.pageSize) || 1
            var page = 1

            var fp = page - Math.ceil(options.pageUnit / 2) + 1
            fp = fp < 1 ? 1 : fp
            var ep = fp + options.pageUnit - 1
            ep = ep >= totalPages ? totalPages : ep
            ep === totalPages ? fp = ep - options.pageUnit + 1 : 0
            fp = fp < 1 ? 1 : fp

            var pageStartPoint = fp // 페이지 전시 시작 포인트
            var pageEndPoint = ep // 페이지 전시 종료 포인트

            _debug.apply(this, ['setGridPaging', totalSize, totalPages, fp, ep])

            const grid = iljinGrid
            grid.enablePaging(true, options.pageSize, options.pageUnit, 'pagingbox', true);
            grid._pgn_custom = (page, start, end) => {
              var htmls = [
                '<button class="btn-page page-first"></button>',
                '<button class="btn-page page-prev"></button>',
                '<button class="btn-page page-next"></button>',
                '<button class="btn-page page-last"></button>'
              ]
              var pages = [2, 0]
              for (var p = fp; p < ep + 1; p++) {
                pages.push(`<button class="page-num">${p}</button>`)
              }
              htmls.splice.apply(htmls, pages)
              grid._pgn_parentObj.innerHTML = htmls.join('')
              $(grid._pgn_parentObj).find('button').each((i, el) => {
                var $el = $(el)
                if ($el.hasClass('page-first')) {
                  $el.on('click', () => {
                    page = 1
                    grid.changePage(page)
                  })
                } else if ($el.hasClass('page-prev')) {
                  $el.on('click', () => {
                    page = page - 1 < 1 ? 1 : page - 1
                    grid.changePage(page)
                  })
                } else if ($el.hasClass('page-next')) {
                  $el.on('click', () => {
                    page = page + 1 > totalPages ? totalPages : page + 1
                    grid.changePage(page)
                  })
                } else if ($el.hasClass('page-last')) {
                  $el.on('click', () => {
                    page = totalPages
                    grid.changePage(page)
                  })
                } else {
                  var p = this.$numeral($el.text()).value()
                  if (page === p) {
                    $el.addClass('active')
                  } else {
                    $el.removeClass('active')
                  }
                  $el.on('click', () => {
                    page = p
                    grid.changePage(page)
                  })
                }
              })
            }
            grid.setPagingSkin('custom')
            this.$nextTick(() => {
              grid.changePage(1) // Goto first page
            })

            // /* paging */
            // iljinGrid._pgn_custom = function(page, start, end) {
            //     /* page - the current page
            //     start - the first visible row
            //     last - the last visible row */
            //     const itemCount = totalPages < options.pageUnit ? totalPages : options.pageUnit;
            //     var html = '<button class="btn-page page-first"></button><button class="btn-page page-prev"></button>';
            //     // for (var i = 0; i < itemCount; i++) {
            //     //     // html += '<button class="page-num active">1</button>'
            //     //     html += `<button class="page-num ${page==i+1?'active':''}">${i+1}</button>`
            //     // }
            //     html += `<span>Current page: ${page}</span>`
            //     html += '<button class="btn-page page-next"></button><button class="btn-page page-last"></button>';

            //     iljinGrid._pgn_parentObj.innerHTML = html;
            //     iljinGrid._pgn_parentObj.firstChild.onclick = function() { // the first button logic
            //         iljinGrid.changePage(1);
            //     }
            //     iljinGrid._pgn_parentObj.firstChild.nextSibling.onclick = function() { // the previous button logic
            //             iljinGrid.changePageRelative(-1);
            //         }
            //         //     // click event of page number
            //         // for (var i = 0; i < itemCount; i++) {
            //         //     iljinGrid._pgn_parentObj.childNodes[i + 2].onclick = function() {
            //         //         iljinGrid.changePage(this.innerText);
            //         //     }
            //         // }
            //     iljinGrid._pgn_parentObj.lastChild.previousSibling.onclick = function() { // the next button logic
            //         iljinGrid.changePageRelative(1);
            //     }
            //     iljinGrid._pgn_parentObj.lastChild.onclick = function() { // the last button logic
            //         iljinGrid.changePage(totalPages)
            //     }
            // }
            // iljinGrid.setPagingSkin('custom');
            // iljinGrid.setPagingSkin('toolbar');
        },
        downloadExcel(grid) {
            grid.toExcel("http://dhtmlxgrid.appspot.com/export/excel");
        },
    },
};
