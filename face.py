import base64
import io

import PIL
import cv2
import face_recognition
import mysql
import numpy as np
import pymysql
import operator
import connect


def encoding0_15ToNp_encoding(id):
    sql = "SELECT * FROM person where id=%d" % id
    cursor.execute(sql)
    row = cursor.fetchone()
    # 依次遍历结果集，发现每个元素，就是表中的一条记录，用一个元组来显示
    encodingList = []
    for i in range(0, 16):
        j = i + 4
        encodingList.append(row[j])
    floatList = []
    for item in encodingList:
        strTOlist = item.split(',')
        strTOlist = list(map(eval, strTOlist))
        floatList.append(strTOlist)
    floatList = np.array(floatList)
    floatList = floatList.reshape(128)
    return floatList


conn = connect.init()
cursor = conn.cursor()


def detect(image_path, known_face_encodings, known_face_names, images):
    print("processing picture")

    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    count = str(len(face_locations))
    face_names = []
    photo_str = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        # 摄像中的人脸与已知人脸对比
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        # face_distance用于计算相似度，距离越小越相似
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        # argmin取最小值
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            # known_str = imgToStr(images[best_match_index])  # todo
            known_str = binToStr(images[best_match_index])  # todo
            # photo_encoding=known_face_encodings[best_match_index]
        face_names.append(name)
        # print("known_str:"+known_str)
        photo_str.append(known_str)

    image1 = cv2.imread(image_path)
    # 创建Font对象:
    # font = ImageFont.truetype(font='Arial.ttf', size=36)
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        print(top, right, bottom, left)
        cv2.rectangle(image1, (left, top), (right, bottom), (0, 0, 255), 20)

    # text = 'Number of persons present: '+count
    # cv2.putText(image1, text, (30,30), font, 1.0, (255, 255, 255), 1)
    # 得到写名字的图片
    cv2.imwrite(image_path, image1)
    print("count:" + count)

    return {
        "locations": face_locations,
        "names": face_names,
        "count": count,
        "image_str": imgToStr(image_path),
        "photo_str": photo_str
    }


def imgToStr(image_path):
    with open(image_path, mode='rb') as file:
        img = file.read()
    return base64.encodebytes(img).decode("utf-8")


def binToStr(image_data):
    return base64.encodebytes(image_data).decode("utf-8")


# def on_EVENT_LBUTTONDOWN(event, x, y, flags, param, matches=None):
#     # print("in click function")
#     i=-1
#     if event == cv2.EVENT_LBUTTONDOWN:
#         click_x=x
#         click_y=y
#         for face_location in face_locations:
#             i=i+1
#             top, right, bottom, left = face_location
#             if left<=click_x<=right and top<=click_y<=bottom:
#
#                 click_location=face_location
#                 #点击的人脸的编码
#                 click_encoding=face_encodings[i]
#                 face_distances = face_recognition.face_distance(known_face_encodings, click_encoding)
#                 # # argmin取最小值
#                 index = np.argmin(face_distances)
#                 print(index)
#                 if matches[index]:
#                     #对应预存照片中的人脸编码
#                     known_encoding=known_face_encodings[index]
#                     print(images[index])
#                     im = Image.open(images[index])
#                     #把im（预存的图片）传给client
#                     im.save("knownImage.png",im)
#                     im.show()
#                 face_image = image[top-30:bottom+30, left-30:right+30]
#                 pil_image = Image.fromarray(face_image)
#                 pil_image.show()
#                 break
#             else:
#                 continue

