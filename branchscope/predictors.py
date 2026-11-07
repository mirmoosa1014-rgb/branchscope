"""Predict first, resolve second. No speculative execution or timing model."""

def validate(budget, history):
    if type(budget) is not int or budget not in (64,128,256,512,1024): raise ValueError('unsupported byte budget')
    if type(history) is not int or history not in (4,8,16,32): raise ValueError('unsupported history length')

def power2_floor(value):
    return 1 << (value.bit_length()-1)

class Predictor:
    def __init__(self, kind, budget=256, history=16):
        validate(budget, history)
        if kind not in ('taken','bimodal','gshare','perceptron'): raise ValueError('unknown predictor')
        self.kind=kind;self.h=history;self.ghr=0;self.hist=[-1]*history
        if kind == 'perceptron':
            self.entries=(budget*8-history)//(8*(history+1))
            self.weights=[[0]*(history+1) for _ in range(self.entries)]
            self.bits=self.entries*(history+1)*8+history
        elif kind in ('bimodal','gshare'):
            hb=history if kind=='gshare' else 0
            self.entries=power2_floor((budget*8-hb)//2)
            self.counters=[1]*self.entries  # weakly not-taken
            self.bits=self.entries*2+hb
        else: self.entries=0;self.bits=0
        self.theta=int(1.93*history+14)

    def predict(self, pc):
        if type(pc) is not int or pc<0 or pc%4: raise ValueError('PC must be a nonnegative aligned integer')
        if self.kind=='taken': return True, {'index':0,'score':1}
        index=(pc>>2)%self.entries
        if self.kind=='gshare': index=((pc>>2)^self.ghr)&(self.entries-1)
        if self.kind=='perceptron':
            w=self.weights[index];score=w[0]+sum(a*b for a,b in zip(w[1:],self.hist))
        else: score=self.counters[index]-1.5
        return score>=0, {'index':index,'score':score}

    def resolve(self, pc, actual):
        if type(actual) is not bool: raise ValueError('outcome must be boolean')
        prediction, state=self.predict(pc)
        index=state['index'];score=state['score'];target=1 if actual else -1
        if self.kind=='perceptron' and (prediction!=actual or abs(score)<=self.theta):
            self.weights[index]=[max(-128,min(127,w+target*x)) for w,x in zip(self.weights[index],[1]+self.hist)]
        elif self.kind in ('bimodal','gshare'):
            self.counters[index]=max(0,min(3,self.counters[index]+target))
        self.ghr=((self.ghr<<1)|int(actual))&((1<<self.h)-1)
        self.hist=[target]+self.hist[:-1]
