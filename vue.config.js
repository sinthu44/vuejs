module.exports = {
  outputDir: 'build',
  assetsDir: 'static',
  devServer: {
    proxy: {
      '/api*': {
        // Forward frontend dev server request for /api to django dev server
        target: 'http://localhost:8000/',
      }
    },
  },
  lintOnSave: process.env.NODE_ENV !== 'production',
}
