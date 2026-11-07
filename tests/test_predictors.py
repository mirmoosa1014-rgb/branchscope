import copy
import unittest
from branchscope.predictors import Predictor
from branchscope.experiment import evaluate
from branchscope.workloads import generate, WORKLOADS

class PredictorTests(unittest.TestCase):
    def test_budget_accounting(self):
        for budget in (64,128,256,512,1024):
            for history in (4,8,16,32):
                for kind in ('taken','bimodal','gshare','perceptron'):
                    p=Predictor(kind,budget,history)
                    self.assertLessEqual(p.bits,8*budget)
                    if kind!='taken':self.assertGreater(p.entries,0)

    def test_counter_saturates_and_recovers(self):
        p=Predictor('bimodal');self.assertFalse(p.predict(0)[0])
        for _ in range(50):p.resolve(0,True)
        self.assertEqual(p.counters[0],3)
        p.resolve(0,False);self.assertTrue(p.predict(0)[0])
        p.resolve(0,False);self.assertFalse(p.predict(0)[0])
        for _ in range(50):p.resolve(0,False)
        self.assertEqual(p.counters[0],0)

    def test_prediction_is_read_only(self):
        for kind in ('taken','bimodal','gshare','perceptron'):
            p=Predictor(kind);before=copy.deepcopy(p.__dict__)
            self.assertEqual(p.predict(0),p.predict(0));self.assertEqual(p.__dict__,before)

    def test_perceptron_manual_update_and_dot_product(self):
        p=Predictor('perceptron',64,4)
        self.assertEqual(p.predict(0)[1]['score'],0)
        p.resolve(0,True)
        self.assertEqual(p.weights[0],[1,-1,-1,-1,-1])
        self.assertEqual(p.hist,[1,-1,-1,-1])
        self.assertEqual(p.predict(0)[1]['score'],3)
        p.resolve(0,False)
        self.assertEqual(p.weights[0],[0,-2,0,0,0])
        self.assertEqual(p.hist,[-1,1,-1,-1])

    def test_weight_saturation(self):
        p=Predictor('perceptron',64,4)
        p.weights[0]=[127]*5;p.hist=[-1]*4
        p.resolve(0,True)
        self.assertEqual(p.weights[0],[127,126,126,126,126])
        p.weights[0]=[-128]*5;p.hist=[-1]*4
        p.resolve(0,False)
        self.assertEqual(p.weights[0],[-128,-127,-127,-127,-127])

    def test_confident_correct_prediction_does_not_train(self):
        p=Predictor('perceptron',64,4);p.weights[0]=[100,0,0,0,0]
        before=copy.deepcopy(p.weights);p.resolve(0,True);self.assertEqual(p.weights,before)

    def test_gshare_uses_pre_resolution_history(self):
        p=Predictor('gshare',64,4)
        self.assertEqual(p.predict(8)[1]['index'],2)
        p.resolve(8,True)
        self.assertEqual(p.counters[2],2)
        self.assertEqual(p.predict(8)[1]['index'],3)

    def test_aliasing_is_real(self):
        p=Predictor('bimodal',64,4)
        self.assertEqual(p.predict(0)[1]['index'],p.predict(4*p.entries)[1]['index'])

    def test_invalid_configuration(self):
        for budget,history in [(0,4),(64,0),(True,8),(256,5),(1.5,16)]:
            with self.assertRaises(ValueError):Predictor('gshare',budget,history)
        with self.assertRaises(ValueError):Predictor('missing')
        with self.assertRaises(ValueError):Predictor('taken').predict(3)
        with self.assertRaises(ValueError):Predictor('taken').resolve(4,1)

class ExperimentTests(unittest.TestCase):
    def test_deterministic_and_distinct_seeds(self):
        for kind in WORKLOADS:self.assertEqual(generate(kind,1,256),generate(kind,1,256))
        self.assertNotEqual(generate('random',1,256),generate('random',2,256))

    def test_delayed_copy_and_xor_ground_truth(self):
        trace=generate('delayed',1,270)
        for i in range(0,270,9):self.assertEqual(trace[i][1],trace[i+8][1])
        trace=generate('xor',1,270)
        for i in range(0,270,3):self.assertEqual(trace[i+2][1],trace[i][1]^trace[i+1][1])

    def test_no_current_or_future_outcome_leakage(self):
        trace=generate('random',1,256);changed=trace[:]
        changed[60:]=[(pc,not actual) for pc,actual in changed[60:]]
        for kind in ('taken','bimodal','gshare','perceptron'):
            a=evaluate(trace,kind,warmup=0,capture=True)['events']
            b=evaluate(changed,kind,warmup=0,capture=True)['events']
            for i in range(61):
                self.assertEqual(a[i]['prediction'],b[i]['prediction'])
                self.assertEqual(a[i]['score'],b[i]['score'])

    def test_counting_and_warmup(self):
        trace=[(0,False)]*600
        r=evaluate(trace,'taken',warmup=512,capture=True)
        self.assertEqual((r['count'],r['misses'],r['miss_rate']),(88,88,100))
        self.assertEqual(sum(b['count'] for b in r['bins']),88)
        self.assertEqual(sum(b['misses'] for b in r['bins']),88)
        self.assertEqual(r['events'][0]['step'],512)
        self.assertEqual(r['per_pc']['0x0']['misses'],88)

    def test_online_learning_beats_constant_on_alternation(self):
        trace=[(0,bool(i%2)) for i in range(2000)]
        learned=evaluate(trace,'perceptron',history=4)['miss_rate']
        self.assertLess(learned,1)
        self.assertEqual(evaluate(trace,'taken')['miss_rate'],50)

    def test_workload_validation(self):
        for kwargs in [dict(kind='missing'),dict(kind='loop',seed=True),dict(kind='loop',count=0),dict(kind='loop',count=50001)]:
            with self.assertRaises(ValueError):generate(**kwargs)
        with self.assertRaises(ValueError):evaluate([(0,True)],'taken',warmup=1)
