from playwright.sync_api import sync_playwright

def before_all(context):
    context.playwright = sync_playwright().start()
    # I used firefox for testing; adapt as needed
    context.browser = context.playwright.firefox.launch(headless=False, slow_mo=500)

def after_all(context):
    context.browser.close()
    context.playwright.stop()

def before_scenario(context, scenario):
    context.page = context.browser.new_page()

def after_scenario(context, scenario):
    context.page.close()