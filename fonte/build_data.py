import json, re, unicodedata

import os
# dados.json é gerado por extract.py a partir das planilhas
D = os.path.dirname(os.path.abspath(__file__)) + '/'
OUT = os.path.dirname(os.path.abspath(__file__)) + '/'
d = json.load(open(D+'dados.json'))

def clean(t):
    if t is None: return ''
    t = str(t).replace('\xa0',' ')
    t = re.sub(r'\n{3,}', '\n\n', t).strip()
    return t

# ---- ramos canônicos (nomes dos nós-raiz da árvore v0.2)
ramo_label = {}
for a in d['arvore']:
    if '.' not in a['codigo']:
        n = a['codigo']
        ramo_label[n] = a['termo'].title().replace(' E ',' e ').replace(' Da ',' da ')
RAMOS = [{'n': k, 'nome': v} for k, v in sorted(ramo_label.items())]

def ramo_n(s):
    m = re.match(r'(\d)', s or '')
    return m.group(1) if m else ''

# ---- árvore
arvore = [[a['codigo'], clean(a['termo']), ramo_n(a['ramo']) or (a['codigo'][0] if '.' not in a['codigo'] else ''),
           clean(a['classificacao']), clean(a['obs'])] for a in d['arvore']]

# ---- verbetes do dicionário
verbetes = [[clean(v['termo']), clean(v['proposta']), clean(v['definicoes']), clean(v['fonte']),
             clean(v['classificacao']), clean(v['outras']), clean(v['escopo']), clean(v['gramatica']),
             clean(v['linguas']), clean(v['analise'])] for v in d['verbetes']]

# ---- resoluções
def dt(t):
    m = re.search(r'de (\d{1,2}) de (\w+) de (\d{4})', t or '')
    return f"{m.group(1)} de {m.group(2)} de {m.group(3)}" if m else ''
resolucoes = [[r['n'], dt(r['titulo']), clean(r['ementa']), r['status'], r['anexo'],
               r['term_origem'], r['term_verif'], r['ocorrencias'], clean(r['onde']), clean(r['obs'])]
              for r in d['resolucoes']]

# ---- termos (diagnóstico)
termos = [[clean(t['termo']), ramo_n(t['ramo']) if t['ramo'] != 'Fora da árvore' else 'X', t['anel'],
           t['ocorrencias'], t['n_res'], t['resolucoes'], t['convergencia'], t['redacoes'],
           t['dbta'], t['selecao'], t['codigo_arvore'], t['ind_formal'],
           t['encaminhamento'], clean(t['obs'])] for t in d['diagnostico']]

# ---- prévia da definição de cada termo (para as listas)
def curta(t, n=170):
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) <= n: return t
    return t[:n].rsplit(' ', 1)[0].rstrip(',;:') + '…'
grupos = {}
for c in d['compilacao']:
    grupos.setdefault(clean(c['termo']), []).append(c)
def melhor(oc):
    boas = [c for c in oc if c['tipo'] != 'Remissiva' and not clean(c['definicao']).lower().startswith('ver ')]
    if not boas: return curta(clean(oc[0]['definicao'])) if oc else ''
    boas.sort(key=lambda c: (c['res'] != '23', c['tipo'] != 'Glossário', int(c['res'] or 999)))
    return curta(clean(boas[0]['definicao']))
for t in termos:
    t.append(melhor(grupos.get(t[0], [])))

# ---- cruzamento dicionário x conarq
cruz = [[c['codigo'], clean(c['termo']), c['situacao'], c['definido'], c['ocorrencias'],
         c['resolucoes'], c['convergencia']] for c in d['cruzamento']]

retiradas = [[clean(r['termo']), clean(r['classificacao']), clean(r['motivo']), clean(r['relacionado'])]
             for r in d['retiradas']]

equilibrio = [[e['ramo'], e['vanderlei'], e['outras'], e['equilibrio'], e['novos'], e['total'], e['depois']]
              for e in d['equilibrio'] if e['ramo'] and e['total'] is not None]
eq_notas = [e['ramo'] for e in d['equilibrio'] if e['total'] is None and len(e['ramo']) > 40]

leiame1 = [[clean(x['t']), clean(x['d'])] for x in d['leiame1'] if clean(x['t'])]
leiame2 = [[clean(x['t']), clean(x['d'])] for x in d['leiame2'] if clean(x['t'])]

# ---- indicadores e séries dos gráficos (recalculados dos dados)
S = d['sintese_raw']
def tabela(i0, i1):
    out = []
    for r in S[i0:i1]:
        cells = [c for c in r if c]
        if len(cells) >= 2: out.append([cells[0], int(float(cells[-1]))])
    return out

kpis = [
    ['Resoluções examinadas', 60], ['Com terminologia', 31], ['Ocorrências compiladas', 2085],
    ['Termos distintos', 1491], ['Anel nuclear', 747], ['Verbetes a harmonizar', 74],
    ['Candidatos prioritários', 101],
]
por_ramo = []
for r in S[7:15]:
    c = [x for x in r if x]
    por_ramo.append([ramo_n(c[0]), int(c[1]), int(c[2]), int(c[3])])
graficos = {
    'ramo_anel': por_ramo,
    'encaminhamento': tabela(18, 23),
    'convergencia': tabela(26, 30),
    'tipo': tabela(32, 37),
    'formais': tabela(39, 44),
    'por_res': [[c[0].replace('Res. nº ',''), int(float(c[1]))] for c in
                ([x for x in r if x] for r in S[46:76]) if len(c) >= 2 and c[0].startswith('Res')],
    'outros': [[c[0], int(float(c[1]))] for c in
               ([x for x in r if x] for r in S[79:90]) if len(c) >= 2],
    'notaRes': S[76][1] if len(S[76]) > 1 and S[76][1] else [x for x in S[76] if x][0],
}

core = {'ramos': RAMOS, 'arvore': arvore, 'verbetes': verbetes, 'resolucoes': resolucoes,
        'termos': termos, 'cruz': cruz, 'retiradas': retiradas, 'equilibrio': equilibrio,
        'eqNotas': eq_notas, 'leiame1': leiame1, 'leiame2': leiame2, 'kpis': kpis, 'graficos': graficos}

with open(OUT+'core.js','w') as f:
    f.write('window.CORE=' + json.dumps(core, ensure_ascii=False, separators=(',',':')) + ';')

# ---- ocorrências (arquivo separado, carregado sob demanda)
oc = [[clean(c['termo']), clean(c['como_consta']), clean(c['definicao']), c['res'],
       clean(c['fonte_doc']), clean(c['local']), c['tipo'], c['anel'], clean(c['superordenado']),
       c['i_repete'], c['i_artigo'], c['i_periodos'], c['i_exemplos'], c['i_negativa'],
       c['extensao'], c['conferencia'], clean(c['outras']), clean(c['fonte_citada']),
       clean(c['relacao']), clean(c['obs'])] for c in d['compilacao']]
with open(OUT+'../data/ocorrencias.json','w') as f:
    json.dump({'rows': oc}, f, ensure_ascii=False, separators=(',',':'))

import os
print('core.js', os.path.getsize(OUT+'core.js')//1024, 'KB')
print('ocorrencias.json', os.path.getsize(OUT+'../data/ocorrencias.json')//1024, 'KB')
print('ramos:', RAMOS)
print('por_res count:', len(graficos['por_res']), graficos['por_res'][:3])
print('kpis ok, graficos keys:', {k: len(v) for k,v in graficos.items()})
print('eq_notas:', len(eq_notas))
