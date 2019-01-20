import asyncio

from aiohttp import web
from aiohttp import request

async def index(request):
    await request
    await asyncio.sleep(0.5)
    return web.Response(content_type='text/html',
                        text='<html><head><title>async io server</title></head><body><h1>hello, aio!</h1></body></html>')


async def hello(request):
    await asyncio.sleep(0.5)
    text = '<html><head><title>async io server</title></head><body><h1>hello, %s!</h1></body></html>' % \
           request.match_info['name']
    return web.Response(text=text, content_type='text/html')


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/hello/{name}', hello)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)
    print('Server started at http://127.0.0.1:8000...')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
