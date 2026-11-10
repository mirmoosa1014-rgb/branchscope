const $=id=>document.getElementById(id);
const colors={taken:'#9A93B0',bimodal:'#8A7CFF',gshare:'#FF2BD6',perceptron:'#27F2FF'};
const names={taken:'Always taken',bimodal:'Bimodal',gshare:'Gshare',perceptron:'Perceptron'};
let data=null;
function svg(body,w,h,label){return `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${label}">${body}</svg>`;}
function text(x,y,s,fill='#9A93B0',size=12){return `<text x="${x}" y="${y}" fill="${fill}" font-family="monospace" font-size="${size}">${s}</text>`;}
function render(){
 $('description').textContent=data.description;
 $('metrics').innerHTML=data.results.map(r=>`<div class="metric ${r.kind}"><span>${names[r.kind]}</span><strong>${r.miss_rate.toFixed(2)}%</strong><small>${r.misses} / ${r.count} missed<br>${r.storage_bits} bits used · ${r.entries} entries</small></div>`).join('');
 let body='';const x=s=>60+(s-data.warmup)/(data.count-data.warmup)*1040,y=r=>250-r*2;
 for(let tick=0;tick<=100;tick+=25){body+=`<line x1="60" x2="1100" y1="${y(tick)}" y2="${y(tick)}" stroke="#9A93B033"/>`+text(10,y(tick)+4,tick+'%');}
 for(const r of data.results){body+=`<polyline points="${r.bins.map(b=>`${x(b.step)},${y(b.rate)}`).join(' ')}" fill="none" stroke="${colors[r.kind]}" stroke-width="2"/>`;}
 for(const s of [512,2000,4000,5999])body+=text(x(s)-16,280,s);
 body+=text(480,305,'Resolved branch index');$('timeline').innerHTML=svg(body,1140,320,'Windowed misprediction percentages for four predictors; exact results available in JSON export');
 $('trace').innerHTML=data.results[0].events.slice(0,16).map((e,i)=>`<tr><td>${e.step}</td><td>${e.pc}</td><td>${e.actual?'T':'N'}</td>${data.results.map(r=>`<td class="${r.events[i].prediction===e.actual?'hit':'miss'}">${r.events[i].prediction?'T':'N'} ${r.events[i].prediction===e.actual?'✓':'×'}</td>`).join('')}</tr>`).join('');
 $('step').value=0;inspect();$('download').disabled=false;
}
function inspect(){if(!data)return;const e=data.results[3].events[Number($('step').value)];$('step-value').textContent=e.step;
 $('branch-info').textContent=`${e.pc} · table row ${e.index} · score ${e.score} · predicts ${e.prediction?'TAKEN':'NOT TAKEN'} · actual ${e.actual?'TAKEN':'NOT TAKEN'}`;
 const contributions=e.weights.map((w,i)=>w*(i===0?1:e.history[i-1]));const max=Math.max(1,...contributions.map(Math.abs));let body='';const width=600/contributions.length;
 body+=`<line x1="35" x2="650" y1="145" y2="145" stroke="#9A93B0"/>`;
 contributions.forEach((v,i)=>{const h=Math.abs(v)/max*90;const xx=40+i*width;body+=`<rect x="${xx}" y="${v>=0?145-h:145}" width="${Math.max(2,width-4)}" height="${Math.max(1,h)}" fill="${v>=0?colors.perceptron:colors.gshare}"><title>${i===0?'Bias':'History lag '+i}: ${v}</title></rect>`;if(contributions.length<20||i%4===0)body+=text(xx,260,i===0?'b':i,undefined,11);});
 body+=text(38,25,'SIGNED CONTRIBUTIONS · bias + weight × history');body+=text(38,285,'b = bias; 1 = most recent resolved branch');$('weights').innerHTML=svg(body,680,310,'Perceptron signed contributions before resolving branch '+e.step);
}
$('controls').addEventListener('submit',async event=>{event.preventDefault();$('run').disabled=true;document.querySelectorAll('#controls input,#controls select').forEach(control=>control.disabled=true);$('status').textContent='Simulating identical traces and training online…';
 try{const response=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({workload:$('workload').value,budget:Number($('budget').value),history:Number($('history').value),seed:Number($('seed').value)})});const result=await response.json();if(!response.ok)throw Error(result.error);data=result;render();$('status').textContent=`Complete · seed ${data.seed} · ${data.count-data.warmup} scored branches per predictor`;}
 catch(error){$('status').textContent='Run failed: '+error.message;}
 finally{$('run').disabled=false;document.querySelectorAll('#controls input,#controls select').forEach(control=>control.disabled=false);}
});
$('step').addEventListener('input',inspect);
$('download').addEventListener('click',()=>{if(!data)return;const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`branchscope-${data.workload}-${data.seed}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('controls').requestSubmit();
