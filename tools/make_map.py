"""Генератор SVG-карты маршрута для index.html.

Запуск:  python3 tools/make_map.py /tmp/map.svg
Затем заменить в index.html блок <svg class="map-svg" ...>...</svg> содержимым файла.
Проекция простая: x = (долгота - 72.6) * 800, y = (4.5 - широта) * 800 (1 км ≈ 7.2 единицы).
Координаты островов — по Википедии; контуры атоллов схематичные.
"""
import math, random
random.seed(7)
K=800
def P(lon,lat): return ((lon-72.6)*K, (4.5-lat)*K)
def f(v): return f"{v:.1f}"

def catmull(pts, closed=False, tension=0.5):
    """Catmull-Rom -> list of cubic bezier segments (p0,c1,c2,p1)."""
    n=len(pts); segs=[]
    rng = range(n) if closed else range(n-1)
    for i in rng:
        p0=pts[(i-1)%n] if (closed or i>0) else pts[i]
        p1=pts[i]; p2=pts[(i+1)%n]
        p3=pts[(i+2)%n] if (closed or i+2<n) else p2
        c1=(p1[0]+(p2[0]-p0[0])*tension/3, p1[1]+(p2[1]-p0[1])*tension/3)
        c2=(p2[0]-(p3[0]-p1[0])*tension/3, p2[1]-(p3[1]-p1[1])*tension/3)
        segs.append((p1,c1,c2,p2))
    return segs
def d_of(segs, closed=False):
    s=f"M{f(segs[0][0][0])} {f(segs[0][0][1])}"
    for _,c1,c2,p in segs: s+=f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p[0])} {f(p[1])}"
    return s+("Z" if closed else "")
def sample(segs, step=3):
    out=[]
    for p0,c1,c2,p1 in segs:
        L=math.dist(p0,p1)+1; n=max(4,int(L/step))
        for k in range(n):
            t=k/n; mt=1-t
            x=mt**3*p0[0]+3*mt*mt*t*c1[0]+3*mt*t*t*c2[0]+t**3*p1[0]
            y=mt**3*p0[1]+3*mt*mt*t*c1[1]+3*mt*t*t*c2[1]+t**3*p1[1]
            out.append((x,y))
    return out

atolls = {
 "north-male":[(73.36,4.62),(73.50,4.64),(73.62,4.52),(73.63,4.36),(73.575,4.225),(73.52,4.165),(73.45,4.18),(73.38,4.24),(73.33,4.38),(73.32,4.52)],
 "south-male":[(73.31,4.10),(73.40,4.135),(73.49,4.12),(73.545,4.03),(73.53,3.94),(73.47,3.885),(73.39,3.90),(73.32,3.97),(73.29,4.04)],
 "vaavu":[(73.40,3.645),(73.50,3.62),(73.57,3.55),(73.60,3.45),(73.56,3.33),(73.47,3.29),(73.39,3.33),(73.35,3.44),(73.36,3.56)],
 "ari":[(72.80,4.24),(72.90,4.22),(72.97,4.12),(72.99,3.98),(72.99,3.82),(72.975,3.66),(72.945,3.535),(72.88,3.462),(72.80,3.458),(72.74,3.53),(72.71,3.68),(72.70,3.86),(72.71,4.04),(72.74,4.17)],
}
small = {"rasdhoo":(72.99,4.265,0.035,0.028), "fulidhoo":(73.416,3.683,0.022,0.016)}

svg=[]
W=['<svg class="map-svg" viewBox="40 120 930 880" role="img" aria-labelledby="mapTitle mapDesc" xmlns="http://www.w3.org/2000/svg">',
   '<title id="mapTitle">Схема маршрута по Мальдивам</title>',
   '<desc id="mapDesc">Яхта выходит из Мале, идёт к острову Гурайдо в атолле Южный Мале и к атоллу Ваафу и возвращается к Мале. Затем скоростной паром везёт группу на остров Дигура в атолле Ари; оттуда выезды на острова Дангети и Омаду, на резорт и к китовым акулам. В последний день паром возвращает группу в аэропорт Мале.</desc>',
   '<defs>',
   '<radialGradient id="lagoon" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#5FC9CC" stop-opacity=".30"/><stop offset="1" stop-color="#2C9FA8" stop-opacity=".12"/></radialGradient>',
   '<radialGradient id="sea" cx="55%" cy="40%" r="75%"><stop offset="0" stop-color="#17435A"/><stop offset="1" stop-color="#0B2233"/></radialGradient>',
   '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>',
   '</defs>',
   '<rect x="40" y="120" width="930" height="880" fill="url(#sea)"/>']
