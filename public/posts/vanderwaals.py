"""
Van der Waals forces can repel — when the medium's dielectric sits BETWEEN the two.

Lifshitz leading (static) term: the Hamaker constant's sign is set by
    A ~ (e1 - em)(e2 - em),
so A < 0 (repulsive) exactly when em is strictly between e1 and e2.

Pure numpy. Usage: python3 vanderwaals.py
"""
import numpy as np
A = lambda e1, em, e2: (e1 - em) * (e2 - em) / ((e1 + em) * (e2 + em))

if __name__ == "__main__":
    e1, e2 = 2.0, 12.0
    print(f"materials e1={e1}, e2={e2}; sweep the medium em:")
    for em in [1, 2, 5, 8, 12, 15]:
        a = A(e1, em, e2)
        print(f"  em={em:>2}  A={a:+.4f}  -> {'REPULSIVE' if a < 0 else 'attractive'}")
    print("\nrule: repulsive iff (e1-em)(e2-em) < 0  <=>  em strictly between e1 and e2")
    print("caveat: real e(iξ) is frequency-dependent; ordering must hold across the")
    print("dominant frequency range for net repulsion (Munday-Capasso-Parsegian 2009).")
