#!/usr/bin/env python

import asyncio
from botstory import chat, story
from botstory.integrations import aiohttp, fb, mongodb
from botstory.integrations.ga import tracker
from botstory.middlewares import any, text
import logging
import os
import pathlib
# import sys

# Makes able to import local modules
# PACKAGE_PARENT = '..'
# SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
# sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from echo.static_files_extension import static_files

logger = logging.getLogger('echo-bot')
logger.setLevel(logging.DEBUG)

PROJ_ROOT = pathlib.Path(__file__).parent


# define stories

@story.on_start()
def on_start():
    """
    User just pressed `get started` button so we can greet him
    """

    @story.part()
    async def greetings(message):
        await chat.say('Hi There! Nice to see you! ', message['user'])

        await chat.say('I''m very simple bot that show basic features of '
                       'https://github.com/botstory/botstory '
                       'open source platform.', message['user'])

        await chat.say('You can send me any text message and '
                       'I will echo it back to you.', message['user'])

        await chat.say('Any other messages will just bounce '
                       'with trivial answer '
                       'that I don''t know what is it.', message['user'])

        await chat.say('You can find my source here '
                       'https://github.com/botstory/echo-bot.', message['user'])

        await chat.say('Lets make the best bot together!', message['user'])


@story.on(receive=text.Any())
def echo_story():
    """
    React on any text message
    """

    @story.part()
    async def echo(message):
        await chat.say('Hi! I just got something from you:', message['user'])
        await chat.say('> {}'.format(message['data']['text']['raw']), message['user'])


@story.on(receive=any.Any())
def else_story():
    """
    And all the rest messages as well
    """

    @story.part()
    async def something_else(message):
        await chat.say('Hm I don''t know what is it', message['user'])


# setup modules

def init(auto_start=True, fake_http_session=None):
    # Interface for communication with FB
    story.use(fb.FBInterface(
        # will show on initial screen
        greeting_text='Hello dear {{user_first_name}}! '
                      'I'' m demo bot of BotStory framework.',
        # you should get on admin panel for the Messenger Product in Token Generation section
        page_access_token=os.environ.get('FB_ACCESS_TOKEN', 'TEST_TOKEN'),
        # menu of the bot that user has access all the time
        persistent_menu=[{
            'type': 'postback',
            'title': 'Monkey Business',
            'payload': 'MONKEY_BUSINESS'
        }, {
            'type': 'web_url',
            'title': 'Source Code',
            'url': 'https://github.com/botstory/bot-story/'
        }],
        # should be the same as in admin panel for the Webhook Product
        webhook_url='/webhook{}'.format(os.environ.get('FB_WEBHOOK_URL_SECRET_PART', '')),
        webhook_token=os.environ.get('FB_WEBHOOK_TOKEN', None),
    ))

    # Interface for HTTP
    http = story.use(aiohttp.AioHttpInterface(
        port=os.environ.get('API_PORT', 8080),
        auto_start=auto_start,
    ))

    # User and Session storage
    story.use(mongodb.MongodbInterface(
        uri=os.environ.get('MONGODB_URI', 'mongo'),
        db_name=os.environ.get('MONGODB_DB_NAME', 'echobot'),
    ))

    story.use(tracker.GAStatistics(
        tracking_id=os.environ.get('GA_ID'),
    ))

    # for test purpose
    http.session = fake_http_session

    return http


async def setup(fake_http_session=None):
    logger.info('setup')
    init(auto_start=False, fake_http_session=fake_http_session)
    await story.setup()


async def start(auto_start=True, fake_http_session=None):
    http = init(auto_start, fake_http_session)

    logger.debug('static {}'.format(str(PROJ_ROOT.parent / 'static')))

    static_files.add_to(http.app.router, '/',
                        path=str(PROJ_ROOT.parent / 'static'),
                        name='static',
                        )
    # start bot
    await story.start()
    logger.info('started')
    return http.app


async def stop():
    await story.stop()
    # TODO: should be something like
    # story.clear()
    story.middlewares = []


# launch app
def main(forever=True):
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(start(auto_start=forever))

    # and run forever
    if forever:
        story.forever(loop)

    # or you can use gunicorn for an app of http interface
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
