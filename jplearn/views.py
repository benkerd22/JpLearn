from django.shortcuts import render
from django.http import HttpResponse, Http404, FileResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from jplearn.models import Word, Realuser
import random
import urllib

import os
    

hiragana = ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', 'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と', 'な', 'に', 'ぬ', 'ね',
            'の', 'は', 'ひ', 'ふ', 'へ', 'ほ', 'ま', 'み', 'む', 'め', 'も', 'や', '', 'ゆ', '', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'わ', '', '', '', 'を', 'ん']
katakana = ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ', 'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト', 'ナ', 'ニ', 'ヌ', 'ネ',
            'ノ', 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ヤ', '', 'ユ', '', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ワ', '', '', '', 'ヲ', 'ン']
roman = ['a', 'i', 'u', 'e', 'o']
mode = ['kanji', 'gana', 'chn', 'play']  # which HTML element should be visible



@login_required(login_url='login')
def audio(request, q):
    fname = urllib.parse.unquote(q)
    fname = 'jplearn/audio/' + fname + '.mp3'
    if os.path.exists(fname):
        return FileResponse(open(fname, 'rb'))
    raise Http404()


@login_required(login_url='login')
def ttf(request):
    return FileResponse(open('jplearn/font/my.ttf', 'rb'))


@login_required(login_url='login')
def test(request):
    return render(request, 'jplearn/index.html')


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


@login_required(login_url='login')
def next(request):
    user = request.user.realuser
    liked_words = user.liked_words.all()
    
    if liked_words.count() == 0:
        return JsonResponse({})

    word = random.choice(liked_words)

    res = {
        'kanji': word.kanji,
        'gana': word.gana,
        'tone': word.tone,
        'chn': word.chn,
        'id': word.pk,
    }

    return JsonResponse(res)


def welcome(request):
    return render(request, "jplearn/welcome.html")


@login_required(login_url='login')
def dict(request):
    return render(request, 'jplearn/dictionary.html')


@login_required(login_url='login')
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


@login_required(login_url='login')
def dictAction(request):
    user = request.user.realuser
    method = request.GET.get('m', None)
    word_id = request.GET.get('q', None)

    word = Word.objects.get(pk=word_id)
    if method == 'add':
        user.liked_words.add(word)
        status = 1
    elif method == 'remove':
        user.liked_words.remove(word)
        status = 0
    else:
        raise Http404()

    return JsonResponse({'checkStatus': status})
