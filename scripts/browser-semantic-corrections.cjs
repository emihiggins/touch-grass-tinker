// Synthetic response injection tests recovery UI; no live inference or model-quality claim.
const fs = require('node:fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
(async () => {
  const browser = await chromium.launch();
  const results = [];
  for (const width of [390, 768, 1440]) {
    const page = await browser.newPage({
      viewport: { width, height: 1000 },
      reducedMotion: 'reduce',
    });
    let interpretations = 0;
    const errors = [];
    page.on('pageerror', (e) => errors.push(e.message));
    await page.route('**/api/interpret', async (route) => {
      interpretations++;
      const response = await route.fetch();
      const data = await response.json();
      data.intent.status = 'clarify';
      data.intent.clarification_fields = ['duration_minutes'];
      data.semantic_validation = {
        valid: false,
        plan_allowed: false,
        issues: [{ code: 'clarification_retains_value', path: 'intent.duration_minutes' }],
      };
      data.notice = 'Synthetic semantic-recovery fixture; not model inference.';
      await route.fulfill({ response, json: data });
    });
    const assert = async (condition, message) => {
      if (!(await condition)) throw Error(`${width}: ${message}`);
    };
    await page.goto(process.env.BASE_URL || 'http://127.0.0.1:8767');
    await page.getByText('Ready. Review constraints before planning.').waitFor();
    const request = 'Only blues, no surface lifts, 45 minutes';
    await page.locator('#request').fill(request);
    await page.locator('#interpret').click();
    await page.locator('#review').waitFor();
    await assert(page.locator('#make-plan').isDisabled(), 'Contradictory clarification can plan');
    await assert(page.locator('#correct-minutes').isEnabled(), 'Local correction unavailable');
    if (width === 390)
      await page.screenshot({
        path: 'research/evidence/model-robustness-r01/clarification-390.png',
        fullPage: true,
      });
    await page.locator('#correct-minutes').fill('8');
    await page.locator('#discard-corrections').click();
    await assert(page.locator('#make-plan').isDisabled(), 'Discard bypassed clarification');
    await page.locator('#correct-minutes').fill('8');
    await page.locator('#apply-corrections').click();
    await page.locator('#make-plan').click();
    await page.getByText('No outing meets these constraints in this scenario.').waitFor();
    await assert(
      page
        .locator('#review-request')
        .textContent()
        .then((x) => x.includes(request)),
      'Original request lost',
    );
    await page.locator('#correct-minutes').fill('45');
    await page.locator('#correct-difficulty').selectOption('');
    await page.locator('#apply-corrections').click();
    await assert(
      page.locator('#make-plan').isDisabled(),
      'Unknown maximum treated as unrestricted',
    );
    await page.locator('#correct-difficulty').selectOption('blue');
    await page.locator('#apply-corrections').click();
    const planned = page.waitForRequest((r) => r.url().endsWith('/api/plan'));
    await page.locator('#make-plan').click();
    const sent = (await planned).postDataJSON().intent;
    if (sent.status !== 'ready' || sent.clarification_fields.length || sent.duration_minutes !== 45)
      throw Error('Incorrect corrected payload');
    for (const lift of ['t-bar', 'platter', 'rope-tow', 'magic-carpet'])
      if (!sent.excluded_lift_types.includes(lift)) throw Error('Lost hard exclusion');
    await page.locator('#itinerary').waitFor();
    const download = page.waitForEvent('download');
    await page.locator('#save-itinerary').click();
    const text = fs.readFileSync(await (await download).path(), 'utf8');
    for (const term of ['Minutes: 45', 'Maximum difficulty: blue', 'rope-tow', 'time budget'])
      if (!text.includes(term)) throw Error(`Export missing ${term}`);
    await page.locator('#correct-minutes').fill('60');
    await assert(page.locator('#itinerary').isHidden(), 'Draft retained route/export');
    await page.locator('#discard-corrections').click();
    let release;
    const gate = new Promise((resolve) => {
      release = resolve;
    });
    await page.route('**/api/plan', async (route) => {
      const response = await route.fetch();
      await gate;
      await route.fulfill({ response });
    });
    const pending = page.waitForRequest((r) => r.url().endsWith('/api/plan'));
    await page.locator('#make-plan').click();
    await pending;
    await page.locator('#correct-minutes').fill('50');
    const received = page.waitForResponse((r) => r.url().endsWith('/api/plan'));
    release();
    await received;
    await page.waitForLoadState('networkidle');
    await assert(page.locator('#itinerary').isHidden(), 'Late response published a stale route');
    await assert(page.locator('#make-plan').isDisabled(), 'Late response enabled pending draft');
    if (interpretations !== 1) throw Error('Recovery made an extra interpreter call');
    if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth))
      throw Error('Overflow');
    await page.screenshot({
      path: `research/evidence/model-robustness-r01/recovery-${width}.png`,
      fullPage: true,
    });
    await page.evaluate(fs.readFileSync(process.env.AXE_SCRIPT, 'utf8'));
    const axe = await page.evaluate(() =>
      axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa'] } }),
    );
    if (axe.violations.length || errors.length)
      throw Error(JSON.stringify({ violations: axe.violations, errors }));
    results.push({
      width,
      noStaleRoute: true,
      correctedExport: true,
      exclusionsPreserved: true,
      shortBudgetReachesNoRoute: true,
      unknownMaximumBlocked: true,
      extraInterpreterCalls: 0,
      axeViolations: 0,
      axeIncomplete: axe.incomplete.map((x) => x.id),
    });
    await page.close();
  }
  await browser.close();
  fs.writeFileSync(
    'research/evidence/model-robustness-r01/recovery-browser.json',
    JSON.stringify({ scope: 'synthetic_semantic_recovery_not_model_accuracy', results }, null, 2) +
      '\n',
  );
  console.log('Semantic recovery/export/stale response matrix passed');
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