svg+=W
# grid
g=['<g class="grid">']
for lat,lbl in [(4.25,"4°15′"),(4.0,"4°00′"),(3.75,"3°45′"),(3.5,"3°30′"),(3.25,"3°15′")]:
    y=(4.5-lat)*K
    if 120<y<1000: g.append(f'<line x1="40" y1="{f(y)}" x2="970" y2="{f(y)}"/><text class="grid-lbl" x="50" y="{f(y-6)}">{lbl} с. ш.</text>')
for lon,lbl in [(72.75,"72°45′"),(73.0,"73°00′"),(73.25,"73°15′"),(73.5,"73°30′"),(73.75,"73°45′")]:
    x=(lon-72.6)*K
    g.append(f'<line x1="{f(x)}" y1="120" x2="{f(x)}" y2="1000"/><text class="grid-lbl" x="{f(x+6)}" y="990">{lbl} в. д.</text>')
g.append('</g>'); svg+=g
svg.append('<text class="ocean-lbl" x="425" y="938" text-anchor="middle">Индийский океан</text>')

# atolls
islands=[]
def organic(xy, amp, seed):
    rnd=random.Random(seed)
    base=sample(catmull(xy,closed=True),step=2.0)
    n=len(base); k=max(18,n//9)
    ph=[rnd.uniform(0,6.28) for _ in range(4)]
    cx=sum(x for x,_ in base)/n; cy=sum(y for _,y in base)/n
    out=[]
    for i in range(0,n,n//k):
        x,y=base[i]; t=i/n*6.283
        r=amp*(0.55*math.sin(3*t+ph[0])+0.3*math.sin(7*t+ph[1])+0.25*math.sin(13*t+ph[2])+0.15*math.sin(19*t+ph[3]))
        dx,dy=x-cx,y-cy; L=math.hypot(dx,dy) or 1
        out.append((x+dx/L*r, y+dy/L*r))
    return out
AMP={"north-male":7,"south-male":6,"vaavu":7,"ari":9}
for name,pts in atolls.items():
    xy=organic([P(*p) for p in pts], AMP[name], sum(map(ord,name))); segs=catmull(xy,closed=True)
    d=d_of(segs,True)
    svg.append(f'<path class="reef-glow" d="{d}"/>')
    svg.append(f'<path class="atoll" d="{d}"/>')
    pts_s=sample(segs,step=2.2)
    for i in range(0,len(pts_s)-1,5):
        if random.random()<0.42:
            (x,y),(x2,y2)=pts_s[i],pts_s[(i+1)%len(pts_s)]
            ang=math.degrees(math.atan2(y2-y,x2-x))
            rx=random.uniform(1.4,4.2); ry=random.uniform(0.9,1.8)
            islands.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(ry)}" transform="rotate({ang:.0f} {f(x)} {f(y)})"/>')
for name,(lon,lat,rlon,rlat) in small.items():
    x,y=P(lon,lat); rx,ry=rlon*K,rlat*K
    svg.append(f'<ellipse class="reef-glow" cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(ry)}"/><ellipse class="atoll" cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(ry)}"/>')
svg.append('<g class="islets">'+''.join(islands)+'</g>')

# atoll labels
svg.append('<text class="atoll-lbl" x="700" y="168">СЕВЕРНЫЙ МАЛЕ</text>')
svg.append('<text class="atoll-lbl" x="604" y="372">ЮЖНЫЙ МАЛЕ</text>')
svg.append('<text class="atoll-lbl" x="622" y="842">ВААФУ</text>')
svg.append('<text class="atoll-lbl" x="132" y="420">АТОЛЛ АРИ</text>')

# named islands (bright dots)
named = {"male":(73.5093,4.1755),"airport":(73.529,4.1918),"guraidhoo":(73.4683,3.90),"alimatha":(73.4978,3.5936),
         "dhigurah":(72.9239,3.5264),"dhangethi":(72.9556,3.6075),"omadhoo":(72.9639,3.7908),"maamigili":(72.8375,3.475)}
NP={k:P(*v) for k,v in named.items()}
for k,(x,y) in NP.items():
    svg.append(f'<circle class="isl" cx="{f(x)}" cy="{f(y)}" r="3.2"/>')

# whale shark zone: outer reef Dhigurah -> Maamigili
ws=[P(72.935,3.505),P(72.885,3.448),P(72.83,3.445)]
svg.append(f'<path class="ws-zone" d="{d_of(catmull(ws))}"/>')

# routes
yacht=[NP["airport"],(770,300),(772,390),(735,455),(700,492),(684,560),(690,640),(712,712),(745,770),(792,735),(805,640),(795,520),(784,400),(770,310),(738,262)]
ferry=[NP["male"],(560,400),(400,620),NP["dhigurah"]]
svg.append(f'<path class="route-ferry" d="{d_of(catmull(ferry))}"/>')
svg.append(f'<path class="route-yacht-glow" d="{d_of(catmull(yacht))}"/>')
svg.append(f'<path class="route-yacht r-draw" pathLength="1" d="{d_of(catmull(yacht))}"/>')
dx,dy=NP["dhigurah"]
for tgt,ctrl in [("dhangethi",(300,750)),("omadhoo",(318,660))]:
    tx,ty=NP[tgt]
    svg.append(f'<path class="route-trip" d="M{f(dx)} {f(dy)}Q{ctrl[0]} {ctrl[1]} {f(tx)} {f(ty)}"/>')
svg.append(f'<path class="route-trip" d="M{f(dx)} {f(dy)}Q232 742 214 700"/>')  # к резорту (схематично)

# place labels
def lbl(cls,x,y,t,anchor="start",extra=""): svg.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}"{extra}>{t}</text>')
lbl("place",700,282,"Мале","end")
lbl("place minor",780,226,"аэропорт")
lbl("place",672,487,"Гурайдо","end")
lbl("place",700,742,"Алимата","end")
lbl("place",284,806,"Дигура")
lbl("place",300,712,"Дангети")
lbl("place",306,566,"Омаду")
lbl("place minor",176,812,"Маамигили","end")
lbl("place minor",200,694,"резорт 5*","end")
lbl("creature",676,516,"дельфины","end")
lbl("creature",640,778,"акулы-няньки","end")
lbl("creature",204,906,"китовые акулы")
lbl("route-lbl",500,540,"скоростной паром","middle",' transform="rotate(-50 500 540)"')
lbl("route-lbl yacht-lbl",838,560,"яхта","middle",' transform="rotate(84 838 560)"')

