from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=100, blank=True)
    full_editor = models.BooleanField(
        default=False, verbose_name='Es capturista',
        help_text='Puede agregar notas, comentarios a los registros,'
                  'pero no tiene todos los permisos')
    mini_editor = models.BooleanField(
        default=False, verbose_name='Servicio social',
        help_text='Puede modificar ubicaciones y otros detalles')

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name or self.last_name:
            return f"{self.first_name or self.last_name}"
        return self.username or self.email

    @property
    def is_full_editor(self):
        if self.is_anonymous:
            return False
        return self.is_superuser or self.is_staff or self.full_editor

    @property
    def is_admin(self):
        if self.is_anonymous:
            return False
        return self.is_superuser or self.is_staff