def insertSql(name, img_path):
    # 复制到main里，可插入成功name，img_path要实体化
    img = face_recognition.load_image_file(img_path)
    encoding = face_recognition.face_encodings(img)[0]
    encodings = np.array(encoding).reshape(16, 8)
    encodingList = encodings.tolist()
    strEncodingList = []
    for i in range(0, 16):
        strEncoding = [str(x) for x in encodingList[i]]
        string = ",".join(strEncoding)
        strEncodingList.append(string)
        # print(string)
    fp = open(img_path, 'rb')
    img = fp.read()
    fp.close()
    imgTuple = (name, img_path, pymysql.Binary(img))
    encodingTuple = tuple(strEncodingList)
    tuple1 = imgTuple + encodingTuple
    # print(tuple)
    sql = "INSERT INTO person(name,img_path,img,encoding0,encoding1,encoding2,encoding3,encoding4,encoding5," \
          "encoding6,encoding7,encoding8,encoding9,encoding10,encoding11,encoding12,encoding13,encoding14,encoding15) " \
          "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
    try:
        # 执行sql
        cursor.execute(sql, tuple1)
        conn.commit()
        print("插入数据成功")
    except Exception as e:
        print(e)
        conn.rollback()
        print("插入数据失败")


if __name__ == "__main__":
    known_face_encodings = []
    known_face_names = []
    images = []
    sql = "SELECT * FROM person"
    cursor.execute(sql)
    rows = cursor.fetchall()
    # 依次遍历结果集，发现每个元素，就是表中的一条记录，用一个元组来显示
    for row in rows:
        id = row[0]
        known_face_encodings.append(encoding0_15ToNp_encoding(id))
        name = row[1]
        known_face_names.append(name)
        image_data = row[3]
        images.append(image_data)

    detect("faces/both.jpg", known_face_encodings, known_face_names, images)

    # detect("faces/woman.jpg")
    # insertSql("ysy", "faces/ysy.jpg")
    # insertSql("xm", "faces/xm.jpg")
    # encoding0_15ToNp_encoding(17)
    # print("main()")

    # 用元祖插入数据库
    # img = face_recognition.load_image_file("faces/ysy.jpg")
    # encoding = face_recognition.face_encodings(img)[0]
    # encodings = np.array(encoding).reshape(16, 8)
    # encodingList = encodings.tolist()
    # strEncodingList = []
    # for i in range(0, 16):
    #     strEncoding = [str(x) for x in encodingList[i]]
    #     string = ",".join(strEncoding)
    #     strEncodingList.append(string)
    #     # print(string)
    # fp = open("faces/ysy.jpg", 'rb')
    # img = fp.read()
    # fp.close()
    # imgTuple = ("ysy", "faces/ysy.jpg", pymysql.Binary(img))
    # encodingTuple = tuple(strEncodingList)
    # tuple = imgTuple + encodingTuple
    # # print(tuple)
    # sql = "INSERT INTO person(name,img_path,img,encoding0,encoding1,encoding2,encoding3,encoding4,encoding5,encoding6,encoding7,encoding8,encoding9,encoding10,encoding11,encoding12,encoding13,encoding14,encoding15) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    # try:
    #     # 执行sql
    #     cursor.execute(sql, tuple)
    #     conn.commit()
    #     print("插入数据成功")
    # except Exception as e:
    #     print(e)
    #     conn.rollback()
    #     print("插入数据失败")

    # strEncodingList=['' for i in range]
    # print(strEncodingList)
    # # print(encodingList)
    # encodings=[[] for i in range(10)]
    # encodings[0]=encodingList[0:10]
    # print(encodings[0])
    # print(len(encodings[0]))
    # newEncodingList = [str(x) for x in encodingList]
    # string=",".join(newEncodingList)
    # print(string)

    # strTOlist=string.split(',')
    # print(strTOlist)
    # strTOlist=list(map(eval,strTOlist))
    # print(strTOlist)
    # for item in encodingList:
    #     result+=item
    # print(ecoding)
    # print(type(ecoding))
    # print(encoding)
    # print(type(encoding))

    # np和list相互转换
    # list转numpy
    # np.array(a)
    # ndarray转list
    # a.tolist()

    # 查询row[0]该行的第一列
    # sql = "SELECT *FROM person"
    # cursor.execute(sql)
    # # 打印执行结果的条数
    # print("表格行数：")
    # print(cursor.rowcount)
    # 将所有的结果放入rr中
    # rr = cursor.fetchall()
    # for row in rr:
    #     print("ID是：=%s, img_path是：=%s, name是：=%s" % row)
