import json, glob, datetime, math, statistics as st
D="c6/"  # folder of cached 6-year daily files: [date, high, low, close, volume]
NC=lambda x:0.5*(1+math.erf(x/math.sqrt(2)))
def bs(S,K,T,v):
    if T<=0: return max(S-K,0)
    d1=(math.log(S/K)+(0.065+v*v/2)*T)/(v*math.sqrt(T)); d2=d1-v*math.sqrt(T)
    return S*NC(d1)-K*math.exp(-0.065*T)*NC(d2)
HOLDS=(1,3,5,10)
GR=("ALL","BRK","WK","FULL")
R={g:{h:[] for h in HOLDS} for g in GR}      # (date, %return of stock)
O={g:{h:[] for h in (3,5)} for g in ("BRK","FULL")}  # (date, option return)
nf=0
for f in glob.glob(D+"*.json"):
    rows=json.load(open(f)); n=len(rows)
    d=[datetime.date.fromisoformat(r[0]) for r in rows]; H=[r[1] for r in rows]; L=[r[2] for r in rows]; C=[r[3] for r in rows]
    wk=[x.isocalendar()[:2] for x in d]
    wH,wL,wC,wEnd=[],[],[],[]; i=0
    while i<n:
        j=i
        while j+1<n and wk[j+1]==wk[i]: j+=1
        wH.append(max(H[i:j+1])); wL.append(min(L[i:j+1])); wC.append(C[j]); wEnd.append(j); i=j+1
    af,as_,ag=2/25,2/53,2/15
    ef=[wC[0]]; es=[wC[0]]
    for c in wC[1:]: ef.append(ef[-1]+af*(c-ef[-1])); es.append(es[-1]+as_*(c-es[-1]))
    mac=[a-b for a,b in zip(ef,es)]; sig=[mac[0]]
    for m in mac[1:]: sig.append(sig[-1]+ag*(m-sig[-1]))
    widx=[0]*n; k=0
    for w,e in enumerate(wEnd):
        for x in range(k,e+1): widx[x]=w
        k=e+1
    lr=[0]+[math.log(C[x]/C[x-1]) for x in range(1,n)]
    nf+=1
    for i in range(1000,n-10):
        w=widx[i]
        if w<210: continue
        s0=wEnd[w-1]+1
        ph=max(H[s0:i+1]); pl=min(L[s0:i+1])
        hh=max(max(wH[w-199:w]),ph); ll=min(min(wL[w-199:w]),pl)
        wr=(hh-C[i])/(hh-ll)*-100
        fm=ef[w-1]+af*(C[i]-ef[w-1]); sm=es[w-1]+as_*(C[i]-es[w-1]); m=fm-sm; sg=sig[w-1]+ag*(m-sig[w-1])
        wkok= wr>-20 and m>sg and m>0
        brk= C[i]>max(H[i-20:i])
        on={"ALL":True,"BRK":brk,"WK":wkok,"FULL":wkok and brk}
        for g in GR:
            if on[g]:
                for h in HOLDS: R[g][h].append((d[i],(C[i+h]/C[i]-1)*100))
        if brk:
            iv=max(math.sqrt(sum(x*x for x in lr[i-19:i+1])/20*252)*1.15,0.15)
            S0=C[i]; step=5 if S0<500 else 10 if S0<2000 else 50; K=round(S0/step)*step
            p0=bs(S0,K,30/365,iv)*1.015
            if p0>0:
                for h in (3,5):
                    v=bs(C[i+h],K,(30-h*1.4)/365,iv)*0.985
                    for g in ("BRK",) + (("FULL",) if wkok else ()):
                        O[g][h].append((d[i],(v/p0-1)*100))
allm=sorted({x[0] for x in R["ALL"][1]}); mid=allm[len(allm)//2]
print("stocks",nf,"test period",allm[0],"to",allm[-1],"split at",mid)
def line(lst):
    if not lst: return "n=0"
    r=[x[1] for x in lst]; a=[x[1] for x in lst if x[0]<mid]; b=[x[1] for x in lst if x[0]>=mid]
    f=lambda z:(100*sum(q>0 for q in z)/len(z)) if z else float('nan')
    g=lambda z:(sum(z)/len(z)) if z else float('nan')
    return "n=%5d up=%4.1f%% avg=%+5.2f%% median=%+5.2f%% | 1st half up=%4.1f%% avg=%+5.2f%% (n=%d) | 2nd half up=%4.1f%% avg=%+5.2f%% (n=%d)"%(len(r),f(r),g(r),st.median(r),f(a),g(a),len(a),f(b),g(b),len(b))
print("\nSTOCK RETURNS (enter at signal-day close)")
for g,name in (("ALL","every day (baseline)"),("BRK","20d breakout only"),("WK","weekly filters only"),("FULL","weekly filters + breakout  <== YOUR STRATEGY")):
    print(name)
    for h in HOLDS: print("  hold %2dd %s"%(h,line(R[g][h])))
print("\nSIMULATED ATM CALL, 30 days to expiry (option return)")
for g,name in (("BRK","20d breakout only"),("FULL","YOUR STRATEGY")):
    for h in (3,5): print("  %-18s hold %dd %s"%(name,h,line(O[g][h])))
