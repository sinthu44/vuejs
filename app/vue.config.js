// const IS_PRODUCTION = process.env.NODE_ENV === 'production'
const path = require('path')

module.exports = {
    outputDir: 'dist',
    assetsDir: 'static',
    // baseUrl: IS_PRODUCTION
    // ? 'http://cdn123.com'
    // : '/',
    // For Production, replace set baseUrl to CDN
    // And set the CDN origin to `yourdomain.com/static`
    // Whitenoise will serve once to CDN which will then cache
    // and distribute
    devServer: {
      proxy: {
        '/api*': {
          // Forward frontend dev server request for /api to django dev server
          target: 'http://localhost:8000/',
        }
      }
    },
    chainWebpack: config => {
      const types = ['vue-modules', 'vue', 'normal-modules', 'normal']
      types.forEach(type => addStyleResource(config.module.rule('stylus').oneOf(type)))
    },
  }

  function addStyleResource (rule) {
    rule.use('style-resource')
      .loader('style-resources-loader')
      .options({
        patterns: [
          path.resolve(__dirname, './src/styles/imports.styl'),
        ],
      })
  }
