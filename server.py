from flask import request, Flask
import time
import os
import base64
import face
import connect

conn = connect.init()
cursor = conn.cursor()
known_face_encodings = []
known_face_names = []
images = []
sql = "SELECT * FROM person"
cursor.execute(sql)
rows = cursor.fetchall()
# 依次遍历结果集，发现每个元素，就是表中的一条记录，用一个元组来显示
for row in rows:
    id = row[0]
    known_face_encodings.append(face.encoding0_15ToNp_encoding(id))
    name = row[1]
    known_face_names.append(name)
    image_data = row[3]
    images.append(image_data)

# todo: modify using id in encoding0_15 to using row

app = Flask(__name__)


@app.route("/", methods=['POST'])
def get_frame():
    if request.method == 'POST':
        print("get photo")
        """from json"""
        # json = request.json
        # if json:
        #     image_data = base64.b64decode(json["image_str"])
        #     file = open('result.png', 'wb')
        #     file.write(image_data)
        #     file.close()
        #     print(json["test_str"])
        #     return 'success'
        # else:
        #     return 'fail'
        """from form"""
        image_str = request.form.get("image_str")
        if image_str:
            image_data = base64.b64decode(image_str)
            file = open('result.png', 'wb')
            file.write(image_data)
            file.close()
            return face.detect("result.png", known_face_encodings, known_face_names, images)
        else:
            return 'fail'
        # todo: deal with the fail situation


if __name__ == "__main__":
    # app.run(port=5000)
    app.run(host="0.0.0.0", port=5000)
