import sys,subprocess,re,math,colorsys,os
# matiz do 1/6 mais claro do recorte 100x100+788+385 (método C291)
for f in sys.argv[1:]:
    t=subprocess.run(['convert',f,'-crop','100x100+788+385','+repage','-depth','8','txt:-'],capture_output=True,text=True).stdout
    px=[tuple(map(int,m)) for m in re.findall(r'\((\d+),(\d+),(\d+)',t)]
    px.sort(key=sum,reverse=True); px=px[:len(px)//6]
    sx=sy=0
    for r,g,b in px:
        h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255); sx+=math.cos(h*2*math.pi)*s; sy+=math.sin(h*2*math.pi)*s
    print(os.path.relpath(f), round(math.degrees(math.atan2(sy,sx))%360))
