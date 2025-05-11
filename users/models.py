from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crear y guardar un usuario con el email y password dados"""
        if not email:
            raise ValueError('El Email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crear y guardar un superusuario con el email y password dados"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Modelo de usuario personalizado que usa email como identificador único"""
    
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('judge', 'Juez'),
        ('viewer', 'Visualizador'),
    )
    
    username = None
    email = models.EmailField('Correo Electrónico', unique=True)
    first_name = models.CharField('Nombre', max_length=30)
    last_name = models.CharField('Apellido', max_length=30)
    role = models.CharField('Rol', max_length=20, choices=ROLE_CHOICES, default='viewer')
    
    # Campos adicionales específicos para jueces
    is_judge = models.BooleanField('Es Juez', default=False)
    judge_level = models.CharField('Nivel de Juez', max_length=30, blank=True, null=True)
    judge_license = models.CharField('Licencia de Juez', max_length=30, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        # Asegurar que los usuarios con rol 'judge' tengan is_judge=True
        if self.role == 'judge':
            self.is_judge = True
        super(User, self).save(*args, **kwargs)


class JudgeProfile(models.Model):
    """Perfil adicional para usuarios con rol de juez"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='judge_profile')
    specialty = models.CharField('Especialidad', max_length=100, blank=True, null=True)
    bio = models.TextField('Biografía', blank=True, null=True)
    contact_phone = models.CharField('Teléfono de Contacto', max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Juez'
        verbose_name_plural = 'Perfiles de Jueces'
        
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"