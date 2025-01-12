from django.db import models

class Article(models.Model):
    title = models.CharField(max_length = 200)
    content = models.TextField()
    author = models.CharField(max_length = 100)
    category = models.CharField(max_length = 50)
    publish_date = models.DateField()

    class Meta:
        permissions = (
            ("can_publish_article", "Can publish article"),
            ("can_edit_article", "Can edit article"),
        )