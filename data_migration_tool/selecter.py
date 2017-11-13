# -*- coding: utf-8 -*-
import json
import datetime
from multiprocessing import Process, Queue
import asyncio
import aiomysql
import pika

host = '192.168.106.231'
port = 3306
user = 'root'
password = 'cnkidras'
db = 'recomm'

rabbitmq = 'localhost'

batch = 10 # 测试、调试使用。实际生产环境设置为None.
batch_size = 100

SQL = "select * from el_user_litera_info where UserID in (select UserID from el_user_all_users where FirstLoginTime >'2017-09-02' and FirstLoginTime <'2017-09-03');"

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

async def selecter(pool, queue, batch=None, batch_size=100):
    ''' selecter '''
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.SSDictCursor) as cur:
            await cur.execute(SQL)
            count = 0
            while True:
                # results = await cur.fetchmany(batch_size)
                results = await cur.fetchone()
                count += 1
                # print('count1: ', count)
                # print('select: ', results)
                queue.put(results)

                if batch is None:
                    if results is None:
                        break
                else:
                    if count >= batch:
                        break
            # aiomysql连接池最大连接个数为10，发送10个None让所有连接的关闭。
            # for i in range(10):
            # queue.put(None)

async def select_task(select_loop, queue):
    pool = await create_pool(select_loop, host=host, port=port, \
        user=user, password=password, db=db, connect_timeout=10)
    await selecter(pool, queue, batch, batch_size)
    await destory_pool(pool)

def select_handle(local_queue):
    select_loop = asyncio.get_event_loop()
    select_loop.run_until_complete(select_task(select_loop, local_queue))
    select_loop.close()

def writer_handle(local_queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq))
    channel = connection.channel()
    channel.queue_declare(queue='data_queue', durable=True)
    while True:
        message = local_queue.get()
        if message is None:
            break
        print("message: %s" % message['LiteratureID'])
        for key, value in message.items():
            if isinstance(value, datetime.datetime):
                message[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        channel.basic_publish(exchange='',
            routing_key='data_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2
            ))
    connection.close()

if __name__ == '__main__':
    Q = Queue(10)

    preader = Process(target=select_handle, args=(Q,))
    pwriter = Process(target=writer_handle, args=(Q,))
    preader.start()
    pwriter.start()
    pwriter.join()
    preader.join()
