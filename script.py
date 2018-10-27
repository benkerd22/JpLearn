import os, sys
sys.path.append('E:/mysite')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
import django
django.setup()
from jplearn.models import Word

with open('jplearn/dictionary/dic.txt', 'r', encoding='UTF-8') as f:
    dic = [line.split() for line in f]  # dic include 漢字、仮名

with open('jplearn/dictionary/chn.txt', 'r', encoding='UTF-8') as f:
    chn = [line.strip() for line in f]  # chn is 中文 only

with open('jplearn/dictionary/tone.txt', 'r', encoding='UTF-8') as f:
    tone = [line.strip() for line in f]

tonestr = '⓪①②③④⑤⑥⑦⑧⑨⑩'

for i in range(len(dic)):
    word = Word(kanji=dic[i][-1], gana=dic[i][0], chn=chn[i], tone=''.join(tonestr[int(t)] for t in tone[i]))
    word.save()
    print(dic[i][-1], end=' ')