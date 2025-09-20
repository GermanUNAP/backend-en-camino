from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField
from mongoengine import signals
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import bcrypt

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, Document):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("store_owner", "Store Owner"),
        ("buyer", "Buyer"),
        ("delivery_point", "Delivery Point"),
        ("shipper", "Shipper"),
    )
    
    username = StringField(max_length=150, unique=True, required=True)
    email = EmailField(unique=True, required=True)
    role = StringField(max_length=20, choices=ROLE_CHOICES, default="buyer")
    phone = StringField(max_length=20, blank=True)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_alias = 'default'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @classmethod
    def from_db(cls, db, collection, pk):
        instance = super(CustomUser, cls).from_db(db, collection, pk)
        instance._hashed_password = instance.password
        return instance

    def save(self, *args, **kwargs):
        if not self._hashed_password:
            self.password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())
        super(CustomUser, self).save(*args, **kwargs)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self._hashed_password)