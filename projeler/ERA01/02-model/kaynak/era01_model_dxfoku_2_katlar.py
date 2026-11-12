import pickle, json, re, math
from shapely.geometry import Polygon, LineString, Point, box, MultiPolygon
from shapely.ops import unary_union, polygonize
from shapely import affinity
P=pickle.load(open('plans.pkl','rb'))
def bbox(ents):
    xs=[p[0] for e in ents if e[0]=='L' for p in e[2]]; ys=[p[1] for e in ents if e[0]=='L' for p in e[2]]
    if not xs: return None
    return (min(xs),max(xs),min(ys),max(ys))
INS=[]
for nm,ents in P:
    b=bbox(ents)
    if b: INS.append((nm,ents,((b[0]+b[1])/2,(b[2]+b[3])/2)))
def get(nm, c):
    best=None
    for n,e,cc in INS:
        if n==nm:
            d=math.hypot(cc[0]-c[0],cc[1]-c[1])
            if best is None or d<best[0]: best=(d,e)
    assert best and best[0]<200, (nm,c,best and best[0])
    return best[1]
FLOORS={
 'A':[('B1',(94875,26684),[('A B1 PLAN',(95875,26729)),('A B1 ST',(95875,26729)),('A B1 BRUT ALAN',(95875,26729)),('A_B1_ALAN',(95875,26719)),('A B1 DOGRAMA',(96118,26956)),('A B1 SAFTLAR',(95875,26144))]),
      ('ZK',(98944,26684),[('A ZK PLAN',(99944,26259)),('A NK ST',(99944,26259)),('A_ZK_BRUT ALAN',(99944,26259)),('A_NK_ALAN',(99944,26674)),('A ZK DOGRAMA',(99969,26266)),('A ZK SAFTLAR',(99944,26144)),('A ZK GIRIS MERD',(100309,25774))]),
      ('K1',(103020,27598),[('A K1 PLAN',(104020,27173)),('A NK ST',(104020,27173)),('A_K1_ALAN',(104020,27173)),('A K1 DOGRAMA',(103965,27180)),('A K1 SAFT',(104020,26975))]),
      ('CATI',(105934,27598),[('A_CATI PLANI',(106934,27223)),('A BLOK CATI KOTLARI',(106934,27223))])],
 'B':[('B2',(94839,22410),[('B_BK2_PLAN',(95839,22200)),('B BK2 STR',(95839,22318)),('B_BK2_NET ALAN',(95839,22203)),('D BLOK_B2_BRUT ALAN',(95839,22203))]),
      ('B1',(99752,23172),[('B_B1 PLAN',(100612,22571)),('B B1 ST',(100597,22556)),('A_B1_NET ALAN',(100612,22561)),('D BLOK_B1_BRUT ALAN',(100597,22557)),('B B1 SAFTLAR',(100997,22162))]),
      ('ZK',(103107,23172),[('B ZK PLAN',(104107,22557)),('B NK ST',(104107,22556)),('B_ZK_BRUT ALAN',(104107,22557)),('B_ZK_NET ALAN',(104107,22557)),('B ZK DOGRAMA',(104107,22564)),('B ZK_SAFTLAR',(104402,22237))]),
      ('CATI',(106020,23172),[('D_CATI PLANI',(107020,22557)),('B BLOK CATI KOTLARI',(107020,22557))])],
 'C':[('B1',(94915,18651),[('C B1 ST',(95815,18276)),('C_B1_PLAN',(95927,18261)),('C_B1_NET ALAN',(95820,18271)),('C_B1_DOGRAMA',(96483,18230))]),
      ('ZK',(97415,18651),[('C ZK ST',(98315,18276)),('C_ZK_PLAN',(98315,18276)),('C_ZK_NET ALAN',(98315,18276)),('C_ZK_DOGRAMA',(98323,18304)),('C BLOK_ZK SAFT',(97890,17946))]),
      ('CATI',(100041,18651),[('C_CATI PLANI',(100941,18276)),('C BLOK CATI KOTLARI',(100941,18276))])],
 'D':[('B1',(94961,14353),[('F_BK_PLAN',(95434,13738)),('D_BRUT ALAN',(95419,13738)),('D_BK_ALAN',(95424,13738)),('D B1 DOGRAMA',(95480,13745)),('D BLOK ST',(94991,13738)),('E-F_BK_SAFT',(95421,13498))]),
      ('ZK',(97584,14353),[('D ZK D1',(97187,13738)),('D ZK D2',(98064,13738)),('D ZK BRUT ALAN',(97614,13738)),('E-F_STR',(97614,13738)),('D_ZK_ALAN',(97619,13738)),('D ZK DOGRAMA',(97660,13745)),('E-F_ZK_SAFT',(97614,13508))]),
      ('K1',(99884,14353),[('E_K1_PLAN',(99914,13738)),('D_K1 BRUT ALAN',(99914,13738)),('E-F_STR',(99914,13738)),('E_K1_ALAN',(99914,13738)),('D_K1_DOGRAMA',(99565,13745)),('E-F_K1_SAFT',(99524,13571))]),
      ('CATI',(102184,14353),[('E-F_CATI PLANI',(102204,13738)),('D BLOK CATI KOTLARI',(101857,13738))])],
}
def polys_of(ents, layer, minarea=1):
    out=[]
    for e in ents:
        if e[0]=='L' and e[1]==layer and len(e[2])>=3:
            pts=e[2]
            if e[4] or math.hypot(pts[0][0]-pts[-1][0],pts[0][1]-pts[-1][1])<1:
                p=Polygon(pts).buffer(0)
                if p.area>minarea: out.append(p)
    return out
