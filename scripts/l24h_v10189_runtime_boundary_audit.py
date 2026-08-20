from playwright.sync_api import sync_playwright
from pathlib import Path
import json, sys
root=Path(__file__).resolve().parent.parent
html=(root/'index.html').read_text(encoding='utf-8')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium')
 pg=b.new_page(); pg.set_content(html, wait_until='domcontentloaded')
 results=[]
 def check(name,expr):
  try: ok=bool(pg.evaluate(expr)); detail=''
  except Exception as e: ok=False; detail=str(e)
  results.append({'test':name,'status':'PASS' if ok else 'FAIL','detail':detail})
 for item in ['PASSION24.TEXT.PREFACE_ANNIBALE','PASSION24.TEXT.HOW_TO_PRACTICE','PASSION24.TEXT.RELATED_HOUR_17']:
  pg.evaluate(f"openLibraryText('{item}', false)")
  tid=item+'.TITLE'
  matrix=pg.evaluate("""(tid)=>{ const h=document.getElementById(tid), s=h.querySelector('.library-title-selectable'), t=s.firstChild; function run(r,show){ state._pending=null; closeContextActions({clearTarget:true,clearPending:true,clearSelection:true}); const ok=setPendingSelectionFromRange(r,null,!!show); return {ok,p:state._pending?{paraId:state._pending.paraId,start:state._pending.start,end:state._pending.end,text:state._pending.text}:null,bar:(document.getElementById('contextActionBar')||{}).textContent||''}; } let o={}; let r=document.createRange(); r.setStart(t,1); r.setEnd(t,Math.min(8,t.length)); o.tt=run(r,true); r=document.createRange(); r.setStart(h,0); r.setEnd(t,Math.min(8,t.length)); o.ht=run(r,true); r=document.createRange(); r.setStart(t,1); r.setEnd(h,1); o.th=run(r,true); r=document.createRange(); r.setStart(h,0); r.setEnd(h,1); o.hh=run(r,true); r=document.createRange(); r.setStart(s,0); r.setEnd(s,s.childNodes.length); o.ss=run(r,true); return o;}""",tid)
  ok=all(v['ok'] and v['p'] and v['p']['paraId']==tid and all(x in v['bar'] for x in ['Surligner','Note','Copier','Fermer']) for v in matrix.values())
  results.append({'test':item+' boundary matrix','status':'PASS' if ok else 'FAIL','detail':json.dumps(matrix,ensure_ascii=False)})
 # body regressions
 pg.evaluate("openLibraryText('PASSION24.TEXT.PREFACE_ANNIBALE', false)")
 body=pg.evaluate("""()=>{ const s=document.querySelector('.library-para-block .para-text'); const t=s.firstChild; const block=s.closest('.library-para-block'); let r=document.createRange(); r.setStart(s,0); r.setEnd(t,Math.min(8,t.length)); state._pending=null; return {ok:setPendingSelectionFromRange(r,null,false),id:state._pending&&state._pending.paraId,block:block&&block.id}; }""")
 results.append({'test':'library body boundary regression','status':'PASS' if body['ok'] and body['id']==body['block'] else 'FAIL','detail':json.dumps(body)})
 pg.evaluate("openHour(1,false)")
 body2=pg.evaluate("""()=>{ const s=document.querySelector('.para-block .para-text'); const t=s.firstChild; const block=s.closest('.para-block'); let r=document.createRange(); r.setStart(s,0); r.setEnd(t,Math.min(8,t.length)); state._pending=null; return {ok:setPendingSelectionFromRange(r,null,false),id:state._pending&&state._pending.paraId,block:block&&block.id}; }""")
 results.append({'test':'hour body boundary regression','status':'PASS' if body2['ok'] and body2['id']==body2['block'] else 'FAIL','detail':json.dumps(body2)})
 # negative marker-button range: must not resolve
 pg.evaluate("openLibraryText('PASSION24.TEXT.PREFACE_ANNIBALE', false)")
 neg=pg.evaluate("""()=>{ const b=document.getElementById('libraryTitleMarkBtn'); const t=b.firstChild; let r=document.createRange(); r.setStart(t,0); r.setEnd(t,Math.min(5,t.length)); state._pending=null; return {ok:setPendingSelectionFromRange(r,null,false),p:state._pending}; }""")
 results.append({'test':'marker button rejected','status':'PASS' if (not neg['ok'] and not neg['p']) else 'FAIL','detail':json.dumps(neg)})
 print(json.dumps(results,ensure_ascii=False,indent=2))
 b.close()
