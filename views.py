'''
    views logic for jplearn
'''

import random
import urllib
import json
import os
from functools import wraps
from django.shortcuts import render
from django.http import *
from django.urls import reverse_lazy
from jplearn.models import Word


def login_(function=None, status=302):

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)

            if status == 302:
                return HttpResponseRedirect(str(reverse_lazy('jplearn:login')) + '?next=' + str(reverse_lazy('jplearn:index')))
            elif status == 403:
                return HttpResponseForbidden()
            else:
                return Http404()
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


@login_(status=403)
def audio(request, q):
    q = urllib.parse.unquote(q)
    fname = 'jplearn/audio/' + q + '.mp3'
    if os.path.exists(fname):
        return FileResponse(open(fname, 'rb'))
    raise Http404()


@login_(status=403)
def ttf(request):
    return FileResponse(open('jplearn/font/my.ttf', 'rb'))


def img(request, q):
    q = urllib.parse.unquote(q)
    fname = 'jplearn/icon/' + q
    if os.path.exists(fname):
        return FileResponse(open(fname, 'rb'))
    raise Http404()


def getRandom(request, action):
    user = request.user.realuser
    status = request.session['dfa_status']

    # dfa logic:
    if status == 0:
        if action == 'next':
            status = 0
        elif action == 'previous':
            status = 2
    elif status == 1:
        if action == 'next':
            status = 0
        elif action == 'previous':
            status = 2
    elif status == 2:
        if action == 'next':
            status = 1
    else:
        status = 3

    if status == 0:
        # do the random selection
        selected_list = request.session['range']

        if 0 in selected_list and not 1 in selected_list:
            real_list = user.liked_words.all()
        else:
            real_list = Word.objects.all()

        word = random.choice(real_list)

        request.session['last'] = request.session['current']  # save last word
        request.session['current'] = word.pk  # save current word

    if status == 1:
        # show the current word
        current = request.session['current']
        if current is None:
            status = 3
        else:
            word = Word.objects.get(pk=current)

    if status == 2:
        # show the current word
        last = request.session['last']
        if last is None:
            status = 3
        else:
            word = Word.objects.get(pk=last)

    if status == 3:
        return JsonResponse({
            'status': 'not allowed'
        })

    request.session['dfa_status'] = status

    return JsonResponse({
        'status': 'random_mode',
        'kanji': word.kanji,
        'gana': word.gana,
        'tone': word.tone,
        'chn': word.chn,
        'id': word.pk,
        'checked': word.realuser_set.filter(pk=user.pk).exists()
    })


def getRound(request, action):
    user = request.user.realuser

    arrangment = request.session['arrangment']
    current = request.session['current']
    if action == 'next':
        current += 1
    elif action == 'previous':
        current -= 1

    if current == -1:
        return JsonResponse({
            'status': 'not allowed',
        })

    if current == len(arrangment):
        request.session['in_test'] = False
        return JsonResponse({
            'status': 'finish',
            'max': len(arrangment),
        })

    wordpk = arrangment[current]
    word = Word.objects.get(pk=wordpk)

    request.session['current'] = current

    return JsonResponse({
        'status': 'continue',
        'current': current,
        'max': len(arrangment),
        'kanji': word.kanji,
        'gana': word.gana,
        'tone': word.tone,
        'chn': word.chn,
        'id': word.pk,
        'checked': word.realuser_set.filter(pk=user.pk).exists()
    })


@login_
def test(request):
    try:
        in_test = request.session.get('in_test', False)

        if request.method == 'GET':
            if in_test:
                return render(request, 'jplearn/index.html')

            return HttpResponseRedirect(reverse_lazy('jplearn:start'))

        if request.method == 'POST':
            if in_test:
                data = json.loads(request.body.decode('utf-8'))
                mode = request.session['mode']
                action = data['action']

                if action == 'quit':
                    request.session['in_test'] = False
                    return JsonResponse({
                        'status': 302,
                        'location': reverse_lazy('jplearn:test'),
                    })

                if mode == 'round':
                    return getRound(request, action)

                if mode == 'random':
                    return getRandom(request, action)

            return HttpResponseBadRequest()

        return HttpResponseNotAllowed(['GET', 'POST'])
    except:
        return HttpResponseBadRequest()


def initTest(request):
    user = request.user.realuser

    data = json.loads(request.body.decode('utf-8'))
    selected_list = data['selected_list']
    mode = data['mode']

    all_words = Word.objects.all()
    my_words = user.liked_words.all()
    # Todo: create a WordList Model

    if 0 in selected_list and not 1 in selected_list:
        real_list = my_words
    else:
        real_list = all_words

    request.session['in_test'] = True
    if mode == 'round':
        request.session['mode'] = 'round'
        arrangment = [word.pk for word in real_list]
        random.shuffle(arrangment)
        request.session['arrangment'] = arrangment
        request.session['current'] = 0
    elif mode == 'random':
        request.session['mode'] = 'random'
        request.session['range'] = selected_list
        request.session['current'] = None
        request.session['last'] = None
        request.session['dfa_status'] = 0
    else:
        return HttpResponseBadRequest()

    return JsonResponse({
        'status': 302,
        'location': reverse_lazy('jplearn:test'),
    })


@login_
def start(request):
    user = request.user.realuser
    in_test = request.session.get('in_test', False)

    if request.method == 'GET':
        if not in_test:
            context = {
                "exists_list": [
                    {
                        'name': 'My Book',
                        'count': user.liked_words.all().count(),
                        'valid': user.liked_words.all().count() > 0,
                    },
                    {
                        'name': '《综合日语》（一）',
                        'count': Word.objects.all().count(),
                        'valid': True,
                    }
                ],
            }

            return render(request, 'jplearn/start.html', context)

        return HttpResponseRedirect(reverse_lazy('jplearn:test'))

    if request.method == 'POST':
        if in_test:
            return HttpResponseBadRequest()

        try:
            return initTest(request)
        except:
            return HttpResponseBadRequest()

    return HttpResponseNotAllowed(['GET', 'POST'])


def welcome(request):
    return render(request, "jplearn/welcome.html")


@login_(status=403)
def dict(request):
    return render(request, 'jplearn/dictionary.html')


@login_(status=403)
def dictData(request):
    user = request.user.realuser

    res = {'data': [], }

    for word in Word.objects.all():
        row = {
            'id': word.pk,
            'kanji': word.kanji,
            'gana': word.gana,
            'tone': word.tone,
            'chn': word.chn,
            'checked': word.realuser_set.filter(pk=user.pk).exists()
        }
        res['data'].append(row)

    return JsonResponse(res)


@login_(status=403)
def dictAction(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user = request.user.realuser

    try:
        data = json.loads(request.body.decode('utf-8'))
        action = data['action']
        wordpk = data['target']

        word = Word.objects.get(pk=wordpk)
        if action == 'add':
            user.liked_words.add(word)
            status = 1
        elif action == 'remove':
            user.liked_words.remove(word)
            status = 0
        else:
            return HttpResponseBadRequest()

        return JsonResponse({'checkStatus': status})
    except:
        return HttpResponseBadRequest()
