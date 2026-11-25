"""Review-to-set reservation ledger. Reservations never authorize training."""
import hashlib,json,time,sqlite3,re
from approval import canonical
def digest_file(f):
    h=hashlib.sha256()
    for chunk in iter(lambda:f.read(1048576),b''): h.update(chunk)
    return h.hexdigest()

def reserve(store,folder,d):
    receipt=d['receipt']; exercise=d['exercise']; start=float(d['start']); end=float(d['end'])
    if not isinstance(exercise,str) or not exercise.strip() or not 0<=start<end<=86400: raise ValueError('invalid set metadata')
    if not re.fullmatch('[a-f0-9]{64}',receipt): raise ValueError('invalid receipt')
    db=store.db
    db.execute('CREATE TABLE IF NOT EXISTS set_reviews(id TEXT PRIMARY KEY,receipt TEXT UNIQUE,digest TEXT,exercise TEXT,start REAL,end REAL,ts REAL)')
    db.commit()
    try:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT digest,payload,status FROM reviews WHERE id=?',(receipt,)).fetchone()
        if not row or row[2]!='PENDING': raise ValueError('pending review required')
        digest,payload,_=row
        p=folder/(digest+'.mp4')
        with p.open('rb') as f:
            if digest_file(f)!=digest: raise ValueError('archive integrity failure')
        points=json.loads(payload)['pred']
        if start>points[0][0] or end<points[-1][0]: raise ValueError('set must cover reviewed ascent')
        key=hashlib.sha256(canonical([digest,exercise,start,end]).encode()).hexdigest()
        existing=db.execute('SELECT id,receipt FROM set_reviews WHERE digest=? AND start<? AND end>?',(digest,end,start)).fetchone()
        if existing:
            if existing==(key,receipt): db.commit(); return dict(set_id=key,status='PENDING',learning_approved=False)
            raise ValueError('overlapping video interval already reserved')
        db.execute('INSERT INTO set_reviews VALUES(?,?,?,?,?,?,?)',(key,receipt,digest,exercise,start,end,time.time()))
        db.commit()
        return dict(set_id=key,status='PENDING',learning_approved=False)
    except Exception:
        db.rollback();raise

def listing(store):
    db=store.db
    db.execute('CREATE TABLE IF NOT EXISTS set_reviews(id TEXT PRIMARY KEY,receipt TEXT UNIQUE,digest TEXT,exercise TEXT,start REAL,end REAL,ts REAL)')
    return [dict(zip(('set_id','receipt','digest','exercise','start','end','ts'),r),status='PENDING',learning_approved=False) for r in db.execute('SELECT * FROM set_reviews ORDER BY ts DESC')]
