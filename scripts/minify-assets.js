#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');

const siteDir = path.join(__dirname, '..', '_site');

function minifyCSS(css) {
  return css
    .replace(/\/\*[\s\S]*?\*\//g, '')   // strip block comments
    .replace(/\s*([{}:;,>~+])\s*/g, '$1') // collapse spaces around operators
    .replace(/;\s*}/g, '}')              // drop trailing semicolon inside block
    .replace(/\s+/g, ' ')               // collapse remaining whitespace
    .replace(/^\s+|\s+$/g, '')          // trim
    .replace(/ {/g, '{')                // no space before brace
    .replace(/: /g, ':');               // no space after colon
}

const cssPath = path.join(siteDir, 'style.css');
if (fs.existsSync(cssPath)) {
  const original = fs.readFileSync(cssPath, 'utf-8');
  const minified = minifyCSS(original);
  fs.writeFileSync(cssPath, minified, 'utf-8');
  const saved = original.length - minified.length;
  console.log(`CSS minified: ${original.length} → ${minified.length} bytes (saved ${saved})`);
}
