from notes.models import *



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


