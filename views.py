'''
    views logic for jplearn
'''

import random
import json
from functools import wraps
from django.shortcuts import render
from django.http import *
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from jplearn.models import Realuser, Word, Book
from django.contrib.auth import login

Share00 = Realuser.objects.get(user=User.objects.get(username='share00'))


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


def getRandom(request, action):
    user = request.user.realuser
    user_book = user.books.first()
    status = request.session['dfa_status']

    # dfa logic:
    if status == 0:
        if action in ('next', 'prefetch'):
            status = 0
        elif action in ('previous', 'prelast'):
            status = 2
    elif status == 1:
        if action in ('next', 'prefetch'):
            status = 0
        elif action in ('previous', 'prelast'):
            status = 2
    elif status == 2:
        if action in ('next', 'prefetch'):
            status = 1
        elif action in ('previous', 'prelast'):
            status = 3

    if not action in ('next', 'prefetch', 'previous', 'prelast', 'new'):
        status = 3

    if status == 0:
        # do the random selection
        selected_list = request.session['range']

        real_list = Word.objects.none()
        for book_pk in selected_list:
            book = Book.objects.get(pk=book_pk)
            if book:
                real_list = real_list | book.words.all()

        real_list = real_list.difference(user.hate_words.all())

        word = random.choice(real_list)

        if action in ('next', 'previous', 'new'):
            # save last word
            request.session['last'] = request.session['current']
            request.session['current'] = word.pk  # save current word

    if status == 1:
        # show the current word
        current = request.session['current']
        if current is None:
            status = 3
        else:
            word = Word.objects.get(pk=current)

    if status == 2:
        # show the last word
        last = request.session['last']
        if last is None:
            status = 3
        else:
            word = Word.objects.get(pk=last)

    if status == 3:
        return JsonResponse({
            'status': 'not allowed'
        })

    if action in ('next', 'previous'):
        request.session['dfa_status'] = status
        return JsonResponse({
            'status': 'random_mode',
        })

    return JsonResponse({
        'status': 'random_mode',
        'kanji': word.kanji,
        'gana': word.gana,
        'tone': word.tone,
        'chn': word.chn,
        'audio': word.related_audio,
        'id': word.pk,
        'checked': user_book.words.filter(pk=word.pk).exists()
    })


def getRound(request, action):
    user = request.user.realuser
    user_book = user.books.first()

    arrangment = request.session['arrangment']
    current = request.session['current']
    if action == 'next':
        current += 1
    elif action == 'previous':
        current -= 1
    elif action == 'new':
        pass
    elif action == 'prefetch':
        current += 1
    elif action == 'prelast':
        current -= 1
    else:
        return HttpResponseBadRequest()

    if current == -1:
        return JsonResponse({
            'status': 'not allowed',
        })

    if current == len(arrangment):
        if action in ('next', 'previous'):
            request.session['in_test'] = False
            
        return JsonResponse({
            'status': 'finish',
            'current': len(arrangment),
            'max': len(arrangment),
        })

    wordpk = arrangment[current]
    word = Word.objects.get(pk=wordpk)

    if action in ('next', 'previous'):
        request.session['current'] = current
        return JsonResponse({
            'status': 'continue',
            'current': current,
            'max': len(arrangment)
        })

    return JsonResponse({
        'status': 'continue',
        'kanji': word.kanji,
        'gana': word.gana,
        'tone': word.tone,
        'chn': word.chn,
        'audio': word.related_audio,
        'id': word.pk,
        'checked': user_book.words.filter(pk=word.pk).exists()
    })


@login_
def test(request):
    try:
        in_test = request.session.get('in_test', False)

        if request.method == 'GET':
            if in_test:
                return render(request, 'jplearn/test.html')

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
    except Exception as err:
        print(err)
        return HttpResponseBadRequest()


def initTest(request):
    user = request.user.realuser

    data = json.loads(request.body.decode('utf-8'))
    selected_list = data['selected_list']
    mode = data['mode']

    request.session['in_test'] = True
    if mode == 'round':
        request.session['mode'] = 'round'

        real_list = Word.objects.none()
        for book_pk in selected_list:
            book = Book.objects.get(pk=book_pk)
            if book:
                real_list = real_list | book.words.all()

        real_list = real_list.difference(user.hate_words.all())

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
            context = {"exists_list": []}

            for book in user.books.all():
                count = book.words.all().difference(user.hate_words.all()).count()
                context['exists_list'].append({
                    'id': book.pk,
                    'name': book.name,
                    'count': count,
                    'valid': count > 0,
                })

            for book in Share00.books.all():
                count = book.words.all().difference(user.hate_words.all()).count()
                context['exists_list'].append({
                    'id': book.pk,
                    'name': book.name,
                    'count': count,
                    'valid': count > 0,
                })

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
    user_book = user.books.first()

    res = {'data': [], }

    for word in Word.objects.all():
        row = {
            'id': word.pk,
            'kanji': word.kanji,
            'gana': word.gana,
            'tone': word.tone,
            'chn': word.chn,
            'checked': user_book.words.filter(pk=word.pk).exists()
        }
        res['data'].append(row)

    return JsonResponse(res)


@login_(status=403)
def dictAction(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user = request.user.realuser
    user_book = user.books.first()

    try:
        data = json.loads(request.body.decode('utf-8'))
        action = data['action']
        wordpk = data['target']

        word = Word.objects.get(pk=wordpk)
        if action == 'add':
            user_book.words.add(word)
            status = 1
        elif action == 'remove':
            user_book.words.remove(word)
            status = 0
        else:
            return HttpResponseBadRequest()

        return JsonResponse({'checked': status})
    except:
        return HttpResponseBadRequest()

def guestlogin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    
    guest = User.objects.get(username='guest')
    login(request, guest)
