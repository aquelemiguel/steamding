const path = require('path');

module.exports = {
  entry: {
    renderer: path.join(__dirname, '/public/js/renderer.js'),
  },
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, './public/js'),
  },
  node: {
    fs: 'empty',
  },
};
