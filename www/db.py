import aiomysql
import logging
import asyncio


def log(sql, args=()):
    logging.info("SQL:%s" % sql)


def creat_args_string(num):
    L = []
    for n in range(num):
        L.append("?")
    return ', '.join(L)

# @asyncio.coroutine
async def creat_pool(loop, **kw):
    logging.info("create database connection pool...")
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get("host", "localhost"),
        port=kw.get("port", 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get("charset", 'utf8'),
        autocommit=kw.get("autocommit", True),
        maxsize=kw.get("maxsize", 10),
        minsize=kw.get("minsize", 1),
        loop=loop
    )

#    @asyncio.coroutine
async def select(sql, args=None, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        # cur =yield from conn.cursor(aiomysql.DictCursor)
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace("?", "%s"), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        # yield from cur.close()
        logging.info("rows returned:%s" % len(rs))
        return rs


@asyncio.coroutine
def execute(sql, args):
    log(sql)
    with(yield from __pool)as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace("?", '%s'), args)
            affected = cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise
        return affected
