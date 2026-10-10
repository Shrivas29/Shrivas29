// Renders cards.html to PNG for each card and theme. Needs Playwright (NODE_PATH or a local install).
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const EXE = process.env.CHROME || undefined;
const OUT = path.join(__dirname, '..', 'assets');
const CARDS = ['gotham', 'bugle', 'ento', 'vidyuth', 'console', 'sujitha'];
(async () => {
  const browser = await chromium.launch(EXE ? { executablePath: EXE } : {});
  const page = await browser.newPage({ viewport: { width: 1000, height: 800 }, deviceScaleFactor: 2 });
  const rects = {};
  for (const mode of ['dark', 'light']) {
    for (const card of CARDS) {
      await page.goto(`file://${path.join(__dirname, 'cards.html')}?card=${card}&mode=${mode}`);
      await page.evaluate(() => window.__ready);
      const el = await page.$('#card');
      const file = path.join(OUT, `card-${card}-${mode}.png`);
      await el.screenshot({ path: file });
      if (card === 'gotham') rects[mode] = await page.evaluate(() => {
        const c = document.getElementById('card').getBoundingClientRect();
        const w = document.getElementById('window').getBoundingClientRect();
        return { x: w.left - c.left + 1, y: w.top - c.top + 1, w: w.width - 2, h: w.height - 2 };
      });
      console.log(path.basename(file));
    }
  }
  fs.writeFileSync(path.join(__dirname, 'window.json'), JSON.stringify(rects, null, 2));
  await browser.close();
})();
