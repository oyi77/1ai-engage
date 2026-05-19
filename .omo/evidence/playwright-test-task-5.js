const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  console.log('=== Scenario 1: View lead list and search ===');
  try {
    page.on('console', msg => console.log('BROWSER:', msg.text()));
    page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
    
    await page.goto('http://localhost:3456/outreach-tracker', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(3000);
    
    const pageContent = await page.content();
    const hasLoader = pageContent.includes('animate-spin');
    if (hasLoader) {
      console.log('⚠ Page is showing loader, waiting for data...');
      await page.waitForTimeout(5000);
    }
    
    const hasTable = await page.locator('table').count() > 0;
    if (!hasTable) {
      console.log('✗ FAIL: Table element not found on page');
      await page.screenshot({ path: '.sisyphus/evidence/task-5-error-no-table.png', fullPage: true });
      await browser.close();
      process.exit(1);
    }
    
    await page.waitForSelector('table tbody tr', { timeout: 10000 });
    
    const initialCount = await page.locator('table tbody tr').count();
    console.log(`✓ Initial lead count: ${initialCount}`);
    
    if (initialCount === 0) {
      console.log('✗ FAIL: No leads found in table');
      await browser.close();
      process.exit(1);
    }
    
    await page.locator('input[placeholder*="Search"]').fill('Digital');
    await page.waitForTimeout(500);
    
    const filteredCount = await page.locator('table tbody tr').count();
    console.log(`✓ Filtered lead count: ${filteredCount}`);
    
    if (filteredCount >= initialCount) {
      console.log('✗ FAIL: Search filter did not reduce results');
      await browser.close();
      process.exit(1);
    }
    
    await page.screenshot({ path: '.sisyphus/evidence/task-5-tracker-search.png', fullPage: true });
    console.log('✓ Screenshot saved: task-5-tracker-search.png');
    console.log('✓ PASS: Search filters lead list correctly\n');
  } catch (error) {
    console.log(`✗ FAIL: ${error.message}`);
    await browser.close();
    process.exit(1);
  }

  console.log('=== Scenario 2: Open lead detail panel and view timeline ===');
  try {
    await page.goto('http://localhost:3456/outreach-tracker', { waitUntil: 'networkidle', timeout: 10000 });
    await page.waitForSelector('table tbody tr', { timeout: 5000 });
    
    await page.locator('table tbody tr:first-child').click();
    await page.waitForSelector('[data-slot="sheet-content"]', { timeout: 3000 });
    console.log('✓ Sheet panel opened');
    
    const researchVisible = await page.locator('h3:has-text("Research Brief")').isVisible();
    if (!researchVisible) {
      console.log('✗ FAIL: Research Brief section not visible');
      await browser.close();
      process.exit(1);
    }
    console.log('✓ Research Brief section visible');
    
    const proposalVisible = await page.locator('h3:has-text("Proposal")').isVisible();
    if (!proposalVisible) {
      console.log('✗ FAIL: Proposal section not visible');
      await browser.close();
      process.exit(1);
    }
    console.log('✓ Proposal section visible');
    
    const whatsappTab = await page.locator('button:has-text("WhatsApp")');
    if (await whatsappTab.count() > 0) {
      await whatsappTab.click();
      await page.waitForTimeout(300);
      console.log('✓ WhatsApp tab clicked');
    }
    
    await page.screenshot({ path: '.sisyphus/evidence/task-5-tracker-detail.png', fullPage: true });
    console.log('✓ Screenshot saved: task-5-tracker-detail.png');
    console.log('✓ PASS: Panel opens with all timeline sections\n');
  } catch (error) {
    console.log(`✗ FAIL: ${error.message}`);
    await browser.close();
    process.exit(1);
  }

  await browser.close();
  console.log('=== All QA scenarios passed ===');
})();
