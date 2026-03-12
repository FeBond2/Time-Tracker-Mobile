from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import TimeEntry, TimePeriod, PTOEntry, PTOPolicy, EntryCategory, PasswordResetCode
from .serializers import (
    TimeEntrySerializer,
    UserSerializer,
    RegisterSerializer,
    PTOEntrySerializer,
    PTOPolicySerializer,
    EntryCategorySerializer,
)

User = get_user_model()


class APIRootView(APIView):
    """Simple root so GET /api/ returns 200 and confirms the API is up."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"ok": True, "message": "Time Tracker API"})


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        user = ser.save()
        tokens = get_tokens_for_user(user)
        return Response(
            {"user": UserSerializer(user).data, **tokens},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        import random
        import string
        email = (request.data.get("email") or "").strip().lower()
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email__iexact=email).first()
        if user:
            code = "".join(random.choices(string.digits, k=6))
            expires_at = timezone.now() + timezone.timedelta(hours=1)
            PasswordResetCode.objects.filter(user=user).delete()
            PasswordResetCode.objects.create(user=user, code=code, expires_at=expires_at)
            subject = "Time Tracker — Password reset code"
            message = f"Your password reset code is: {code}\n\nIt expires in 1 hour. If you didn't request this, you can ignore this email."
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@timetracker.app")
            try:
                send_mail(subject, message, from_email, [user.email], fail_silently=False)
            except Exception:
                if settings.DEBUG:
                    print(f"[Password reset] Code for {user.email}: {code}")
                pass
        return Response({"detail": "If an account exists with that email, you will receive a reset code shortly."})


class ResetPasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = (request.data.get("code") or "").strip()
        new_password = request.data.get("new_password")
        if not code or not new_password:
            return Response(
                {"detail": "Code and new_password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(new_password) < 8:
            return Response(
                {"detail": "Password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        record = PasswordResetCode.objects.filter(code=code).first()
        if not record:
            return Response({"detail": "Invalid or expired code."}, status=status.HTTP_400_BAD_REQUEST)
        if timezone.now() > record.expires_at:
            record.delete()
            return Response({"detail": "Invalid or expired code."}, status=status.HTTP_400_BAD_REQUEST)
        record.user.set_password(new_password)
        record.user.save()
        record.delete()
        return Response({"detail": "Password has been reset. You can log in with your new password."})


class TimeEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = TimeEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimeEntry.objects.filter(user=self.request.user).select_related("category")

    def perform_create(self, serializer):
        serializer.save()


class TimeEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TimeEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimeEntry.objects.filter(user=self.request.user).select_related("category")


class EntryCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = EntryCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EntryCategory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class EntryCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EntryCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EntryCategory.objects.filter(user=self.request.user)


class PTOEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = PTOEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PTOEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class PTOEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PTOEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PTOEntry.objects.filter(user=self.request.user)


class PTOSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get("year")
        if not year:
            year = timezone.now().year
        try:
            year = int(year)
        except ValueError:
            year = timezone.now().year
        entries = PTOEntry.objects.filter(user=request.user, date__year=year)
        vacation = entries.filter(type=PTOEntry.TYPE_VACATION).count()
        sick = entries.filter(type=PTOEntry.TYPE_SICK).count()
        personal = entries.filter(type=PTOEntry.TYPE_PERSONAL).count()
        policy = PTOPolicy.objects.filter(year__isnull=True).first() or PTOPolicy.objects.filter(year=year).first()
        if policy:
            limits = {"vacation": policy.vacation_days, "sick": policy.sick_days, "personal": policy.personal_days}
        else:
            limits = {"vacation": 15, "sick": 5, "personal": 5}
        return Response(
            {
                "year": year,
                "totals": {"vacation": vacation, "sick": sick, "personal": personal},
                "limits": limits,
            }
        )


class PTOPolicyView(APIView):
    """Read-only for authenticated users; super admin edits via Django admin."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get("year")
        if year:
            try:
                year = int(year)
                policy = PTOPolicy.objects.filter(year=year).first() or PTOPolicy.objects.filter(year__isnull=True).first()
            except ValueError:
                policy = PTOPolicy.objects.filter(year__isnull=True).first()
        else:
            policy = PTOPolicy.objects.filter(year__isnull=True).first()
        if not policy:
            return Response({"vacation_days": 15, "sick_days": 5, "personal_days": 5})
        return Response(PTOPolicySerializer(policy).data)


