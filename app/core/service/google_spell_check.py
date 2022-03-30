import os
import time

import numpy as np
import pandas as pd
import pygsheets
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from app.settings import get_app_settings

config = get_app_settings()


def fill_google_sheet(df):

    try:
        # Authorization
        client = None
        if os.path.exists(config.CREDENTIALS_JSON_PATH):
            client = pygsheets.authorize(service_file = config.CREDENTIALS_JSON_PATH)
        else:
            client = pygsheets.authorize(service_account_env_var = config.CREDENTIALS_ENV_VAR)

        # Open the google spreadsheet (where config.SHEET_NAME is the name of my sheet)
        spreadsheet = client.open(config.SHEET_NAME)

        # Select the first worksheet and clear it
        wks = spreadsheet[0]
        wks.clear()

        # Increase rows in sheet
        wks.resize(192000)

        df.iloc[:, 1] = df.iloc[:, 1].apply(lambda k: str(k).replace('\r\n', ' '))

        div, rem = len(df) // 191000, len(df) % 191000
        a = 0
        for i in range(div):
            b = a + 191000
            wks.set_dataframe(pd.DataFrame(df.iloc[a : b, 1]), (1, i + 1))
            a = b
        # DO NOT REPLACE "a + rem" WITH "b + rem" AS IT THROWS ERROR!
        wks.set_dataframe(pd.DataFrame(df.iloc[a : a + rem, 1]), (1, div + 1))

        return wks
    except Exception as e:
        print(e)

def mark_bad_words_from_file(df):
    df.replace(np.NaN, '', regex = True, inplace = True)
    # Explicitly mark words from BLACKLIST_WORDS
    print('Marking bad words from file...')
    for i in tqdm(df.index):
        # Creating set and taking intersection to reduce inner for loop iterations
        bad_words = config.BLACKLIST_WORDS & set(df.at[i, df.columns[1]].split())
        for j in bad_words:
            if df.at[i, 'INCORRECT WORDS'] == '':
                df.at[i, 'INCORRECT WORDS'] = j
                df.at[i, 'DESCRIPTION'] = j + ' marked using black-listed words'
            if j not in df.at[i, 'INCORRECT WORDS']:
                df.at[i, 'INCORRECT WORDS'] = df.at[i, 'INCORRECT WORDS'] + ', ' + j
                df.at[i, 'DESCRIPTION'] = (df.at[i, 'DESCRIPTION'] + ', ' + j + ' marked using black-listed words') if df.at[i, 'DESCRIPTION'] != '' else (j + ' marked using black-listed words')
    return df

def run_spell_check(df, browser):
    wks = fill_google_sheet(df)

    df['INCORRECT WORDS'] = '' * len(df)
    df['SUGGESTED WORDS'] = '' * len(df)
    df['DESCRIPTION'] = '' * len(df)

    browser.get(wks.url)
    # Checking if Sheet Title can be changed. This indicates spreadsheet is ready to use.
    title_box = WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.XPATH, "//input[@class='docs-title-input']")))
    ActionChains(browser).key_down(Keys.CONTROL).send_keys(Keys.ARROW_DOWN).key_up(Keys.CONTROL).perform()

    # Tools --> Spelling --> Spell Check
    tools = WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.ID, 'docs-tools-menu')))
    tools.click()
    ActionChains(browser).send_keys(Keys.ENTER, Keys.ARROW_DOWN, Keys.ARROW_DOWN, Keys.ARROW_DOWN, Keys.ARROW_DOWN, Keys.ARROW_DOWN, Keys.ARROW_RIGHT, Keys.ENTER).perform()

    flag = 1
    no_result = None
    ignore_btn = None
    try:
        ignore_btn = WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.ID, 'docs-spellcheckslidingdialog-button-ignore')))
        no_result = WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.ID, 'docs-spellcheckslidingdialog-no-misspellings-footer')))
    except:
        flag = 0

    old_phrase = ''
    old_word = ''
    while(flag and not no_result.is_displayed()):
        suggested_word = ''
        incorrect_phrase = browser.find_element_by_class_name("cell-input").text
        incorrect_word = browser.find_element_by_id("docs-spellcheckslidingdialog-original-word").text
        # 3 attempts to overcome "Stale Element" error
        for _ in range(3):
            try:
                suggested_word = browser.find_element_by_class_name("goog-menuitem-content").text
                break
            except:
                continue

        # For unknown error where incorrect_word is empty even when it is seen in UI. Continue the loop to read it correctly
        if incorrect_word == '':
            time.sleep(1)
            continue

        # Following case indicates that incorrect_word has already been recorded. Hence pressing "Ignore" in UI AND CONTINUING LOOP
        if old_phrase == incorrect_phrase and old_word == incorrect_word:
            if ignore_btn.is_displayed():
                ignore_btn.click()
                continue

        incorrect_word_indices = df.index[df[df.columns[1]] == incorrect_phrase].tolist()
        for i in incorrect_word_indices:

            # Marking incorrect_word
            if df.at[i, 'INCORRECT WORDS'] == '' and incorrect_word not in config.WHITELIST_WORDS:
                df.at[i, 'INCORRECT WORDS'] = incorrect_word
                df.at[i, 'SUGGESTED WORDS'] = suggested_word
            if incorrect_word not in df.at[i, 'INCORRECT WORDS'] and incorrect_word in df.iloc[i, 1] and incorrect_word not in config.WHITELIST_WORDS:
                df.at[i, 'INCORRECT WORDS'] = df.at[i, 'INCORRECT WORDS'] + ', ' + incorrect_word
                df.at[i, 'SUGGESTED WORDS'] = df.at[i, 'SUGGESTED WORDS'] + ', ' + suggested_word

            # Adding description if incorrect_word was not marked because it was present in config.WHITELIST_WORDS
            if df.at[i, 'DESCRIPTION'] == '' and incorrect_word in config.WHITELIST_WORDS:
                df.at[i, 'DESCRIPTION'] = incorrect_word + ' found in white-listed words'
            if df.at[i, 'DESCRIPTION'] != '' and incorrect_word in config.WHITELIST_WORDS:
                df.at[i, 'DESCRIPTION'] = (df.at[i, 'DESCRIPTION'] + ', ' + incorrect_word + ' found in white-listed words') if incorrect_word not in df.at[i, 'DESCRIPTION'] else df.at[i, 'DESCRIPTION']

        if ignore_btn.is_displayed():
            ignore_btn.click()
        else:
            # Adding sleep to allow spell check to search for next incorrect word
            time.sleep(1)
            continue

        old_phrase = incorrect_phrase
        old_word = incorrect_word

    # Reset Sheet
    wks.clear()

    return mark_bad_words_from_file(df)
