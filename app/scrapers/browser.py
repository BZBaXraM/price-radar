"""Playwright helper for Cloudflare-protected stores (kontakt.az)."""
from __future__ import annotations

from contextlib import asynccontextmanager

_STEALTH_INIT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'languages', {get: () => ['az-AZ', 'az', 'ru', 'en']});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
"""

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


@asynccontextmanager
async def browser_page():
    """Yield a stealth-ish Playwright page; auto-closes browser afterwards.

    Raises ImportError/RuntimeError if Playwright/chromium is unavailable so the
    caller can degrade gracefully and mark the store unavailable.
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        try:
            context = await browser.new_context(
                user_agent=UA,
                locale="az-AZ",
                viewport={"width": 1366, "height": 900},
            )
            await context.add_init_script(_STEALTH_INIT)
            page = await context.new_page()
            yield page
        finally:
            await browser.close()


async def get_rendered_html(url: str, wait_selector: str | None = None, timeout_ms: int = 30000) -> str:
    async with browser_page() as page:
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        # Give Cloudflare challenge time to resolve.
        try:
            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=timeout_ms)
            else:
                await page.wait_for_load_state("networkidle", timeout=timeout_ms)
        except Exception:
            pass
        return await page.content()
