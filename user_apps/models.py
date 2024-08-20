from django.db import models
import uuid, string, random
from google_auth.models import TimestampModel
from google_auth.models import NewUser
# Create your models here.

def generate_unique_id():
    length = 16
    characters = string.ascii_letters + string.digits
    while True:
        unique_id = ''.join(random.choice(characters) for _ in range(length))
        if not user_app.objects.filter(unique_id=unique_id).exists():
            break
    return unique_id

class user_app(TimestampModel):
    app_name = models.CharField(max_length=255)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    
