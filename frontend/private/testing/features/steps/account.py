import behave.runner, re
from behave import *
from playwright.sync_api import expect

use_step_matcher("re")

@when("navigate to account details")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    context.page.locator('button div:has-text("C")').click()
    context.page.locator('ul a').filter(has_text="Account Settings").click()

@then("see account details")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    expect(context.page).to_have_url(re.compile(r".*/profile"))

@when('edit account name to (.+) and confirm action via current password (.+)')
def step_impl(context: behave.runner.Context, new_name: str, password: str):
    """
    :type context: behave.runner.Context
    :type new_name: str
    :type password: str
    """
    context.page.locator('input[type="text"]').fill(new_name)
    context.page.locator('input[placeholder="Enter current password to save changes"]').fill(password)
    context.page.locator('button:has-text("Save changes")').click() # Adjust locator

@when("navigate back to home")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    context.page.locator('text=DrChord').click() # Clicking the Navbar logo