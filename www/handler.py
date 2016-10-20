import asyncio

class RequestHandler(object):

    def __init__(self,app,fn):
        self._app =app
        self._func=fn

    @asyncio.coroutine
    def __call__(self,request):
        kw = ...abs
        r = yield from self._func(**kw)
        return r