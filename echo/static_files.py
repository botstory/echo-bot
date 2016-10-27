"""
TODO: move to separate pip module
"""

from aiohttp.file_sender import FileSender
from aiohttp.web_exceptions import (HTTPExpectationFailed, HTTPForbidden,
                                    HTTPMethodNotAllowed, HTTPNotFound)
from aiohttp.web_reqrep import Response, StreamResponse
from aiohttp.web_urldispatcher import AbstractResource, ResourceRoute, UrlMappingMatchInfo
import asyncio
from pathlib import Path
from yarl import URL, quote, unquote


def add_to(router, prefix, path, *, name=None, expect_handler=None,
           chunk_size=256 * 1024, response_factory=StreamResponse,
           show_index=False, follow_symlinks=False):
    """Add static files view.
    prefix - url prefix
    path - folder with files
    """
    # TODO: implement via PrefixedResource, not ResourceAdapter
    assert prefix.startswith('/')
    if not prefix.endswith('/'):
        prefix += '/'
    resource = StaticResource(prefix, path,
                              name=name,
                              expect_handler=expect_handler,
                              chunk_size=chunk_size,
                              response_factory=response_factory,
                              show_index=show_index,
                              )
    router._reg_resource(resource)
    return resource


class PrefixResource(AbstractResource):
    def __init__(self, prefix, *, name=None):
        assert prefix.startswith('/'), prefix
        assert prefix.endswith('/'), prefix
        super().__init__(name=name)
        self._prefix = quote(prefix, safe='/')
        self._prefix_len = len(self._prefix)


class StaticResource(PrefixResource):
    def __init__(self, prefix, directory, *, name=None,
                 expect_handler=None, chunk_size=256 * 1024,
                 response_factory=StreamResponse,
                 show_index=False):
        super().__init__(prefix, name=name)
        try:
            directory = Path(directory)
            if str(directory).startswith('~'):
                directory = Path(os.path.expanduser(str(directory)))
            directory = directory.resolve()
            if not directory.is_dir():
                raise ValueError('Not a directory')
        except (FileNotFoundError, ValueError) as error:
            raise ValueError(
                "No directory exists at '{}'".format(directory)) from error
        self._directory = directory
        self._file_sender = FileSender(resp_factory=response_factory,
                                       chunk_size=chunk_size)
        self._show_index = show_index
        self._routes = {'GET': ResourceRoute('GET', self._handle, self,
                                             expect_handler=expect_handler),

                        'HEAD': ResourceRoute('HEAD', self._handle, self,
                                              expect_handler=expect_handler)}

    def url(self, *, filename, query=None):
        return str(self.url_for(filename=filename).with_query(query))

    def url_for(self, *, filename):
        if isinstance(filename, Path):
            filename = str(filename)
        while filename.startswith('/'):
            filename = filename[1:]
        url = self._prefix + quote(filename, safe='/')
        return URL(url)

    def get_info(self):
        return {'directory': self._directory,
                'prefix': self._prefix}

    @asyncio.coroutine
    def resolve(self, method, path):
        allowed_methods = {'GET', 'HEAD'}
        if not path.startswith(self._prefix):
            return None, set()

        if method not in allowed_methods:
            return None, allowed_methods

        match_dict = {'filename': unquote(path[self._prefix_len:])}
        return (UrlMappingMatchInfo(match_dict, self._routes[method]),
                allowed_methods)

    def __len__(self):
        return len(self._routes)

    def __iter__(self):
        return iter(self._routes.values())

    @asyncio.coroutine
    def _handle(self, request):
        filename = unquote(request.match_info['filename'])
        try:
            filepath = self._directory.joinpath(filename).resolve()
        except (ValueError, FileNotFoundError) as error:
            # relatively safe
            raise HTTPNotFound() from error
        except Exception as error:
            # perm error or other kind!
            request.app.logger.exception(error)
            raise HTTPNotFound() from error

        # on opening a dir, load it's contents if allowed
        if filepath.is_dir():
            if self._show_index:
                try:
                    ret = yield from self._file_sender.send(request, self._directory.joinpath(filename) / 'index.html')
                except PermissionError:
                    raise HTTPForbidden()
            else:
                raise HTTPForbidden()
        elif filepath.is_file():
            ret = yield from self._file_sender.send(request, filepath)
        else:
            raise HTTPNotFound

        return ret

    def __repr__(self):
        name = "'" + self.name + "'" if self.name is not None else ""
        return "<StaticResource {name} {path} -> {directory!r}".format(
            name=name, path=self._prefix, directory=self._directory)
