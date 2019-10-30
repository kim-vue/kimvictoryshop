<template>
<layout>
  <span slot="header">
    {{ title }}
    <button class="btn-pop-close delete" aria-label="close" @click="$emit('close', a_files)"></button>
  </span>
  <div slot="content">
    <div class="scan-area">
      <div class="scan-item01">
        <div class="scan-name">
          <span><img src="/img/arr_right.png" alt="image">모바일 스캔</span>
        </div>
        <div class="scan-desc">
          <ul>
            <li v-for="(file, index) in m_files" :key="index">
              <article class="media">
                <input type="checkbox" :id="'mobile-file-' + index" v-model="file.chk" @change="toggle(file, mobileCheckHandler)" v-if="!readonly" /><label :for="'mobile-file-' + index" v-if="!readonly">&nbsp;</label>
                <div class="media-left">
                  <figure class="image" v-if="isPdf(file)">
                    <img src="/img/pdf.png" alt="Image">
                  </figure>
                  <figure class="image" v-else>
                    <img :src="file.attribute2" alt="Image" onerror="this.src='/img/image.png'">
                  </figure>
                </div>
                <div class="media-content">
                  <div class="content">
                    <p class="name-tit">{{ file.originalName }}</p>
                    <p class="name-sub">{{ $moment(file.modifiedDate).format('MM.DD(dd) HH:mm') }}</p>
                  </div>
                </div>
              </article>
            </li>
          </ul>
        </div>
      </div>
      <div class="scan-item02">
        <div class="scan-name">
          <span><img src="/img/arr_right.png" alt="image">첨부파일</span>
        </div>
        <div class="scan-btn" v-if="!readonly">
          <input type="file" ref="file" @change="proceedFileUpload()" style="display: none;" accept="image/jpeg,image/gif,image/png,application/pdf" multiple />
          <button @click="startFileUpload()"><i class="fas fa-plus"></i></button>
          <button @click="clearAll()"><i class="far fa-trash-alt"></i></button>
        </div>
        <div class="scan-desc">
          <ul>
            <li v-for="(file, index) in a_files" :key="index" :class="{ 'selected': isSel(file) }">
              <article class="media" @click="toggle(file, file.chk = !file.chk)">
                <div class="media-left">
                  <figure class="image" v-if="isPdf(file)">
                    <img src="/img/pdf.png" alt="Image">
                  </figure>
                  <figure class="image" v-else>
                    <img :src="file.attribute2" alt="Image" onerror="this.src='/img/image.png'">
                  </figure>
                </div>
                <div class="media-content">
                  <div class="content">
                    <p class="name-tit">{{ file.originalName }}</p>
                    <p class="name-sub">{{ file.fileKind }} / {{ getFileSize(file) }}</p>
                  </div>
                </div>
              </article>
              <button class="scan-trash" @click="clear(file)" v-if="!readonly"><i class="far fa-trash-alt"></i></button>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="scan-img-area">
      <!-- TODO::이미지/PDF 전시 영역 -->
      <div class="display-area" v-if="sel.length > 0">
        <pdf-viewer :src="sel[0].downloadUrl" style="height: 595px;" v-if="isPdf(sel[0])" />
        <img :src="sel[0].downloadUrl" alt="Image" onerror="this.src='/img/image.png'" v-else />
      </div>
      <!-- <div class="display-area" v-if="finalSelection !== undefined">
        <img src="/img/pdf.png" alt="Image" />
      </div> -->
    </div>
  </div>
</layout>
</template>

<script>
import Layout from '@/components/ModalSlot.vue'
import PdfViewer from '@/components/PdfViewer'

