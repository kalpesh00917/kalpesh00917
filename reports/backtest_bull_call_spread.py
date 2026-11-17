import json, glob, datetime, math
D="c6/"  # cached 6-year daily files
NC=lambda x:0.5*(1+math.erf(x/math.sqrt(2)))
def bs(S,K,T,v):
    if T<=0: return max(S-K,0)
    d1=(math.log(S/K)+(0.065+v*v/2)*T)/(v*math.sqrt(T)); d2=d1-v*math.sqrt(T)
    return S*NC(d1)-K*math.exp(-0.065*T)*NC(d2)
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
SIGS=["dip_weakclose_uptrend","user_breakout_weekly"]
STRATS=[("plain call",None),("spread width 0.5 sd",0.5),("spread width 1.0 sd",1.0)]
HOLDS=(3,5)
T={s:{(n,h):[] for n,_ in STRATS for h in HOLDS} for s in SIGS}   # (date, rsi2, ret fraction of debit)
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
        on={"dip_weakclose_uptrend":up and r2[i]<10 and ibs<0.25,
            "user_breakout_weekly":wkok and C[i]>max(H[i-20:i])}
        if not any(on.values()): continue
        iv=max(math.sqrt(sum(x*x for x in lr[i-19:i+1])/20*252)*1.15,0.15)
        S0=C[i]; step=5 if S0<500 else 10 if S0<2000 else 50
        K1=round(S0/step)*step; sd=S0*iv*math.sqrt(30/365)
        for sname,on_ in on.items():
            if not on_: continue
            for name,wd in STRATS:
                K2=None if wd is None else max(K1+step, round((K1+wd*sd)/step)*step)
                debit=bs(S0,K1,30/365,iv)*1.015-(0 if K2 is None else bs(S0,K2,30/365,iv)*0.985)
                if debit<=0.002*S0: continue
                for h in HOLDS:
                    Tm=(30-h*1.4)/365
                    val=bs(C[i+h],K1,Tm,iv)*0.985-(0 if K2 is None else bs(C[i+h],K2,Tm,iv)*1.015)
                    T[sname][(name,h)].append((d[i],r2[i],val/debit-1))
alld=sorted({x[0] for s in T for k in T[s] for x in T[s][k]}); mid=alld[len(alld)//2]
def st(lst):
    if not lst: return (0,)*7
    r=[x[2] for x in lst]; byd={}
    for dt,r2v,ret in lst:
        if dt not in byd or r2v<byd[dt][0]: byd[dt]=(r2v,ret)
    eq=1.0; pk=1.0; dd=0.0
    for dt in sorted(byd):
        eq*=1+0.01*byd[dt][1]; pk=max(pk,eq); dd=min(dd,eq/pk-1)
    rs=sorted(r)
    return (len(r),100*sum(x>0 for x in r)/len(r),100*sum(r)/len(r),100*rs[len(rs)//2],100*rs[0],100*(eq-1),100*dd)
print("period %s to %s (split %s). Return = %% of money paid. Portfolio: 1 trade/day, 1%% of equity per trade (debit).\n"%(alld[0],alld[-1],mid))
for s in SIGS:
    print("SIGNAL:",s)
    print("  %-22s %-5s %6s %6s %8s %8s %8s | %8s %8s | %8s"%("structure","hold","N","WIN%","avg%","median%","worst%","port ret%","maxDD%","avg%1sthalf/2nd"))
    for name,_ in STRATS:
        for h in HOLDS:
            L_=T[s][(name,h)]; a=st(L_); b=st([x for x in L_ if x[0]<mid]); c=st([x for x in L_ if x[0]>=mid])
            print("  %-22s %-5s %6d %6.1f %+8.1f %+8.1f %+8.1f | %+8.1f %+8.1f | %+6.1f / %+6.1f"%(name,"%dd"%h,a[0],a[1],a[2],a[3],a[4],a[5],a[6],b[2],c[2]))
    print()
