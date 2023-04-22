from ..models import RegisteredEvent,PublishedEvent,HeldEvent,Attendees
from authentication.models import CustomUser
import qrcode
from cryptography.fernet import Fernet
from django.conf import settings
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from io import BytesIO
from datetime import datetime
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


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
def scan_qr_code(request,event_id):
    # return render(request,'qrCodeTemplates/display_qr_code.html')
    event = get_object_or_404(PublishedEvent, id=event_id)
    held_event=HeldEvent.objects.filter(published_event=event).exists()

    if not held_event:
        HeldEvent.objects.create(published_event=event,number_of_attendees=0)
        event.is_held=True
        event.save()
    return render(request,'qrCodeTemplates/scan_qr_code.html')

@csrf_exempt
@require_POST
def validate_qr_code(request):
    qr_code_data = request.POST.get('qr_code_data')
    if qr_code_data is None:
        return JsonResponse({'success': False, 'error': 'No QR code data provided'})
        # return HttpResponseBadRequest('No QR code data provided')
    
    # Decrypt the QR code data
    try:
        key = settings.QR_CODE_KEY.encode()
        f = Fernet(key)
        decrypted_data = f.decrypt(qr_code_data.encode()).decode()

        # Check if the user and event IDs exist in the RegisteredEvent model
        user_id, event_id = decrypted_data.split(',')
        user = CustomUser.objects.get(id=user_id)
        event = PublishedEvent.objects.get(id=event_id)
        registered_event = RegisteredEvent.objects.filter(user=user, published_event=event).first()

        if not registered_event:
            return JsonResponse({'success': False, 'error': 'User is not registered for this event'})
                
        held_event=HeldEvent.objects.get(published_event=event)
        is_attendee=Attendees.objects.filter(user=user,held_event=held_event).first()
        if is_attendee:
            return JsonResponse({'success': False, 'error': 'QR code is already scanned!'})
        
        Attendees.objects.create(user=user,held_event=held_event)
        RegisteredEvent.objects.get(user=user,published_event=event).delete()

        
        context = {
            'user_email': user.email,
            'scanned_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': True,
        }

        return JsonResponse(context)
        # return render(request,'qrCodeTemplates/scanned_qr_code.html',context)

    except Exception as e:
        print("Decryption error: ", e)
        # return HttpResponse("QR code is invalid")
        return JsonResponse({'success': False, 'error': 'QR code is invalid'})