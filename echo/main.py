import asyncio
from botstory import chat, story
from botstory.integrations import aiohttp, fb, mongodb
from botstory.middlewares import any, text
import logging
import os
import pathlib

from . import static_files

logger = logging.getLogger('echo-bot')
logger.setLevel(logging.DEBUG)

PROJ_ROOT = pathlib.Path(__file__).parent


# define stories

@story.on(receive=text.Any())
def echo_story():
    @story.part()
    async def echo(message):
        await chat.say('Hi! I just got something from you:', message['user'])
        await chat.say('> {}'.format(message['data']['text']['raw']), message['user'])


@story.on(receive=any.Any())
def else_story():
    @story.part()
    async def something_else(message):
        await chat.say('Hm I don''t know what is it', message['user'])


# setup modules

async def init(auto_start=True, fake_http_session=None):
    # Interface for communication with FB
    story.use(fb.FBInterface(
        page_access_token=os.environ.get('FB_ACCESS_TOKEN', None),
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

    # Start bot
    await story.start()

    logger.info('started!')

    # for test purpose
    http.session = fake_http_session

    logger.debug('static {}'.format(str(PROJ_ROOT.parent / 'static')))

    # sadly aiohttp doesn't assume that index.html is default name for root page
    # we should expose index.html directory

    static_files.add_to(http.app.router, '/',
                        path=str(PROJ_ROOT.parent / 'static'),
                        name='static',
                        )

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
    app = loop.run_until_complete(init(auto_start=forever))
    if forever:
        story.forever(loop)

    return app


if __name__ == '__main__':
    main(forever=True)
