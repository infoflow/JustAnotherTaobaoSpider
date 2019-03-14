import asyncio

import aioredis
import pandas as pd

data = pd.read_csv(r"D:\myworkspace\pythonWorkspace\JustAnotherTaobaoSpider\config\accounts.csv",encoding='utf-8')

loop = asyncio.get_event_loop()


async def init():
    conn = await aioredis.create_connection(
        'redis://localhost:6379', loop=loop)
    accounts = []
    for index, row in data.iterrows():
        accounts.append(row['username'])
        accounts.append(row['password'])
    response = await conn.execute('hmset', 'user:password', *accounts)
    print(type(response))
    print(response)
    conn.close()
    await conn.wait_closed()


loop.run_until_complete(init())
