import pickle,re,sys,numpy as np
from shapely.geometry import LineString, box
from shapely.ops import unary_union
P=pickle.load(open('plans.pkl','rb'))
seen=set()
res={}
for nm,ents in P:
    if not re.search(r'GR\d', nm) or nm in seen: continue
    seen.add(nm)
    pts=[]
    for e in ents:
        if e[0]=='T':
            m=re.match(r'\s*(%%P|±|\+|-)?(\d+\.\d\d)\s*\((\d+\.\d\d)\)', e[3])
            if m: pts.append((e[2][1], float(m.group(3))))
    pts=np.array(sorted(set(pts)))
    a,b=np.polyfit(pts[:,0],pts[:,1]*100,1)
    resid=np.abs(np.polyval([a,b],pts[:,0])-pts[:,1]*100).max()
    lines=[LineString(e[2]).buffer(1.5) for e in ents if e[0]=='L' and e[1]=='3_IFC_Window']
    U=unary_union(lines)
    geoms=getattr(U,'geoms',[U])
    xs=[p[0] for e in ents if e[0]=='L' and e[1] in ('0_IFC_Elevation_3','0_IFC_Elevation_4','0_IFC_Concrete Trace') for p in e[2]]
    wins=[]
    for g in geoms:
        x0,y0,x1,y1=g.bounds
        if x1-x0>30 and y1-y0>30:
            wins.append((round(x0+1.5),round(x1-1.5),round(np.polyval([a,b],y0+1.5)/100,2),round(np.polyval([a,b],y1-1.5)/100,2)))
    print(nm, 'scale',round(a,4),'resid',round(resid,1), 'levels', sorted(set(pts[:,1])))
    for w in sorted(wins,key=lambda w:(w[2],w[0])): print('   x %d-%d w=%d  z %.2f-%.2f h=%d'%(w[0],w[1],w[1]-w[0],w[2],w[3],round((w[3]-w[2])*100)))
    res[nm]=dict(a=a,b=b,wins=wins)
pickle.dump(res,open('elev.pkl','wb'))
