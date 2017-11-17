# -*- coding: utf-8 -*-
import os
import sys
from multiprocessing import Process, Queue
import asyncio
import pymysql
import aiomysql
import pika
import json
import datetime
import logging
import sqlalchemy as sa
from aiomysql.sa import create_engine
from relationship import column_dict, extra_key, extra_column

host = '192.168.103.53'
port = 8066
user = 'root'
password = '123456'
db = 'psmc'
rabbitmq = 'localhost'

filename = 'inserter_' + str(os.getpid()) + '.log'
logging.basicConfig(filename=filename)

metadata = sa.MetaData()

document_extra = sa.Table('document_extra_data', metadata,
                          sa.Column('ID', sa.String(64),primary_key=True),
                          sa.Column('KeyID', sa.Integer,primary_key=True),
                          sa.Column('Name', sa.String(64)),
                          sa.Column('Value', sa.Text))

document_tb = sa.Table('document', metadata,
                    sa.Column('Id', sa.String(255), primary_key=True),
                    sa.Column('Type', sa.Integer),
                    sa.Column('Title', sa.Text),
                    sa.Column('Author', sa.Text),
                    sa.Column('DutyPerson', sa.String(32)),
                    sa.Column('Year', sa.Integer),
                    sa.Column('PubDate', sa.DateTime),
                    sa.Column('Issue', sa.String(64)),
                    sa.Column('Keyword', sa.Text),
                    sa.Column('Publisher', sa.Text),
                    sa.Column('Source', sa.Text),
                    sa.Column('Summary', sa.Text),
                    sa.Column('FileName', sa.String(255)),
                    sa.Column('FileFormat', sa.Integer),
                    sa.Column('FileSize', sa.Integer),
                    sa.Column('MediaType', sa.Integer),
                    sa.Column('DOI', sa.String(64)),
                    sa.Column('URI', sa.Text),
                    sa.Column('Download', sa.Integer),
                    sa.Column('Cited', sa.Integer),
                    sa.Column('PostUser', sa.String(64)),
                    sa.Column('PostDate', sa.DateTime),
                    sa.Column('LocalUpdateDate', sa.DateTime),
                    sa.Column('ServerUpdateDate', sa.DateTime),
                    sa.Column('IsModify', sa.Integer))

def check_handle(queue1, queue2, queue3):
    while True:
        data = queue1.get()
        if data is None:
            break
        print('ID: {}'.format(data['LiteratureID']), end=' ... ')

        values_dict = {}
        for key in column_dict.keys():
            values_dict.setdefault(column_dict[key].name, None)

        extra_values_dict = {}

        for key,value in data.items():
            if key in column_dict:
                if column_dict[key].check(value):
                    values_dict[column_dict[key].name] = column_dict[key].value
                else:
                    values_dict[column_dict[key].name] = None 
            else:
                if key in extra_column:
                    if value is not None and value != '':
                        if extra_key[extra_column[key]]['Checker'].check(value):
                            extra_values_dict['Value'] = extra_key[extra_column[key]]['Checker'].value
                        else:
                            extra_values_dict['Value'] = None
                        extra_values_dict['ID'] = data['LiteratureID']
                        extra_values_dict['KeyID'] = extra_key[extra_column[key]]['id']
                        extra_values_dict['Name'] = extra_column[key]
                    
        # print(str(values_dict))
        queue2.put(values_dict)
        if extra_values_dict is not None:
            queue3.put(extra_values_dict)
        print("Checker completed.")

async def writer(loop, queue, table):
    engine = await create_engine(user=user, host=host, port=port,
                                 db=db, password=password,
                                 charset='utf8', loop=loop,
                                 autocommit=True)
    async with engine.acquire() as conn:
        while True:
            insert_dict = queue.get()
            if insert_dict is None:
                break
            # print(document_tb.insert(), insert_dict)
            try:
                await conn.execute(table.insert(), insert_dict)
            except Exception as e:
                print(' [inserter]: %s' % e)
                logging.debug(' [inserter]: %s', e)
    engine.close()
    await engine.wait_closed()

def write_handle(local_queue, table):
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(*[writer(loop, local_queue, table), ])
    loop.run_until_complete(tasks)
    loop.close()

def read_handle(local_queue1):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq))
    channel = connection.channel()
    channel.queue_declare(queue='update_data_queue', durable=True)
    print(' [*] Waiting for message. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        data = json.loads(body.decode('utf-8'))
        # print(" [x] Receive %r" % data)
        local_queue1.put(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='update_data_queue')
    channel.start_consuming()

if __name__ == '__main__':
    print("Encoding: ", sys.getdefaultencoding())
    Q1 = Queue(10)
    Q2 = Queue(10)
    Q3 = Queue(50)
    preader = Process(target=read_handle, args=(Q1,))
    pchecker = Process(target=check_handle, args=(Q1, Q2, Q3))
    pwriter = Process(target=write_handle, args=(Q2, document_tb))
    pwriter2 = Process(target=write_handle, args=(Q3, document_extra))

    preader.start()
    pchecker.start()
    pwriter.start()
    pwriter2.start()

    pchecker.join()
    pwriter.join()
    preader.join()
    pwriter2.join()
