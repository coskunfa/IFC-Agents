import pickle,re,sys
P=pickle.load(open('plans.pkl','rb'))
want=sys.argv[1]; xlim=float(sys.argv[2]) if len(sys.argv)>2 else 1e9
for nm,ents in P:
    if nm!=want: continue
    xs=[p[0] for e in ents if e[0]=='L' for p in e[2]]; ys=[p[1] for e in ents if e[0]=='L' for p in e[2]]
    print(nm, round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)))
    rows=[]
    for e in ents:
        if e[0]=='T' and e[2][0]<xlim and ('Level' in e[1] or re.search(r'[±+-]\d+[.,]\d\d',e[3])):
            rows.append((round(e[2][1]),round(e[2][0]),e[1][9:25],e[3].replace('\n',' ')[:40]))
    for r in sorted(set(rows)): print(r)
    break
