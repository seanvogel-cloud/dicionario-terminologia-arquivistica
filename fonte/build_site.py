"""Monta a versão do site (PWA) na raiz do repositório a partir do modelo do app e dos dados."""
import json, os, shutil, hashlib
F = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(F)
SITE = ROOT  # no repositório o site fica na raiz

tpl = open(os.path.join(F, 'app_tpl.html'), encoding='utf-8').read()
core = open(os.path.join(F, 'core.js'), encoding='utf-8').read().replace('</', '<\\/')
tpl = tpl.replace('__CORE__', core, 1)
cut = tpl.index('<header class="topbar"')
head, body = tpl[:cut], tpl[cut:]
head = head.replace('<meta charset="utf-8">\n', '')


page = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Aplicativo da Câmara Técnica de Terminologia Arquivística: árvore de domínio, dicionário em construção e diagnóstico da terminologia nas resoluções do Conarq.">
<meta name="theme-color" content="#0d4a44" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0f2f2b" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Terminologia">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
<script>window.SITE=true;</script>
""" + head + "</head>\n<body>\n" + body + """
<script>
if('serviceWorker' in navigator && (location.protocol==='https:'||location.hostname==='localhost')){
  window.addEventListener('load',function(){ navigator.serviceWorker.register('sw.js').catch(function(){}); });
}
</script>
</body>
</html>
"""
open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(page)

manifest = {
  "name": "Terminologia Arquivística Conarq", "short_name": "Terminologia",
  "description": "Aplicativo da Câmara Técnica de Terminologia Arquivística: árvore de domínio, dicionário em construção e diagnóstico da terminologia nas resoluções do Conarq.",
  "lang": "pt-BR", "start_url": "./", "scope": "./", "display": "standalone",
  "background_color": "#eef1ef", "theme_color": "#0d4a44",
  "icons": [
    {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
json.dump(manifest, open(os.path.join(SITE, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# a versão do cache muda sozinha sempre que o conteúdo muda
h = hashlib.sha1()
for p in ['index.html', 'data/ocorrencias.json', 'manifest.webmanifest']:
    h.update(open(os.path.join(SITE, p), 'rb').read())
ver = h.hexdigest()[:10]
sw = """const CACHE='conarq-%s';
const PRE=['./','index.html','data/ocorrencias.json','manifest.webmanifest',
  'icons/icon-192.png','icons/icon-512.png','icons/icon-maskable-512.png','icons/apple-touch-icon.png','icons/favicon-32.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(PRE)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  const r=e.request; if(r.method!=='GET') return;
  if(r.mode==='navigate'){
    e.respondWith(fetch(r).then(res=>{const cp=res.clone();caches.open(CACHE).then(c=>c.put('index.html',cp));return res;})
      .catch(()=>caches.match('index.html')));
    return;
  }
  e.respondWith(caches.match(r,{ignoreSearch:true}).then(hit=>{
    const net=fetch(r).then(res=>{ if(res&&(res.ok||res.type==='opaque')){const cp=res.clone();caches.open(CACHE).then(c=>c.put(r,cp));} return res; });
    return hit||net;
  }));
});
""" % ver
open(os.path.join(SITE, 'sw.js'), 'w', encoding='utf-8').write(sw)
open(os.path.join(SITE, '.nojekyll'), 'w').close()
print('site pronto, cache', ver)
for root, _, files in os.walk(SITE):
    for f in files:
        p = os.path.join(root, f); print(' ', os.path.relpath(p, SITE), os.path.getsize(p)//1024, 'KB')
