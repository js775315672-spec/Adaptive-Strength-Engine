"""Local review ledger. Manual review is not independent measurement validation."""
import hashlib,json,time,re
from validation import audit

def canonical(d):
 return json.dumps(d,sort_keys=True,separators=(',',':'),allow_nan=False)

def submit(store,folder,d):
 digest=d['digest']
 if not re.fullmatch('[a-f0-9]{64}',digest):raise ValueError('invalid digest')
 p=folder/(digest+'.mp4')
 if not p.is_file():raise ValueError('archive video first')
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 if h.hexdigest()!=digest:raise ValueError('archive integrity failure')
 payload={k:d[k] for k in ('pred','reference','scale','center','kg')}
 result=audit(**payload,synthetic=d.get('synthetic') is True)
 key=hashlib.sha256(canonical({'digest':digest,'payload':payload,'source':result['source']}).encode()).hexdigest()
 db=store.db
 with db:
  db.execute('CREATE TABLE IF NOT EXISTS reviews(id TEXT PRIMARY KEY,digest TEXT,payload TEXT,result TEXT,ts REAL,status TEXT)')
  db.execute('INSERT OR IGNORE INTO reviews VALUES(?,?,?,?,?,?)',(key,digest,canonical(payload),canonical(result),time.time(),'PENDING' if result['threshold_pass'] and result['source']!='synthetic' else 'REJECTED'))
  row=db.execute('SELECT status,result FROM reviews WHERE id=?',(key,)).fetchone()
 return dict(receipt=key,status=row[0],report=json.loads(row[1]),learning_approved=False)