# markers
def mk(stop,x,y,t,minor=False):
    r=15 if len(t)<3 else 19
    svg.append(f'<g class="mk{" mk-sm" if minor else ""}" data-stop="{stop}" transform="translate({f(x)} {f(y)})"><g class="mk-s"><circle r="{r}"/><text y="4.6" text-anchor="middle">{t}</text></g></g>')
mk("1",*NP["airport"],"1")
mk("2",NP["guraidhoo"][0],NP["guraidhoo"][1],"2")
mk("3",*NP["alimatha"],"3")
mk("4",805,640,"4")
mk("5",*NP["dhigurah"],"5")
mk("6",*NP["dhangethi"],"6")
mk("7",214,700,"7")
mk("8",186,872,"8")
mk("9",*NP["omadhoo"],"9")

# compass + scale
svg.append('<g class="compass" transform="translate(905 200)"><circle r="34"/><circle r="26" class="c2"/><path d="M0 -40 L7 0 L0 6 L-7 0Z" class="n"/><path d="M0 40 L7 0 L0 -6 L-7 0Z"/><text y="-48" text-anchor="middle">С</text></g>')
svg.append('<g class="scale" transform="translate(72 950)"><line x1="0" y1="0" x2="144" y2="0"/><line x1="0" y1="-5" x2="0" y2="5"/><line x1="72" y1="-3" x2="72" y2="3"/><line x1="144" y1="-5" x2="144" y2="5"/><text x="0" y="-12">0</text><text x="144" y="-12" text-anchor="middle">20 км</text></g>')
svg.append('</svg>')
open(f"{__import__('sys').argv[1]}",'w').write('\n'.join(svg))
print(len('\n'.join(svg)))
