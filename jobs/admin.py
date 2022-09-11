from django.contrib import admin

from .models import Job, JobInvite, SavedJob, Review

admin.site.register(Job)
admin.site.register(JobInvite)
admin.site.register(SavedJob)
admin.site.register(Review)
