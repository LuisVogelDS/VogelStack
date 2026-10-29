"""Onde os tokens dos subagentes foram (rodada 11, 08/10/2026). Lê as transcrições JSONL e reparte:
- custo direto por chamada (usage da API), em 'tokens equivalentes de entrada':
  entrada + 1,25 x escrita de cache + 0,1 x leitura de cache + 5 x saída;
- quanto cada resultado de ferramenta pesa no contexto: o resultado entra uma vez (escrita de cache)
  e é relido em toda chamada seguinte (leitura de cache). Tamanho estimado em caracteres/4; imagem = 1600.

Uso: python Ferramentas/medir_tokens.py <pasta subagents da sessão> [ids dos agentes...]
A pasta fica em ~/.claude/projects/<projeto>/<sessão>/subagents; sem ids, mede todos os agentes dela.
(Versão canônica do VogelStack: a do Galinha, de 26/10, com a saída contada pela última linha de cada resposta; a do Slime
anterior subcontava a saída em ~30x. Não tem configuração por projeto.)

Agregado (09/10): python Ferramentas/medir_tokens.py --agregado <pasta de projeto em ~/.claude/projects>...
Junta todos os subagentes das sessões desses projetos e reparte o custo por faixa de chamadas, por modelo e
esforço, e por classe de trabalho (tipo nativo do agente, ou verbo inicial da descrição no histórico). Se existir o
registro de roteamento do HarpyNest (HarpyNest-legado/painel/logs/roteamento.<HOST>.jsonl), reparte também pela origem
da escolha e pela entrega (o quadro do plano).
"""
import json, sys, re, collections, os, glob, statistics

if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
    print(__doc__)
    sys.exit(0 if len(sys.argv) > 1 else 2)

