import cv2
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Image
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import firebase_admin
from mtcnn import MTCNN
from firebase_admin import credentials, storage

# Initialize Firebase
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "attendence-jec",
  "private_key_id": "24556db2ac78fdcdc243ce4bc77432102ec974ac",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDflEDfxFTVtmR4\nNKiU7pIsE29T8brXD8kwjbDcXzmKmlQIrJGctYa322qXg+D5i2u+6OsKAKKC3j4u\n5TQZK8ZuryUEm11PNIZAW8xU3EUmhNXhs0EU55FRNzqdKCZYC5ARufijw1c4ZLJq\ncYsyI6/n6zDYzwLgOeOGzNZ76b5cW1CgojugrLRYCmlGaofcD5J+1Zi52b9wu80e\niJ6jMifT41NSrBPLd+1h9S0LpmWFDbEVPERvPrBwVgdL8wDJ4gfdF8jK5ng69yGk\n4Jvq/zFU+NSMuGyiBxsdkMGGOmNzTJIJpQ70JzS8HmawuDp3U9cylWyaOl2Tsw0d\nhMwN77x3AgMBAAECggEAESqo8IV6ng4rGK+yYf0PbCLx4VgmKG0l3XyDn+gP2vyO\nhzv40jd96JAIVynhFEgINdhcc6Ao2jOGQsOGhIg/7C+2f+wN9g7qX/ascbeX96Ur\nZvEEhj5hggLjlT2H9CqvHS1SUgClqcbRjCq7rVXgI8aDMaJzbhQDzE3eChWgcCbN\n8ptOSP0I91j6AlmKuIfanSGuHU/uzHPH77UsNLyJrDPuQR/iJ/os7vWrpJs1DIVx\n21KtbbRORVzY1M83zoQehKo2mv6ja/0ML2sLDBVnxoqMKzGaRpl41IseYa167Byu\nor7KkP5RrsbpNVbf9hsXtiFKlPYKFrc+2sN0pI6ggQKBgQD+nwIfGsuZl+jRH49+\nTol5zASOkqz0vkWSid8xOL1JjXVA/lWbWRPX6vJaPu5h4iA5esA4RwFPiKGrfA/2\nN1EAeL6ydi4VNBCIMvPkPaB8uhXITQBYw+b5lkzi6TaV1Z4pPeADZUqjWi0xOebC\n+HgLGPkH2heSrwxz2m6/Agt/zwKBgQDgyjXXHYUGLYOcdaHMzhrlkgnalfodgEUq\nh8j5UzhOkXBjeKez4A8t06xodUX4qVAK5YxKAEQYYAQ4uegY7sE0h0/3ipV3Pjpu\ne7tYfBm6GiiBlBSYIX79aCHwryIYA9tyL51L388AO6eLH7eOcN2JSmY6Gt0+pRd1\nwFK5NGy62QKBgQDOqa7mIjCI3OSqAAzOvt4UjoRQWDqrd1guxVrzr5LrhTZbZ1OC\ngH17rgXBO/zuU8RGAxzLUM5+iG54Kn0mIeXMFTTq0sM6kISul3Sfl2mQctVFO0KB\nyZfKkrSbJCEa4kS6Qq908hzvkzzFDLMBIv0EPOO7/MdPVmcsDWn//J/qvwKBgQCN\nBe8PHKLmxEkMMDQow6jWG295JZv7RAygaP1phY8Oo2mpzfkP/OIo8uH3ypLyNG5V\n17rSdiZCUIJ1gBQfCDJHnRhLCTNJ0s1foNpg4cJWIbEF0fu1kVYU7m5Ui9rMzCax\nFTQOdMNttv8eZfCHOUGSrw1BKLdiZLo6EkUTkdMgyQKBgCFwdB5L2SWSv6OJxm6N\nGYGo8AOeCHXXoiVytjEehMomTaGSLaBb+jIXgKoKNmDl3i9bv7O3bgiOXvjnBVw0\nF7c7eqp6kJ+ZNzfD9aY+5kI8jgCUAfpPHgtoTlwm4zUF2pJRx30SvleshvXf665P\nFMj7HBedMHPZjNsdf73Th6Mm\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-14xnk@attendence-jec.iam.gserviceaccount.com",
  "client_id": "104927837988307933320",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-14xnk%40attendence-jec.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'attendence-jec.appspot.com'
})

def detect_faces(image_path):
    face_cascade = MTCNN()
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    faces = face_cascade.detect_faces(gray)
    return len(faces[0]) > 0

@csrf_exempt
def handle_image_upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        path = default_storage.save(f'tmp/{image_file.name}', ContentFile(image_file.read()))
        tmp_file = default_storage.path(path)

        if detect_faces(tmp_file):
            bucket = storage.bucket()
            blob = bucket.blob(f'images/{image_file.name}')
            blob.upload_from_filename(tmp_file)

           
            

            return JsonResponse({'status': 'success', 'message': 'Image contains a face and has been saved.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No face detected in the image.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})
