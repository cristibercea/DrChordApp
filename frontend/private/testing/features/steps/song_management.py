import behave.runner, re
from behave import *
from playwright.sync_api import expect

use_step_matcher("re")

@when('upload song (.+) with name (.+) and genre (.+)')
def step_impl(context: behave.runner.Context, file_name: str, name: str, genre: str):
    """
    :type context: behave.runner.Context
    :type file_name: str
    :type name: str
    :type genre: str
    """
    context.page.locator('button:has-text("Upload recording")').click() # Adjust locator
    context.page.locator('input[placeholder="e.g., My Awesome Riff"]').fill(name)
    context.page.locator('input[placeholder="e.g., Acoustic, Rock, Blues"]').fill(genre)
    context.page.locator('input[type="file"]').set_input_files(file_name)
    context.page.locator('button[type="submit"]').click()

@then('see song (.+) in the main page')
def step_impl(context: behave.runner.Context, song_name: str):
    """
    :type context: behave.runner.Context
    :type song_name: str
    """
    expect(context.page.locator(f'text={song_name}')).to_be_visible()

@when('search by name of the song (.+)')
def step_impl(context: behave.runner.Context, search_term: str):
    """
    :type context: behave.runner.Context
    :type search_term: str
    """
    context.page.locator('input[name="search"]').fill(search_term)

@when('edit song genre to (.+)')
def step_impl(context: behave.runner.Context, genre: str):
    """
    :type context: behave.runner.Context
    :type genre: str
    """
    context.page.locator('button:has-text("Edit")').first.click()
    context.page.locator('input[placeholder="e.g., Acoustic, Rock, Blues"]').fill(genre)
    context.page.locator('button:has-text("Save changes")').click()

@when('delete song (.+)')
def step_impl(context: behave.runner.Context, song_name: str):
    """
    :type context: behave.runner.Context
    :type song_name: str
    """
    context.page.once("dialog", lambda dialog: dialog.accept())
    context.page.locator('button:has-text("Delete")').first.click()

@then("should see no recordings text")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    expect(context.page.locator(f'text="No recordings"')).to_be_visible()