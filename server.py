from flask import request, Flask
import time
import os
import base64
import face

app = Flask(__name__)


@app.route("/", methods=['POST'])
def get_frame():
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
        face_location = face.locate('result.png')
        return {"locations": face_location}
    else:
        return 'fail'

# todo:return so little thing. Need to return names too.
# todo:deal with the client


if __name__ == "__main__":
    # app.run(port=5000)
    app.run(host="0.0.0.0", port=5000)
