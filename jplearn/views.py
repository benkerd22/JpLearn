from functools import wraps
from django.shortcuts import render
from django.http import *
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from jplearn.models import Word, Realuser
import random
import urllib
import json


import os

'''
hiragana = ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', 'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と', 'な', 'に', 'ぬ', 'ね',
            'の', 'は', 'ひ', 'ふ', 'へ', 'ほ', 'ま', 'み', 'む', 'め', 'も', 'や', '', 'ゆ', '', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'わ', '', '', '', 'を', 'ん']
katakana = ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ', 'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト', 'ナ', 'ニ', 'ヌ', 'ネ',
            'ノ', 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ヤ', '', 'ユ', '', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ワ', '', '', '', 'ヲ', 'ン']
roman = ['a', 'i', 'u', 'e', 'o']'''


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
    fname = urllib.parse.unquote(q)
    fname = 'jplearn/audio/' + fname + '.mp3'
    if os.path.exists(fname):
        return FileResponse(open(fname, 'rb'))
    raise Http404()


@login_(status=403)
def ttf(request):
    return FileResponse(open('jplearn/font/my.ttf', 'rb'))


def getnext(request):
    user = request.user.realuser

    mode = request.session['mode']
    arrangment = request.session.get('arrangment', [])
    current = request.session.get('current', -1)
    current += 1

    if mode == 'random':
        selected_list = request.session['range']
        if 0 in selected_list and not 1 in selected_list:
            real_list = user.liked_words.all()
        else:
            real_list = Word.objects.all()

        word = random.choice(real_list)
    elif mode == 'round':
        if current == len(arrangment):
            request.session['in_test'] = False
            return JsonResponse({
                'status': 'finish',
                'max': len(arrangment),
            })

        wordpk = arrangment[current]
        word = Word.objects.get(pk=wordpk)

        request.session['current'] = current
    else:
        return HttpResponseBadRequest()

    res = {
        'status': 'continue',
        'current': current,
        'max': len(arrangment),
        'kanji': word.kanji,
        'gana': word.gana,
        'tone': word.tone,
        'chn': word.chn,
        'id': word.pk,
    }

    return JsonResponse(res)


@login_
def test(request):
    if True:
        in_test = request.session.get('in_test', False)

        if request.method == 'GET':
            if in_test:
                return render(request, 'jplearn/index.html')

            return HttpResponseRedirect(reverse_lazy('jplearn:start'))

        if request.method == 'POST':
            if in_test:
                data = json.loads(request.body.decode('utf-8'))
                action = data['action']

                if action == 'getnext':
                    return getnext(request)

                if action == 'quit':
                    request.session['in_test'] = False
                    return JsonResponse({
                        'status': 302,
                        'location': reverse_lazy('jplearn:test'),
                    })

            return HttpResponseBadRequest()

        return HttpResponseNotAllowed(['GET', 'POST'])
    else:
        return HttpResponseBadRequest()


'''
    choice = random.randint(0, len(dic) - 1)

    context = {'kanji':dic[choice][-1], 'gana':dic[choice][0], 'chn':chn[choice]}
    context['tone'] = ''.join(tonestr[int(t)] for t in tone[choice])

    context['urls'] = [] # generate urls for gif showing

    for x in dic[choice][-1]:
        url = ''
        gif = ''
        if x == 'ん':
            gif = 'h9n' 
        elif x == 'ン':
            gif = 'k9n'
        elif x in hiragana:
            index = hiragana.index(x)
            gif = 'h' + str(index // 5) + roman[index % 5]
        elif x in katakana:
            index = katakana.index(x)
            gif = 'k' + str(index // 5) + roman[index % 5]
        elif ord(x) in range(0x4e00, 0x9fb0):
            url = 'http://img.kakijun.com/kanjiphoto/gif/'+ format(ord(x), 'x') + '.gif'

        if not gif == '':
            url = 'https://kakijun.jp/gif-h-k-al/' + gif + '.gif'
        
        context['urls'].append({'name':url, 'alt':x})

    return context'''


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
        request.session['current'] = -1
    else:
        request.session['mode'] = 'random'
        request.session['range'] = selected_list

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
                        'valid': user.liked_words.all().count() >= 0,
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

        # try:
        return initTest(request)
        # except:
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
