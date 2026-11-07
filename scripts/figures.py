"""Generate the research plate only from saved benchmark and demo measurements."""
import json
import statistics as st
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/benchmark.json').read_text());rows=r['rows']
colors={'taken':'#9A93B0','bimodal':'#8A7CFF','gshare':'#FF2BD6','perceptron':'#27F2FF'}
plt.rcParams.update({'figure.facecolor':'#07060F','axes.facecolor':'#07060F','text.color':'#F8F6FF','axes.labelcolor':'#F8F6FF','xtick.color':'#9A93B0','ytick.color':'#9A93B0','axes.edgecolor':'#9A93B0','font.size':11,'savefig.facecolor':'#07060F'})
fig,axes=plt.subplots(2,2,figsize=(15,10),layout='constrained')
fig.suptitle('BRANCHSCOPE / Where history helps—and where it does not',fontsize=22,fontweight='bold')
workloads=['loop','biased','delayed','xor','phase','random'];kinds=list(colors)
values=np.array([[st.mean(x['miss_rate'] for x in rows if x['workload']==w and x['kind']==k and x['budget_bytes']==256) for k in kinds] for w in workloads])
a=axes[0,0];im=a.imshow(values,cmap='magma',vmin=0,vmax=55,aspect='auto')
a.set(xticks=range(4),xticklabels=['Taken','Bimodal','Gshare','Perceptron'],yticks=range(6),yticklabels=workloads,title='A / Held-out error by workload · 256-byte ceiling')
for i in range(6):
 for j in range(4):a.text(j,i,f'{values[i,j]:.1f}%',ha='center',va='center',color='white' if values[i,j]<30 else 'black',fontsize=12)
fig.colorbar(im,ax=a,label='Mispredictions (%)',shrink=.8)
a=axes[0,1]
for kind in kinds:
 means=[];sds=[]
 for budget in (64,128,256,512,1024):
  by_seed=[st.mean(x['miss_rate'] for x in rows if x['kind']==kind and x['budget_bytes']==budget and x['seed']==s) for s in r['test_seeds']]
  means.append(st.mean(by_seed));sds.append(st.stdev(by_seed))
 means=np.array(means);sds=np.array(sds);xs=[64,128,256,512,1024]
 a.plot(xs,means,'o-',label=kind,color=colors[kind]);a.fill_between(xs,means-sds,means+sds,color=colors[kind],alpha=.15)
a.set(xscale='log',xticks=xs,xticklabels=xs,xlabel='Nominal storage ceiling (bytes)',ylabel='Macro-average miss rate (%)',title='B / Storage sweep · mean ± 1 seed standard deviation');a.legend(frameon=False,fontsize=10);a.grid(alpha=.15)
a=axes[1,0];v=r['validation'];a.plot([x['history'] for x in v],[x['mean'] for x in v],'o-',color=colors['perceptron'])
a.axvline(r['selected_history'],color=colors['gshare'],linestyle='--',label=f'Selected history = {r["selected_history"]}')
a.set(xticks=[4,8,16,32],xlabel='History length (resolved branches)',ylabel='Validation macro-average error (%)',title='C / Configuration selection · validation seeds only');a.legend(frameon=False);a.grid(alpha=.15)
a=axes[1,1];d=json.loads((ROOT/'results/demo.json').read_text())
for result in d['results']:
 a.plot([b['step'] for b in result['bins']],[b['rate'] for b in result['bins']],color=colors[result['kind']],label=result['kind'],linewidth=1.5)
a.set(xlabel='Resolved branch index',ylabel='Window miss rate (%)',ylim=(0,80),title='D / Delayed correlation · seed 101 · 256-branch windows');a.grid(alpha=.15)
fig.supxlabel('Synthetic traces only. A–B: 5 held-out seeds × 12,000 branches; first 512 warm up. D: 6,000-branch demo. No CPU speedup claim.',fontsize=10)
fig.savefig(ROOT/'docs/images/research.png',dpi=160);fig.savefig(ROOT/'docs/images/research.svg')
svg=ROOT/'docs/images/research.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
print('Saved research.png and research.svg from results/*.json')
