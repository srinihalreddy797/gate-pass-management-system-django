from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        SECURITY = "SECURITY", "Security"
        USER = "USER", "User"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER,
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Pass(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    pass_id = models.CharField(max_length=10, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="passes",
    )
    purpose = models.TextField()
    department = models.CharField(max_length=120)
    out_time = models.DateTimeField()
    return_time = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.pass_id

    def save(self, *args, **kwargs):
        if not self.pass_id:
            self.pass_id = self.generate_pass_id()
        super().save(*args, **kwargs)

    @classmethod
    def generate_pass_id(cls):
        prefix = "GP2026"
        with transaction.atomic():
            latest_pass = (
                cls.objects.select_for_update()
                .filter(pass_id__startswith=prefix)
                .order_by("-id")
                .first()
            )
            next_number = 1
            if latest_pass and latest_pass.pass_id:
                next_number = int(latest_pass.pass_id[-4:]) + 1
            return f"{prefix}{next_number:04d}"


class Log(models.Model):
    gate_pass = models.ForeignKey(
        Pass,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Log for {self.gate_pass.pass_id}"
