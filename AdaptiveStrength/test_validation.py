import pytest
from validation import audit

def trajectory():return [[i/20,80,100-i*2] for i in range(21)]
def test_exact():
 r=audit(trajectory(),trajectory(),.005,80,100,True);assert r['threshold_pass'] and not r['learning_approved'];assert r['speed_error_mps']==0

def test_offset():
 p=trajectory();q=[[t,x+8,y] for t,x,y in p];assert not audit(q,p,.005,80,100)['threshold_pass']
def test_missing():
 with pytest.raises(ValueError):audit(trajectory(),trajectory()[1:],.005,80,100)
def test_nan():
 with pytest.raises(ValueError):audit(trajectory(),trajectory(),float('nan'),80,100)
