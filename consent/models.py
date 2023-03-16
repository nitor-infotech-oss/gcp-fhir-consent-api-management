from django.db import models


class ConsentRequest(models.Model):
    patientid = models.CharField(max_length=50, null=False)
    requestedrole = models.CharField(max_length=30, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=25, default='Pending')
    consentid = models.UUIDField(null=True)

    def __str__(self):
        return self.patientid + ' (' + self.requestedrole + ')'
