import behave.runner, re
from behave import *
from playwright.sync_api import expect

use_step_matcher("re")

@when('trigger generate tabs for (.+)')
def step_impl(context: behave.runner.Context, song_name: str):
    context.page.locator('button:has-text("Generate Tab")').first.click()

@when("filter by songs that have tabs")
def step_impl(context: behave.runner.Context):
    context.page.locator('select').select_option("yes")

@when('wait until tabs generation is done for (.+)')
def step_impl(context: behave.runner.Context, song_name: str):
    with context.page.expect_event("dialog", timeout=60000) as dialog_info: pass
    dialog = dialog_info.value
    dialog.accept()

@when('click see tabs for (.+)')
def step_impl(context: behave.runner.Context, song_name: str):
    context.page.locator('button:has-text("View Tablature")').first.click()

@then("should be on the tabs page")
def step_impl(context: behave.runner.Context):
    expect(context.page).to_have_url(re.compile(r".*/tabs/.*"))