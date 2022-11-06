const path = require("path")
const { WebpackManifestPlugin } = require("webpack-manifest-plugin")


const config = {
  devtool: "source-map",
  entry:{
    main: [path.resolve("src", "js", "app.js"),
    path.resolve("src", "js", "search.js")
    ],
    colorMode: [path.resolve("src", "js", "colorMode.js")],
    lightbox: [path.resolve("src", "js", "lightbox.js")]
  },
  output: {
    filename: "[name]-[contenthash:8].bundle.min.js",
    chunkFilename: "[name]-[contenthash:8].chunk.min.js",
    path: path.join(__dirname, "../../themes/geekdoc/assets/js"),
    clean: true
  },

  plugins: [
    new WebpackManifestPlugin({
      fileName: "../../data/assets.json",
      publicPath: "js",
      writeToFileEmit: true,
      generate(seed, files) {
        let manifest = {}

        files.forEach(function (element, index) {
          if (element.name.endsWith("VERSION")) return
          if (element.name.endsWith(".svg")) return
          if (element.name.startsWith("fonts/")) return
          if (element.name.startsWith("/favicon")) return

          Object.assign(manifest, {
            [element.name]:  { src: element.path }
          })
        })

        return manifest
      }
    }),
  ]
}

module.exports = config