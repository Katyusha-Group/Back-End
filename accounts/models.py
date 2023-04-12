import datetime
from django.db import models
from django.contrib.auth.models import  AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError


class User(AbstractUser):
    email = models.EmailField(unique=True)
   
    is_email_verified = models.BooleanField(default=False)
    COMPUTER_ENGINEERING = 'CE'
    ELECTRICAL_ENGINEERING = 'EE'
    MECHANICAL_ENGINEERING = 'ME'
    CIVIL_ENGINEERING = 'CE'
    INDUSTRIAL_ENGINEERING = 'IE'
    CHEMICAL_ENGINEERING = 'CHE'
    MATERIAL_ENGINEERING = 'MATE'
    RAILWAY_ENGINEERING = 'RE'
    COMPUTER_SCIENCE = 'CS'

    DEPARTMENT_CHOICES = [
        (COMPUTER_ENGINEERING, 'Computer Engineering'),
        (ELECTRICAL_ENGINEERING, 'Electrical Engineering'),
        (MECHANICAL_ENGINEERING, 'Mechanical Engineering'),
        (CIVIL_ENGINEERING, 'Civil Engineering'),
        (INDUSTRIAL_ENGINEERING, 'Industrial Engineering'),
        (CHEMICAL_ENGINEERING, 'Chemical Engineering'),
        (MATERIAL_ENGINEERING, 'Material Engineering'),
        (RAILWAY_ENGINEERING, 'Railway Engineering'),
        (COMPUTER_SCIENCE, 'Computer Science'),
    ]
    department = models.CharField(max_length=4, choices=DEPARTMENT_CHOICES)


    

    GENDER_Male = 'M'
    GENDER_Female = 'F'
    GENDER_CHOICES = [
        (GENDER_Female, 'Female'),
        (GENDER_Male, 'Male'),
    ]
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES)
 
    def __str__(self):
        return self.email


