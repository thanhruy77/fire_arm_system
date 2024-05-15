from ultralytics import YOLO
import cvzone
import cv2
import math
import firebase_admin
from firebase_admin import credentials, storage, db
from datetime import datetime ,timedelta
import uuid
import serial

# ser = serial.Serial('COM6', '9600')


# Khởi tạo Firebase App
cred = credentials.Certificate("datn-fire-2024-firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'datn-fire-2024.appspot.com',
    'databaseURL': 'https://datn-fire-2024-default-rtdb.firebaseio.com/'
})
# Kết nối tới Firebase Storage
bucket = storage.bucket()
TIME_INTERVAL_MINUTES = 5
expiration_time = datetime.now() + timedelta(days=365*100)
def main():
    cap = cv2.VideoCapture(0)
    model = YOLO('fire.pt')
    classnames = ['fire']

    last_save_time = datetime.now() - timedelta(minutes=TIME_INTERVAL_MINUTES)
    while True:
        ret, image = cap.read()
        image = cv2.resize(image, (640, 480))
        result = model(image, stream=True)
        for info in result:
            boxes = info.boxes
            for box in boxes:
                confidence = box.conf[0]
                confidence = math.ceil(confidence * 100)
                Class = int(box.cls[0])
                if confidence > 80:
                    current_time = datetime.now()
                    # Kiểm tra nếu đã đủ thời gian để lưu ảnh mới
                    if (current_time - last_save_time).total_seconds() >= TIME_INTERVAL_MINUTES * 60:
                        checkfire = db.reference('checkfire')
                        checkfire.set(1)

                        # Lưu URL vào Firebase Realtime Database
                        ref = db.reference('fire/' + datetime.now().strftime("%d-%m-%Y"))

                        random_filename = str(uuid.uuid4())
                        image_filename = f"fire_{random_filename}.jpg"
                        cv2.imwrite(f"img/fire_{random_filename}.jpg", image)
                        # Lưu ảnh vào Firebase Storage
                        blob = bucket.blob(image_filename)
                        blob.upload_from_filename(f"img/fire_{random_filename}.jpg")
                        # Lấy URL của ảnh từ Firebase Storage
                        image_url = blob.generate_signed_url(expiration=expiration_time)
                        image_data = {
                            'img': image_url,
                            'fire': 1,
                            'date': datetime.now().strftime("%d-%m-%Y")
                        }
                        ref.push(image_data)
                        last_save_time = current_time
                    # ser.write(b'true')
                    x, y, w, h = box.xyxy[0]
                    x, y, w, h = int(x), int(y), int(w), int(h)
                    cv2.rectangle(image, (x, y), (w, h), (0, 0, 255), 5)
                    print('tdxywh:', x, y, w, h)
                    cvzone.putTextRect(image, f'{classnames[Class]} {confidence}%', [x + 8, y + 100],
                                       scale=1.5, thickness=2)

        cv2.imshow('image', image)
        k = cv2.waitKey(1)
        if k % 256 == 27:
            print("Close")
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
