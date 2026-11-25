from fastapi.testclient import TestClient
import app
from test_validation import trajectory

def test_validation_api():
 c=TestClient(app.app);p=trajectory();r=c.post('/validation',json=dict(pred=p,reference=p,scale=.005,center=80,kg=100));assert r.status_code==200;assert r.json()['threshold_pass'] and not r.json()['learning_approved']
def test_feedback_block(tmp_path,monkeypatch):
 monkeypatch.setattr(app,'root',tmp_path);assert TestClient(app.app).post('/feedback',json=dict(id=1,kg=100,reps=1,actual=.5)).status_code==400
