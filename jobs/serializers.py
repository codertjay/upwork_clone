from rest_framework import serializers

from jobs.models import Job


class CreateJobSerializers(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "name",
            "description",
            "budget",
            "categorys",
            "location",
            "project_stage",
            "duration",
        ]
