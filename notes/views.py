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
from notes.util import *

def index(request):
    posts = Post.objects.order_by('-trendScore') #orders by trendScore in decreasing order
    paginator = Paginator(posts, 8)
    try: page = int(request.GET.get("page", 1))
    except ValueError: page = 1

    try: posts = paginator.page(page)
    except(InvalidPage, EmptyPage):
        posts= paginator.page(paginator.num_pages)

    #print(posts[0].created.naturaltime())
    print(request.user.username)
    #print(posts[0] not in request.user.likes.all())
    if request.user.username == '':
        return render_to_response("college/index.html", dict(posts=posts, 
        user='Anonymous', 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated(), trends = get_trends()) )
    #print(request.user.username)
    print(   type(User.objects.filter(username=request.user.username)))
    return render_to_response("college/index.html", dict(posts=posts, 
        user=UserProfile.objects.get_or_create(user=User.objects.get(username=request.user.username))[0], 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated(), trends = get_trends())) 

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

            p.trendScore = calc_trend_score(p)
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
def upvote(request):
    results = {'success':False, 'points': 0} #default json response
	
    if request.method == u'GET':
        GET = request.GET
        if GET.has_key(u'pk') and GET.has_key(u'vote'):
            pk = int(GET[u'pk'])
            vote = GET[u'vote']
            p = Post.objects.get(pk=pk)
            if vote == u"up":
                user = UserProfile.objects.get_or_create(user=request.user)[0]
                if p not in user.likes.all():
                    p.rating += 1
                    p.trendScore = calc_trend_score(p) #update trendscore
                else:
                    print('already voted')
                p.save()
                user.likes.add(p)
                d = dict(post=p, user=request.user, is_authenticated=request.user.is_authenticated() )
                d.update(csrf(request))
            #elif vote == u"down":
            results = {'success':True, 'points':p.rating}
    json = simplejson.dumps(results)
    #return HttpResponseRedirect(reverse('notes.views.index'))
    return HttpResponse(json, mimetype='application/json')
       
    
def users(request, username):
    posts = Post.objects.filter(user=User.objects.filter(username=username))
    #print(likedposts)
    #print(posts[0].created.naturaltime())
    #print(request.user.is_authenticated())
    return render_to_response("college/users.html",  dict(posts=posts, user=UserProfile.objects.get_or_create(user=User.objects.get(username=request.user.username))[0], page_user=username, active='submitted',
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
    paginator = Paginator(posts, 8)
    try: page = int(request.GET.get("page", 1))
    except ValueError: page = 1

    try: posts = paginator.page(page)
    except(InvalidPage, EmptyPage):
        posts= paginator.page(paginator.num_pages)
    #print(posts[0].created.naturaltime())
    #print(request.user.username) <- is this just a debug?
    #print(posts[0] not in request.user.likes.all())
    if request.user.username == '':
        return render_to_response("college/index.html", dict(posts=posts, 
        user='Anonymous', 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated(), trends = get_trends()))
    #print(request.user.username)
    print(   type(User.objects.filter(username=request.user.username)))
    return render_to_response("college/index.html", dict(posts=posts, 
        user=UserProfile.objects.get_or_create(user=User.objects.get(username=request.user.username))[0], 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated(), trends = get_trends())) 
		
def new(request):
# framework is copied from index, so this may be the source of any errors -bks
    posts = Post.objects.order_by('-created')
    paginator = Paginator(posts, 8)
    try: page = int(request.GET.get("page", 1))
    except ValueError: page = 1

    try: posts = paginator.page(page)
    except(InvalidPage, EmptyPage):
        posts= paginator.page(paginator.num_pages)
    #print(posts[0].created.naturaltime())
    #print(request.user.username) <- is this just a debug?
    #print(posts[0] not in request.user.likes.all())
    if request.user.username == '':
        return render_to_response("college/index.html", dict(posts=posts, 
        user='Anonymous', 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated(), trends = get_trends()))
    #print(request.user.username)
    print(   type(User.objects.filter(username=request.user.username)))
    return render_to_response("college/index.html", dict(posts=posts, 
        user=UserProfile.objects.get_or_create(user=User.objects.get(username=request.user.username))[0], 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated(), trends = get_trends()))

def trending(request, tag):
    posts = Post.objects.filter(tags__tag__iexact=tag)
    paginator = Paginator(posts, 8)
    try: page = int(request.GET.get("page", 1))
    except ValueError: page = 1

    try: posts = paginator.page(page)
    except(InvalidPage, EmptyPage):
        posts= paginator.page(paginator.num_pages)

    #print(posts[0].created.naturaltime())
    print(request.user.username)
    #print(posts[0] not in request.user.likes.all())
    if request.user.username == '':
        return render_to_response("college/index.html", dict(posts=posts, 
        user='Anonymous', 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated(), trends = get_trends()) )
    #print(request.user.username)
    print(   type(User.objects.filter(username=request.user.username)))
    return render_to_response("college/index.html", dict(posts=posts, 
        user=UserProfile.objects.get_or_create(user=User.objects.get(username=request.user.username))[0], 
        path=request.path,
        media_url=MEDIA_URL, is_authenticated=request.user.is_authenticated(), trends = get_trends())) 


        
    
