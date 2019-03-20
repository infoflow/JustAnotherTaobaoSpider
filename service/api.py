import asyncio
from aiohttp import web

from cookies.TaobaoCookiesGenerator import TaobaoCookiesGenerator
from service.RedisUtil import RedisUtil

routes = web.RouteTableDef()


@routes.get("/user/{name}")
async def user(request):
    name = request.match_info.get('name')
    if name:
        password = await redis_util.get_password(name)
        cookies = await redis_util.get_cookies(name)
        return web.Response(text=f"{name} 的密码为:{password} cookies为 {cookies}")


@routes.delete("/user/{name}")
async def user(request):
    name = request.match_info.get('name')
    if name:
        await redis_util.delete_user(name)
        return web.Response(text=f"{name}已经删除")


@routes.get("/user/{name}/password")
async def user_password(request):
    name = request.match_info.get('name')
    if name:
        password = await redis_util.get_password(name)
        return web.Response(text=f"{name} 的密码为:{password}")
    else:
        return web.Response(text="the username parameters is missing!")


@routes.get("/user/{name}/cookies")
async def user_cookies(request):
    name = request.match_info.get('name')
    if name:
        password = await redis_util.get_cookies(name)
        return web.Response(text=f"{name} 的cookies为:{password}")
    else:
        return web.Response(text="the username parameters is missing!")


@routes.get("/user/{name}/generate_cookies")
async def user_cookies(request):
    name = request.match_info.get('name')
    if name:
        password = await redis_util.get_password(name)
        cookies = cookies_generator.get_cookies(name, password)
        result = await redis_util.set_cookies(name, cookies)
        return web.Response(text=f"{name} 的cookies为生成结果为:{result}")
    else:
        return web.Response(text="the username parameters is missing!")


loop = asyncio.get_event_loop()

redis_util = RedisUtil("redis://localhost:6379", loop)
cookies_generator = TaobaoCookiesGenerator("http://localhost:8080", headless=True)
app = web.Application(loop=loop)
app.add_routes(routes)
web.run_app(app, port=8888)
