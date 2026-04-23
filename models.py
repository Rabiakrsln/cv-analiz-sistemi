from django.db import models

class CV(models.Model):
    fullname = models.CharField(max_length=100)
    pdf_file = models.FileField(upload_to='csv/')
    skills = models.TextField(blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname