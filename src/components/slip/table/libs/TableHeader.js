const fr = {
  props: {
    'value': {
      type: Object,
      required: true
    },
    'readonly': {
      type: Boolean,
      required: false,
      default: false
    }
  },
  template: `
  <tr>
    <th>전표번호</th>
    <td colspan="2" style="width: 180px;">{{ value.eaSlipNo }}</td>

    <th>전표유형</th>
    <td>{{ value.slipTypeNm }}</td>

    <th>전표상태</th>
    <td><span class="color_table_org" style="width: 80px;">{{ value.slipStatNm }}</span></td>
    <td style="width: 100px;"></td>
  </tr>
  `
}

const sr = {
  props: {
    'value': {
      type: Object,
      required: true
    },
    'readonly': {
      type: Boolean,
      required: false,
      default: false
    }
  },
  template: `
  <tr>
    <th>작성부서</th>
    <td>{{ value.wrtDeptCd }} / {{ value.wrtDeptNm }}</td>
    <td>{{ value.bpNm }}</td>

    <th>작성자</th>
    <td>{{ value.wrtNm }}</td>

    <th>작성일자</th>
    <td class="Rt-M" colspan="2">{{ this.$moment(value.wrtDtm).format('YYYY-MM-DD') }}</td>
  </tr>
  `
}

export default {
  functional: true,
  props: {
    'value': {
      type: Object,
      required: true
    },
    'readonly': {
      type: Boolean,
      required: false,
      default: false
    }
  },
  render(createElement, context) {
    const fre = createElement(fr, { props: context.props })
    const sre = createElement(sr, { props: context.props })
    return [fre, sre]
  }
}
