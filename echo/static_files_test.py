from aiohttp import web
from . import static_files
import asyncio
import os
import pytest
import shutil
import tempfile


@pytest.fixture(scope='function')
def tmp_dir_path(request):
    """
    Give a path for a temporary directory
    The directory is destroyed at the end of the test.
    """
    # Temporary directory.
    tmp_dir = tempfile.mkdtemp()

    def teardown():
        # Delete the whole directory:
        shutil.rmtree(tmp_dir)

    request.addfinalizer(teardown)
    return tmp_dir


@asyncio.coroutine
async def test_index_html_is_default_file(tmp_dir_path, loop, test_client):
    """
    Tests the operation of static file server.
    Try to access the root of static file server, and make
    sure that correct HTTP statuses are returned depending if we directory
    index should be shown or not.
    """
    # Put a file inside tmp_dir_path:
    my_file_path = os.path.join(tmp_dir_path, 'index.html')
    with open(my_file_path, 'w') as fw:
        fw.write('hello world!')

    app = web.Application(loop=loop)

    # Register global static route:
    # app.router.add_static('/', tmp_dir_path, show_index=True)
    static_files.add_to(app.router, '/', tmp_dir_path, show_index=True)
    client = await test_client(app)

    # Request the root of the static directory.
    r = await client.get('/')
    assert r.status == 200
    assert r.headers['Content-Type'] == 'text/html'
    assert 'hello world!' in await r.text()
    await r.release()
