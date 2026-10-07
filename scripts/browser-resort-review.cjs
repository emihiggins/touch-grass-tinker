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
      await page.waitForFunction((n) => document.querySelectorAll('#map .e').length === n, count);
      const bounds = await page.locator('#map').evaluate((m) => {
        const b = m.getBBox();
        return { x: b.x, y: b.y, w: b.width, h: b.height };
      });
      if (bounds.x < 0 || bounds.y < 0 || bounds.x + bounds.w > 900 || bounds.y + bounds.h > 560)
        throw Error('Clipped ' + resort + JSON.stringify(bounds));
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth))
        throw Error('Horizontal overflow');
      await page.locator('#map .e').first().focus();
      await page.keyboard.press('Enter');
      if (!(await page.locator('#detail').innerText()).includes('Source way'))
        throw Error('Missing details');
      await page.uncheck('#d');
      const subset = await page.locator('#map .e').count();
      if (subset >= count) throw Error('Component filter ineffective');
      if (await page.locator('#detail').innerText()) throw Error('Stale detail after filtering');
      await page.check('#d');
      await page.uncheck('#p');
      if (await page.locator('#map .piste').count()) throw Error('Piste filter');
      await page.check('#p');
      if (resort === 'winter-park' || resort === 'breckenridge') {
        await page.locator('#lift-review').selectOption({ index: 1 });
        if ((await page.locator('#map .endpoint').count()) !== 2)
          throw Error('Missing source endpoint markers');
        const text = await page.locator('#lift-detail').innerText();
        if (
          !text.includes('Exact incoming piste segments:') ||
          !text.includes('Inspect source node')
        )
          throw Error('Missing endpoint evidence');
        if (resort === 'winter-park' && text.includes('Raw station tags not recovered'))
          throw Error('Missing raw evidence');
        await page.screenshot({
          path: `research/evidence/resort-review/lift-${resort}-${width}.png`,
          fullPage: true,
        });
        await page.locator('#lift-review').selectOption('');
        if (await page.locator('#map .endpoint').count()) throw Error('Stale endpoint markers');
      } else if (!(await page.locator('#lift-review').isDisabled()))
        throw Error('Missing diagnostics offered');
      if (resort === 'winter-park' || resort === 'breckenridge') {
        const excludedCount = await page.locator('#map .excluded').count();
        if (excludedCount !== (resort === 'winter-park' ? 2 : 35))
          throw Error('Wrong excluded count');
        await page.uncheck('#x');
        if (await page.locator('#map .excluded').count()) throw Error('Excluded toggle');
        await page.locator('#excluded-list button').first().click();
        if (
          !(await page.isChecked('#x')) ||
          (await page.locator('#map .excluded.selected').count()) !== 1
        )
          throw Error('Selected excluded not visible');
        const text = await page.locator('#detail').innerText();
        if (!text.includes('excluded from sanitized graph')) throw Error('Missing excluded status');
        await page.locator('#map .e').first().focus();
        await page.keyboard.press('Enter');
        if (await page.locator('#map .excluded.selected').count())
          throw Error('Stale excluded highlight');
        if (resort === 'winter-park') {
          await page.getByRole('button', { name: /Dogpatch —/ }).click();
          if (!(await page.locator('#detail').innerText()).includes('closed-area'))
            throw Error('Dogpatch is not labeled area');
          if ((await page.locator('#map polygon.excluded').count()) !== 1)
            throw Error('Dogpatch missing polygon');
        } else {
          const edge = page.locator('#map polyline.excluded').first();
          if ((await edge.evaluate((e) => getComputedStyle(e).fill)) !== 'none')
            throw Error('Open geometry filled as area');
        }
        await page.screenshot({
          path: `research/evidence/resort-review/excluded-${resort}-${width}.png`,
          fullPage: true,
        });
      }
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
