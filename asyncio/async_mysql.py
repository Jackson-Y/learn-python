#-*- coding: utf-8 -*-
""" MySQL connection pool. """
from multiprocessing import Process, Queue, cpu_count
import asyncio
import aiomysql

async def create_pool(loop, **kw):
    ''' create database connection pool '''
    pool = await aiomysql.create_pool(
        host=kw.get('host', '127.0.0.1'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )
    return pool

async def destory_pool(pool):
    ''' destory connection pool '''
    if pool is not None:
        pool.close()
        await pool.wait_closed()

async def select(pool, sql, queue, batch=None, batch_size=10):
    ''' select XX from XXtable, batch_size rows per time '''
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.SSCursor) as cur:
            await cur.execute(sql)
            count = 0
            while True:
                results = await cur.fetchmany(batch_size)
                count += 1
                print('count1: ', count)
                # print('select: ', results)
                queue.put(results)
                if batch is None:
                    if len(results) < batch_size:
                        break
                else:
                    if count <= batch:
                        break
            # aiomysql连接池最大连接个数为10，发送10个None让所有连接的关闭。
            for i in range(10):
                queue.put(None)

async def insert(pool, sql, queue, autocommit=True):
    ''' insert into XXtable(`XX`,`XX`) values(xxx,xxx),(xxx,xxx) '''
    async with pool.acquire() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.SSCursor) as cur:
                count = 0
                while True:
                    values = queue.get()
                    if values is None:
                        break
                    else:
                        count += 1
                        print('count2: ', count)
                        print('values: ', values[0])
                        await cur.executemany(sql, values)
                        affected = cur.rowcount
                        print('affected: ', affected)
            if not autocommit:
                await conn.commit()
        except BaseException:
            if not autocommit:
                await conn.rollback()
SQL = {
    # 专题1 psmc_user_study_group <--- el_user_cel_info
    'group_cel_info': {
        'select_sql': 'SELECT \
                        `CelID`, `CelName`, `UserID`, \
                        `CreateTime`, `LocalModifyTime`, `ServerModifyTime`, \
                        `IsRecycled`, `IsRemoved`, `IsModify` \
                        from `el_user_cel_info`',
        'insert_sql': "INSERT INTO `psmc_user_study_group`( \
                        `GroupId`, `GroupName`, `GroupPath`, `UserName`, \
                        `CTime`, `UTime`, `ServerModifyTime`, \
                        `IsRecycled`, `IsRemoved`, `IsModify`) \
                        values(%s, %s, '', %s, %s, %s, %s, %s, %s, %s)",
        'merge_handle': None
    },
    # 专题2 psmc_user_study_group <--- el_user_category
    'group_category': {
        'select_sql': 'SELECT \
                        `CategoryID`, `CategoryName`, `UserID`, \
                        `ParentID`, `RecycleID`, `CreateTime`, `LocalModifyTime`, \
                        `ServerModifyTime`, `IsRecycled`, `IsRemoved`, `IsModify` \
                        from `el_user_category`',
        'insert_sql': "INSERT ignore INTO `psmc_user_study_group`( \
                        `GroupId`, `GroupName`, `GroupPath`, `UserName`, \
                        `ParentId`, `RecycleId`, `CTime`, `UTime`, \
                        `ServerModifyTime`, `IsRecycled`, `IsRemoved`, `IsModify`) \
                        values(%s, %s, '', %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        'merge_handle': None
    },

    # others
    'other': {
        'select_sql': None,
        'insert_sql': None,
        'merge_handle': None
    }
}

async def select_task(loop, queue):
    ''' The task to select data from E-Study. '''
    sql = SQL['group_category']['select_sql']
    pool = await create_pool(loop, host='192.168.106.231', port=3306, \
        user='root', password='cnkidras', db='recomm', connect_timeout=10)
    await select(pool, sql, queue, None, 100)
    await destory_pool(pool)

async def insert_task(loop, queue):
    ''' The task to insert data to PSMC. '''
    sql = SQL['group_category']['insert_sql']
    pool = await create_pool(loop, host='192.168.106.231', port=3306, \
        user='root', password='cnkidras', db='psmc', connect_timeout=10)
    await insert(pool, sql, queue)
    await destory_pool(pool)

def insert_thread(queue):
    '''' thread insert '''
    insert_loop = asyncio.get_event_loop()
    insert_loop.run_until_complete(insert_task(insert_loop, queue))
    insert_loop.close()

def select_thread(queue):
    '''' thread select '''
    select_loop = asyncio.get_event_loop()
    select_loop.run_until_complete(select_task(select_loop, queue))
    select_loop.close()

if __name__ == '__main__':
    Q = Queue(10)

    preader = Process(target=select_thread, args=(Q,))
    pwriter = Process(target=insert_thread, args=(Q,))
    preader.start()
    pwriter.start()
    pwriter.join()
    preader.join()
