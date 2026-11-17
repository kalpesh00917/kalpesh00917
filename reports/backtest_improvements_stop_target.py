import json, glob, datetime, math, itertools
D="c6/"  # cached 6-year daily files
def ema(x,n):
    k=2/(n+1); o=[x[0]]
    for v in x[1:]: o.append(v+0 if False else o[-1]+k*(v-o[-1]))
    return o
def rsi2(c):
    o=[50]*len(c); g=l=0.0
    for i in range(1,len(c)):
        d=c[i]-c[i-1]; u,dn=max(d,0),max(-d,0)
        if i<=2: g+=u/2; l+=dn/2
        else: g=(g+u)/2; l=(l+dn)/2
        if i>=2: o[i]=100 if l==0 else 100-100/(1+g/l)
    return o
ENT=["breakout","dip_in_weekly_uptrend","dip_weakclose_weeklyuptrend","dip_weakclose_uptrend_only"]
EXITS=[(0.5,1.5),(1.0,1.5),(1.5,1.5),(2.0,1.0),(3.0,1.0)]   # (target ATR, stop ATR); max hold 5 days
sig={e:[] for e in ENT}   # (date, rsi2, [results per exit in R])
for f in glob.glob(D+"*.json"):
    rows=json.load(open(f)); n=len(rows)
    d=[datetime.date.fromisoformat(r[0]) for r in rows]; H=[r[1] for r in rows]; L=[r[2] for r in rows]; C=[r[3] for r in rows]
    wk=[x.isocalendar()[:2] for x in d]; wH,wL,wC,wEnd=[],[],[],[]; i=0
    while i<n:
        j=i
        while j+1<n and wk[j+1]==wk[i]: j+=1
        wH.append(max(H[i:j+1])); wL.append(min(L[i:j+1])); wC.append(C[j]); wEnd.append(j); i=j+1
    af,as_,ag=2/25,2/53,2/15
    ef=[wC[0]]; es=[wC[0]]
    for c in wC[1:]: ef.append(ef[-1]+af*(c-ef[-1])); es.append(es[-1]+as_*(c-es[-1]))
    mac=[a-b for a,b in zip(ef,es)]; sg=[mac[0]]
    for m in mac[1:]: sg.append(sg[-1]+ag*(m-sg[-1]))
    widx=[0]*n; k=0
    for w,e in enumerate(wEnd):
        for x in range(k,e+1): widx[x]=w
        k=e+1
    e20,e50=ema(C,20),ema(C,50); r2=rsi2(C)
    tr=[0]+[max(H[x]-L[x],abs(H[x]-C[x-1]),abs(L[x]-C[x-1])) for x in range(1,n)]
    for i in range(1000,n-6):
        w=widx[i]
        if w<210: continue
        s0=wEnd[w-1]+1; ph=max(H[s0:i+1]); pl=min(L[s0:i+1])
        hh=max(max(wH[w-199:w]),ph); ll=min(min(wL[w-199:w]),pl)
        wr=(hh-C[i])/(hh-ll)*-100
        fm=ef[w-1]+af*(C[i]-ef[w-1]); sm=es[w-1]+as_*(C[i]-es[w-1]); m=fm-sm; sgl=sg[w-1]+ag*(m-sg[w-1])
        wkok=wr>-20 and m>sgl and m>0
        up=C[i]>e50[i] and e20[i]>e50[i]
        ibs=(C[i]-L[i])/(H[i]-L[i]) if H[i]>L[i] else .5
        atr=sum(tr[i-13:i+1])/14
        on={"breakout":wkok and C[i]>max(H[i-20:i]),
            "dip_in_weekly_uptrend":wkok and r2[i]<10,
            "dip_weakclose_weeklyuptrend":wkok and r2[i]<10 and ibs<0.25,
            "dip_weakclose_uptrend_only":up and r2[i]<10 and ibs<0.25}
        for e,o in on.items():
            if not o: continue
            res=[]
            for tg,st in EXITS:
                out=None
                for h in range(1,6):
                    if L[i+h]<=C[i]-st*atr: out=-1.0; break          # stop first if both hit
                    if H[i+h]>=C[i]+tg*atr: out=tg/st; break
                if out is None: out=(C[i+5]-C[i])/atr/st
                res.append(out-0.03/st*0.0)  # R units (costs ignored here, noted)
            sig[e].append((d[i],r2[i],res))
mid=sorted({s[0] for e in sig for s in sig[e]})[len(sig["breakout"] and {s[0] for s in sig["breakout"]} or [0])*0]
alld=sorted({s[0] for e in sig for s in sig[e]}); mid=alld[len(alld)//2]
def stats(lst,xi):
    # one trade per day (lowest RSI2), 1% risk per trade, compounding
    byd={}
    for dt,r,res in lst:
        if dt not in byd or r<byd[dt][0]: byd[dt]=(r,res[xi])
    eq=1.0; peak=1.0; mdd=0.0; w=0; n=0; sumR=0
    for dt in sorted(byd):
        R=byd[dt][1]; n+=1; w+= R>0; sumR+=R
        eq*=1+0.01*R; peak=max(peak,eq); mdd=min(mdd,eq/peak-1)
    return n, (100*w/n if n else 0), (sumR/n if n else 0), 100*(eq-1), 100*mdd
print("Test period %s to %s (split %s). One trade per day, risk 1%% per trade, max hold 5 days, stop checked first.\n"%(alld[0],alld[-1],mid))
print("%-30s %-14s %5s %6s %7s %8s %8s | %s"%("ENTRY","target/stop ATR","N","WIN%","avgR","return%","maxDD%","1st half win/avgR | 2nd half win/avgR"))
for e in ENT:
    for xi,(tg,st) in enumerate(EXITS):
        a=stats(sig[e],xi); h1=stats([s for s in sig[e] if s[0]<mid],xi); h2=stats([s for s in sig[e] if s[0]>=mid],xi)
        print("%-30s %-14s %5d %6.1f %+7.3f %8.1f %8.1f | %4.0f%% %+6.3f | %4.0f%% %+6.3f"%(e,"%.1f/%.1f"%(tg,st),a[0],a[1],a[2],a[3],a[4],h1[1],h1[2],h2[1],h2[2]))
    print()