export default {
  props: {
    title: {
      type: String,
      required: false,
      default: '스캔'
    },
    docMngNo: {
      type: String,
      required: true
    },
    readonly: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  components: {
    Layout,
    PdfViewer
  },
  data() {
    return {
      m_files: [],
      a_files: [],
      sel: []
    }
  },
  methods: {
    startFileUpload() {
      // Trigger click event
      this.$refs.file.click()
    },
    proceedFileUpload() {
      let files = this.$refs.file.files

      // Ok to proceed
      if (files.length > 0) {
        let form = new FormData()

        _.forEach(files, (file, i) => {
          form.append(`files`, file)
        })

        this.$store.commit('loading')
        this.$http.post(`/api/evid/addFiles/${this.docMngNo}`, form, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }).then(response => {
          this.$swal({
            type: 'success',
            text: '파일이 업로드 되었습니다.'
          }).then(() => {
            this.a_files = this.a_files.concat(response.data)
          })
          return response
        }).catch(response => {
          this.$swal({
            type: 'error',
            text: '파일업로드에 실패하였습니다.'
          })
          return response
        }).finally(() => {
          this.$store.commit('finish')
        })
      }
    },
    clearAll() {
      this.$store.commit('loading')
      this.$http.post('/api/evid/removeFiles', {
        documentHId: this.docMngNo
      }).then(() => {
        let am_files = this.a_files.filter(x => x.attribute3)

        let m_filtered = this.m_files.filter(x => am_files.filter(y => y.id === x.id)[0])
        _.forEach(m_filtered, x => {
          x.chk = false
        })

        this.a_files = []
        this.sel = []
      }).finally(() => {
        this.$store.commit('finish')
      })
    },
    clear(file) {
      if (file.lock) {
        return
      } else {
        // 모바일 파일
        let m_f = this.m_files.filter(x => x.id === file.id)[0]
        // 모바일 파일에 있음
        if (m_f !== undefined) {
          m_f.lock = true
        }
        // 업로드 파일 목록
        let a_f = this.a_files.filter(x => x.id === file.id)[0]
        // 파일 목록에 있다
        if (a_f !== undefined) {
          a_f.lock = true
        }
        this.$store.commit('loading')
        this.$http.post('/api/evid/removeFiles', {
          documentHId: this.docMngNo,
          id: file.id
        }).then(response => {
          // 파일 목록을 정리해봅니다.
          // 모바일 파일
          let m_f = this.m_files.filter(x => x.id === file.id)[0]
          // 모바일 파일에 있음
          if (m_f !== undefined) {
            m_f.chk = false
            delete m_f.lock
            let index = this.sel.indexOf(m_f)
            index >= 0 ? this.sel.splice(index, 1) : 0
          }
          // 업로드 파일 목록
          let a_f = this.a_files.filter(x => x.id === file.id)[0]
          // 파일 목록에 있다
          if (a_f !== undefined) {
            a_f.chk = false
            let index = this.sel.indexOf(a_f)
            index >= 0 ? this.sel.splice(index, 1) : 0
            this.a_files.splice(this.a_files.indexOf(a_f), 1)
          }
        }).finally(() => {
          this.$store.commit('finish')
        })
      }
    },
    /**
     * 선택 이벤트 핸들러
     */
    toggle(file, callback) {
      if (file.chk) {
        this.sel.unshift(file)
      } else {
        this.sel.splice(this.sel.indexOf(file), 1)
      }

      if (callback !== undefined && typeof callback === 'function') {
        callback.apply(this, [file])
      }
    },
    mobileCheckHandler(file) {
      // 추가를 해야한다
      if (file.chk) {
        this.$http.post('/api/evid/mCheck', {
          documentHId: this.docMngNo,
          id: file.id
        }).then(response => {
          this.a_files.unshift(response.data)
          this.a_files = this.a_files.sort((a, b) => a.modifiedDate > b.modifiedDate)
        })
      } else {
        this.clear(file)
      }
    },
    /**
     * 선택되었는지 체크
     */
    isSel(file) {
      return file.chk
    },
    /**
     * 서버에서 첨부된 파일 정보를 가져온다
     */
    query() {
      this.$store.commit('loading')
      this.$http.get(`/api/evid/fileList/${this.docMngNo}`)
        .then(response => {
          let m_files = response.data.mFiles.map(x => {
            x.chk = false
            return x
          })
          let a_files = response.data.aFiles.map(x => {
            x.chk = false
            return x
          })

          let a_filtered = m_files.filter(x => a_files.filter(y => y.id === x.id)[0])
          _.forEach(a_filtered, x => {
            x.chk = true
          })

          this.m_files = m_files
          this.a_files = a_files
          this.sel = m_files.filter(x => x.chk)
        })
        .finally(() => {
          this.$store.commit('finish')
        })
    },
    isPdf(item) {
      return item && item.fileKind === '.pdf'
    },
    getFileSize(file) {
      let types = ['Byte', 'KB', 'MB', 'GB', 'TB', 'PB']
      var amt = (file || {}).fileAmount || 0
      var cnt = 0
      while (amt > 1000) {
        amt /= 1000
          ++cnt
      }
      let rst = ''
      if (cnt === 0) {
        rst = [this.$numeral(amt).format('0,0'), types[cnt]].join(' ')
      } else {
        rst = [this.$numeral(amt).format('0,0.00'), types[cnt]].join(' ')
      }
      return rst
    }
  },
  created() {
    this.query()
  }
}
</script>

<style lang="scss" scoped>
.modal-card {
  width: 1060px;
}

.display-area {
  :global(img) {
    width: 100%;
  }
}
</style>
