// Presentation-only reflow of the real app; no app data or behavior is replaced.
// This recorder is deliberately separate from browser-ai-demo.cjs's broad UI tests.
const fs = require('node:fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
const preview = process.argv.includes('--preview');
const width = 2560, height = 1440;
const css = `
body {font-size:16px} header {padding:14px 32px} main {max-width:none;padding:20px 32px}
.intro {margin-bottom:18px} h1 {font-size:40px} .section-links {display:none}
.workspace {grid-template-columns:360px 430px minmax(600px,1fr) 420px;gap:24px;align-items:start}
#review,#itinerary {margin:0;padding:18px;background:var(--surface);border-top:3px solid var(--ink)}
.controls {grid-column:1;grid-row:1} #review {grid-column:2;grid-row:1} .map-panel {grid-column:3;grid-row:1} #itinerary {grid-column:4;grid-row:1}
#correction-form fieldset {display:grid;grid-template-columns:1fr 1fr;gap:6px}
#correction-form legend,#correction-form .hint {grid-column:1 / -1}
#correction-form label {margin:6px 0} #correction-form button {font-size:13px}
#review h2,#itinerary h2 {margin-top:0} #lift-checks {grid-template-columns:1fr 1fr}
#review p {margin:8px 0} #review fieldset {margin:12px 0;padding:10px}
#review input,#review select,#review button {min-height:36px;margin-top:6px;padding:6px 10px}
#lift-checks label {min-height:36px} #lift-checks input {width:20px;min-height:20px;padding:0;margin:0}
#review dl {margin:12px 0} #map {max-height:540px} #steps {max-height:none;overflow:visible}
footer {max-width:none;font-size:14px;margin-top:22px;padding-top:12px}
#demo-caption {position:fixed;left:32px;right:32px;bottom:24px;padding:18px 24px;
background:#173e40;color:#fffef9;border-left:6px solid #dc966a;font-size:25px;line-height:1.35;z-index:1000}
#demo-caption small {display:block;font-size:16px;color:#d0ded9;margin-top:6px}
#demo-cursor {position:fixed;width:22px;height:22px;border:3px solid #a53b16;background:#fff8;
border-radius:50%;pointer-events:none;z-index:1001;left:16px;top:16px;transform:translate(-50%,-50%)}
`;
(async()=>{
 const browser=await chromium.launch({headless:true});
 const ctx=await browser.newContext({viewport:{width,height}, ...(preview?{}:{recordVideo:{dir:'/tmp/liftlap-fixed-video',size:{width,height}}})});
 const page=await ctx.newPage(); const errors=[]; const chapters=[]; let interpretations=0;
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(r.url().endsWith('/api/interpret')) interpretations++;});
 await page.goto(process.env.DEMO_URL || 'http://127.0.0.1:8772');
 await page.getByText('Ready. Review constraints before planning.').waitFor();
 await page.addStyleTag({content:css});
 await page.evaluate(()=>{
  const ws=document.querySelector('.workspace');const review=document.querySelector('#review');
  ws.insertBefore(review,document.querySelector('.map-panel'));ws.append(document.querySelector('#itinerary'));
  const cap=document.createElement('div');cap.id='demo-caption';document.body.append(cap);
  const cursor=document.createElement('div');cursor.id='demo-cursor';document.body.append(cursor);
  window.addEventListener('mousemove',e=>{cursor.style.left=e.clientX+'px';cursor.style.top=e.clientY+'px'});
  window.__demoScrolls=0;window.addEventListener('scroll',()=>window.__demoScrolls++);
 });
 const start=Date.now();
 async function caption(title,seconds=5){
  chapters.push({seconds:Math.round((Date.now()-start)/100)/10,title});
  await page.locator('#demo-caption').evaluate((e,t)=>{e.replaceChildren();e.append(document.createTextNode(t));const s=document.createElement('small');s.textContent='Recorded AI replay · presentation-only desktop layout · simulation, not navigation · no paid calls';e.append(s)},title);
  await page.waitForTimeout(preview?50:seconds*1000);
 }
 async function point(selector){const box=await page.locator(selector).boundingBox();if(!box||box.y<0||box.y+box.height>height-130)throw Error('Control outside fixed frame: '+selector);await page.mouse.move(box.x+box.width/2,box.y+box.height/2,{steps:preview?1:35});await page.waitForTimeout(preview?0:500);}
 async function click(selector){await point(selector);await page.locator(selector).click();await page.waitForTimeout(preview?0:750);}
 async function select(selector,value){await point(selector);await page.locator(selector).selectOption(value);await page.waitForTimeout(preview?0:1000);}
 async function frame(name){
  const sizes=await page.evaluate(()=>({scrollX,scrollY,scrolls:window.__demoScrolls,height:document.documentElement.scrollHeight,width:document.documentElement.scrollWidth}));
  if(sizes.scrollX||sizes.scrollY||sizes.scrolls||sizes.height>1440||sizes.width>2560)throw Error('Frame moved/overflowed '+JSON.stringify(sizes));
  await page.screenshot({path:'/tmp/liftlap-fixed-'+name+'.png'});
 }
 await caption('A short outing starts with your limits—not a route invented by a model.',4);
 await click('#load-example');await select('#adapter','replay');
 await caption('“Only blues, no drag lifts, 45 minutes.” This replays one real Qwen3-8B response.',5);
 await click('#interpret');await page.getByText('Ready for your confirmation.').waitFor();
 if(await page.locator('#itinerary').isVisible())throw Error('Unconfirmed route');
 await caption('The mistake is visible: “no drag lifts” became a preference, not a hard exclusion.',7);
 await frame('interpretation');
 await caption('Correct the hard exclusions locally. The model is not called again.',2);
 for(const type of ['t-bar','platter','rope-tow'])await click('#lift-checks input[value="'+type+'"]');
 await caption('T-bar, platter and rope-tow are now prohibited. Confirm before planning.',5);
 const planRequest=page.waitForRequest(r=>r.url().endsWith('/api/plan'));
 await click('#make-plan');const sent=(await planRequest).postDataJSON();
 for(const t of ['t-bar','platter','rope-tow'])if(!sent.intent.excluded_lift_types.includes(t))throw Error('Missing correction');
 await page.getByText('Simulated route passed the independent validator. No real-world access claim.').waitFor();
 if(interpretations!==1)throw Error('Correction caused extra interpretation');
 await caption('The planner finds a 20-minute simulated outing. Approved constraints stay beside it.',7);
 await frame('route');
 await click('#steps li:first-child button');
 await click('#step-next');
 await caption('Inspect each leg on the same map. Times include assumed queues—not live conditions.',6);
 const downloadEvent=page.waitForEvent('download');await click('#save-itinerary');const download=await downloadEvent;
 const exported=fs.readFileSync(await download.path(),'utf8');if(!exported.includes('rope-tow')||!exported.includes('Not navigation'))throw Error('Export missing constraints/disclosure');
 await caption('Save the itinerary locally. Its restrictions and simulation warning travel with it.',5);
 await caption('Inspect the AI. Correct the constraints. Take away a plan you can examine.',5);
 if(errors.length)throw Error(errors.join('\n'));
 const video=page.video();await ctx.close();if(video)await video.saveAs('demo/walkthrough.webm');await browser.close();
 const report={scope:'continuous_fixed_frame_real_app_with_presentation_only_DOM_reflow',viewport:{width,height},preview,chapters,pageErrors:errors,windowScrollEvents:0,viewportChanges:0,hardExclusionsVerified:true,correctionExtraInterpretationCalls:0,textExportVerified:true,liveProviderCalls:0};
 fs.writeFileSync(preview?'/tmp/liftlap-fixed-preview.json':'research/evidence/app-integration/fixed-frame-video.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exit(1)});
