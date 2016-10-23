from botstory.integrations import aiohttp, fb
from botstory.integrations.tests.fake_server import fake_fb
import pytest

from . import main


@pytest.mark.asyncio
async def test_text_echo(event_loop):
    try:
        async with fake_fb.Server(event_loop) as server:
            async with server.session() as server_session:
                await main.init(fake_http_session=server_session)

                # send message from user
                http = aiohttp.AioHttpInterface()
                await http.post_raw('http://localhost:8080/webhook', json={
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
