from datetime import datetime
from idlelib.pyparse import trans

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
from django_enumfield import  enum

# Create your models here.
#ENUM
class UserRole(enum.Enum):
    CIVILIAN = 0
    CHARITY_ORG = 1
    ADMIN = 2

class ContentPictureType(enum.Enum):
    CONTENT = 0
    RESULT = 1

class LocationState(enum.Enum):
    NORMAL = 0
    PANDEMIC = 1
    DISASTER = 2

#CLASS MODELS
class BaseModel(models.Model):
    class Meta:
        abstract = True

    id = models.AutoField(primary_key=True)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

class User(AbstractUser):
    birthdate = models.DateField(null=False, default=date(2024, 1, 1))
    address = models.CharField(max_length=100, null=False, default='ABC')
    gender = models.BooleanField(null=False, default=True)
    avatar = CloudinaryField('image', default= None, null=True)
    role = enum.EnumField(UserRole, default=UserRole.CIVILIAN)

    @property
    def name(self):
        return self.last_name + ' ' + self.first_name

    @property
    def image_url(self):
        return self.avatar.url

class Civilian (models.Model):
    user_info = models.OneToOneField(User,related_name="civilian_info",on_delete=models.CASCADE, primary_key=True, null=False)
    money = models.IntegerField(default=0)

class Admin (models.Model):
    user_info = models.OneToOneField(User,related_name="admin_info",on_delete=models.CASCADE, primary_key=True, null=False)

class CharityOrg (models.Model):
    user_info = models.OneToOneField(User,related_name="charity_org_info",on_delete=models.CASCADE, primary_key=True, null=False)
    is_verified = models.BooleanField(default=False)
    badge = models.ForeignKey('Badge', related_name='orgs', on_delete=models.SET_NULL, null=True)

class Chat (BaseModel):
    civilian = models.ForeignKey(Civilian,on_delete=models.CASCADE, null= False, related_name="chat")
    org = models.ForeignKey(CharityOrg, on_delete=models.CASCADE, null= False, related_name="chat")
    firebase_id = models.CharField(max_length=20, null= False)

class Badge (BaseModel):
    tittle = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)

class DonationCampaign (BaseModel):
    org = models.ForeignKey(CharityOrg, on_delete=models.CASCADE, null=False, related_name="campaign")
    content = models.TextField()
    expected_fund = models.IntegerField()
    expected_charity_start_date = models.DateField()
    expected_charity_end_date = models.DateField()
    current_fund = models.IntegerField(default=0)
    is_permitted = models.BooleanField(default=False)
    enclosed_article = models.ManyToManyField('Article', related_name='articles')

class ContentPicture (BaseModel):
    donation = models.ForeignKey(DonationCampaign, on_delete=models.CASCADE, null=False, related_name="pictures")
    type = enum.EnumField(ContentPictureType, default=ContentPictureType.CONTENT)
    path = CloudinaryField('image', default= None, null=True)

class Approval (models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name= 'approvals')
    donation = models.OneToOneField(DonationCampaign, on_delete=models.CASCADE, primary_key=True)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

class Confimation (models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='confirmed')
    donation = models.OneToOneField(DonationCampaign, on_delete=models.CASCADE, primary_key=True)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

class Donation (BaseModel):
    civilian = models.ForeignKey(Civilian, on_delete=models.CASCADE, null=False, related_name="donated")
    campaign = models.ForeignKey(DonationCampaign, on_delete=models.CASCADE, null=False, related_name="donated")
    donated = models.IntegerField()

class Article (BaseModel):
    title = models.CharField(max_length=100)
    brief = models.TextField()
    real_path = models.CharField(max_length=100)

class Comment (BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    content = models.CharField(max_length=100)

class Reply (models.Model):
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE, primary_key=True, null=False, related_name='reply')
    parent = models.OneToOneField(Comment, on_delete=models.CASCADE, null=False, related_name='childs')

class LocationStatus (BaseModel):
    location = models.CharField(max_length=45, unique=True)
    current_status = enum.EnumField(LocationState, default=LocationState.NORMAL)

class StatInfo (BaseModel):
    status = models.ForeignKey(LocationStatus, related_name='stat_info', on_delete=models.CASCADE)
    label = models.CharField(max_length=40)
    number = models.FloatField()