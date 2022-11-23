const postcssLightningcss = require("postcss-lightningcss");

const purgecss = require('@fullhuman/postcss-purgecss')({
  content: ['./hugo_stats.json'],
  variables: true,
  defaultExtractor: content => {
    const els = JSON.parse(content).htmlElements;
    return [
      ...(els.tags || []),
      ...(els.classes || []),
      ...(els.ids || []),
    ];
  },
  safelist: []
});

const mediasort = require('postcss-sort-media-queries')({
    sort: 'desktop-first'
});



module.exports = {
  plugins: [
    purgecss,
    mediasort,
    postcssLightningcss
  ]
};
