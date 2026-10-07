const fs = require('node:fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 900 } });
  let interpretationCalls = 0;
  page.on('request', (r) => {
    if (r.url().endsWith('/api/interpret')) interpretationCalls++;
  });
  const assert = async (p, message) => {
    if (!(await p)) throw Error(message);
  };
  await page.goto('http://127.0.0.1:8767');
  await page.getByText('Ready. Review constraints before planning.').waitFor();
  await page.locator('#load-example').click();
  await page.getByText('Ready. Review constraints before planning.').waitFor();
  await page.locator('#adapter').selectOption('replay');
  await page.locator('#interpret').click();
  await page.getByText('Ready for your confirmation.').waitFor();
  const originalBudget = await page.locator('#correct-minutes').inputValue();
  await page.locator('#make-plan').click();
  await page.locator('#itinerary').waitFor();
  await page.locator('#correct-minutes').fill('0');
  await assert(page.locator('#itinerary').isHidden(), 'Editing retained old route');
  await page.locator('#lift-checks input[value=rope-tow]').check();
  await assert(
    page.locator('#make-plan').isDisabled(),
    'Lift change unlocked pending invalid time',
  );
  await assert(
    page.locator('#correction-form').evaluate((f) => !f.checkValidity()),
    'Zero time accepted',
  );
  await page.locator('#correct-minutes').fill('1.5');
  await assert(
    page.locator('#correction-form').evaluate((f) => !f.checkValidity()),
    'Fractional time accepted',
  );
  await page.locator('#correct-minutes').fill('1441');
  await assert(
    page.locator('#correction-form').evaluate((f) => !f.checkValidity()),
    'Horizon exceeded',
  );
  await page.locator('#discard-corrections').click();
  await assert(
    page
      .locator('#correct-minutes')
      .inputValue()
      .then((v) => v === originalBudget),
    'Discard did not restore approved time',
  );
  await assert(
    page.locator('#lift-checks input[value=rope-tow]').isChecked(),
    'Discard lost lift correction',
  );
  await assert(page.locator('#itinerary').isHidden(), 'Discard restored an invalidated route');
  await assert(page.locator('#make-plan').isEnabled(), 'Discard did not allow reconfirmation');
  await page.locator('#correct-minutes').fill('90');
  await page.locator('#correct-difficulty').selectOption('red');
  await page.locator('#apply-corrections').click();
  await assert(page.locator('#make-plan').isEnabled(), 'Valid correction not confirmable');
  const planning = page.waitForRequest((r) => r.url().endsWith('/api/plan'));
  await page.locator('#make-plan').click();
  const sent = (await planning).postDataJSON();
  if (
    sent.intent.duration_minutes !== 90 ||
    sent.intent.hard_max_difficulty !== 'red' ||
    !sent.intent.excluded_lift_types.includes('rope-tow')
  )
    throw Error('Corrections not sent');
  await page.locator('#itinerary').waitFor();
  const text = await page.locator('#route-source').textContent();
  if (
    !text.includes('hard lift exclusions') ||
    !text.includes('time budget') ||
    !text.includes('maximum difficulty')
  )
    throw Error('Correction provenance lost');
  await assert(
    page
      .locator('#review-settings')
      .textContent()
      .then((t) => t.includes('60 minutes') && t.includes('maximum blue')),
    'Original selected settings overwritten',
  );
  const downloaded = page.waitForEvent('download');
  await page.locator('#save-itinerary').click();
  const file = await downloaded;
  const exported = fs.readFileSync(await file.path(), 'utf8');
  if (
    !exported.includes('Minutes: 90') ||
    !exported.includes('Maximum difficulty: red') ||
    !exported.includes('rope-tow')
  )
    throw Error('Export lost corrected constraints');
  await page.screenshot({
    path: 'research/evidence/app-integration/local-corrections-mobile.png',
    fullPage: true,
  });
  if (interpretationCalls !== 1) throw Error('Local correction called interpreter again');
  await page.locator('#adapter').selectOption('rules');
  await page.locator('#request').fill('Fly me to Mars');
  await page.locator('#interpret').click();
  await page.getByText('No route requested until the interpretation is resolved.').waitFor();
  await assert(
    page.locator('#apply-corrections').isDisabled(),
    'Unsupported intent unlocked by correction editor',
  );
  fs.writeFileSync(
    'research/evidence/app-integration/local-corrections.json',
    JSON.stringify(
      {
        draftDiscardPreservesLiftCorrections: true,
        durationAndDifficultyApplied: true,
        draftEditsInvalidateRoute: true,
        invalidDurationBlocksConfirmation: true,
        liftEditsCannotBypassDraft: true,
        combinedProvenanceRetained: true,
        correctedExportVerified: true,
        originalSettingsRetained: true,
        localEditsAddNoInterpretationCalls: true,
        unsupportedStillBlocked: true,
      },
      null,
      2,
    ) + '\n',
  );
  await browser.close();
  console.log('Local constraint correction checks passed');
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
