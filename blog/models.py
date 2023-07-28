from django.db import models
from django.utils import timezone
# Create your models here.
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length= 100)
    content = models.TextField()
    date_posted = models.DateTimeField(default= timezone.now)
    author = models.ForeignKey(User, on_delete= models.CASCADE)
    #author_id = User.id
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,)
    content = models.TextField(null=False, max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

