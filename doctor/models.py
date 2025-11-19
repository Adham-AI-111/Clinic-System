from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, role='patient', **extra_fields):
        """
        Create and save a regular user.
        Views will handle role-specific logic (password requirements, etc.)
        """
        if not phone:
            # TODO: should i tpye that here, while i can add parameter require=true in the model?
            raise ValueError('The phone field must be set')
        
        # Set defaults
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        # Set role
        extra_fields['role'] = role
        
        # If no password provided, generate random one (for patients)
        # ! is that apply on other users
        if password is None:
            password = get_random_string(length=15)
        
        # Create user
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        """Create and save a superuser (admin access only)."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        if password is None:
            raise ValueError('Superuser must have a password')
        
        return self.create_user(phone, password=password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [('admin', 'Admin'), ('doctor', 'Doctor'), ('reception', 'Reception'), ('patient', 'Patient')]
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default='patient')
    # one source phone field to use it in authentication
    phone = PhoneNumberField(region="EG", unique=True)  # add region="EG" 
    username = None
 
    USERNAME_FIELD = 'phone' # when register a superuser
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return str(self.phone)

class Doctor(models.Model):
    name = models.CharField(max_length=30)
    # phone = PhoneNumberField(region="EG")  # add region="EG" 
    major = models.CharField(max_length=50)
    addresses = models.CharField(max_length=70)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Reception(models.Model):
    name = models.CharField(max_length=30)
    # phone = PhoneNumberField(region="EG")
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Patient(models.Model):
    name = models.CharField(max_length=30)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])  # max digit
    # phone = PhoneNumberField(region="EG")  # add region="EG" 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    APPOINT_STATUS = [('Completed', 'Completed'), ('Pending', 'Pending'), ('Canceled', 'Canceled')]
    # i will use this field to handle the appointments date operation like order matter in home page
    created_at = models.DateTimeField(auto_now_add=True)
    # date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=12, choices=APPOINT_STATUS, default='Pending')
    is_prior = models.BooleanField(default=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at'] # the newest first
     
    def __str__(self):
        return f"{self.date} - {self.status}"



class Diagnosis(models.Model):
    diagnosis = models.TextField(max_length=200)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.diagnosis[:15]


class Prescription(models.Model):
    prescription = models.TextField(max_length=100)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
