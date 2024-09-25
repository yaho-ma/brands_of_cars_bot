import re, logging

from datetime import date
from typing import Final
import validators
from analyze_page import get_page_content, analyze_brands_with_bs4, analyze_page_with_selenium
from sql import add_user_query_toDb, show_history, show_todays_history, show_history_for_current_week
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from api_key import TOKEN, BOT_USERNAME, GOOGLE_API_KEY, CUSTOM_SEARCH_ENGINE_ID

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# search function


def search_brand(brand_name):
    lowered_brand_name = brand_name.lower()

    # get results from 0 to 10
    url_1 = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={CUSTOM_SEARCH_ENGINE_ID}&q={lowered_brand_name}&num=10&start=1"
    response_1 = requests.get(url_1)

    # get requests from 10 to 20
    url_2 = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={CUSTOM_SEARCH_ENGINE_ID}&q={lowered_brand_name}&num=10&start=11"
    response_2 = requests.get(url_2)

    if response_1.status_code == 200 and response_2.status_code == 200:
        search_results_1 = response_1.json().get('items', [])
        search_results_2 = response_2.json().get('items', [])

        return search_results_1 + search_results_2
    return []


def filter_social_networks(results):
    social_media_links = []
    social_media_patterns = [
        r'(https?://(?:www\.)?facebook\.com/[\w.-]+)',  ## https? - s? is optional
        r'https?://(?:www\.)?instagram\.com/[A-Za-z0-9._-]+/?',  ## it ?:www\. can be URL with or without www
        r'(https?://(?:www\.)?twitter\.com/[\w.-]+)',
        ## twitter\.com - this matches the twitter.com - he \. escapes the dot, ensuring it is treated as a literal dot and not as "any character."
        r'(https?://(?:www\.)?linkedin\.com/[\w.-]+)',
        r'(https?://(?:www\.)?youtube\.com/[\w.-]+)'
    ]

    for one_result in results:
        link = one_result.get('link')
        for pattern in social_media_patterns:
            if re.search(pattern, link):
                social_media_links.append(link)
                break  ### terminates the inner for loop once a match is found
    return social_media_links


### -- COMMANDS -- ###############################################################################################
### 1) command /brand

async def brand_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        logger.error("Received an update without a message")
        return

    # insert the user input to the database
    message_from_user = update.message.text
    add_user_query_toDb(message_from_user)
    print(f'user input added to DB: "{message_from_user}" ')

    if len(context.args) == 0:
        await update.message.reply_text('please enter the name of the brand: /brand <name_of_brand>')
        return

    brand_name = ' '.join(context.args)
    await update.message.reply_text(f'Searching the brand: {brand_name.lower()}...')

    results = search_brand(brand_name)  ### calling search brand function with the brand form user
    social_links = filter_social_networks(results)

    if social_links:
        await update.message.reply_text('here are your social media links:')
        for link in social_links:
            await update.message.reply_text(link)
    else:
        await update.message.reply_text('Cannot find any links.')


### 2) command /page
async def analyze_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        logger.error('Got an update without a message')
        return

    message_from_user = update.message.text
    add_user_query_toDb(message_from_user)
    print(f'user input added to DB: "{message_from_user}" ')

    if len(context.args) == 0:
        await update.message.reply_text('Please enter the page URL like this: /page <url>')
        return

    url = context.args[0]

    if not validators.url(url):
        await update.message.reply_text("The URL you entered is not valid. Please enter a valid URL")
        return
    await update.message.reply_text(f'Analyzing the page: {url}')

    # page_content = analyze_page_with_selenium(url)
    page_content = get_page_content(url)

    if page_content:
        sorted_brand_counts = analyze_brands_with_bs4(page_content)

        table_text = "| Brand: | Times mentioned |\n"
        table_text += "-------------------------------\n"
        for brand, count in sorted_brand_counts:
            table_text += f"| {brand} --> {count} times         \n"

        await update.message.reply_text(table_text)


    else:
        await update.message.reply_text('Failed to fetch the message page content')


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_history = show_history()

    if all_history:
        history_message = '\n'.join(all_history)
        await update.message.reply_text(history_message)
    else:
        await update.message.reply_text('No history found')


async def show_history_for_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history_today = show_todays_history()

    await update.message.reply_text(history_today)


async def show_history_for_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history_for_week = show_history_for_current_week()
    await  update.message.reply_text(history_for_week)


##### -- MAIN -- ######################################################################################################


def main():
    application = Application.builder().token(TOKEN).build()

    # commands
    application.add_handler(CommandHandler('brand', brand_search))
    application.add_handler(CommandHandler('page', analyze_page))
    application.add_handler(CommandHandler('history', history))
    application.add_handler(CommandHandler('history_for_today', show_history_for_today))
    application.add_handler(CommandHandler('history_for_week', show_history_for_week))

    print('Polling...')
    application.run_polling(poll_interval=2)


if __name__ == '__main__':
    main()
