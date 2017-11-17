#-*- coding:utf-8 -*-
from checker import Checker

# 通用表字段
# Define Checkers to check their types and values.
Type = Checker('Type', 'integer', 2)
Id = Checker('Id', 'string', 64)
Title = Checker('Title', 'text')
Author = Checker('Author', 'text')
DutyPerson = Checker('DutyPerson', 'string', 32)
# OrganizationID = Checker('Organization@ID', ['',], 'string', 64)
# AuthorID = Checker('Author@ID', ['',], 'string', 64)
# Organization = Checker('Organization', ['',], 'string', 255)
Year = Checker('Year', 'integer', 8)
PubDate = Checker('PubDate', 'datetime')
Issue = Checker('Issue', 'string', 64)
# UpdateDate = Checker('UpdateDate', ['',], 'datetime')
Keyword = Checker('Keyword', 'text')
# Subject = 
# Category = 
# Collection = 
# CategoryName = 
# CollectionName = 
Publisher = Checker('Publisher', 'text')
Source = Checker('Source', 'text')
# SourceID = 
Summary = Checker('Summary', 'text')
FileName = Checker('FileName', 'string', 255)
FileFormat = Checker('FileFormat', 'integer', 2)
FileSize = Checker('FileSize', 'integer', 11)
MediaType = Checker('MediaType', 'integer', 2)
Language = Checker('Language', 'integer', 2)
DOI = Checker('DOI', 'string', 64)
URI = Checker('URI', 'text')
# FullText = 
# Fund = 
# FundID =
# DocID = 
Download = Checker('Download', 'integer', 11)
Cited = Checker('Cited', 'integer', 11)
# VSM = 
# SMARTS = 
# FFD = 
# References = 
PostUser = Checker('PostUser', 'string', 64)
# LastPostUser = 
# PostIP = 
PostDate = Checker('PostDate', 'datetime')
LocalUpdateDate = Checker('LocalUpdateDate', 'datetime')
ServerUpdateDate = Checker('ServerUpdateDate', 'datetime')
# Rights = 
# SecurityClassification = 
# IsRecycled = Checker('IsRecycled', 'integer', 2)
# IsRemoved = Checker('IsRemoved', 'integer', 2)
IsUpdated = Checker('IsModify', 'integer', 2)

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

