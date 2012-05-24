from django.template import Context, loader
from django.http import HttpResponse
from django import template
from django.http import QueryDict
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms import ModelForm
from noteproj.settings import MEDIA_URL
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import simplejson

from notes.models import *

def index(request):
    posts = Post.objects.all()
    #print(posts[0].created.naturaltime())
    print(request.user.username)
    #print(posts[0] not in request.user.likes.all())
    if request.user.username == '':
        return render_to_response("college/index.html", dict(posts=posts, 
        user='Anonymous', 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated()))
    #print(request.user.username)
    print(   type(User.objects.filter(username=request.user.username)))
    return render_to_response("college/index.html", dict(posts=posts, 
        user=UserProfile.objects.get_or_create(user=User.objects.get(username=request.user.username))[0], 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated())) 

def post(request, pk):
    """Single post with comments and a comment form."""
    post = Post.objects.get(pk=int(pk))
    comments = Comment.objects.filter(post=post)
    #print(comments)
    
    
    
    d = dict(post=post, comments=comments, form=CommentForm(), user=request.user, is_authenticated=request.user.is_authenticated())
    
    
    
    if request.user.username == '':
        d = dict(post=post, comments=comments, form=CommentForm(), user='Anonymous', is_authenticated=request.user.is_authenticated())
    else:
        d = dict(post=post, comments=comments, form=CommentForm(), 
        user=UserProfile.objects.get_or_create(user=User.objects.get(username=request.user.username))[0],
        is_authenticated=request.user.is_authenticated())
         
        
    d.update(csrf(request))
    return render_to_response("college/post.html", d)

@login_required(login_url='/accounts/login') 
def submit(request):
    form = PostForm()
    if request.method == 'POST':
        try:
            print('try')
            post = request.POST
            if post['title'] == '' or post['description'] == '' or post['link'] == '':
                return render_to_response('college/submit.html', {
                'form': form,
                'error_message': "Make sure all fields are filled out", 'is_authenticated': request.user.is_authenticated()
                }, context_instance=RequestContext(request))
            
            #
            p = Post(title=post['title'], 
                description=post['description'], link=post['link'], user=request.user)
                
            p.save()
        except:
            print('except')
            return render_to_response('college/submit.html', {
            'form': form, 'is_authenticated': request.user.is_authenticated()}, context_instance=RequestContext(request))
        else:
            print('else')
            set_tags(p, post['description'])
            #print(st)
            
            return HttpResponseRedirect(reverse('notes.views.index'))
    return render_to_response('college/submit.html', {
        'form': form, 'is_authenticated': request.user.is_authenticated()}, context_instance=RequestContext(request))
   
def set_tags(post, input):
    import unicodedata
    strings = unicodedata.normalize('NFKD', input).encode('ascii','ignore').split()
    for word in strings:
        if word[0] == '#':
            try:
                tag = Tag.objects.get(tag=word)
                post.tags.add(tag)
                post.save()
            except:
                post.tags.create(tag=word)
                
    



   
def log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('notes.views.index'))
    
    
def add_comment(request, pk):
    p = request.POST
    if p.has_key("body") and p["body"]:
        comment = Comment(post=Post.objects.get(pk=pk), author = request.user, body=p["body"])
        comment.save()
    return HttpResponseRedirect(reverse("notes.views.post", args=[pk]))

@login_required(login_url='/accounts/login') 
# edited this for jquery -bks
def upvote(request):
    results = {'success':False} #default json response
	
    if request.method == u'POST':
        POST = request.POST
        if POST.has_key(u'pk') and POST.has_key(u'vote'):
            pk = int(POST[u'pk'])
            vote = POST[u'vote']
            p = Post.objects.get(pk=pk)
            if vote == u"up":
                user = UserProfile.objects.get_or_create(user=request.user)[0]
                if p not in user.likes.all():
                    p.rating += 1
                else:
                    print('already voted')
                p.save()
                user.likes.add(p)
                d = dict(post=p, user=request.user, is_authenticated=request.user.is_authenticated() )
                d.update(csrf(request))
            #elif vote == u"down":
            results = {'success':True}
    json = simplejson.dumps(results)
    #return HttpResponseRedirect(reverse('notes.views.index'))
    return HttpResponse(json, mimetype='application/json')
       
    
def users(request, username):
    posts = Post.objects.filter(user=User.objects.filter(username=username))
    #print(likedposts)
    #print(posts[0].created.naturaltime())
    #print(request.user.is_authenticated())
    return render_to_response("college/users.html",  dict(posts=posts, user=request.user, page_user=username, active='submitted',
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated())) 
        
        
def liked(request, username):
    posts = UserProfile.objects.get_or_create(user=User.objects.filter(username=username))[0].likes.all()
    return render_to_response("college/users.html",  dict(posts=posts, user=request.user, page_user = username, active='liked',
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated())) 

		
#the method below may be wrong so feel free to edit if it doesn't work -bks
#just kidding, i think it works -bks
def best(request):
	# framework is copied from index, so this may be the source of any errors -bks
    posts = Post.objects.order_by('-rating')
    #print(posts[0].created.naturaltime())
    #print(request.user.username) <- is this just a debug?
    #print(posts[0] not in request.user.likes.all())
    if request.user.username == '':
        return render_to_response("college/index.html", dict(posts=posts, 
        user='Anonymous', 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated()))
    #print(request.user.username)
    print(   type(User.objects.filter(username=request.user.username)))
    return render_to_response("college/index.html", dict(posts=posts, 
        user=UserProfile.objects.get_or_create(user=User.objects.get(username=request.user.username))[0], 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated())) 
		
def new(request):
# framework is copied from index, so this may be the source of any errors -bks
    posts = Post.objects.order_by('-created')
    #print(posts[0].created.naturaltime())
    #print(request.user.username) <- is this just a debug?
    #print(posts[0] not in request.user.likes.all())
    if request.user.username == '':
        return render_to_response("college/index.html", dict(posts=posts, 
        user='Anonymous', 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated()))
    #print(request.user.username)
    print(   type(User.objects.filter(username=request.user.username)))
    return render_to_response("college/index.html", dict(posts=posts, 
        user=UserProfile.objects.get_or_create(user=User.objects.get(username=request.user.username))[0], 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated()))
