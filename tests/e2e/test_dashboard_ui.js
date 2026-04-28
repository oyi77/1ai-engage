const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  console.log('Navigating to UI on port 3000...');
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(4000);
  
  const title = await page.title();
  console.log(`Page title: ${title}`);
  
  await page.screenshot({ path: 'dashboard-active.png', fullPage: true });
  console.log('Saved screenshot to dashboard-active.png');
  
  const text = await page.textContent('body');
  console.log(`Contains 'Dashboard': ${text.includes('Dashboard')}`);
  console.log(`Contains 'Lead Funnel': ${text.includes('Lead Funnel') || text.includes('Lead')}`);
  console.log(`Contains '1ai-reach': ${text.includes('1ai-reach')}`);
  
  // Get all card/widget titles to verify data loaded
  const headings = await page.$$eval('h1, h2, h3, h4', els => els.map(e => e.textContent));
  console.log('Headings found:');
  headings.slice(0, 10).forEach(h => console.log(`- ${h.trim()}`));

  await browser.close();
})();
