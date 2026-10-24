/**
 * optimize-images.cjs
 *
 * Generates a .webp sibling for every raster image (.jpg/.jpeg/.png) under
 * public/images/. WebP is ~25-35% smaller than JPEG and far smaller than PNG,
 * which directly improves LCP and total page weight.
 *
 * The BlogImage component serves these via a <picture><source type="image/webp">
 * element, falling back to the original raster on unsupported browsers or when
 * a .webp is missing — so this step is purely additive and safe.
 *
 * Very large images are also downscaled to a max width (their intrinsic size is
 * far bigger than any render slot), cutting bytes further.
 *
 * Usage:  node scripts/optimize-images.cjs
 * Idempotent: skips a .webp that is already newer than its source.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const ROOT = path.resolve(__dirname, '..');
const IMAGES_DIR = path.join(ROOT, 'public', 'images');
const MAX_WIDTH = 1600; // no rendered slot exceeds this; downscale bigger sources
const WEBP_QUALITY = 78;
const RASTER = new Set(['.jpg', '.jpeg', '.png']);

function walk(dir, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, out);
    else out.push(full);
  }
  return out;
}

async function main() {
  if (!fs.existsSync(IMAGES_DIR)) {
    console.log('[optimize-images] no public/images directory, nothing to do.');
    return;
  }
  const files = walk(IMAGES_DIR).filter((f) => RASTER.has(path.extname(f).toLowerCase()));
  let created = 0;
  let skipped = 0;
  let savedBytes = 0;

  for (const src of files) {
    const webp = src.replace(/\.(jpe?g|png)$/i, '.webp');
    try {
      // Skip if webp exists and is newer than the source (idempotent).
      if (fs.existsSync(webp) && fs.statSync(webp).mtimeMs >= fs.statSync(src).mtimeMs) {
        skipped++;
        continue;
      }
      const img = sharp(src, { failOn: 'none' });
      const meta = await img.metadata();
      if (meta.width && meta.width > MAX_WIDTH) {
        img.resize({ width: MAX_WIDTH });
      }
      await img.webp({ quality: WEBP_QUALITY }).toFile(webp);
      const before = fs.statSync(src).size;
      const after = fs.statSync(webp).size;
      savedBytes += Math.max(0, before - after);
      created++;
      console.log(
        `[optimize-images] ${path.relative(ROOT, webp)}  ${(before / 1024).toFixed(0)}KB -> ${(after / 1024).toFixed(0)}KB`
      );
    } catch (err) {
      console.warn(`[optimize-images] FAILED ${path.relative(ROOT, src)}: ${err.message}`);
    }
  }

  console.log(
    `[optimize-images] done. created=${created} skipped=${skipped} approx saved=${(savedBytes / 1024 / 1024).toFixed(2)}MB`
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
