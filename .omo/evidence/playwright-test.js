const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const results = {
    test1: { name: 'WA Numbers Page', passed: false, errors: [], details: {} },
    test2: { name: 'Outreach Tracker Page', passed: false, errors: [], details: {} },
    test3: { name: 'Navigation', passed: false, errors: [], details: {} },
    test4: { name: 'Real-time Updates', passed: false, errors: [], details: {} }
  };

  const consoleErrors = [];
  
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  // Capture console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(`[${msg.type()}] ${msg.text()}`);
    }
  });

  page.on('pageerror', error => {
    consoleErrors.push(`[pageerror] ${error.message}`);
  });

  try {
    // TEST 1: WA Numbers Page
    console.log('=== TEST 1: WA Numbers Page ===');
    await page.goto('http://localhost:3456/wa-numbers', { waitUntil: 'networkidle', timeout: 15000 });
    
    // Wait for table to load
    await page.waitForSelector('table tbody tr', { timeout: 10000 });
    
    // Count sessions
    const sessionCount = await page.locator('table tbody tr').count();
    console.log(`Sessions found: ${sessionCount}`);
    results.test1.details.sessionCount = sessionCount;
    
    if (sessionCount < 4) {
      results.test1.errors.push(`Expected >= 4 sessions, found ${sessionCount}`);
    }
    
    // Check for status badges
    const statusBadges = await page.locator('[class*="badge"], [class*="status"]').count();
    console.log(`Status badges found: ${statusBadges}`);
    results.test1.details.statusBadges = statusBadges;
    
    // Check for persona dropdowns
    const personaDropdowns = await page.locator('select, [role="combobox"]').count();
    console.log(`Persona dropdowns found: ${personaDropdowns}`);
    results.test1.details.personaDropdowns = personaDropdowns;
    
    // Try to select persona from first dropdown
    const firstDropdown = page.locator('select').first();
    const dropdownExists = await firstDropdown.count() > 0;
    
    if (dropdownExists) {
      const options = await firstDropdown.locator('option').allTextContents();
      console.log(`Dropdown options: ${options.join(', ')}`);
      
      // Try to select "Skincare Expert"
      const hasSkincareExpert = options.some(opt => opt.includes('Skincare Expert'));
      if (hasSkincareExpert) {
        await firstDropdown.selectOption({ label: 'Skincare Expert' });
        console.log('Selected Skincare Expert');
        await page.waitForTimeout(2000);
        
        // Reload and verify persistence
        await page.reload({ waitUntil: 'networkidle' });
        await page.waitForSelector('table tbody tr', { timeout: 10000 });
        
        const selectedValue = await firstDropdown.inputValue();
        console.log(`Persisted value: ${selectedValue}`);
        results.test1.details.personaPersisted = selectedValue.includes('skincare');
      }
    }
    
    // Take screenshot
    await page.screenshot({ path: '.sisyphus/evidence/wa-numbers-verified.png', fullPage: true });
    console.log('Screenshot saved: wa-numbers-verified.png');
    
    results.test1.passed = sessionCount >= 4 && statusBadges > 0;
    
    // TEST 2: Outreach Tracker Page
    console.log('\n=== TEST 2: Outreach Tracker Page ===');
    const test2ConsoleStart = consoleErrors.length;
    
    await page.goto('http://localhost:3456/outreach-tracker', { waitUntil: 'networkidle', timeout: 15000 });
    
    // Wait for lead table
    await page.waitForSelector('table tbody tr', { timeout: 10000 });
    
    // Count leads
    const leadCount = await page.locator('table tbody tr').count();
    console.log(`Leads found: ${leadCount}`);
    results.test2.details.leadCount = leadCount;
    
    if (leadCount < 10) {
      results.test2.errors.push(`Expected >= 10 leads, found ${leadCount}`);
    }
    
    // Test search
    const searchInput = page.locator('input[type="text"], input[placeholder*="search" i], input[placeholder*="filter" i]').first();
    const searchExists = await searchInput.count() > 0;
    
    if (searchExists) {
      await searchInput.fill('Digital');
      console.log('Typed "Digital" in search');
      await page.waitForTimeout(1000);
      
      const filteredCount = await page.locator('table tbody tr').count();
      console.log(`Filtered leads: ${filteredCount}`);
      results.test2.details.filteredCount = filteredCount;
      results.test2.details.searchWorks = filteredCount < leadCount;
      
      // Clear search
      await searchInput.fill('');
      await page.waitForTimeout(500);
    }
    
    // Click first lead row
    const firstRow = page.locator('table tbody tr').first();
    await firstRow.click();
    console.log('Clicked first lead row');
    
    // Wait for detail panel
    await page.waitForSelector('[role="dialog"], [class*="sheet"], [class*="panel"], [class*="drawer"]', { timeout: 5000 });
    console.log('Detail panel opened');
    
    // Check for panel sections
    const panelText = await page.locator('[role="dialog"], [class*="sheet"], [class*="panel"], [class*="drawer"]').first().textContent();
    
    const hasResearchBrief = panelText.includes('Research Brief') || panelText.includes('Research');
    const hasEmail = panelText.includes('Email');
    const hasWhatsApp = panelText.includes('WhatsApp');
    const hasMessages = panelText.includes('Messages') || panelText.includes('Message');
    
    console.log(`Panel sections - Research: ${hasResearchBrief}, Email: ${hasEmail}, WhatsApp: ${hasWhatsApp}, Messages: ${hasMessages}`);
    
    results.test2.details.panelSections = {
      research: hasResearchBrief,
      email: hasEmail,
      whatsapp: hasWhatsApp,
      messages: hasMessages
    };
    
    // Try to click WhatsApp tab
    const whatsappTab = page.locator('button, [role="tab"]').filter({ hasText: /WhatsApp/i }).first();
    const whatsappTabExists = await whatsappTab.count() > 0;
    
    if (whatsappTabExists) {
      await whatsappTab.click();
      console.log('Clicked WhatsApp tab');
      await page.waitForTimeout(500);
      
      const whatsappContent = await page.locator('[role="tabpanel"], [class*="tab-content"]').first().textContent();
      results.test2.details.whatsappProposalVisible = whatsappContent.length > 50;
      console.log(`WhatsApp proposal length: ${whatsappContent.length} chars`);
    }
    
    // Take screenshot
    await page.screenshot({ path: '.sisyphus/evidence/outreach-tracker-verified.png', fullPage: true });
    console.log('Screenshot saved: outreach-tracker-verified.png');
    
    results.test2.passed = leadCount >= 10 && hasResearchBrief && (hasEmail || hasWhatsApp);
    
    // TEST 3: Navigation
    console.log('\n=== TEST 3: Navigation ===');
    
    const closeButton = page.locator('[data-slot="sheet-close"], button[aria-label*="close" i]').first();
    const closeExists = await closeButton.count() > 0;
    if (closeExists) {
      await closeButton.click();
      console.log('Closed detail panel');
      await page.waitForTimeout(500);
    }
    
    const waNumbersLink = page.locator('a, button').filter({ hasText: /WA Numbers/i }).first();
    const linkExists = await waNumbersLink.count() > 0;
    
    if (linkExists) {
      await waNumbersLink.click();
      console.log('Clicked WA Numbers link');
      await page.waitForTimeout(1000);
      
      const currentUrl = page.url();
      console.log(`Current URL: ${currentUrl}`);
      results.test3.details.url = currentUrl;
      results.test3.passed = currentUrl.includes('/wa-numbers');
      
      await page.waitForSelector('table tbody tr', { timeout: 5000 });
      
      await page.screenshot({ path: '.sisyphus/evidence/navigation-verified.png', fullPage: true });
      console.log('Screenshot saved: navigation-verified.png');
    } else {
      results.test3.errors.push('WA Numbers link not found in sidebar');
    }
    
    // TEST 4: Real-time Updates
    console.log('\n=== TEST 4: Real-time Updates ===');
    const test4ConsoleStart = consoleErrors.length;
    
    const apiCalls = [];
    const requestHandler = request => {
      if (request.url().includes('/api/')) {
        apiCalls.push({ url: request.url(), time: new Date().toISOString() });
      }
    };
    page.on('request', requestHandler);
    
    console.log('Waiting 15 seconds to observe polling...');
    await page.waitForTimeout(15000);
    
    console.log(`API calls observed: ${apiCalls.length}`);
    results.test4.details.apiCalls = apiCalls.length;
    results.test4.details.consoleErrorsDuringPolling = consoleErrors.length - test4ConsoleStart;
    
    results.test4.passed = apiCalls.length > 0 && (consoleErrors.length - test4ConsoleStart) === 0;
    
  } catch (error) {
    console.error('Test execution error:', error.message);
    results.error = error.message;
  } finally {
    await browser.close();
    
    // Write results to JSON
    fs.writeFileSync('.sisyphus/evidence/test-results.json', JSON.stringify({
      timestamp: new Date().toISOString(),
      consoleErrors,
      results
    }, null, 2));
    
    console.log('\n=== SUMMARY ===');
    console.log(`Test 1 (WA Numbers): ${results.test1.passed ? 'PASS' : 'FAIL'}`);
    console.log(`Test 2 (Outreach Tracker): ${results.test2.passed ? 'PASS' : 'FAIL'}`);
    console.log(`Test 3 (Navigation): ${results.test3.passed ? 'PASS' : 'FAIL'}`);
    console.log(`Test 4 (Real-time Updates): ${results.test4.passed ? 'PASS' : 'FAIL'}`);
    console.log(`Console errors: ${consoleErrors.length}`);
    
    process.exit(results.test1.passed && results.test2.passed && results.test3.passed && results.test4.passed ? 0 : 1);
  }
})();
