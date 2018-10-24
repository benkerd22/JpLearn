from django.shortcuts import render
from django.http import HttpResponse, Http404
import random
import urllib

import os

def index(request):
    choice = random.randint(0, len(dic) - 1)
    context = {'gachi':dic[choice][0], 'chn':chn[choice]}
    context['kanji'] = []

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
        
        context['kanji'].append({'name':url, 'alt':x})
        context['visible'] = mode[random.randint(0, 3)]

    return render(request, 'jplearn/index.html', context)

def audio(request, q):
    fname = urllib.parse.unquote(q)
    try:
        with open('jplearn/audio/' + fname + '.mp3', 'rb') as f:
            mp3 = f.read()
        return HttpResponse(mp3)
    except:
        raise Http404()

with open('jplearn/dictionary/dic.txt', 'r', encoding='UTF-8') as f:
    dic = [line.split() for line in f]

with open('jplearn/dictionary/chn.txt', 'r', encoding='UTF-8') as f:
    chn = [line for line in f]

hiragana = ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', 'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ひ', 'ふ', 'へ', 'ほ', 'ま', 'み', 'む', 'め', 'も', 'や', '', 'ゆ', '', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'わ', '', '', '', 'を', 'ん']
katakana = ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ', 'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ヤ', '', 'ユ', '', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ワ', '', '', '', 'ヲ', 'ン']
roman = ['a', 'i', 'u', 'e', 'o']
mode = ['kanji', 'gachi', 'chn', 'play']