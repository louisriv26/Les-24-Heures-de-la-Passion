import sys,re,json,hashlib,csv,subprocess
from pathlib import Path
root=Path(sys.argv[1])
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
def add(n,ok,e=''): checks.append((n,bool(ok),e))
html=(root/'index.html').read_text(encoding='utf-8'); sw=(root/'sw.js').read_text(encoding='utf-8')
add('runtime twins',(root/'index.html').read_bytes()==(root/'luisa_24_heures.html').read_bytes())
add('runtime version',"const APP_VERSION = 'v101.89';" in html)
add('cache',"const CACHE_NAME = 'luisa-24h-v101-89';" in sw)
try: m=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
except Exception: m={}
add('manifest version',m.get('version')=='v101.89',repr(m.get('version')))
try: v=json.loads((root/'version.json').read_text(encoding='utf-8'))
except Exception: v={}
add('version json',v.get('app_version')=='v101.89')
qa=(root/'REAL_DEVICE_QA_CHECKLIST.md').read_text(encoding='utf-8')
rows=list(csv.DictReader((root/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open(encoding='utf-8')))
add('QA current','v101.89' in qa and 'v101.88' not in qa)
add('QA NOT_TESTED',len(rows)==10 and all(r.get('status')=='NOT_TESTED' and r.get('build')=='v101.89' for r in rows))
# packaged runtime audit
r=subprocess.run([sys.executable,str(root/'scripts/l24h_v10189_runtime_boundary_audit.py')],capture_output=True,text=True)
try: rr=json.loads(r.stdout) if r.returncode==0 else []
except Exception: rr=[]
add('runtime boundary matrix',bool(rr) and all(x.get('status')=='PASS' for x in rr),r.stderr)
# active current-facing stale scan, including manifest (the R1 omission)
active=[root/'manifest.json',root/'version.json',root/'sw.js',root/'REAL_DEVICE_QA_CHECKLIST.md',root/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv',root/'index.html',root/'luisa_24_heures.html']
bad=[]
for p in active:
 t=p.read_text(encoding='utf-8',errors='ignore')
 if 'luisa-24h-v101-88' in t: bad.append(f'{p.name}:old-cache')
 if 'v101.88' in t:
  allowed=(p.name=='version.json' and 'v101.88 physical iPhone exact-title selection failed' in t)
  if not allowed: bad.append(f'{p.name}:old-version')
add('active stale current strings',not bad,';'.join(bad))
add('schema snapshot',bool(re.search(r'const\s+STORAGE_SCHEMA_VERSION\s*=\s*8\s*;',html)) and bool(re.search(r'const\s+PERSONAL_SNAPSHOT_VERSION\s*=\s*5\s*;',html)))
add('physical gate honest','physical-iPhone retest required' in (root/'version.json').read_text(encoding='utf-8'))
report='\n'.join([f"- {'PASS' if ok else 'FAIL'} — {n}"+(f' — {e}' if e else '') for n,ok,e in checks])+'\n'
(root/'audit').mkdir(exist_ok=True)
(root/'audit'/'independent_four_pass_audit.md').write_text('# Independent four-pass audit — v101.89 R2\n\n'+report,encoding='utf-8')
(root/'reports').mkdir(exist_ok=True)
summary={'pass':sum(1 for _,o,_ in checks if o),'fail':sum(1 for _,o,_ in checks if not o),'checks':len(checks)}
(root/'reports'/'independent_four_pass_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
if summary['fail']: sys.exit(3)
