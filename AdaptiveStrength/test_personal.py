import pytest
from personal import profile,compare,rest_fatigue,joint_samples
from advanced import detail

def test_path():
 p=[[i*.1,10+i,100-5*i] for i in range(11)]; c=profile(p,.01); r=dict(kg=100,rpe=7,data=dict(successful=True,profiles=[c])); assert compare([r]*5,100,c)['rms_m']==0; assert compare([r]*4,100,c)['rms_m'] is None; assert compare([r]*5,120,c)['support']==0

def test_rest():
 r=dict(kg=100,reps=5,data=dict(rest_seconds=120,loss=15)); assert rest_fatigue([r]*5,100,5,120)['loss']==15;assert rest_fatigue([r]*5,100,5,60)['loss'] is None

def test_joint():
 p=[[i*.1,10,100-5*i] for i in range(11)]; j={'hip':[[i*.1,5,.9] for i in range(11)]}; assert detail(p,.01,10,100,joints=joint_samples(p,j))['joint_moments']['hip']['arm_m']['mean']==pytest.approx(.05);j['hip'][0][2]=.5
 with pytest.raises(ValueError):joint_samples(p,j)
