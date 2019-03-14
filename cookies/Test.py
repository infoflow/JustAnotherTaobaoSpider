import asyncio

from cookies.TaobaoCookiesGenerator import TaobaoCookiesGenerator
from service.RedisUtil import RedisUtil

loop = asyncio.get_event_loop()
from config import log

if __name__ == "__main__":
    log.logger.debug("启动...")
    accounts_util = RedisUtil("redis://localhost:6379", loop=loop)
    # 账号数据存储在redis中 (先运行account_import 将账号数据初始到redis中)
    user_password = loop.run_until_complete(accounts_util.get_accounts())
    log.logger.debug("获取账号数据:" + str(user_password))
    user_cookies = dict()
    cookiesGen = TaobaoCookiesGenerator("http://localhost:8080", headless=True)
    loop.run_until_complete(
        asyncio.gather(*[accounts_util.set_cookies(username, cookiesGen.get_cookies(username, password))
                         for username, password in user_password.items()]))
