Echo-bot
========

.. image:: https://travis-ci.org/hyzhak/echo-bot.svg?branch=develop
    :target: https://travis-ci.org/hyzhak/echo-bot

.. image:: https://coveralls.io/repos/github/hyzhak/echo-bot/badge.svg?branch=feature%2Fcov
    :target: https://coveralls.io/github/hyzhak/echo-bot?branch=feature%2Fcov


Very simple example of using `bot-story framework (github.com/hyzhak/bot-story) <https://github.com/hyzhak/bot-story/>`_.
Bot should just replay on received message.

Code
====

Logic
-----

.. code-block:: python

    # define stories

    # React on any text message
    @story.on(receive=text.Any())
    def echo_story():
        @story.part()
        async def echo(message):
            await chat.say('Hi! I just got something from you:', message['user'])
            await chat.say('> {}'.format(message['data']['text']['raw']), message['user'])

    # And all the rest messages as well
    @story.on(receive=any.Any())
    def else_story():
        @story.part()
        async def something_else(message):
            await chat.say('Hm I don''t know what is it', message['user'])


Init
----

.. code-block:: python

    # Interface for communication with FB
    story.use(fb.FBInterface(
        page_access_token='<fb_token>',
        webhook_url='/webhook/<secret_string>',
        webhook_token='webhook_token',
    ))

    # Interface for HTTP
    story.use(aiohttp.AioHttpInterface(
        port=8080,
    ))

    # User and Session storage
    story.use(mongodb.MongodbInterface(
        uri='mongo://localhost',
        db_name='echobot',
    ))

    # Start bot
    await story.start()
