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

host = '192.168.103.53'
port = 8066
user = 'root'
password = '123456'
db = 'psmc'

rabbitmq = 'localhost'

columns = {
    'Type': {
        # 对应的列
        'corresponding': ['DataType',],
        # 字段类型
        'type': int,
        # 字段长度
        'len': 2
    }
}

filename = 'inserter_' + str(os.getpid()) + '.log'
logging.basicConfig(filename=filename)
logger = logging.getLogger(__name__).setLevel(logging.DEBUG)

class Column(object):
    def __init__(self, name, mtype=None, max_len=None):
        self.name = name
        self.type = mtype
        self.max_len = max_len
        self.value = None
    def check(self, value):
        if value is None:
            self.value = None
            return True
        if value == '':
            self.value == ''
            return True

        if self.type == 'text':
            if isinstance(value, int):
                self.value = str(value)
            elif isinstance(value, datetime.datetime):
                self.value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, str):
                self.value = value
            else:
                logger.debug(" [inserter] ({}-{})Type(text) error!".format(self.name, value))
                return False

        elif self.type == 'string':
            if isinstance(value, int):
                self.value = str(value)
            elif isinstance(value, str):
                if len(value) > self.max_len:
                    logger.debug(" [inserter] ({}-{}) max-length({}), length is too long!".format(self.name, value, self.max_len))
                    return False
                self.value = value
            elif isinstance(value, datetime.datetime):
                self.value = value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                logger.debug(" [inserter] ({}-{})Type(string) error!".format(self.name, value))
                return False

        elif self.type == 'integer':
            if isinstance(value, int):
                self.value = value
            elif isinstance(value, str):
                if len(value) > self.max_len:
                    logger.debug(" [inserter] ({}-{}) max-length({}), length is too long!".format(self.name, value, self.max_len))
                    return False
                if not value.isdigit():
                    logger.debug(" [inserter] ({}-{})Type(integer) error!".format(self.name, value))
                    return False
                self.value = int(value)
            else:
                logger.debug(" [inserter] ({}-{})Type(integer) error!".format(self.name, value))
                return False

        elif self.type == 'datetime':
            if isinstance(value, datetime.datetime):
                self.value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, str):
                # len('2015-04-19 12:20:00') = 20
                if len(value) > 20:
                    logger.debug(" [inserter] ({}-{}) max-length({}), length is too long!".format(self.name, value, self.max_len))
                    return False
                self.value = value
                # self.value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            else:
                logger.debug(" [inserter] ({}-{})Type(integer) error!".format(self.name, value))
                return False
            return True
        else:
            logger.debug(" [inserter] ({}-{})Type(integer) error!".format(self.name, value))
            return False
        return True

# Define columns to check their types and values.
Type = Column('Type', 'integer', 2)
Id = Column('Id', 'string', 64)
Title = Column('Title', 'text')
Author = Column('Author', 'text')
DutyPerson = Column('DutyPerson', 'string', 32)
# OrganizationID = Column('Organization@ID', ['',], 'string', 64)
# AuthorID = Column('Author@ID', ['',], 'string', 64)
# Organization = Column('Organization', ['',], 'string', 255)
Year = Column('Year', 'integer', 8)
PubDate = Column('PubDate', 'datetime')
Issue = Column('Issue', 'string', 64)
# UpdateDate = Column('UpdateDate', ['',], 'datetime')
Keyword = Column('Keyword', 'text')
# Subject = 
# Category = 
# Collection = 
# CategoryName = 
# CollectionName = 
Publisher = Column('Publisher', 'text')
Source = Column('Source', 'text')
# SourceID = 
Summary = Column('Summary', 'text')
FileName = Column('FileName', 'string', 255)
FileFormat = Column('FileFormat', 'integer', 2)
FileSize = Column('FileSize', 'integer', 11)
MediaType = Column('MediaType', 'integer', 2)
Language = Column('Language', 'integer', 2)
DOI = Column('DOI', 'string', 64)
URI = Column('URI', 'text')
# FullText = 
# Fund = 
# FundID =
# DocID = 
Download = Column('Download', 'integer', 11)
Cited = Column('Cited', 'integer', 11)
# VSM = 
# SMARTS = 
# FFD = 
# References = 
PostUser = Column('PostUser', 'string', 64)
# LastPostUser = 
# PostIP = 
PostDate = Column('PostDate', 'datetime')
LocalUpdateDate = Column('LocalUpdateDate', 'datetime')
ServerUpdateDate = Column('ServerUpdateDate', 'datetime')
# Rights = 
# SecurityClassification = 
# IsRecycled = Column('IsRecycled', 'integer', 2)
# IsRemoved = Column('IsRemoved', 'integer', 2)
IsUpdated = Column('IsModify', 'integer', 2)


column_dict = {}
column_dict['DataType'] = Type
column_dict['LiteratureID'] = Id
column_dict['Title'] = Title
column_dict['Author'] = Author
column_dict['DutyPerson'] = DutyPerson
column_dict['Teacher'] = DutyPerson
column_dict['PubYear'] = Year
column_dict['PubTime'] = PubDate
column_dict['Period'] = Issue
column_dict['Keyword'] = Keyword
column_dict['Publisher'] = Publisher
column_dict['Source'] = Source
column_dict['Summary'] = Summary
column_dict['adjunct_AdjunctGuid'] = FileName
column_dict['reader_FileType'] = FileFormat
column_dict['adjunct_FileSize'] = FileSize
column_dict['adjunct_AdjunctType'] = MediaType
column_dict['Doi'] = DOI
column_dict['Link'] = URI
column_dict['DownloadNum'] = Download
column_dict['ReferenceNum'] = Cited
column_dict['UserID'] = PostUser
column_dict['reader_CreateTime'] = PostDate
column_dict['LocalModifyTime'] = LocalUpdateDate
column_dict['ServerModifyTime'] = ServerUpdateDate
# column_dict['IsRecycled'] = IsRecycled
# column_dict['IsRemoved'] = IsRemoved
column_dict['IsModify'] = IsUpdated

metadata = sa.MetaData()
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

def check_handle(queue1, queue2):
    while True:
        data = queue1.get()
        if data is None:
            break
        print('ID: {}'.format(data['LiteratureID']), end=' ...')

        values_dict = {}
        for key in column_dict.keys():
            # print("--", key)
            values_dict.setdefault(column_dict[key].name, None)
        # print(str(values_dict))

        for key,value in data.items():
            if key in column_dict:
                # print("column: ", key)
                if column_dict[key].check(value):
                    values_dict[column_dict[key].name] = column_dict[key].value
                else:
                    values_dict[column_dict[key].name] = None

        # print(str(values_dict))
        queue2.put(values_dict)
        print("Checker completed.")

async def writer(loop, queue):
    engine = await create_engine(user=user, host=host, port=port,
                                 db=db, password=password,
                                 charset='utf8', loop=loop,
                                 autocommit=True)
    async with engine.acquire() as conn:
        while True:
            values_dict = queue.get()
            if values_dict is None:
                break
            # print(document_tb.insert(), values_dict)
            try:
                await conn.execute(document_tb.insert(), values_dict)
            except pymysql.err.IntegrityError as e:
                logger.debug("[inserter] ", values_dict)
    engine.close()
    await engine.wait_closed()

def write_handle(local_queue):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(writer(loop, local_queue))
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
    preader = Process(target=read_handle, args=(Q1,))
    pchecker = Process(target=check_handle, args=(Q1, Q2))
    pwriter = Process(target=write_handle, args=(Q2,))

    preader.start()
    pchecker.start()
    pwriter.start()

    pchecker.join()
    pwriter.join()
    preader.join()