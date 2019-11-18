import base64
import cv2
import face_recognition
import numpy as np
import pymysql
import connect

conn = connect.init()
cursor = conn.cursor()

def encoding0_15ToNp_encoding(encodingList):
    floatList = []
    for item in encodingList:
        strTolist = item.split(',')
        strTolist = list(map(eval, strTolist))
        floatList.append(strTolist)
    floatList = np.array(floatList)
    floatList = floatList.reshape(128)
    return floatList


def imgToStr(image_path):
    with open(image_path, mode='rb') as file:
        img = file.read()
    return base64.encodebytes(img).decode("utf-8")


def binToStr(image_data):
    return base64.encodebytes(image_data).decode("utf-8")


# todo: implement detecting Similarity
def detect(image_path, known_face_encodings, known_face_names, images, unknown_str):
    print("processing picture")

    similarities = []

    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    count = str(len(face_locations))
    face_names = []
    photo_str = []

    for face_encoding in face_encodings:
        # init
        name = "Unknown"
        known_str = unknown_str
        # face_compare摄像中的人脸与已知人脸对比
        # face_distance用于计算相似度，距离越小越相似
        # np.argmin取出最小值所在坐标
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        # similarities.append(max(1 - np.linalg.norm(face_encodings - face_encoding, axis=1)))
        similarities.append(1-face_distances[best_match_index])
        # 假如能匹配上，才作修改
        if(1-face_distances[best_match_index]>0.55):
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                known_str = binToStr(images[best_match_index])

        face_names.append(name)
        photo_str.append(known_str)

    new_image = cv2.imread(image_path)
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        print(top, right, bottom, left)
        cv2.rectangle(new_image, (left, top), (right, bottom), (0, 0, 255), 20)
    cv2.imwrite(image_path, new_image)

    print("face_locations: ", face_locations)
    print("face_names: ", face_names)
    print("count: ", count)
    print("similarities: ", similarities)

    return {
        "locations": face_locations,
        "names": face_names,
        "count": count,
        "image_str": imgToStr(image_path),
        "photo_str": photo_str,
        "similarities": similarities
    }


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
    imgTuple = (name, pymysql.Binary(img))
    encodingTuple = tuple(strEncodingList)
    tuple1 = imgTuple + encodingTuple
    # print(tuple)
    sql = "INSERT INTO person(name,img,encoding0,encoding1,encoding2,encoding3,encoding4,encoding5," \
          "encoding6,encoding7,encoding8,encoding9,encoding10,encoding11,encoding12,encoding13,encoding14,encoding15) " \
          "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
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
    unknown_str = imgToStr("faces/Unknown.jpg")

    known_face_encodings = []
    known_face_names = []
    known_face_images = []

    sql = "SELECT * FROM person"
    cursor.execute(sql)
    rows = cursor.fetchall()

    # 依次遍历结果集，发现每个元素，就是表中的一条记录，用一个元组来显示

    for row in rows:
        # row[1] is name
        # row[2] is image in binary data
        # row[3:19] is face_encoding
        known_face_names.append(row[1])
        known_face_images.append(row[2])
        known_face_encodings.append(encoding0_15ToNp_encoding(row[3:19]))

    detect("faces/both.jpg", known_face_encodings, known_face_names, known_face_images, unknown_str)
