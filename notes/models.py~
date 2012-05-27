from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.forms import ModelForm
from django.db.models.signals import post_save
# Create your models here.

    
class Subject(models.Model):
    title = models.CharField(max_length=60)
    def __unicode__(self):
        return self.title
        
class Tag(models.Model):
    tag= models.CharField(max_length=50)
    def __unicode__(self):
        return self.tag  

class Post(models.Model):
    title = models.CharField(max_length=60, blank=True,null=True)
    content = models.FileField(upload_to="content/")
    description = models.TextField()
    link = models.URLField()
    tags = models.ManyToManyField(Tag, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    user = models.ForeignKey(User,null=True, blank=True)
    trendScore = models.IntegerField(default=0) #field for frontpage score
    
    def __unicode__(self):
        return self.title
      
    def num_comments(self):
        return Comment.objects.filter(post=self).count()
        
class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)
    likes = models.ManyToManyField(Post, blank=True, related_name = 'user_likes') 
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    post = models.ForeignKey(Post)
    author = models.ForeignKey(User, null=True, blank=True)
    
    def __unicode__(self):
        return unicode("%s: %s" % (self.post, self.body[:60]))
        
class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ["post", "author"]
        

        
        
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'link')
        
class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        
       

