# -*- coding: utf-8 -*-
"""ERA01 - zemin kat paftası -> vaziyet dönüşümü (köşe kotu sembolleri eşleştirilerek; ölçek 0.25 sabit). Çıktı: era01_vaziyet_donusum.json"""
import pickle, numpy as np, collections, json
D=pickle.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'era01_geo.pkl'),'rb'))
G=D['geo'];T={t['i']:t for t in D['tops']}
def anchors(items):
    circ=[]
    for g in items:
        if g['t']=='P' and g.get('ty')=='CIRCLE':
            a=np.array(g['pts']); circ.append(a.mean(0))
    circ=np.array(circ)
    out={}
    for g in items:
        if g['t']=='T' and g['txt'].strip() and len(circ):
            k=g['txt'].strip().split()[0]
            if not k[0].isdigit(): continue
            dd=np.linalg.norm(circ-np.array([g['x'],g['y']]),axis=1)
            out.setdefault(k,[]).append(circ[dd.argmin()])
    return out
vz=[g for g in G if g['top']==367 and len(g['blk'])>1 and g['blk'][1]=='BLOK KOSE KOTLARI']
va=anchors(vz)
res={}
for name,blok in [('A KOSE KOTLARI','A'),('B KOSE KOTLARI','B'),('C KOSE KOTLARI','C'),('D KOSE KOTLARI','D')]:
    t=[t for t in T.values() if t['name']==name][0]
    pa=anchors([g for g in G if g['top']==t['i']])
    P=[];Q=[]
    for k,l in pa.items():
        if k in va and len(l)==1 and len(va[k])==1: P.append(l[0]);Q.append(va[k][0])
    P=np.array(P);Q=np.array(Q)
    mp,mq=P.mean(0),Q.mean(0);A=P-mp;B=Q-mq
    U,S_,Vt=np.linalg.svd(B.T@A);R=U@Vt
    sc=0.25
    ang0=np.degrees(np.arctan2(R[1,0],R[0,0])); ang0={'A':0.0,'B':0.0,'C':90.0}.get(blok,ang0)
    th=np.radians(ang0); R=np.array([[np.cos(th),-np.sin(th)],[np.sin(th),np.cos(th)]])
    tt=mq-sc*R@mp
    res_=np.abs((sc*(R@P.T)).T+tt-Q).max()
    ang=np.degrees(np.arctan2(R[1,0],R[0,0]))
    print(blok,len(P),round(sc,5),round(ang,3),round(res_,3))
    res[blok]=dict(s=float(sc),ang=float(ang),t=tt.tolist())
json.dump(res,open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'era01_vaziyet_donusum.json'),'w'),indent=1)
