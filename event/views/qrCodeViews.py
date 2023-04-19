from ..models import RegisteredEvent,PublishedEvent
from authentication.models import CustomUser
import os
import qrcode
import base64
from cryptography.fernet import Fernet
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from io import BytesIO


def test(request,user,event):
     return generate_qr_code(request=request,event_id=event,user_id=user)

def generate_qr_code(request, event_id, user_id):
    # Get the user and event objects
    user = CustomUser.objects.get(id=user_id)
    event = PublishedEvent.objects.get(id=event_id)

    # Generate the QR code data
    qr_code_data = f"{user_id},{event_id}"
    
    # Encrypt the QR code data
    key = settings.QR_CODE_KEY.encode()
    f = Fernet(key)
    encrypted_data = f.encrypt(qr_code_data.encode())
    
    # Generate the QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(encrypted_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the QR code image to the disk
    # filename = f"{event.event.name}_{user.email}.png"
    # filepath = os.path.join(settings.QR_CODE_DIR, filename)
    # img.save(filepath)
    # response = HttpResponse(content_type="image/png")
    # img.save(response, "PNG")
    
    qr_code_buffer = BytesIO()
    img.save(qr_code_buffer, format='PNG')
    qr_code_buffer.seek(0)
    return qr_code_buffer


#scanning.....
def test2(request):
    # return render(request,'qrCodeTemplates/display_qr_code.html')
    return render(request,'qrCodeTemplates/test.html')

def scan_qr_code(request):
    qr_code_data = request.POST.get('qr_code_data')
    print("QR code data: ", qr_code_data)
    if qr_code_data is None:
        return HttpResponseBadRequest('No QR code data provided')
    # Decrypt the QR code data
    try:
        key = settings.QR_CODE_KEY.encode()
        f = Fernet(key)
        decrypted_data = f.decrypt(qr_code_data.encode()).decode()
        print("Decrypted data: ", decrypted_data)
        # Check if the user and event IDs exist in the RegisteredEvent model
        user_id, event_id = decrypted_data.split(',')
        # print(user_id,event_id)
        user = CustomUser.objects.get(id=user_id)
        event = PublishedEvent.objects.get(id=event_id)
        #registered_event = RegisteredEvent.objects.get(user=user, published_event=event)
        return HttpResponse("QR code is valid")
    except Exception as e:
        print("Decryption error: ", e)
        return HttpResponse("QR code is invalid")