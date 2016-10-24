import models,db
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def test(loop):
    await db.creat_pool(loop=loop,user='www-data',password='www-data',
    db='awesome')

    u = models.User(name='Test',email='test@example.com',
    passwd='1234567890',image='about:blank')

    await u.save()

# 同样的，把函数改成generator后，我们基本上从来不会用next()来获取下一个返回值，而是直接使用for循环来迭代："""
# for x in test(loop):#为什么要用这种方式调用函数
#     pass
loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()

# test sucess
