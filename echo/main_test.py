from botstory.integrations import aiohttp, fb
from botstory.integrations.tests.fake_server import fake_fb
import os
import pytest

from . import main


@pytest.mark.asyncio
async def test_text_echo(event_loop):
    async with fake_fb.Server(event_loop) as server:
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
                assert len(server.history) == 2
                assert await server.history[0]['request'].json() == {
                    'message': {
                        'text': 'Hi! I just got something from you:'
                    },
                    'recipient': {'id': 'USER_ID'},
                }
                assert await server.history[1]['request'].json() == {
                    'message': {
                        'text': '> hello, world!'
                    },
                    'recipient': {'id': 'USER_ID'},
                }
            finally:
                await main.stop()


@pytest.mark.asyncio
async def test_should_ignore_like(event_loop):
    async with fake_fb.Server(event_loop) as server:
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
                assert len(server.history) == 1
                assert await server.history[0]['request'].json() == {
                    'message': {
                        'text': 'Hm I don''t know what is it'
                    },
                    'recipient': {'id': '1034692249977067'},
                }
            finally:
                await main.stop()
