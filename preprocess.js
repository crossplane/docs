"use strict";

// on publish this script will check all docs versions and prepare static data
// so it does not have to be generated using complicated logic from liquid templates / jekyll

const fs = require("fs");
const jsonfile = require("jsonfile");
const path = require("path");
const semver = require("semver");

function getDirectories(srcpath) {
  return fs
    .readdirSync(srcpath)
    .filter(file => fs.lstatSync(path.join(srcpath, file)).isDirectory());
}

const ROOT_DIR = `${__dirname}`;

// This version map and version function allow versions that do not follow semver syntax to also
// be included in the version selection sorting for the site.  "local" is the developer version
// used when testing docs changes in a local development environment.  We set this "local"
// version as 7.7.7 (a high value) so that it will show up as the "latest" version in the site's
// version selection dropdown.
const versionMap = new Map([
  ["local", "7.7.7"]
])
function version(v) {
  if (versionMap.has(v)){
    return versionMap.get(v)
  }
  return semver.coerce(v).version
}

// collect all docs versions (forcing master to the end)
const data = [];
const versions = [
  ...getDirectories(`${ROOT_DIR}/docs`)
    .filter(v => v !== "master")
    .sort((a, b) =>
      semver.rcompare(version(a), version(b))
    ),
  "master"
];

// write json for jekyll (and browser)
jsonfile.writeFileSync(
  "./_data/versions.json",
  versions.map(pv => {
    return {
      version: pv,
      path: `/docs/${pv}`
    };
  })
);