def _build_entry_key(entry):
    import json
    date = entry.get("date") or ""
    description = entry.get("description") or ""
    time_periods = entry.get("timePeriods") if isinstance(entry.get("timePeriods"), list) else []
    return json.dumps({"date": date, "description": description, "timePeriods": time_periods})


class ImportBackupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from datetime import date as date_type
        data = request.data
        if not isinstance(data, dict):
            return Response({"detail": "JSON body with 'entries' array required."}, status=status.HTTP_400_BAD_REQUEST)
        entries_data = data.get("entries")
        if not isinstance(entries_data, list):
            return Response({"detail": "Body must contain 'entries' array."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        existing_keys = set()
        for entry in TimeEntry.objects.filter(user=user).prefetch_related("time_periods"):
            periods = [{"startTime": p.start_time, "endTime": p.end_time} for p in entry.time_periods.all()]
            existing_keys.add(_build_entry_key({"date": str(entry.date), "description": entry.description, "timePeriods": periods}))
        added_entries = 0
        skipped_entries = 0
        for entry in entries_data:
            key = _build_entry_key(entry)
            if key in existing_keys:
                skipped_entries += 1
                continue
            date_str = entry.get("date")
            if not date_str:
                skipped_entries += 1
                continue
            try:
                entry_date = date_type.fromisoformat(date_str)
            except (ValueError, TypeError):
                skipped_entries += 1
                continue
            time_periods = entry.get("timePeriods") or []
            te = TimeEntry.objects.create(
                user=user,
                date=entry_date,
                description=(entry.get("description") or "")[:500],
                completed=bool(entry.get("completed")),
            )
            for i, p in enumerate(time_periods):
                if isinstance(p, dict) and p.get("startTime") and p.get("endTime"):
                    TimePeriod.objects.create(
                        entry=te,
                        start_time=str(p["startTime"]),
                        end_time=str(p["endTime"]),
                        order=i,
                    )
            te.recalc_total_seconds()
            existing_keys.add(key)
            added_entries += 1
        result = {"entries": {"added": added_entries, "skipped": skipped_entries}}
        pto_data = data.get("pto")
        if isinstance(pto_data, dict) and isinstance(pto_data.get("entries"), list):
            existing_pto_dates = set(PTOEntry.objects.filter(user=user).values_list("date", flat=True))
            added_pto = 0
            skipped_pto = 0
            for pto in pto_data["entries"]:
                date_str = pto.get("date")
                if not date_str:
                    continue
                try:
                    pto_date = date_type.fromisoformat(date_str)
                except (ValueError, TypeError):
                    continue
                if pto_date in existing_pto_dates:
                    skipped_pto += 1
                    continue
                pto_type = (pto.get("type") or "vacation").lower()
                if pto_type not in ("vacation", "sick", "personal"):
                    pto_type = "vacation"
                PTOEntry.objects.create(
                    user=user,
                    date=pto_date,
                    type=pto_type,
                    notes=(pto.get("notes") or "")[:500],
                )
                existing_pto_dates.add(pto_date)
                added_pto += 1
            result["pto"] = {"added": added_pto, "skipped": skipped_pto}
        return Response(result, status=status.HTTP_200_OK)


class ExportBackupView(APIView):
    """Returns backup JSON in same shape as legacy app for compatibility."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone as tz
        entries = TimeEntry.objects.filter(user=request.user).prefetch_related("time_periods")
        entries_list = []
        for e in entries:
            periods = [{"startTime": p.start_time, "endTime": p.end_time} for p in e.time_periods.all()]
            entries_list.append({
                "id": e.id,
                "date": str(e.date),
                "day": e.date.strftime("%A"),
                "description": e.description or "",
                "completed": e.completed,
                "timePeriods": periods,
                "duration": {
                    "hours": e.total_seconds // 3600,
                    "minutes": (e.total_seconds % 3600) // 60,
                    "seconds": e.total_seconds % 60,
                    "totalSeconds": e.total_seconds,
                    "totalMinutes": e.total_seconds // 60,
                },
            })
        pto_entries = PTOEntry.objects.filter(user=request.user).order_by("-date")
        pto_list = [
            {"id": p.id, "date": str(p.date), "type": p.type, "notes": p.notes or "", "createdAt": p.created_at.isoformat()}
            for p in pto_entries
        ]
        data = {
            "entries": entries_list,
            "pto": {"entries": pto_list},
            "exportDate": tz.now().isoformat(),
            "version": "1.0",
        }
        return Response(data)
