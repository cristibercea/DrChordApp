import behave.runner, re
from behave import *
from playwright.sync_api import expect

use_step_matcher("re")

@given("the user is on the login page")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    context.page.goto("http://localhost:5173/login")

@when('enter email (.+) and password (.+)')
def step_impl(context: behave.runner.Context, email: str, password: str):
    """
    :param password:
    :param email:
    :type context: behave.runner.Context
    """
    context.page.locator('input[type="email"]').fill(email)
    context.page.locator('input[type="password"]').fill(password)

@step("click login button")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    context.page.locator('button[type="submit"]').click()

@then("stays on login page and sees error feedback")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    expect(context.page).to_have_url("http://localhost:5173/login")
    expect(context.page.locator("text=Invalid")).to_be_visible()


@then("proceeds to homepage and sees DeChord logo")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    expect(context.page).to_have_url("http://localhost:5173/")
    expect(context.page.locator("text=My Songs")).to_be_visible()

@when("click logout")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    context.page.locator('button div:has-text("C")').click()
    context.page.locator('ul li').filter(has_text="Log out").click()

@then("the user is redirected to the login page")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    expect(context.page).to_have_url(re.compile(r".*/login"))