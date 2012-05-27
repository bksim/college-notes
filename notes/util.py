from notes.models import *
import math
from datetime import datetime



def set_tags(post, input):
    import unicodedata
    strings = unicodedata.normalize('NFKD', input).encode('ascii','ignore').split()
    for word in strings:
        if word[0] == '#':
            try:
                tag = Tag.objects.get(tag=word[1:])
                post.tags.add(tag)
                post.save()
            except:
                post.tags.create(tag=word[1:])


def get_trends():
    tags = list(Tag.objects.all())
    tag_words = []
    for word in tags:
        tag_words.append( str(word.tag))
    return tag_words[:20]
	
def calc_trend_score(p):
    time_standard = datetime(2012,1,1) #january 1, 2012
    d = p.created - time_standard
    t_s = d.seconds + d.days * 86400 #seconds elapsed
    return int(math.log(p.rating+1,2) + (t_s/43200.0)) #rating = log(base 2) of (points+1) + (time of submit - january 1, 2012) / (12 hrs)



