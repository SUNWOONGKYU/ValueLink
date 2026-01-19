const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    await page.setViewport({ width: 900, height: 800 });

    const htmlPath = path.join(__dirname, 'valuation_post_image.html');
    await page.goto('file://' + htmlPath);

    await page.screenshot({
        path: path.join(__dirname, 'valuation_post_image.png'),
        fullPage: true
    });

    await browser.close();
    console.log('PNG saved: valuation_post_image.png');
})();
