Echo-bot
========

.. image:: https://travis-ci.org/botstory/echo-bot.svg?branch=develop
    :target: https://travis-ci.org/botstory/echo-bot

.. image:: https://coveralls.io/repos/github/botstory/echo-bot/badge.svg?branch=feature%2Fcov
    :target: https://coveralls.io/github/botstory/echo-bot?branch=feature%2Fcov


Very simple example of using `bot-story framework (github.com/botstory/bot-story) <https://github.com/botstory/bot-story/>`_.
Bot should just replay on received message.

Code
====

Logic
-----

.. code-block:: python

    # Define stories

    # User just pressed `get started` button so we can greet him
    @story.on_start()
    def on_start():
        @story.part()
        async def greetings(message):
            await chat.say('Hi There! Nice to see you here!', message['user'])


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
        # will show on initial screen
        greeting_text='it is greeting message to {{user_first_name}}!',
        # you should get on admin panel for the Messenger Product in Token Generation section
        page_access_token='<fb_token>',
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
        webhook_url='/webhook/<secret_string>',
        webhook_token='webhook_token',
    ))

    # Interface for HTTP
    http = story.use(aiohttp.AioHttpInterface(
        port=8080,
    ))

    # User and Session storage
    story.use(mongodb.MongodbInterface(
        uri='mongo://localhost',
        db_name='echobot',
    ))

    # Start bot
    await story.start()

    # and run forever
    story.forever(loop)

    # or you can use gunicorn for an app of http interface
    app = http.app
