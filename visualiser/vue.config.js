/* eslint-disable no-undef */
// eslint-disable-next-line @typescript-eslint/no-var-requires
const Dotenv = require('dotenv-webpack')

module.exports = {
  chainWebpack: config => config.resolve.symlinks(false),
  configureWebpack: {
    plugins: [
      new Dotenv()
    ]
  }
}