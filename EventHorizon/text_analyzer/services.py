from django.http import HttpResponse
import simplejson as json
from models import *
import nltk
import sys

#def get_tweets(request, since_id, user, password):
def extract_named_entities(request):
    """
    Uses the NLTK to extract named entities from a given text.
    """
    named_entities = []
    if request.GET:
        if 'text' not in request.GET:
            return HttpResponse('Please enter the text to analyze')
    else:
        return HttpResponse('Please enter the text to analyze')
    try:
        text = request.GET["text"]
        tokenized = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokenized)
        result = nltk.ne_chunk(tagged)
        if len(result.productions()) > 1:
            for ne in result.productions()[1:]:
                name = ne.rhs()[0][0]
                pos_tag = ne.rhs()[0][1]
                inferred_type = ne.lhs().symbol()
                named_entities.append( {"name":name, "pos_tag":pos_tag, "guessed_type":inferred_type,} )
    except:
        return HttpResponse('Failed to extract named entitied from text "%s": %s' % (text, str(sys.exc_info()[1])) )

    return HttpResponse(json.dumps(named_entities))

def extract_essence(request):
    if request.GET:
        if 'text' not in request.GET:
            return HttpResponse('Please enter the text to analyze')
    else:
        return HttpResponse('Please enter the text to analyze')
    try:
        text = request.GET["text"]
        text = text.strip()
        if text.startswith('RT'):
            text = (":").join(text.split(":")[1:]).strip()
        if text.find('by @') != -1 and len(text.split('by @')[1].split(" ")) < 3:
            text = text.split('by @')[0].strip()
        if text.find('via @') != -1 and len(text.split('via @')[1].split(" ")) < 3:
            text = text.split('via @')[0].strip()
    except:
        return HttpResponse('Failed to extract the essence from text "%s": %s' % (text, str(sys.exc_info()[1])) )
    return HttpResponse(text)










