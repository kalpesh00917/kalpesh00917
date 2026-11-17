import json, glob, datetime, math
D="c6/"  # cached 6-year daily files
NC=lambda x:0.5*(1+math.erf(x/math.sqrt(2)))
R_=0.065
def put(S,K,T,v):
    if T<=0: return max(K-S,0)
    d1=(math.log(S/K)+(R_+v*v/2)*T)/(v*math.sqrt(T)); d2=d1-v*math.sqrt(T)
    return K*math.exp(-R_*T)*NC(-d2)-S*NC(-d1)
def ema(x,n):
    k=2/(n+1); o=[x[0]]
    for v in x[1:]: o.append(o[-1]+k*(v-o[-1]))
    return o
def rsi2(c):
    o=[50]*len(c); g=l=0.0
    for i in range(1,len(c)):
        d=c[i]-c[i-1]; u,dn=max(d,0),max(-d,0)
        if i<=2: g+=u/2; l+=dn/2
        else: g=(g+u)/2; l=(l+dn)/2
        if i>=2: o[i]=100 if l==0 else 100-100/(1+g/l)
    return o
SIGS=["any_uptrend_day","dip_weakclose_uptrend","user_breakout_weekly"]
STR=[("short 0.5sd below",0.5),("short 1.0sd below",1.0)]; WID=0.5
HOLDS=(5,21)   # trading days; 21 = held to expiry
T={s:{(n,h):[] for n,_ in STR for h in HOLDS} for s in SIGS}
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
    lr=[0]+[math.log(C[x]/C[x-1]) for x in range(1,n)]
    for i in range(1000,n-22):
        w=widx[i]
        if w<210: continue
        s0=wEnd[w-1]+1; ph=max(H[s0:i+1]); pl=min(L[s0:i+1])
        hh=max(max(wH[w-199:w]),ph); ll=min(min(wL[w-199:w]),pl)
        wr=(hh-C[i])/(hh-ll)*-100
        fm=ef[w-1]+af*(C[i]-ef[w-1]); sm=es[w-1]+as_*(C[i]-es[w-1]); m=fm-sm; sgl=sg[w-1]+ag*(m-sg[w-1])
        wkok=wr>-20 and m>sgl and m>0
        up=C[i]>e50[i] and e20[i]>e50[i]
        ibs=(C[i]-L[i])/(H[i]-L[i]) if H[i]>L[i] else .5
        on={"any_uptrend_day":up,
            "dip_weakclose_uptrend":up and r2[i]<10 and ibs<0.25,
            "user_breakout_weekly":wkok and C[i]>max(H[i-20:i])}
        if not any(on.values()): continue
        iv=max(math.sqrt(sum(x*x for x in lr[i-19:i+1])/20*252)*1.15,0.15)
        S0=C[i]; step=5 if S0<500 else 10 if S0<2000 else 50; sd=S0*iv*math.sqrt(30/365)
        for name,kk in STR:
            Ks=round((S0-kk*sd)/step)*step; Kl=min(round((Ks-WID*sd)/step)*step, Ks-step)
            if Kl<=0: continue
            width=Ks-Kl
            credit=put(S0,Ks,30/365,iv)*0.985-put(S0,Kl,30/365,iv)*1.015
            if credit<=0.002*S0 or credit>=width*0.95: continue
            risk=width-credit
            for h in HOLDS:
                if h==21:
                    pnl=credit-(max(Ks-C[i+h],0)-max(Kl-C[i+h],0))
                else:
                    Tm=(30-h*1.4)/365
                    pnl=credit-(put(C[i+h],Ks,Tm,iv)*1.015-put(C[i+h],Kl,Tm,iv)*0.985)
                for sname,o in on.items():
                    if o: T[sname][(name,h)].append((d[i],r2[i],pnl/risk))
alld=sorted({x[0] for s in T for k in T[s] for x in T[s][k]}); mid=alld[len(alld)//2]
def st(lst):
    if not lst: return (0,)*8
    r=[x[2] for x in lst]; byd={}
    for dt,rv,ret in lst:
        if dt not in byd or rv<byd[dt][0]: byd[dt]=(rv,ret)
    eq=1.0; pk=1.0; dd=0.0
    for dt in sorted(byd):
        eq*=1+0.01*byd[dt][1]; pk=max(pk,eq); dd=min(dd,eq/pk-1)
    rs=sorted(r)
    return (len(r),100*sum(x>0 for x in r)/len(r),100*sum(r)/len(r),100*rs[0],100*sum(x<=-0.99 for x in r)/len(r),100*(eq-1),100*dd,0)
print("period %s to %s (split %s). Return = %% of max risk (width - credit). Portfolio: 1 trade/day, 1%% of equity at max loss.\n"%(alld[0],alld[-1],mid))
for s in SIGS:
    print("SIGNAL:",s)
    print("  %-19s %-8s %6s %6s %8s %8s %7s | %8s %8s | %s"%("structure","exit","N","WIN%","avg%","worst%","full-loss%","port ret%","maxDD%","avg% 1st half / 2nd half"))
    for name,_ in STR:
        for h in HOLDS:
            L_=T[s][(name,h)]; a=st(L_); b=st([x for x in L_ if x[0]<mid]); c=st([x for x in L_ if x[0]>=mid])
            print("  %-19s %-8s %6d %6.1f %+8.1f %+8.0f %9.1f | %+8.1f %+8.1f | %+6.1f / %+6.1f"%(name,"5 days" if h==5 else "expiry",a[0],a[1],a[2],a[3],a[4],a[5],a[6],b[2],c[2]))
    print()
