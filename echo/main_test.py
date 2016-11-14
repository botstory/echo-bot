import asyncio
from botstory import story
from botstory.integrations import aiohttp
from botstory.integrations.tests.fake_server import fake_fb
import os
import pytest

from . import main


def teardown_function():
    story.clear(clear_library=False)


NUM_OF_HTTP_REQUEST_ON_START = 6


@pytest.mark.asyncio
async def test_text_echo(event_loop):
    async with fake_fb.FakeFacebook(event_loop) as server:
        async with server.session() as server_session:
            try:
                await main.init(fake_http_session=server_session)

                # send message from user
                http = aiohttp.AioHttpInterface()
                await http.post_raw('http://0.0.0.0:{}/webhook'.format(os.environ.get('API_PORT', 8080)), json={
                    "object": "page",
                    "entry": [{
                        "id": "PAGE_ID",
                        "time": 1458692752478,
                        "messaging": [{
                            "sender": {
                                "id": "USER_ID"
                            },
                            "recipient": {
                                "id": "PAGE_ID"
                            },
                            "timestamp": 1458692752478,
                            "message": {
                                "mid": "mid.1457764197618:41d102a3e1ae206a38",
                                "seq": 73,
                                "text": "hello, world!",
                            }
                        }]
                    }]
                })

                # receive message from bot
                assert len(server.history) == NUM_OF_HTTP_REQUEST_ON_START + 2
                assert await server.history[-2]['request'].json() == {
                    'message': {
                        'text': 'Hi! I just got something from you:'
                    },
                    'recipient': {'id': 'USER_ID'},
                }
                assert await server.history[-1]['request'].json() == {
                    'message': {
                        'text': '> hello, world!'
                    },
                    'recipient': {'id': 'USER_ID'},
                }
            finally:
                await main.stop()


@pytest.mark.asyncio
async def test_should_ignore_like(event_loop):
    async with fake_fb.FakeFacebook(event_loop) as server:
        async with server.session() as server_session:
            try:
                await main.init(fake_http_session=server_session)

                http = aiohttp.AioHttpInterface()
                await http.post_raw('http://0.0.0.0:{}/webhook'.format(os.environ.get('API_PORT', 8080)), json={
                    "entry": [
                        {
                            "id": "329188380752158",
                            "messaging": [
                                {
                                    "message": {
                                        "attachments": [
                                            {
                                                "payload": {
                                                    "sticker_id": 369239263222822,
                                                    "url": "https://scontent.xx.fbcdn.net/t39.1997-6/851557_369239266556155_759568595_n.png?_nc_ad=z-m"
                                                },
                                                "type": "image"
                                            }
                                        ],
                                        "mid": "mid.1477264110799:ac44f49883",
                                        "seq": 50,
                                        "sticker_id": 369239263222822
                                    },
                                    "recipient": {
                                        "id": "329188380752158"
                                    },
                                    "sender": {
                                        "id": "1034692249977067"
                                    },
                                    "timestamp": 1477264110799
                                }
                            ],
                            "time": 1477264110878
                        }
                    ],
                    "object": "page"
                })

                # receive message from bot
                assert len(server.history) == NUM_OF_HTTP_REQUEST_ON_START + 1
                assert await server.history[-1]['request'].json() == {
                    'message': {
                        'text': 'Hm I don''t know what is it'
                    },
                    'recipient': {'id': '1034692249977067'},
                }
            finally:
                await main.stop()


@pytest.mark.asyncio
async def test_on_start(event_loop):
    async with fake_fb.FakeFacebook(event_loop) as server:
        async with server.session() as server_session:
            try:
                await main.init(fake_http_session=server_session)

                http = aiohttp.AioHttpInterface()
                await http.post_raw('http://0.0.0.0:{}/webhook'.format(os.environ.get('API_PORT', 8080)), json={
                    'object': 'page',
                    'entry': [{
                        'id': 'PAGE_ID',
                        'time': 1473204787206,
                        'messaging': [{
                            'sender': {
                                'id': 'USER_ID'
                            },
                            'recipient': {
                                'id': 'PAGE_ID'
                            },
                            'timestamp': 1458692752478,
                            'postback': {
                                'payload': 'BOT_STORY.PUSH_GET_STARTED_BUTTON'
                            }
                        }]
                    }]
                })

                # receive message from bot
                assert len(server.history) > NUM_OF_HTTP_REQUEST_ON_START
                assert await server.history[-1]['request'].json() == {
                    'message': {
                        'text': 'Hi There! Nice to see you here!'
                    },
                    'recipient': {'id': 'USER_ID'},
                }
            finally:
                await main.stop()


async def test_should_expose_static_content_at_the_root(loop, test_client):
    asyncio.set_event_loop(loop)
    async with fake_fb.FakeFacebook(loop) as server:
        async with server.session() as server_session:
            try:
                app = await main.init(fake_http_session=server_session)
                client = await test_client(app)
                # TODO: it looks like bug in aiohttp
                # because this one doesn't work
                resp = await client.get('/')
                # resp = await client.get('/index.html')
                assert resp.status == 200
                assert 'My name is' in await resp.text()
            finally:
                await main.stop()