data={}
for blk,fls in FLOORS.items():
    data[blk]={}
    for fl,anc,names in fls:
        ents=[]
        for nm,c in names: ents+= [(nm,)+e for e in get(nm,c)]
        T=lambda g: affinity.translate(g,-anc[0],-anc[1])
        E=[e[1:] for e in ents]
        brut=[T(p) for p in polys_of(E,'0_IFC_Brüt_Alan')]
        rooms=[]; areas=[T(p) for p in polys_of(E,'0_IFC_Area')]
        texts=[(e[3],Point(e[2][0]-anc[0],e[2][1]-anc[1]),e[1],e[5] if len(e)>5 else '') for e in E if e[0]=='T']
        names_t=[t for t in texts if t[2].startswith('0_IFC_Room_Text')]
        for a in areas:
            nmz=[t for t in names_t if a.contains(t[1]) and not re.match(r'^[\d.,]+$',t[0].strip()) and t[0].strip()]
            nm=nmz[0][0].strip() if nmz else '?'
            rooms.append((nm,a))
        cols=[T(p) for p in polys_of(E,'1_IFC_Concrete_Section',minarea=50)]
        walls=[T(p) for p in polys_of(E,'2_IFC_Wall',minarea=50)]
        # windows: cluster window lines
        wl=[T(LineString(e[2])) for e in E if e[0]=='L' and e[1]=='3_IFC_Window']
        U=unary_union([l.buffer(2) for l in wl]) if wl else None
        wins=[]
        if U is not None:
            for g in getattr(U,'geoms',[U]):
                x0,y0,x1,y1=g.bounds
                if max(x1-x0,y1-y0)>40: wins.append((x0+2,y0+2,x1-2,y1-2))
        wtags=[(t[3],t[0],t[1]) for t in texts if t[2]=='0_IFC_Window_Text']
        doors=[T(LineString(e[2])) for e in E if e[0]=='L' and e[1] in ('1_IFC_Door','2_IFC_Door')]
        roof=[ [(x-anc[0],y-anc[1]) for x,y in e[2]] for e in E if e[0]=='L' and e[1].startswith('0_IFC_Elevation')]
        lvl=[(t[0],t[1].x,t[1].y) for t in texts if 'Level' in t[2]]
        data[blk][fl]=dict(brut=brut,rooms=rooms,cols=cols,walls=walls,wins=wins,wtags=wtags,doors=doors,roof=roof,lvl=lvl,texts=texts)
        print(blk,fl,'brut',[round(b.area/1e4,1) for b in brut],'rooms',len(rooms),'cols',len(cols),'walls',len(walls),'wins',len(wins),'tags',len(wtags))
pickle.dump(data,open('floors.pkl','wb'))
