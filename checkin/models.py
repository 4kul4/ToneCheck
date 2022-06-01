from django.db import models


class Publics(models.Model):
    public_start = models.CharField(max_length=30)
    public_end = models.CharField(max_length=30)
    language = models.CharField(max_length=2)
    page = models.CharField(max_length=10)

    def __srt__(self):
        return [self.public_start, self.public_end, self.language, self.page]