if len(sys.argv) > 1 and sys.argv[1] == '--agregado':
    TIPOS = {'executor', 'corretor', 'leitor', 'mecanico', 'especialista', 'arquiteto', 'validador'}
    def classe(d, tipo):
        if tipo in TIPOS: return 'tipo: ' + tipo   # 09/10: tipo nativo declarado no disparo; a regex abaixo é para o histórico
        dl = d.lower()
        if tipo == 'Explore' or re.match(r'(levantar|mapear|inventariar|procurar|investigar|inspecionar)', dl): return 'leitura: levantamento'
        if re.match(r'(diagnosticar|causas|auditar|auditoria|análise|conferir)', dl): return 'leitura: diagnóstico'
        if re.match(r'(corrigir|correções)', dl) or 'arremates' in dl: return 'correção de falhas'
        if re.search(r'integra|costura|fechar ', dl): return 'integração'
        return 'implementação'
    eq = lambda u: u.get('input_tokens',0)+1.25*u.get('cache_creation_input_tokens',0)+0.1*u.get('cache_read_input_tokens',0)+5*u.get('output_tokens',0)
    # 09/10: o registro de roteamento do HarpyNest (uma linha por disparo) dá a origem da escolha e o quadro,
    # que é a chave da entrega. Junta por tool_use_id e, sem ele, por descrição + tipo.
    roteamento = {}
    for rf in glob.glob(os.path.join(os.path.expanduser('~'), 'Documents', 'HarpyNest-legado', 'painel', 'logs', 'roteamento.*.jsonl')):
        for l in open(rf, encoding='utf-8'):
            try: x = json.loads(l)
            except Exception: continue
            if x.get('tool_use_id'): roteamento[x['tool_use_id']] = x
            roteamento.setdefault((x.get('descricao'), x.get('subagent_type')), x)
            roteamento.setdefault(x.get('descricao'), x)   # sem tipo no pedido, o .meta.json diz general-purpose
    rows = []
    for proj in sys.argv[2:]:
        for f in glob.glob(os.path.join(proj, '*', 'subagents', 'agent-*.jsonl')):
            try: meta = json.load(open(f[:-6] + '.meta.json', encoding='utf-8'))
            except Exception: meta = {}
            txt = open(f, encoding='utf-8').read()
            ef = re.search(r'"effort":"(\w+)"', txt)
            # A mesma resposta vem em várias linhas (uma por bloco), e só a última traz a saída inteira:
            # fica, por id, o usage de maior output_tokens (26/10: pegar o primeiro subcontava a saída em ~30x).
            porid = {}; mod = None
            for l in txt.splitlines():
                try: j = json.loads(l)
                except Exception: continue
                m = j.get('message') or {}
                if j.get('type') == 'assistant' and m.get('usage'):
                    u = m['usage']; v = porid.get(m.get('id'))
                    if v is None or u.get('output_tokens', 0) > v.get('output_tokens', 0): porid[m.get('id')] = u
                    mod = mod or m.get('model')
            us = list(porid.values())
            if not us: continue   # 09/10: agente curto também conta na entrega (antes: menos de 3 chamadas saía)
            rt = roteamento.get(meta.get('toolUseId')) or roteamento.get((meta.get('description'), meta.get('agentType'))) or roteamento.get(meta.get('description')) or {}
            rows.append(dict(origem=rt.get('origem', 'antes do roteamento'), quadro=rt.get('quadro') or '(sem quadro)', n=len(us), custo=sum(eq(u) for u in us), mod=(mod or '?').replace('claude-', ''),
                             ef=meta.get('effort') or (ef.group(1) if ef else '?'), c=classe(meta.get('description', ''), meta.get('agentType'))))
    tot = sum(r['custo'] for r in rows)
    print(f"{len(rows)} agentes, {tot/1e6:.0f} M equivalentes")
    def bloco(titulo, chave):
        print('\n== ' + titulo)
        for k in sorted({chave(r) for r in rows}, key=lambda k: -sum(r['custo'] for r in rows if chave(r) == k)):
            g = [r for r in rows if chave(r) == k]
            print(f"   {str(k):34} {len(g):>4} ag  {sum(r['custo'] for r in g)/tot:5.0%}  mediana {statistics.median(r['n'] for r in g):>4.0f} ch, {statistics.median(r['custo'] for r in g)/1e6:5.2f} M")
    faixas = [(0, 30), (30, 60), (60, 100), (100, 150), (150, 10**9)]
    bloco('faixa de chamadas', lambda r: next(f"{a}-{b if b < 10**9 else ''}" for a, b in faixas if a <= r['n'] < b))
    bloco('modelo e esforço', lambda r: f"{r['mod']} / {r['ef']}")
    bloco('classe de trabalho', lambda r: r['c'])
    if roteamento:
        bloco('origem da escolha (roteamento)', lambda r: r['origem'])
        bloco('entrega (quadro do plano)', lambda r: r['quadro'])
    sys.exit(0)

D = sys.argv[1]
ids = sys.argv[2:] or [os.path.basename(p)[6:-6] for p in sorted(glob.glob(os.path.join(D, 'agent-*.jsonl')))]

def cat_bash(cmd):
    c = cmd
    if 'testar.py' in c or 'unity_batch' in c: return 'Bash: Unity (testar/fila)'
    if 'compilar_fora' in c: return 'Bash: compilar fora'
    if re.search(r'\bgit\b', c): return 'Bash: git'
    if re.search(r'Logs/|\.log\b|Editor\.log|bateria', c): return 'Bash: ler log/bateria'
    if re.search(r'\b(grep|rg|find|ls)\b', c): return 'Bash: busca (grep/find/ls)'
    if re.search(r'\b(sed|cat|head|tail|awk)\b', c): return 'Bash: ler arquivo (sed/cat)'
    if 'sleep' in c or 'tasks/' in c: return 'Bash: espera/consulta'
    return 'Bash: outro'

def cat_tool(name, inp):
    if name == 'Bash': return cat_bash(inp.get('command', ''))
    if name == 'Read':
        p = inp.get('file_path', '').lower()
        if p.endswith(('.png', '.jpg')): return 'Read: imagem'
        if p.endswith('.cs'): return 'Read: código .cs'
        if p.endswith('.md'): return 'Read: docs .md'
        if p.endswith(('.log', '.txt')): return 'Read: log/relatório'
        return 'Read: outro'
    if name in ('Edit', 'Write'): return name
    return name

