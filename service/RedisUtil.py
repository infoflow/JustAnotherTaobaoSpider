import aioredis

from config import log


class RedisUtil(object):

    def __init__(self, url, loop):
        self.url = url
        self.loop = loop
        self.conn = None

    async def set_cookies(self, username, cookies):
        if self.conn is None:
            self.conn = await self.get_connection()
        resp = await self.conn.execute("hset", "user:cookies", username, cookies)
        if resp == 1:
            log.logger.debug(f"{username}cookies创建成功")
            return True
        elif resp == 0:
            log.logger.debug(f"{username}cookies更新成功")
            return True
        else:
            log.logger.debug(f"{username}cookies存储失败")
            return False

    async def get_connection(self):
        self.conn = await aioredis.create_connection(self.url, loop=self.loop)
        return self.conn

    async def get_password(self, username):
        if self.conn is None:
            await self.get_connection()
        password = await self.conn.execute("hget", "user:password", username)
        return password.decode('utf-8')

    async def get_cookies(self, username):
        if self.conn is None:
            await self.get_connection()
        cookies = await self.conn.execute("hget", "user:cookies", username)
        return cookies.decode('utf-8')

    async def get_accounts(self):
        if self.conn is None:
            self.conn = await self.get_connection()
        usernames = await self.conn.execute("hkeys", "user:password")
        accounts = dict()
        for u in usernames:
            p = await self.get_password(u)
            accounts[u.decode('utf-8')] = p
        return accounts

    async def delete_user(self, name):
        if self.conn is None:
            self.conn = await self.get_connection()
        await self.conn.execute("hdel", "accounts", name)
        await self.conn.execute("hdel", "user_cookies", name)
