# -*- coding: utf-8 -*-
import sys
import os
from multiprocessing import Process, Queue
import asyncio
import aiomysql
import pika
import json
import datetime
import logging

host = '192.168.103.51'
port = 3306
user = 'LibSvr'
password = 'P@$$W0rd'
db = 'el'

rabbitmq = 'localhost'

SQL1 = "SELECT * FROM `el_user_litera_reader_info` WHERE LiteratureID='%s';"
SQL2 = "SELECT * FROM `el_user_adjunct_info` WHERE LiteratureGuid='%s';"

filename = 'updater_' + str(os.getpid()) + '.log'
logging.basicConfig(filename=filename)
logger = logging.getLogger(__name__).setLevel(logging.DEBUG)


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

async def updater(pool, queue1, queue2):
    ''' selecter '''
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.SSDictCursor) as cur:
            while True:
                data = queue1.get()
                if data is None:
                    break
                print('ID: {}'.format(data['LiteratureID']), end=' ...')
                sql1 = SQL1 % data['LiteratureID']
                sql2 = SQL2 % data['LiteratureID']
                # print(sql1)
                await cur.execute(sql1)
                count = 0
                while True:
                    results = await cur.fetchone()
                    if results is None:
                        break
                    count += 1
                    if count > 1:
                        logger.debug(" [updater] Table: \
                            el_user_litera_reader_info, count > 1. ID='%s'", \
                            data['LiteratureID'])
                    else:
                        for key,value in results.items():
                            # if key in data:
                            key = 'reader_' + key
                            data[key] = value

                await cur.execute(sql2)
                count = 0
                while True:
                    results = await cur.fetchone()
                    if results is None:
                        break
                    count += 1
                    if count > 1:
                        logger.debug(" [updater] Table: \
                            el_user_adjunct_info, count > 1. ID='%s'", \
                            data['LiteratureID'])
                    else:
                        for key,value in results.items():
                            # if key in data:
                            key = 'adjunct_' + key
                            data[key] = value
                queue2.put(data)
                print('Update Completed.')

async def update_task(select_loop, queue1, queue2):
    pool = await create_pool(select_loop, host=host, port=port, \
        user=user, password=password, db=db, connect_timeout=10)
    await updater(pool, queue1, queue2)
    await destory_pool(pool)

def update_handle(local_queue1, local_queue2):
    select_loop = asyncio.get_event_loop()
    select_loop.run_until_complete(update_task(select_loop, local_queue1, local_queue2))
    select_loop.close()

def write_handle(local_queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq))
    channel = connection.channel()
    channel.queue_declare(queue='update_data_queue', durable=True)
    while True:
        message = local_queue.get()
        if message is None:
            break
        # print("message: %s" % message['LiteratureID'])
        for key, value in message.items():
            if isinstance(value, datetime.datetime):
                message[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        channel.basic_publish(exchange='',
            routing_key='update_data_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2
            ))
    connection.close()

def read_handle(local_queue1):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq))
    channel = connection.channel()
    channel.queue_declare(queue='data_queue', durable=True)
    print(' [*] Waiting for message. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        # print(" [x] Receive %r" % json.loads(body))
        local_queue1.put(json.loads(body.decode('utf-8')))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='data_queue')
    channel.start_consuming()

if __name__ == '__main__':
    Q1 = Queue(10)
    Q2 = Queue(10)
    preader = Process(target=read_handle, args=(Q1,))
    pupdater = Process(target=update_handle, args=(Q1, Q2))
    pwriter = Process(target=write_handle, args=(Q2,))

    preader.start()
    pupdater.start()
    pwriter.start()

    pupdater.join()
    pwriter.join()
    preader.join()
