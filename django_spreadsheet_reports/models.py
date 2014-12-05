from django.db import models


class Bookmark(models.Model):
    name = models.CharField(max_length=255)
    uri = models.CharField(max_length=4096)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Notice(models.Model):
    slug = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    group_name = models.CharField(max_length=255)
    group_val = models.IntegerField(default=0)
    low_limit = models.IntegerField(default=0)
    high_limit = models.IntegerField(default=0)
    prev_val = models.IntegerField(default=0)

    def get_change_pct(self):
        before_data = float(self.prev_val)
        after_data = float(self.group_val)
        delta = after_data - before_data
        if before_data == 0.0:
            val = after_data
        else:
            val = delta / before_data
        val = val * 100.0
        return "%.0f" % val
