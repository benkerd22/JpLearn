from django.shortcuts import render
from django.http import HttpResponse, Http404, FileResponse, JsonResponse
import random
import urllib

import os

with open('jplearn/dictionary/dic.txt', 'r', encoding='UTF-8') as f:
    dic = [line.split() for line in f] # dic include 漢字、仮名

with open('jplearn/dictionary/chn.txt', 'r', encoding='UTF-8') as f:
    chn = [line.strip() for line in f] # chn is 中文 only

with open('jplearn/dictionary/tone.txt', 'r', encoding='UTF-8') as f:
    tone = [line.strip() for line in f]

hiragana = ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', 'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ひ', 'ふ', 'へ', 'ほ', 'ま', 'み', 'む', 'め', 'も', 'や', '', 'ゆ', '', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'わ', '', '', '', 'を', 'ん']
katakana = ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ', 'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ヤ', '', 'ユ', '', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ワ', '', '', '', 'ヲ', 'ン']
roman = ['a', 'i', 'u', 'e', 'o']
mode = ['kanji', 'gana', 'chn', 'play'] # which HTML element should be visible
tonestr = '⓪①②③④⑤⑥⑦⑧⑨⑩'

def audio(request, q):
    fname = urllib.parse.unquote(q)
    fname = 'jplearn/audio/' + fname + '.mp3'
    if os.path.exists(fname):
        return FileResponse(open(fname, 'rb'))
    raise Http404()

def ttf(request):
    return FileResponse(open('jplearn/font/my.ttf', 'rb'))

def test(request):
    return render(request, 'jplearn/index.html', getNextContext())

def getNextContext():
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

    return context

def next(request):
    return JsonResponse(getNextContext())



