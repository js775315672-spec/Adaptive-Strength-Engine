import pytest
from advanced import detail,split

def test_split():
 p=[[i*.05,10,100-2*(i if i<=10 else 20-i)] for i in range(21)];assert len(split(p,.01))==1;assert not split(p[:11],.01)
def test_moment():
 p=[[i*.05,10,100-i*5] for i in range(11)];r=detail(p,.01,10,100,joints={'hip':[5]*11});assert r['joint_moments']['hip']['bar_only_nm']['mean']==pytest.approx(49.03325);assert len(r['trace'])==10
 def_dummy=0
def test_grind():
 y=[100,95,90,85,84.5,84,83.5,83,82.5,77,72,67];r=detail([[i*.05,10,z] for i,z in enumerate(y)],.01,10,100);assert r['grind_seconds']>=.15
