import { test,expect,type APIRequestContext } from '@playwright/test';
const api='http://127.0.0.1:4175';
async function fresh(request:APIRequestContext,seed:number){await request.post(`${api}/api/scenarios/select`,{data:{seed}});await request.post(`${api}/api/test/reset`);}
test('employee booking updates credits, protected break and live mission control',async({page,request})=>{
 await fresh(request,(page.viewportSize()?.width??1280)<600?20261115:20261114);await page.goto('/#/resort');
 await expect(page.getByRole('heading',{name:'Take a protected break.'})).toBeVisible();
 await page.getByRole('button',{name:'preview & confirm break'}).click();
 await expect(page.getByText('Garden table, held for 2.')).toBeVisible();
 await expect(page.getByText('12 Experience Credits redeemed.')).toBeVisible();
 await expect(page.getByText('clanker · dispatch · accepted')).toBeVisible();
 await page.getByRole('link',{name:/mission control/}).click();
 await expect(page.getByRole('heading',{name:'mission control'})).toBeVisible();
 await expect(page.getByText('1/2',{exact:true})).toBeVisible();
 await expect(page.getByText('1 assigned · 2 in simulated fleet')).toBeVisible();
});
test('engineering scenario selector and guarded actuator fault work on phone viewport',async({page,request})=>{
 await fresh(request,20261116);await page.setViewportSize({width:390,height:844});await page.goto('/#/engineering');
 await page.getByRole('button',{name:'settings'}).click();await page.getByLabel('Simulated role').selectOption('engineer');await page.getByRole('button',{name:'settings'}).click();
 await page.getByLabel('Choose deterministic resort fixture').selectOption('20261116');
 await expect(page.getByText('Percival begins faulted; route coverage to Cogsworth.')).toBeVisible();
 await expect(page.getByText('No eligible coverage unit available')).toHaveCount(0);
 await expect(page.getByRole('button',{name:'verify repair'})).toBeVisible();await page.getByRole('button',{name:'verify repair'}).click();await expect(page.getByRole('button',{name:'inject fault'})).toBeVisible();
 await expect(page.getByText('local simulation connected')).toBeVisible();
});
