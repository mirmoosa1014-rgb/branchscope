import json
import unittest
from pathlib import Path
from branchscope.experiment import evaluate
from branchscope.workloads import generate
ROOT=Path(__file__).resolve().parents[1]

class ArtifactTests(unittest.TestCase):
    def test_held_out_seeds_and_validation_choice(self):
        r=json.loads((ROOT/'results/benchmark.json').read_text())
        self.assertFalse(set(r['validation_seeds']) & set(r['test_seeds']))
        self.assertEqual(r['selected_history'],min(r['validation'],key=lambda x:(x['mean'],x['history']))['history'])
        self.assertEqual(len(r['rows']),600)
        for row in r['rows']:
            self.assertIn(row['seed'],r['test_seeds']);self.assertLessEqual(row['storage_bits'],row['budget_bytes']*8)
            self.assertAlmostEqual(row['miss_rate'],100*row['misses']/row['count'])
    def test_saved_demo_reproduces_exactly(self):
        demo=json.loads((ROOT/'results/demo.json').read_text());trace=generate(demo['workload'],demo['seed'],demo['count'])
        for result in demo['results']:
            self.assertEqual(result,evaluate(trace,result['kind'],result['budget_bytes'],result['history'],demo['warmup'],True))
    def test_model_snapshot_matches_demo(self):
        d=json.loads((ROOT/'results/demo.json').read_text())
        self.assertEqual(json.loads((ROOT/'models/demo-perceptron.json').read_text()),d['results'][-1]['final_model'])
