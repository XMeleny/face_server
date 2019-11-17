from flask import request, Flask
import time
import os
import base64
import face
import connect

# ******************************************init******************************************
unknown_str = face.imgToStr("faces/Unknown.jpg")

known_face_encodings = []
known_face_names = []
known_face_images = []

conn = connect.init()
cursor = conn.cursor()
sql = "SELECT * FROM person"
cursor.execute(sql)
rows = cursor.fetchall()

for row in rows:
    known_face_names.append(row[1])
    known_face_images.append(row[2])
    known_face_encodings.append(face.encoding0_15ToNp_encoding(row[3:19]))

# ******************************************init******************************************

# turn on the server
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
            return face.detect("result.png", known_face_encodings, known_face_names, known_face_images,unknown_str)
        else:
            return 'fail'
        # todo: deal with the fail situation


if __name__ == "__main__":
    # app.run(port=5000)
    app.run(host="0.0.0.0", port=5000)
