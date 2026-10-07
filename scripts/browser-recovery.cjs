const fs = require('node:fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  const assert = async (condition, message) => {
    if (!(await condition)) throw Error(message);
  };
  async function hold(pattern) {
    let release, ready;
    const captured = new Promise((r) => (ready = r));
    const handler = async (route) => {
      const response = await route.fetch();
      release = async () => {
        const received = page.waitForResponse((r) => r.url() === route.request().url());
        await route.fulfill({ response });
        await (await received).finished();
        await page.evaluate(
          () =>
            new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))),
        );
      };
      ready();
    };
    await page.route(pattern, handler);
    return { captured, release: () => release(), remove: () => page.unroute(pattern, handler) };
  }
  await page.goto('http://127.0.0.1:8767');
  await page.getByText('Ready. Review constraints before planning.').waitFor();
  await page.route('**/api/context?terrain=alpendorf', (r) =>
    r.fulfill({ status: 503, contentType: 'application/json', body: '{"error":"test failure"}' }),
  );
  await page.locator('#terrain').selectOption('alpendorf');
  await page.locator('#retry-terrain').waitFor();
  await assert(page.locator('#interpret').isDisabled(), 'Failed terrain enabled interpretation');
  await assert(
    page
      .locator('#map > *')
      .count()
      .then((n) => n === 0),
    'Old terrain remains visible after failure',
  );
  await page.unroute('**/api/context?terrain=alpendorf');
  await page.locator('#retry-terrain').click();
  await page.getByText('Ready. Review constraints before planning.').waitFor();
  await assert(page.locator('#retry-terrain').isHidden(), 'Retry did not recover');
  await page.locator('#terrain').selectOption('synthetic');
  await page.getByText('Fictional terrain · not to scale').waitFor();
  await page.locator('#adapter').selectOption('replay');
  await page.locator('#terrain').selectOption('alpendorf');
  await page.getByText('Unreviewed OSM geometry · geographic').waitFor();
  await assert(
    page
      .locator('#adapter')
      .inputValue()
      .then((v) => v === 'rules'),
    'Unavailable replay mode remained selected',
  );
  await assert(
    page.locator('#adapter option[value=replay]').isDisabled(),
    'Replay offered on unsupported terrain',
  );
  await page.locator('#terrain').selectOption('synthetic');
  await page.getByText('Fictional terrain · not to scale').waitFor();
  await assert(
    page.locator('#adapter option[value=replay]').isEnabled(),
    'Recorded Pine mode not restored',
  );
  const interpretation = await hold('**/api/interpret');
  await page.locator('#interpret').click();
  await interpretation.captured;
  const terrain = await hold('**/api/context?terrain=alpendorf');
  await page.locator('#terrain').selectOption('alpendorf');
  await terrain.captured;
  await interpretation.release();
  await interpretation.remove();
  await page.waitForFunction(() => !interpreting);
  await assert(
    page.locator('#interpret').isDisabled(),
    'Old interpretation unlocked pending terrain',
  );
  await assert(page.locator('#review').isHidden(), 'Old interpretation displayed');
  await terrain.release();
  await terrain.remove();
  await page.getByText('Ready. Review constraints before planning.').waitFor();
  await page.locator('#terrain').selectOption('synthetic');
  await page.getByText('Fictional terrain · not to scale').waitFor();
  const stale = await hold('**/api/context?terrain=alpendorf');
  await page.locator('#terrain').selectOption('alpendorf');
  await stale.captured;
  await page.locator('#terrain').selectOption('synthetic');
  await page.getByText('Fictional terrain · not to scale').waitFor();
  await stale.release();
  await stale.remove();
  await assert(
    page.evaluate(() => graph.id === 'synthetic-pine-v1'),
    'Stale terrain overwrote latest selection',
  );
  await page.locator('#interpret').click();
  await page.getByText('Ready for your confirmation.').waitFor();
  const planning = await hold('**/api/plan');
  await page.locator('#make-plan').click();
  await planning.captured;
  await page.locator('#minutes').fill('30');
  await planning.release();
  await planning.remove();
  await assert(page.locator('#itinerary').isHidden(), 'Stale plan displayed');
  await assert(page.locator('#step-inspector').isHidden(), 'Stale inspector displayed');
  await assert(page.locator('#make-plan').isDisabled(), 'Stale plan enabled confirmation');
  if (errors.length) throw Error(errors.join('\n'));
  fs.writeFileSync(
    'research/evidence/app-integration/request-recovery.json',
    JSON.stringify(
      {
        terrainSpecificModeAvailability: true,
        failedTerrainClearsMap: true,
        retryRecovers: true,
        oldInterpretationCannotUnlockTerrain: true,
        staleTerrainDiscarded: true,
        stalePlanDiscarded: true,
        pageErrors: errors,
        providerCalls: 0,
      },
      null,
      2,
    ) + '\n',
  );
  await browser.close();
  console.log('Failed, delayed and out-of-order request recovery passed');
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
