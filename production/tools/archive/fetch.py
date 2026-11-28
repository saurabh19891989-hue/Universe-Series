import json,sys,os,urllib.request,subprocess,hashlib
V=os.path.dirname(os.path.abspath(__file__))
UA={'User-Agent':'Mozilla/5.0 (research script)'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90))
def ia(i):
    d=get('https://archive.org/metadata/'+i); m=d['metadata']
    lic=m.get('licenseurl')
    if not lic: return dict(id=i,skip='no licenseurl in metadata')
    if 'nc' in lic.split('/licenses/')[-1].split('/')[0].split('-') or '-sa' in lic or '/by-sa' in lic: return dict(id=i,skip='licence '+lic)
    fs=[f for f in d['files'] if f.get('format')=='h.264' and f['name'].endswith('.mp4')]
    if not fs: fs=[f for f in d['files'] if f.get('format') in ('512Kb MPEG4','MPEG4')]
    f=min(fs,key=lambda f:int(f.get('size',0)))
    url=f"https://archive.org/download/{i}/{f['name']}"
    return dict(id=i,src='archive.org/prelinger',title=m.get('title'),year=m.get('year') or m.get('date'),page=f'https://archive.org/details/{i}',
                url=url,lic_field='licenseurl',lic=lic,size=int(f.get('size',0)),wh=[f.get('width'),f.get('height')],
                creator=m.get('creator') or m.get('sponsor'),color=m.get('color'),sound=m.get('sound'),meta=m)
def loc(i):
    d=get(f'https://www.loc.gov/item/{i}/?fo=json'); it=d['item']
    fl=[x for r in d.get('resources',[]) for g in r.get('files',[]) for x in g if x.get('mimetype','').startswith(('application/x-video','video'))]
    url=fl[0].get('download') or fl[0].get('url')
    return dict(id='loc-'+i,src='loc.gov/national-screening-room',title=it.get('title'),year=it.get('date'),page=f'https://www.loc.gov/item/{i}/',
                url=url,lic_field='rights / date',lic=(it.get('rights') or it.get('rights_advisory') or ''),created_published=it.get('created_published'),
                contributors=it.get('contributor_names'),meta={k:it.get(k) for k in ('title','date','created_published','rights','rights_advisory','notes','summary','contributor_names')})
out=[]
for a in sys.argv[1:]:
    try:
        r=loc(a[4:]) if a.startswith('loc:') else ia(a)
    except Exception as e:
        r=dict(id=a,skip=f'error {e}')
    if 'skip' not in r:
        p=os.path.join(V,'dl',r['id']+'.mp4')
        if not os.path.exists(p):
            subprocess.run(['curl','-sL','--retry','4','-A',UA['User-Agent'],'-o',p+'.part',r['url']],check=False)
            os.replace(p+'.part',p)
        r['local']=p; r['bytes']=os.path.getsize(p); r['sha256']=hashlib.sha256(open(p,'rb').read()).hexdigest()
    json.dump(r,open(os.path.join(V,'meta',r['id']+'.json'),'w'),indent=1)
    print(r['id'],r.get('skip') or f"{r['bytes']//1000000}MB {r['lic'][:50]} {str(r['title'])[:40]} {r.get('year')}",flush=True)
