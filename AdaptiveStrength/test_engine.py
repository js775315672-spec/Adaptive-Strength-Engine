import pytest
from engine import analyze,Store,stats

def test_metrics():
 r=analyze([[i*.05,12,100-i*5] for i in range(11)],.01,10,100); assert r['mean_speed']==pytest.approx(1); assert r['error_pct']==pytest.approx(4);assert r['speed']['max90']==pytest.approx(.9)
def test_gap():
 with pytest.raises(ValueError):analyze([[i,0,100-i*5] for i in range(5)],.01,0,100)
def test_archive(tmp_path):
 s=Store(tmp_path/'x.db');s.add('squat',100,3,8,{'first_speed':.5});s.db.execute('UPDATE sets SET ts=0');s.db.commit();s.add('squat',100,3,8,{'first_speed':.5});assert len(s.rows('squat'))==1;assert len(s.rows('squat',False))==2
 def dummy():pass

def test_recommend(tmp_path):
 s=Store(tmp_path/'x.db');r=s.recommend('squat',200,5,9.5,[],35);assert r['kg']==180 and r['reps']==3