# 扩展字段 及其对应的index和原始数据表中的字段名
## 原始数据表中的字段，el_user_litera_reader_info中的，前边加'reader_'
## 原始数据表中的字段，el_user_adjunct_info中的，前边加'adjunct_'
extra_key = {
    'Adjunct':{
        'Checker': Checker('reader_Adjunct', 'text'),
        'id': 1,
        'name': 'reader_Adjunct',
    },
    'ApplicationNum':{
        'Checker': Checker('ApplicationNum', 'text'),
        'id': 2,
        'name': 'ApplicationNum' ## 对应el_user_litera_info表中的字段'ApplicationNum'
    },
    'City':{
        'Checker': Checker('City', 'text'),
        'id': 3,
        'name': 'City'
    },
    'Country': {
        'Checker': Checker('Country', 'text'),
        'id': 4,
        'name': 'Country'
    },
    'CountryEn': {
        'Checker': Checker('CountryEn', 'text'),
        'id': 5,
        'name': 'CountryEn'
    },
    'Degree': {
        'Checker': Checker('Degree', 'text'),
        'id': 6,
        'name': 'Degree'
    },
    'DegreeType': {
        'Checker': Checker('DegreeType', 'text'),
        'id': 7,
        'name': 'DegreeType'
    },
    'Department': {
        'Checker': Checker('Department', 'text'),
        'id': 8,
        'name': 'Department'
    },
    'EAuthor': {
        'Checker': Checker('EAuthor', 'text'),
        'id': 9,
        'name': 'EAuthor'
    },
    'EPublisher': {
        'Checker': Checker('EPublisher', 'text'),
        'id': 10,
        'name': 'EPublisher'
    },
    'EPubLocate': {
        'Checker': Checker('EPubLocate', 'text'),
        'id': 11,
        'name': 'EPubLocate'
    },
    'ETitle': {
        'Checker': Checker('ETitle', 'text'),
        'id': 12,
        'name': 'ETitle'
    },
    'FileCode': {
        'Checker': Checker('adjunct_AdjunctGuid', 'text'),
        'id': 13,
        'name': 'adjunct_AdjunctGuid'
    },
    'FilePath': {
        'Checker': Checker('FilePath', 'text'),
        'id': 14,
        'name': 'FilePath'
    },
    'ImportantDegree': {
        'Checker': Checker('ImportantDegree', 'text'),
        'id': 15,
        'name': 'ImportantDegree'
    },
    'InternationalClassification': {
        'Checker': Checker('InternationalClassification', 'text'),
        'id': 16,
        'name': 'InternationalClassification'
    },
    'IsModify': {
        'Checker': Checker('IsModify', 'text'),
        'id': 17,
        'name': 'IsModify'
    },
    'IsRead': {
        'Checker': Checker('reader_IsRead', 'text'),
        'id': 18,
        'name': 'reader_IsRead'
    },
    'Issn': {
        'Checker': Checker('Issn', 'text'),
        'id': 19,
        'name': 'Issn'
    },
    'KnowledgeID': {
        'Checker': Checker('KnowledgeID', 'text'),
        'id': 20,
        'name': 'KnowledgeID' ## 对应el_user_litera_info表中的字段'KnowledgeID'
    },
    'LastReadPos': {
        'Checker': Checker('reader_LastReadPos', 'text'),
        'id': 21,
        'name': 'reader_LastReadPos'
    },
    'LastReadTime': {
        'Checker': Checker('reader_LastReadTime', 'text'),
        'id': 22,
        'name': 'reader_LastReadTime'
    },
    'Lcid': {
        'Checker': Checker('Lcid', 'text'),
        'id': 23,
        'name': 'Lcid'
    },
    'Locked': {
        'Checker': Checker('reader_Locked', 'text'),
        'id': 24,
        'name': 'reader_Locked'
    },
    'MarkPos': {
        'Checker': Checker('reader_MarkPos', 'text'),
        'id': 25,
        'name': 'reader_MarkPos'
    },
    'MaxReadProcess': {
        'Checker': Checker('reader_MaxReadProcess', 'text'),
        'id': 26,
        'name': 'reader_MaxReadProcess'
    },
    'Md5': {
        'Checker': Checker('adjunct_Md5', 'text'),
        'id': 27,
        'name': 'adjunct_Md5'
    },
    'Media': {
        'Checker': Checker('Media', 'text'),
        'id': 28,
        'name': 'Media'
    },
    'MediaAddressEn': {
        'Checker': Checker('MediaAddressEn', 'text'),
        'id': 29,
        'name': 'MediaAddressEn'
    },
    'MediaEn': {
        'Checker': Checker('MediaEn', 'text'),
        'id': 30,
        'name': 'MediaEn'
    },
    'NoteGuid': {
        'Checker': Checker('adjunct_NoteGuid', 'text'),
        'id': 31,
        'name': 'adjunct_NoteGuid'
    },
    'Page': {
        'Checker': Checker('Page', 'text'),
        'id': 32,
        'name': 'Page'
    },
    'PageCount': {
        'Checker': Checker('PageCount', 'text'),
        'id': 33,
        'name': 'PageCount'
    },
    'Prints': {
        'Checker': Checker('Prints', 'text'),
        'id': 34,
        'name': 'Prints'
    },
    'PublicationDate': {
        'Checker': Checker('PublicationDate', 'text'),
        'id': 35,
        'name': 'PublicationDate'
    },
    'PubLocate': {
        'Checker': Checker('PubLocate', 'text'),
        'id': 36,
        'name': 'PubLocate'
    },
    'ReadingProgress': {
        'Checker': Checker('reader_ReadingProgress', 'text'),
        'id': 37,
        'name': 'reader_ReadingProgress'
    },
    'RecentReadTime': {
        'Checker': Checker('RecentReadTime', 'text'),
        'id': 38,
        'name': 'RecentReadTime' ## 对应el_user_litera_info表中的字段'RecentReadTime'
    },
    'Remark': {
        'Checker': Checker('reader_Remark', 'text'),
        'id': 39,
        'name': 'reader_Remark'
    },
    'Roll': {
        'Checker': Checker('Roll', 'text'),
        'id': 40,
        'name': 'Roll'
    },
    'SrcDataBase': {
        'Checker': Checker('SrcDataBase', 'text'),
        'id': 41,
        'name': 'SrcDataBase'
    },
    'URI_TableName': {
        'Checker': Checker('TableName', 'text'),
        'id': 42,
        'name': 'TableName' ## 对应el_user_litera_info表中的字段'TableName'
    },
    'URI_FileName': {
        'Checker': Checker('FileName', 'text'),
        'id': 43,
        'name': 'FileName' ## 对应el_user_litera_info表中的字段'FileName'
    },
    'VersionEn': {
        'Checker': Checker('VersionEn', 'text'),
        'id': 44,
        'name': 'VersionEn' ## 对应el_user_litera_info表中的字段'VersionEn'
    },
    'Versions': {
        'Checker': Checker('Versions', 'text'),
        'id': 45,
        'name': 'Versions' ## 对应el_user_litera_info表中的字段'Versions'
    },
    'AdjunctFileName': {
        'Checker': Checker('adjunct_FileName', 'text'),
        'id': 46,
        'name': 'adjunct_FileName' ## 对应el_user_litera_info表中的字段'FileName'
    }
}

extra_column = {}
for key,value in extra_key.items():
    extra_column[value['name']] = key
