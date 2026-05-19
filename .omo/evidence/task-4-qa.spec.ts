import { test, expect } from '@playwright/test';

test.describe('WAHA Assignments Page', () => {
  test('should display all WAHA sessions with live status', async ({ page }) => {
    await page.goto('http://localhost:3456/wa-numbers');
    
    await page.waitForSelector('table tbody tr', { timeout: 10000 });
    
    const rows = await page.locator('table tbody tr').count();
    expect(rows).toBeGreaterThanOrEqual(4);
    
    const firstStatus = await page.locator('table tbody tr:first-child td:nth-child(4) .inline-flex').textContent();
    expect(firstStatus).toMatch(/WORKING|SCAN_QR_CODE|FAILED|STOPPED|UNKNOWN/);
    
    await page.screenshot({ path: '.sisyphus/evidence/task-4-wa-numbers-list.png', fullPage: true });
  });

  test('should update persona assignment and persist after reload', async ({ page }) => {
    await page.goto('http://localhost:3456/wa-numbers');
    
    await page.waitForSelector('table tbody tr', { timeout: 10000 });
    
    const firstSelect = page.locator('table tbody tr:first-child button[role="combobox"]').first();
    await firstSelect.click();
    
    await page.waitForSelector('[role="option"]', { timeout: 5000 });
    await page.locator('[role="option"]:has-text("Skincare Expert")').click();
    
    await page.waitForTimeout(2000);
    
    await page.reload();
    await page.waitForSelector('table tbody tr', { timeout: 10000 });
    
    const selectedValue = await page.locator('table tbody tr:first-child button[role="combobox"]').first().textContent();
    expect(selectedValue).toContain('Skincare Expert');
    
    await page.screenshot({ path: '.sisyphus/evidence/task-4-persona-update.png', fullPage: true });
  });
});
