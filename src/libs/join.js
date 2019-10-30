let join = (delim, ...args) => {
  let exp = new RegExp(['^\\', delim, '*|\\', delim, '*$'].join(''))
  return args.map(x => String(x || '').trim().replace(exp, '')).filter(x => x).join(delim)
}

let url = (...args) => {
  args.unshift('/')
  return join.apply(null, args)
}

export default {
  join: join,
  url: url
}

export { url as url, join as join }