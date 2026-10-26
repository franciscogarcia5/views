import asyncio
import random
from playwright.async_api import async_playwright

# ─── TUS 3 URLs ───
URLS = [
    "https://youtube.com/shorts/uNFRmlaXQVs?si=Y9qjOKJg6q0JUg0y",
    "https://www.tiktok.com/@felsedecohogar/video/7699551496840416513",
    "https://www.instagram.com/reel/De8XHkWvlUE/?utm_source=ig_web_copy_link&vrfl=MzRlODBiNWFlZA==&srtk=MzRlODBiNWFlZA==",
]

SESSIONS = 50   # sesiones por job (subí/bajá esto para ajustar volumen)
WATCH = 25      # segundos viendo cada video

MOBILE_UAS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
]

VIEWPORTS = [
    {"width": 390, "height": 844},
    {"width": 412, "height": 915},
    {"width": 393, "height": 852},
]


async def dismiss(page):
    """Cierra cookies, modales y carteles de login."""
    selectors = [
        "button:has-text('Accept all')",
        "button:has-text('Accept All')",
        "button:has-text('Aceptar todo')",
        "button:has-text('Not now')",
        "button:has-text('Not Now')",
        "button:has-text('Ahora no')",
        "div[role='button']:has-text('Not now')",
        "svg[aria-label='Close']",
        "[aria-label='Close']",
        "button[aria-label='Close']",
    ]
    for sel in selectors:
        try:
            el = await page.query_selector(sel)
            if el:
                await el.click(timeout=2500)
                await page.wait_for_timeout(500)
        except Exception:
            pass


async def play(page):
    """Arranca el video si quedó pausado."""
    for sel in ["video", "button[aria-label='Play']", ".ytp-large-play-button"]:
        try:
            el = await page.query_selector(sel)
            if el:
                await el.click(timeout=1500)
                return
        except Exception:
            pass


async def run_session(context):
    page = await context.new_page()
    for url in URLS:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)
            await dismiss(page)
            await play(page)
            await page.wait_for_timeout(WATCH * 1000)
        except Exception as e:
            print("ERR", url, repr(e))
    await page.close()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        for i in range(SESSIONS):
            ctx = await browser.new_context(
                user_agent=random.choice(MOBILE_UAS),
                viewport=random.choice(VIEWPORTS),
                locale="en-US",
                is_mobile=True,
                has_touch=True,
            )
            try:
                await run_session(ctx)
            except Exception as e:
                print("SESSION ERR", repr(e))
            finally:
                await ctx.close()
            print(f"sesion {i + 1}/{SESSIONS}")
        await browser.close()


asyncio.run(main())
