from django.db import models
from django.urls import reverse


# Create your models here.

class Job(models.Model):
    uploader = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='battles')
    uploader_agent_name = models.CharField(max_length=32, blank=True, null=True)
    uploader_agent_version = models.CharField(max_length=50, blank=True, null=True)
    uploader_agent_extra = models.CharField(max_length=100, blank=True, null=True)
    splatnet_id = models.CharField(max_length=100, blank=True, null=True)
    raw_data = models.JSONField()
    data_type = models.CharField(max_length=32)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    played_time = models.DateTimeField()

    after_coop_grade = models.IntegerField()

    gpt_description = models.TextField(blank=True)
    gpt_description_generated = models.BooleanField(default=False)
    gpt_description_generated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Coop Job {self.id} ({self.splatnet_id}) - @{self.uploader.username}'

    def get_absolute_url(self):
        return reverse('grizzco_jobs:view_job', args=[str(self.id)])

    def get_related_jobs(self):
        if self.splatnet_id and self.splatnet_id != '':
            return Job.objects.filter(splatnet_id=self.splatnet_id).exclude(id=self.id)
        else:
            return []
