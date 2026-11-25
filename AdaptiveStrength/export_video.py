import argparse,json
from video_tools import render
p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('trace_json');p.add_argument('output');a=p.parse_args();d=json.load(open(a.trace_json,encoding='utf8'));print(render(a.video,a.output,d['trace'],d['center']))
