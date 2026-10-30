const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  let failed = false;
  for (const path of ['/', '/es/', '/pt/', '/pl/', '/ja/', '/bonuses/']) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const response = await page.goto(`http://127.0.0.1:4173${path}`, { waitUntil: 'networkidle' });
    const result = await page.evaluate(() => ({
      width: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      title: document.title,
    }));
    const ok = response && response.status() === 200 && result.title && result.scrollWidth <= result.width + 1 && errors.length === 0;
    console.log(`${ok ? 'OK' : 'FAIL'} ${path} status=${response?.status()} viewport=${result.width}/${result.scrollWidth} title=${Boolean(result.title)} jsErrors=${errors.length}`);
    if (!ok) failed = true;
    await page.close();
  }
  await browser.close();
  if (failed) process.exit(1);
})().catch(error => { console.error(error); process.exit(1); });
