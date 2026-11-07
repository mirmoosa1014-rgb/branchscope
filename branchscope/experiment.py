"""Paired prequential evaluation: count each prediction before updating on its label."""
import argparse
import csv
import json
import statistics
from pathlib import Path
from .predictors import Predictor
from .workloads import generate, WORKLOADS

KINDS=('taken','bimodal','gshare','perceptron')
ROOT=Path(__file__).resolve().parents[1]

def evaluate(trace, kind, budget=256, history=16, warmup=512, capture=False):
    if type(warmup) is not int or not 0<=warmup<len(trace): raise ValueError('warmup must leave scored branches')
    model=Predictor(kind,budget,history);errors=0;bins=[];window_errors=0;window_n=0;events=[];per_pc={}
    for i,(pc,actual) in enumerate(trace):
        prediction,state=model.predict(pc)
        # All recorded state is from BEFORE resolution, including weights/history.
        if capture and warmup<=i<warmup+96:
            events.append(dict(step=i,pc=hex(pc),actual=int(actual),prediction=int(prediction),score=state['score'],index=state['index'],history=model.hist[:],weights=model.weights[state['index']][:] if kind=='perceptron' else []))
        if i>=warmup:
            miss=int(prediction!=actual);errors+=miss;window_errors+=miss;window_n+=1
            item=per_pc.setdefault(hex(pc),{'count':0,'misses':0});item['count']+=1;item['misses']+=miss
            if window_n==256 or i==len(trace)-1:
                bins.append(dict(step=i,count=window_n,misses=window_errors,rate=100*window_errors/window_n));window_n=0;window_errors=0
        model.resolve(pc,actual)
    total=len(trace)-warmup
    result=dict(kind=kind,budget_bytes=budget,history=history,storage_bits=model.bits,entries=model.entries,count=total,misses=errors,miss_rate=100*errors/total,bins=bins,events=events,per_pc=per_pc)
    if capture and kind=='perceptron':result['final_model']=dict(format_version=1,history_length=history,weights=model.weights,history=model.hist,threshold=model.theta,weight_bits=8,note='Post-trace online-trained snapshot, not used to initialize evaluation.')
    return result

def demo(workload='delayed',seed=101,budget=256,history=16,count=6000):
    trace=generate(workload,seed,count)
    return dict(workload=workload,description=WORKLOADS[workload],seed=seed,count=count,warmup=512,results=[evaluate(trace,k,budget,history,capture=True) for k in KINDS])

def benchmark(quick=False):
    count=3000 if quick else 12000
    validation_seeds=[11] if quick else [11,12,13]
    test_seeds=[101,102] if quick else [101,102,103,104,105]
    # Only validation traces choose history. Test traces never select configurations.
    validation=[]
    for history in (4,8,16,32):
        rates=[evaluate(generate(w,s,count),'perceptron',256,history)['miss_rate'] for w in WORKLOADS for s in validation_seeds]
        validation.append(dict(history=history,mean=statistics.mean(rates)))
    selected=min(validation,key=lambda r:(r['mean'],r['history']))['history']
    rows=[]
    for workload in WORKLOADS:
        for seed in test_seeds:
            trace=generate(workload,seed,count)
            for budget in (64,128,256,512,1024):
                for kind in KINDS:
                    r=evaluate(trace,kind,budget,selected)
                    rows.append(dict(workload=workload,seed=seed,kind=kind,budget_bytes=budget,history=selected,storage_bits=r['storage_bits'],count=r['count'],misses=r['misses'],miss_rate=r['miss_rate']))
    report=dict(schema_version=1,mode='quick' if quick else 'full',count=count,warmup=512,validation_seeds=validation_seeds,test_seeds=test_seeds,validation=validation,selected_history=selected,rows=rows)
    out=ROOT/('artifacts/quick' if quick else 'results');out.mkdir(parents=True,exist_ok=True)
    (out/'benchmark.json').write_text(json.dumps(report,indent=2)+'\n')
    with (out/'benchmark.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    if not quick:
        d=demo(history=selected);(out/'demo.json').write_text(json.dumps(d,indent=2)+'\n')
        (ROOT/'models/demo-perceptron.json').write_text(json.dumps(d['results'][-1]['final_model'],indent=2)+'\n')
    print(json.dumps(dict(mode=report['mode'],selected_history=selected,rows=len(rows),output=str(out)),indent=2))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true');args=parser.parse_args();benchmark(args.quick)
