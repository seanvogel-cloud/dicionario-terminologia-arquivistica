"""Gera os ícones do app: pasta verde-petróleo com linhas mostarda sobre fundo mostarda."""
from PIL import Image, ImageDraw
import sys
out = sys.argv[1]
HI=(242,193,78); BRAND=(13,74,68)
def make(size, maskable=False, rounded=True):
    S=1024; im=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    if maskable or not rounded: d.rectangle([0,0,S,S],fill=HI)
    else: d.rounded_rectangle([0,0,S-1,S-1],radius=int(S*0.24),fill=HI)
    k = (0.62 if maskable else 0.80) * S / 34.0   # mesmo desenho do selo do app (grade 34x34)
    o = S/2 - 17*k
    P=lambda x,y:(o+x*k,o+y*k)
    # aba e corpo da pasta
    d.rounded_rectangle([*P(7.5,9.4),*P(15.5,14)],radius=1.8*k,fill=BRAND)
    d.polygon([P(13.4,9.4),P(16,11.6),P(13.4,13)],fill=BRAND)
    d.rounded_rectangle([*P(7.5,11.6),*P(26.5,24.6)],radius=1.8*k,fill=BRAND)
    d.rounded_rectangle([*P(11,15.4),*P(23,17.6)],radius=1.1*k,fill=HI)
    d.rounded_rectangle([*P(11,19.4),*P(18.5,21.6)],radius=1.1*k,fill=HI)
    return im.resize((size,size),Image.LANCZOS)
make(192).save(out+'/icon-192.png'); make(512).save(out+'/icon-512.png')
make(512,maskable=True).save(out+'/icon-maskable-512.png')
make(180,rounded=False).convert('RGB').save(out+'/apple-touch-icon.png')
make(32).save(out+'/favicon-32.png')
print('ícones ok')
