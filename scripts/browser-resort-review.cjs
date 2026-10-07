const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const errors = [],
    external = [];
  const evidence = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('request', (r) => {
    if (!r.url().startsWith('http://127.0.0.1:8767/')) external.push(r.url());
  });
  page.setDefaultTimeout(10000);
  for (const width of [390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('http://127.0.0.1:8767/research-review.html');
    for (const [resort, count] of [
      ['winter-park', 520],
      ['breckenridge', 1146],
      ['wachusett', 520],
      ['patscherkofel', 144],
    ]) {
      await page.selectOption('#s', resort);
      await page.waitForFunction(
        (n) => document.querySelectorAll('#map polyline').length === n,
        count,
      );
      const bounds = await page.locator('#map').evaluate((m) => {
        const b = m.getBBox();
        return { x: b.x, y: b.y, w: b.width, h: b.height };
      });
      if (bounds.x < 0 || bounds.y < 0 || bounds.x + bounds.w > 900 || bounds.y + bounds.h > 560)
        throw Error('Clipped ' + resort + JSON.stringify(bounds));
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth))
        throw Error('Horizontal overflow');
      await page.locator('#map polyline').first().focus();
      await page.keyboard.press('Enter');
      if (!(await page.locator('#detail').innerText()).includes('Source way'))
        throw Error('Missing details');
      await page.uncheck('#d');
      const subset = await page.locator('#map polyline').count();
      if (subset >= count) throw Error('Component filter ineffective');
      if (await page.locator('#detail').innerText()) throw Error('Stale detail after filtering');
      await page.check('#d');
      await page.uncheck('#p');
      if (await page.locator('#map .piste').count()) throw Error('Piste filter');
      await page.check('#p');
      evidence.push({ resort, width, edges: count, largest_component_edges: subset, bounds });
      if (
        (width === 390 && resort === 'winter-park') ||
        (width === 1440 && resort === 'breckenridge')
      )
        await page.screenshot({
          path: `research/evidence/resort-review/${resort}-${width}.png`,
          fullPage: true,
        });
    }
  }
  if (errors.length || external.length) throw Error(JSON.stringify({ errors, external }));
  fs.writeFileSync(
    'research/evidence/resort-review/browser-check.json',
    JSON.stringify(
      { checks: evidence, errors, external, scope: 'browse_only_geometry_not_route_validation' },
      null,
      2,
    ) + '\n',
  );
  await browser.close();
  console.log(
    'Four resort previews: rendering, bounds, keyboard, filters and zero external requests passed at three widths',
  );
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
