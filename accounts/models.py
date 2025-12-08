from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import BaseModel


class User(AbstractUser, BaseModel):
    ROLE_MEMBER = 'member'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = (
        (ROLE_MEMBER, 'Member'),
        (ROLE_ADMIN, 'Administrator'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)

    @property
    def is_admin(self) -> bool:
        return self.role == self.ROLE_ADMIN or self.is_staff

    def __str__(self) -> str:
        return f'{self.username} ({self.get_role_display()})'


