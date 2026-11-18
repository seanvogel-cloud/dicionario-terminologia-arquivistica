import openpyxl, json, re, unicodedata
from datetime import datetime

import os, sys
# uso: python3 extract.py Selecao_termos_e_arvore.xlsx Terminologia_Resolucoes_Conarq_Diagnostico.xlsx
if len(sys.argv) != 3:
    sys.exit('uso: python3 extract.py <planilha de seleção e árvore> <planilha de diagnóstico>')
F1, F2 = sys.argv[1], sys.argv[2]

def s(v):
    if v is None: return ''
    if isinstance(v, datetime): return v.isoformat()
    if isinstance(v, float) and v == int(v): return str(int(v))
    t = str(v).replace('\r\n','\n').strip()
    if t in ("'", '"'): return ''
    return t

def num(v):
    if v is None or v == '': return None
    try: return float(v)
    except: return None

out = {}

# ---------- FILE 1 ----------
wb1 = openpyxl.load_workbook(F1)  # keep formats for code repair
p1 = wb1['Plan1']
hdr = [s(c) for c in next(p1.iter_rows(min_row=1, max_row=1, values_only=True))]
keys = ['termo','proposta','definicoes','fonte','classificacao','outras','escopo','gramatica','linguas','analise']
verbetes = []
for row in p1.iter_rows(min_row=2, values_only=True):
    if not s(row[0]): continue
    d = {k: s(row[i]) for i, k in enumerate(keys)}
    verbetes.append(d)
out['verbetes'] = verbetes

# tree v0.2 with code repair
def repair(cell):
    v = cell.value
    if isinstance(v, datetime):
        fmt = (cell.number_format or '').lower()
        code = f"{v.day}.{v.month}"
        if 'y' in fmt:
            yy = v.year % 100 if v.year < 2000 or v.year >= 2000 else v.year
            code += f".{v.year - 2000}"
        return code
    return s(v)

tw = wb1[' Árvore de domínio - ver 0.2']
tree = []
for i in range(5, tw.max_row + 1):
    code = repair(tw.cell(i, 1))
    termo = s(tw.cell(i, 2).value)
    if not termo: continue
    tree.append({
        'codigo': code,
        'termo': termo.strip(),
        'ramo': s(tw.cell(i, 3).value),
        'classificacao': s(tw.cell(i, 4).value),
        'obs': s(tw.cell(i, 5).value),
    })
out['arvore'] = tree

eq = wb1['Equilíbrio dos ramos']
eqrows = []
for i in range(3, eq.max_row + 1):
    r = [s(eq.cell(i, j).value) for j in range(1, 9)]
    if not r[0] or r[0].startswith('Critério'): continue
    eqrows.append({'ramo': r[0], 'vanderlei': num(r[1]), 'outras': num(r[2]),
                   'equilibrio': num(r[3]), 'novos': num(r[4]), 'total': num(r[5]),
                   'antes': num(r[6]), 'depois': num(r[7])})
out['equilibrio'] = eqrows

lr = wb1['Linhas retiradas']
ret = []
for i in range(3, lr.max_row + 1):
    r = [s(lr.cell(i, j).value) for j in range(1, 6)]
    if not r[1]: continue
    ret.append({'linha': r[0], 'termo': r[1], 'classificacao': r[2], 'motivo': r[3], 'relacionado': r[4]})
out['retiradas'] = ret

lm = wb1['Leia-me']
out['leiame1'] = [{'t': s(lm.cell(i,1).value), 'd': s(lm.cell(i,2).value)}
                  for i in range(1, lm.max_row+1) if s(lm.cell(i,1).value) or s(lm.cell(i,2).value)]

# ---------- FILE 2 ----------
wb2 = openpyxl.load_workbook(F2, data_only=True)

rs = wb2['Resoluções']
resolucoes = []
for row in rs.iter_rows(min_row=2, values_only=True):
    if not s(row[1]): continue
    numero = s(row[1])
    m = re.search(r'nº\s*(\d+)', numero)
    resolucoes.append({
        'n': m.group(1) if m else s(row[0]),
        'titulo': numero,
        'ementa': s(row[2]), 'status': s(row[3]), 'anexo': s(row[4]),
        'term_origem': s(row[5]), 'term_verif': s(row[6]),
        'ocorrencias': int(num(row[7]) or 0),
        'onde': s(row[8]), 'obs': s(row[9]),
    })
out['resolucoes'] = resolucoes

comp_ws = wb2['Compilação']
ch = [s(c) for c in next(comp_ws.iter_rows(min_row=1, max_row=1, values_only=True))]
ck = ['id','termo','como_consta','definicao','res','fonte_doc','local','tipo','ramo','superordenado','anel',
      'i_repete','i_artigo','i_periodos','i_exemplos','i_negativa','extensao','conferencia','situacao',
      'outras','fonte_citada','relacao','obs']
comp = []
for row in comp_ws.iter_rows(min_row=2, values_only=True):
    if not s(row[0]): continue
    d = {}
    for i, k in enumerate(ck):
        v = s(row[i]) if i < len(row) else ''
        if k == 'res':
            v = v.replace('.0','')
        if k == 'extensao':
            d[k] = int(num(row[i]) or 0); continue
        if k.startswith('i_'):
            d[k] = 1 if v else 0; continue
        d[k] = v
    comp.append(d)
out['compilacao'] = comp

dg = wb2['Diagnóstico por termo']
dk = ['termo','ramo','anel','ocorrencias','n_res','resolucoes','convergencia','redacoes','dbta','selecao',
      'codigo_arvore','ind_formal','encaminhamento','obs']
diag = []
for row in dg.iter_rows(min_row=2, values_only=True):
    if not s(row[0]): continue
    d = {}
    for i, k in enumerate(dk):
        v = s(row[i]) if i < len(row) else ''
        if k in ('ocorrencias','n_res','redacoes','ind_formal'):
            d[k] = int(num(row[i]) or 0); continue
        d[k] = v.replace('.0','') if k == 'resolucoes' else v
    diag.append(d)
out['diagnostico'] = diag

dx = wb2['Dicionário x Conarq']
cruz = []
for row in dx.iter_rows(min_row=2, values_only=True):
    if not s(row[1]): continue
    cruz.append({'codigo': s(row[0]), 'termo': s(row[1]), 'situacao': s(row[2]),
                 'definido': s(row[3]), 'ocorrencias': int(num(row[4]) or 0),
                 'resolucoes': s(row[5]).replace('.0',''), 'convergencia': s(row[6])})
out['cruzamento'] = cruz

lm2 = wb2['Leia-me']
out['leiame2'] = [{'t': s(lm2.cell(i,2).value), 'd': s(lm2.cell(i,3).value)}
                  for i in range(1, lm2.max_row+1) if s(lm2.cell(i,2).value) or s(lm2.cell(i,3).value)]

sin = wb2['Síntese']
sintese = []
for i in range(1, sin.max_row+1):
    r = [s(sin.cell(i,j).value) for j in range(1,16)]
    if any(r): sintese.append(r)
out['sintese_raw'] = sintese

D = os.path.dirname(os.path.abspath(__file__)) + '/'
with open(D+'dados.json','w') as f: json.dump(out, f, ensure_ascii=False)
for k,v in out.items():
    print(k, len(v))
print('codes sample:', [t['codigo'] for t in tree[:12]])
