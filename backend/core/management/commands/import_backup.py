import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import TimeEntry, TimePeriod, PTOEntry

User = get_user_model()


def build_entry_key(entry):
    date = entry.get("date") or ""
    description = entry.get("description") or ""
    time_periods = entry.get("timePeriods") if isinstance(entry.get("timePeriods"), list) else []
    return json.dumps({"date": date, "description": description, "timePeriods": time_periods})


class Command(BaseCommand):
    help = "Import time tracker backup JSON for a user. JSON must have 'entries' array; optional 'pto' with 'entries'."

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Path to backup JSON file")
        parser.add_argument("--username", type=str, help="Username of the user to import for")
        parser.add_argument("--user-id", type=int, help="User ID to import for (alternative to --username)")

    def handle(self, *args, **options):
        path = options["json_file"]
        username = options.get("username")
        user_id = options.get("user_id")
        if not username and not user_id:
            self.stderr.write(self.style.ERROR("Provide --username or --user-id"))
            return
        try:
            user = User.objects.get(username=username) if username else User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"User not found: {username or user_id}"))
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        from datetime import date
        entries_data = data.get("entries")
        if not isinstance(entries_data, list):
            self.stderr.write(self.style.ERROR("JSON must contain 'entries' array"))
            return
        existing_keys = set()
        for entry in TimeEntry.objects.filter(user=user).prefetch_related("time_periods"):
            periods = [{"startTime": p.start_time, "endTime": p.end_time} for p in entry.time_periods.all()]
            key = build_entry_key({"date": str(entry.date), "description": entry.description, "timePeriods": periods})
            existing_keys.add(key)
        added_entries = 0
        skipped_entries = 0
        for entry in entries_data:
            key = build_entry_key(entry)
            if key in existing_keys:
                skipped_entries += 1
                continue
            date_str = entry.get("date")
            if not date_str:
                skipped_entries += 1
                continue
            try:
                entry_date = date.fromisoformat(date_str)
            except (ValueError, TypeError):
                skipped_entries += 1
                continue
            time_periods = entry.get("timePeriods")
            if not isinstance(time_periods, list):
                time_periods = []
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
        self.stdout.write(self.style.SUCCESS(f"Time entries: added {added_entries}, skipped {skipped_entries}"))
        pto_data = data.get("pto")
        if isinstance(pto_data, dict) and isinstance(pto_data.get("entries"), list):
            added_pto = 0
            skipped_pto = 0
            existing_dates = set(PTOEntry.objects.filter(user=user).values_list("date", flat=True))
            for pto in pto_data["entries"]:
                date_str = pto.get("date")
                if not date_str:
                    continue
                try:
                    pto_date = date.fromisoformat(date_str)
                except (ValueError, TypeError):
                    continue
                if pto_date in existing_dates:
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
                existing_dates.add(pto_date)
                added_pto += 1
            self.stdout.write(self.style.SUCCESS(f"PTO entries: added {added_pto}, skipped {skipped_pto}"))
