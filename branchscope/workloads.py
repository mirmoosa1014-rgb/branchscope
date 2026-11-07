"""Synthetic branch outcomes; never passed to a predictor before prediction."""
import random

WORKLOADS = {
    'loop': 'Loop exits: seven taken iterations followed by one exit, across eight sites.',
    'biased': 'Sixteen sites with independent 90/10 direction biases.',
    'delayed': 'A random source, seven random distractors, then a target copying the source.',
    'xor': 'Two random source branches followed by their XOR; a nonlinear counterexample.',
    'phase': 'Sixteen biased sites reverse their bias at each quarter of the trace.',
    'random': 'Independent fair-coin outcomes: an irreducible-noise control.',
}

def generate(kind, seed=101, count=12000):
    if kind not in WORKLOADS: raise ValueError('unknown workload')
    if type(seed) is not int or not 0 <= seed <= 2**32-1: raise ValueError('seed must be a 32-bit unsigned integer')
    if type(count) is not int or not 256 <= count <= 50000: raise ValueError('count must be 256..50000')
    rng = random.Random(seed)
    source = 0; bits = [0, 0]; result = []
    for t in range(count):
        site = 0
        if kind == 'loop':
            site = (t // 8) % 8; taken = t % 8 != 7
        elif kind in ('biased', 'phase'):
            site = rng.randrange(16)
            high = site % 2 == 0
            if kind == 'phase': high ^= (t // max(1, count//4)) % 2 == 1
            taken = rng.random() < (.9 if high else .1)
        elif kind == 'delayed':
            site = t % 9
            if site == 0: source = rng.randrange(2)
            taken = source if site in (0,8) else rng.randrange(2)
        elif kind == 'xor':
            site = t % 3
            if site < 2: bits[site] = rng.randrange(2)
            taken = bits[site] if site < 2 else bits[0] ^ bits[1]
        else: taken = rng.randrange(2)
        result.append((0x1000 + 4*site, bool(taken)))
    return result
