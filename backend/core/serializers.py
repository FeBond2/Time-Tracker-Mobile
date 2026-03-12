from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TimeEntry, TimePeriod, PTOEntry, PTOPolicy, EntryCategory

User = get_user_model()


class EntryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryCategory
        fields = ["id", "name", "color"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


def duration_from_seconds(total_seconds):
    s = int(total_seconds or 0)
    hours = s // 3600
    minutes = (s % 3600) // 60
    seconds = s % 60
    return {
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "totalSeconds": s,
        "totalMinutes": s // 60,
    }


class TimePeriodSerializer(serializers.ModelSerializer):
    startTime = serializers.CharField(source="start_time")
    endTime = serializers.CharField(source="end_time")

    class Meta:
        model = TimePeriod
        fields = ["id", "startTime", "endTime", "order"]


class TimeEntrySerializer(serializers.ModelSerializer):
    timePeriods = TimePeriodSerializer(source="time_periods", many=True, required=False)
    duration = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()
    category = serializers.PrimaryKeyRelatedField(
        queryset=EntryCategory.objects.none(), required=False, allow_null=True
    )
    categoryName = serializers.SerializerMethodField(read_only=True)
    categoryColor = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TimeEntry
        fields = [
            "id",
            "date",
            "day",
            "description",
            "completed",
            "category",
            "categoryName",
            "categoryColor",
            "order",
            "timePeriods",
            "duration",
            "total_seconds",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["total_seconds", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("request"):
            self.fields["category"].queryset = EntryCategory.objects.filter(user=self.context["request"].user)

    def get_categoryName(self, obj):
        return obj.category.name if obj.category else None

    def get_categoryColor(self, obj):
        return (obj.category.color or "") if obj.category else None

    def get_duration(self, obj):
        return duration_from_seconds(obj.total_seconds)

    def get_day(self, obj):
        return obj.date.strftime("%A") if obj.date else ""

    def create(self, validated_data):
        from django.db.models import Max
        periods_data = validated_data.pop("time_periods", [])
        user = self.context["request"].user
        category = validated_data.pop("category", None)
        validated_data.pop("order", None)
        entry_date = validated_data.get("date")
        max_order = TimeEntry.objects.filter(user=user, date=entry_date).aggregate(Max("order"))["order__max"]
        order = (max_order or 0) + 1
        entry = TimeEntry.objects.create(user=user, category=category, order=order, **validated_data)
        for i, p in enumerate(periods_data):
            TimePeriod.objects.create(
                entry=entry,
                start_time=p.get("start_time", ""),
                end_time=p.get("end_time", ""),
                order=i,
            )
        entry.recalc_total_seconds()
        return entry

    def update(self, instance, validated_data):
        periods_data = validated_data.pop("time_periods", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if periods_data is not None:
            instance.time_periods.all().delete()
            for i, p in enumerate(periods_data):
                TimePeriod.objects.create(
                    entry=instance,
                    start_time=p.get("start_time", ""),
                    end_time=p.get("end_time", ""),
                    order=i,
                )
            instance.recalc_total_seconds()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "timezone"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class PTOEntrySerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=PTOEntry.TYPE_CHOICES)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = PTOEntry
        fields = ["id", "date", "type", "notes", "createdAt"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class PTOPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PTOPolicy
        fields = ["id", "year", "vacation_days", "sick_days", "personal_days"]