def tamanho(content):
    if isinstance(content, str): return len(content) / 4, 0
    t = 0; img = 0
    for b in content or []:
        if b.get('type') == 'text': t += len(b.get('text', '')) / 4
        elif b.get('type') == 'image': t += 1600; img += 1
    return t, img

tot = collections.Counter()
for aid in ids:
    f = os.path.join(D, f'agent-{aid}.jsonl')
    linhas = [json.loads(l) for l in open(f, encoding='utf-8') if l.strip()]
    vistos = set(); chamadas = []   # (indice de linha, usage)
    usos = {}; nomes = {}
    eventos = []  # sequência: ('call', usage) | ('result', cat, tok, img)
    for l in linhas:
        m = l.get('message') or {}
        if l.get('type') == 'assistant':
            mid = m.get('id')
            for b in m.get('content') or []:
                if b.get('type') == 'tool_use': nomes[b['id']] = cat_tool(b['name'], b.get('input') or {})
            u = m.get('usage') or {}
            if mid and mid not in usos:
                usos[mid] = len(eventos); eventos.append(('call', u))
            elif mid and u.get('output_tokens', 0) > eventos[usos[mid]][1].get('output_tokens', 0):
                eventos[usos[mid]] = ('call', u)   # a última linha da resposta traz a saída inteira
        elif l.get('type') == 'user' and isinstance(m.get('content'), list):
            for b in m['content']:
                if b.get('type') == 'tool_result':
                    tk, img = tamanho(b.get('content'))
                    eventos.append(('result', nomes.get(b.get('tool_use_id'), '?'), tk, img))
    calls = [e for e in eventos if e[0] == 'call']
    n = len(calls)
    def eq(u): return u.get('input_tokens', 0) + 1.25 * u.get('cache_creation_input_tokens', 0) + 0.1 * u.get('cache_read_input_tokens', 0) + 5 * u.get('output_tokens', 0)
    direto = sum(eq(u) for _, u in calls)
    saida = sum(5 * u.get('output_tokens', 0) for _, u in calls)
    leit = sum(0.1 * u.get('cache_read_input_tokens', 0) for _, u in calls)
    escr = sum(1.25 * u.get('cache_creation_input_tokens', 0) + u.get('input_tokens', 0) for _, u in calls)
    pico = max((u.get('cache_read_input_tokens', 0) + u.get('cache_creation_input_tokens', 0) + u.get('input_tokens', 0)) for _, u in calls)
    base = calls[0][1]; base_ctx = base.get('cache_read_input_tokens', 0) + base.get('cache_creation_input_tokens', 0) + base.get('input_tokens', 0)
    por = collections.Counter(); qtd = collections.Counter(); imgs = 0
    restantes = n
    for e in eventos:
        if e[0] == 'call': restantes -= 1; continue
        _, c, tk, img = e
        por[c] += tk * (1.25 + 0.1 * restantes); qtd[c] += 1; imgs += img
    meta = json.load(open(f.replace('.jsonl', '.meta.json'), encoding='utf-8'))
    print(f"\n== {meta.get('description', aid)}: {n} chamadas, contexto inicial {base_ctx/1e3:.0f} mil, pico {pico/1e3:.0f} mil, {imgs} imagens")
    print(f"   custo equivalente {direto/1e3:.0f} mil  (saída {saida/direto:.0%}, releitura do contexto {leit/direto:.0%}, escrita/entrada {escr/direto:.0%})")
    base_carry = base_ctx * 0.1 * n
    print(f"   só o contexto inicial relido em toda chamada: {base_carry/1e3:.0f} mil ({base_carry/direto:.0%})")
    for c, v in por.most_common(9):
        print(f"   {v/direto:5.0%}  {c}  ({qtd[c]}x)")
        tot[c] += v
    tot['__total'] += direto; tot['__saida'] += saida; tot['__base'] += base_carry
print('\n== TOTAL', f"{tot['__total']/1e3:.0f} mil; saída {tot['__saida']/tot['__total']:.0%}; contexto inicial {tot['__base']/tot['__total']:.0%}")
for c, v in sorted(((c, v) for c, v in tot.items() if not c.startswith('__')), key=lambda x: -x[1])[:12]:
    print(f"   {v/tot['__total']:5.0%}  {c}")
