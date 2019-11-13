import pymysql


def init():
    connector = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='123456',
        db='faceRecognition',
        charset='utf8'
    )
    return connector

