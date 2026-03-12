from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extended user for time tracker. Optional profile fields."""
    timezone = models.CharField(max_length=64, default="UTC", blank=True)

    class Meta:
        db_table = "core_user"


class EntryCategory(models.Model):
    """User-defined task classification (e.g. Work, Personal, Exercise)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entry_categories")
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, blank=True, help_text="Hex color for charts/UI")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Entry categories"
        unique_together = [["user", "name"]]

    def __str__(self):
        return self.name


class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="time_entries")
    category = models.ForeignKey(
        EntryCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="time_entries"
    )
    date = models.DateField(db_index=True)
    description = models.CharField(max_length=500, blank=True)
    completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Display order within same date (lower = higher in list)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_seconds = models.PositiveIntegerField(default=0, help_text="Cached total duration in seconds")

    class Meta:
        ordering = ["-date", "order", "-created_at"]
        verbose_name_plural = "Time entries"

    def __str__(self):
        return f"{self.date} - {self.description or '(no description)'}"

    def _time_to_seconds(self, time_str):
        parts = [int(x) for x in (time_str or "0:0").split(":")]
        h = parts[0] if len(parts) > 0 else 0
        m = parts[1] if len(parts) > 1 else 0
        s = parts[2] if len(parts) > 2 else 0
        return h * 3600 + m * 60 + s

    def recalc_total_seconds(self):
        total = 0
        for p in self.time_periods.all():
            if p.start_time and p.end_time:
                total += max(0, self._time_to_seconds(p.end_time) - self._time_to_seconds(p.start_time))
        self.total_seconds = total
        self.save(update_fields=["total_seconds", "updated_at"])


class TimePeriod(models.Model):
    entry = models.ForeignKey(TimeEntry, on_delete=models.CASCADE, related_name="time_periods")
    start_time = models.CharField(max_length=12)  # "HH:MM" or "HH:MM:SS"
    end_time = models.CharField(max_length=12)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


class PTOEntry(models.Model):
    TYPE_VACATION = "vacation"
    TYPE_SICK = "sick"
    TYPE_PERSONAL = "personal"
    TYPE_CHOICES = [
        (TYPE_VACATION, "Vacation"),
        (TYPE_SICK, "Sick"),
        (TYPE_PERSONAL, "Personal"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pto_entries")
    date = models.DateField(db_index=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "PTO entry"
        verbose_name_plural = "PTO entries"
        constraints = [
            models.UniqueConstraint(fields=["user", "date"], name="unique_user_pto_date"),
        ]

    def __str__(self):
        return f"{self.date} - {self.get_type_display()}"


class PTOPolicy(models.Model):
    """Global or per-year PTO limits. Editable by super admin."""
    year = models.PositiveIntegerField(null=True, blank=True, help_text="Null = default policy")
    vacation_days = models.PositiveSmallIntegerField(default=15)
    sick_days = models.PositiveSmallIntegerField(default=5)
    personal_days = models.PositiveSmallIntegerField(default=5)

    class Meta:
        verbose_name_plural = "PTO policies"
        ordering = ["-year"]

    def __str__(self):
        return f"PTO Policy {self.year or 'default'}"


class PasswordResetCode(models.Model):
    """One-time code for password reset. Sent by email; expires after 1 hour."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_codes")
    code = models.CharField(max_length=8, db_index=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-expires_at"]
