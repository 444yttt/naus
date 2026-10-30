const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
for(const n of ['a','b','c','d']){await p.goto('file:///home/user/naus/concepts/'+n+'.html');await p.waitForTimeout(300);await p.screenshot({path:`/home/user/naus/concepts/${n}.png`})}await b.close()})()
