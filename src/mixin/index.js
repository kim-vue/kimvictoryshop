/* eslint-disable */
import { DateTime } from 'luxon';
import { closestIndexTo } from 'date-fns';

export default {
    data() {
        return {
            gData: {},
        };
    },
    methods: {
        downloadFile(url) {
            this.$store.commit('loading');
            this.$http
                .get(url, { responseType: 'blob' })
                .then((response) => {
                    const downloadedfile = new Blob([response.data], { type: 'blob' });
                    let url;

                    const contentDisposition = response.headers['content-disposition'];
                    let fileName = 'unknown';
                    if (contentDisposition) {
                        const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
                        if (fileNameMatch.length === 2)
                            fileName = fileNameMatch[1];
                    }

                    if (window.navigator.msSaveOrOpenBlob) {
                        window.navigator.msSaveOrOpenBlob(downloadedfile, fileName);
                    } else {
                        url = window.URL.createObjectURL(downloadedfile);

                        const link = document.createElement('a');
                        link.href = url;
                        link.setAttribute('download', fileName);
                        document.body.appendChild(link);
                        link.click();
                    }

                    this.$store.commit('finish');
                });
        },
        toLocaleString(time) {
            if (time !== null && typeof time !== 'undefined') {
                return DateTime.fromISO(time)
                    .toLocaleString(DateTime.DATETIME_SHORT_WITH_SECONDS);
            }
            return null;
        },
        toLocaleShortString(time) {
            if (time !== null && typeof time !== 'undefined') {
                return DateTime.fromISO(time)
                    .toLocaleString(DateTime.DATE_SHORT);
            }
            return null;
        },
        loadData(url) {
            this.$http
                .get(url);
        },
        save(url, dtoObj, successMsg, failMsg) {
            if (typeof successMsg === 'undefined') successMsg = '저장했습니다.';
            if (typeof failMsg === 'undefined') failMsg = '저장 실패했습니다';

            this.$http
                .post(url, dtoObj)
                .then(() => {
                    this.$swal({
                        animation: false,
                        type: 'success',
                        text: successMsg,
                    });
                })
                .catch((ex) => {
                    this.$swal({
                        animation: false,
                        type: 'error',
                        text: failMsg,
                    });
                    console.error(ex);
                })
        },
        adjustGridColumns(grid) {
            const cols = grid.getColumnsNum();
            let cnt = 0;
            for (let i = 0; i < cols; i++) {
                if (grid.isColumnHidden(i)) cnt = cnt + 1;
            }

            const visibleCols = cols - cnt;

            const strArr = [];
            let ratio = Math.round(100 / visibleCols);
            let sum = 0;
            for (let i = 0; i < cols; i++) {
                if (i === cols - 1) { // 마지막일 때
                    if (!grid.isColumnHidden(i)) {
                        strArr.push(`${100-sum}`);
                        sum += ratio;
                    } else strArr.push('0');
                } else {
                    if (!grid.isColumnHidden(i)) {
                        if (grid.getColType(i) === 'ch') {
                            strArr.push('5');
                            sum += 5;
                        } else {
                            strArr.push(`${ratio}`);
                            sum += ratio;
                        }
                    } else strArr.push('0');
                }
            }
            if (sum !== 100) {
                strArr[strArr.lastIndexOf()] = 100 - sum + strArr[strArr.lastIndexOf()];
            }

            grid.setInitWidthsP(strArr.toString());
        },
    },
};