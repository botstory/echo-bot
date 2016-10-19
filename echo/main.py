import asyncio
import botstory
from botstory import chat, story
from botstory.integrations import aiohttp, fb, mongodb
from botstory.middlewares import any, text
import logging
import os

logger = logging.getLogger('echo-bot')
logger.setLevel(logging.DEBUG)


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
    async def something_else():
        await chat.say('Hm I don''t know what is it')


# setup modules

async def init(auto_start=True, fake_http_session=None):
    story.use(fb.FBInterface(
        page_access_token=os.environ.get('FB_ACCESS_TOKEN', None),
        webhook_url='/webhook{}'.format(os.environ.get('FB_WEBHOOK_URL_SECRET_PART', '')),
        webhook_token=os.environ.get('FB_WEBHOOK_TOKEN', None),
    ))
    http = story.use(aiohttp.AioHttpInterface(
        port=os.environ.get('API_PORT', 8080),
        auto_start=auto_start,
    ))
    story.use(mongodb.MongodbInterface(
        uri=os.environ.get('MONGODB_URL', 'mongo'),
        db_name='tests',
    ))

    await story.start()

    logger.info('started!')

    # for test purpose
    http.session = fake_http_session

    return http.app


async def stop():
    await botstory.story.stop()


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
