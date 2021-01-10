import os
from typing import List

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from ..core.models.browser import Browser
from ..core.schema.spell_check_schema import SpellCheckResponse
from ..core.service.google_spell_check import run_spell_check
from ..settings import get_app_settings

config = get_app_settings()
router_name = 'Spell Check'
router_description = 'APIs to get spell-check results'
openapi_tag = {'name': router_name, 'description': router_description}
router = APIRouter(prefix = '/spell-check', tags = [router_name])


@router.get("/words/{word}",
            summary = 'Spell-check a single word',
            response_model = SpellCheckResponse,
            response_model_exclude_unset = True)
async def spell_single_word(word: str):
    try:
        browser_object = Browser(google_login_flag = True)
        if not browser_object.google_logged_in:
            browser_object.google_login()
        df = pd.DataFrame(range(1), columns = ['ID'])
        df['ACTUAL WORDS'] = [word]
        df = run_spell_check(df, browser_object.browser)
        df = df[df['INCORRECT WORDS'] != ''].copy()
        incorrect_words = {}
        for i in df.index:
            incorrect_words[df.loc[i, 'ACTUAL WORDS']] = {
                'suggested_word': df.loc[i, 'SUGGESTED WORDS'],
                'description': df.loc[i, 'DESCRIPTION']
            }
        return SpellCheckResponse(incorrect_words = incorrect_words)
    except Exception as e:
        error_message = f"Could not run spell-check due to exception: '{e}'"
        print(error_message)
        raise HTTPException(status_code = 500, detail = error_message)

@router.get("/words",
            summary = 'Spell-check list of words',
            response_model = SpellCheckResponse,
            response_model_exclude_unset = True)
async def spell_word_list(word_list: List[str] = Query(
            [],
            description = "List of words to run spell-check on")):
    try:
        browser_object = Browser(google_login_flag = True)
        if not browser_object.google_logged_in:
            browser_object.google_login()
        df = pd.DataFrame(range(len(word_list)), columns = ['ID'])
        df['ACTUAL WORDS'] = word_list
        df = run_spell_check(df, browser_object.browser)
        df = df[df['INCORRECT WORDS'] != ''].copy()
        incorrect_words = {}
        for i in df.index:
            incorrect_words[df.loc[i, 'ACTUAL WORDS']] = {
                'incorrect_word': df.loc[i, 'INCORRECT WORDS'],
                'suggested_word': df.loc[i, 'SUGGESTED WORDS'],
                'description': df.loc[i, 'DESCRIPTION']
            }
        return SpellCheckResponse(incorrect_words = incorrect_words)
    except Exception as e:
        error_message = f"Could not run spell-check due to exception: '{e}'"
        print(error_message)
        raise HTTPException(status_code = 500, detail = error_message)

@router.get("/file",
            summary = 'Run spell-check on uploaded file',
            response_model = SpellCheckResponse,
            response_model_exclude_unset = True)
async def spell_file(file_name: str = Query(
            ...,
            description = "Name of file to be used as input")):
    try:
        if not os.path.exists(os.path.join(config.UPLOAD_FOLDER, file_name)):
            error_message = f"'{file_name}' does not exist! Use File Input APIs to ensure valid input"
            print(error_message)
            raise HTTPException(status_code = 422, detail = error_message)
        browser_object = Browser(google_login_flag = True)
        if not browser_object.google_logged_in:
            browser_object.google_login()
        if file_name.lower().endswith('.csv'):
            df = pd.read_csv(os.path.join(config.UPLOAD_FOLDER, file_name))
        elif (file_name.lower().endswith('.xlsx')) or file_name.lower().endswith('.xls'):
            df = pd.read_excel(os.path.join(config.UPLOAD_FOLDER, file_name))
        else:
            with open(os.path.join(config.UPLOAD_FOLDER, file_name), 'r') as f:
                word_list = [i.strip('\n\r') for i in f.readlines()]
            df = pd.DataFrame(range(len(word_list)), columns = ['ID'])
            df['ACTUAL WORDS'] = word_list
        df = run_spell_check(df, browser_object.browser)
        df = df[df['INCORRECT WORDS'] != ''].copy()
        incorrect_words = {}
        for i in df.index:
            incorrect_words[df.loc[i, 'ACTUAL WORDS']] = {
                'incorrect_word': df.loc[i, 'INCORRECT WORDS'],
                'suggested_word': df.loc[i, 'SUGGESTED WORDS'],
                'description': df.loc[i, 'DESCRIPTION']
            }
        return SpellCheckResponse(incorrect_words = incorrect_words)
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        error_message = f"Could not run spell-check due to exception: '{e}'"
        print(error_message)
        raise HTTPException(status_code = 500, detail = error_message)
