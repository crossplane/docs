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

// collect all docs versions (forcing master to the end)
const data = [];
const versions = [
  ...getDirectories(`${ROOT_DIR}/docs`)
    .filter(v => v !== "master")
    .sort((a, b) =>
      semver.rcompare(semver.coerce(a).version, semver.coerce(b).version)
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
