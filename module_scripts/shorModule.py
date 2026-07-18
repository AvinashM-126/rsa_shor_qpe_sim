'''
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 

Project: RSA and Shor's Algorithm
Title: Shor's Algorithm - Quantum Phase Estimation (QPE) Implementation
File: shorModule.py
Author: Avinash M
Last Modified Date: 2026-07-18

DESCRIPTION:
QPE-based Shor's algorithm for RSA-key breaking.
- Two-register architecture (counting + work)
- Quantum Fourier Transform (QFT) for phase estimation
- Continued fractions post-processing to extract period

Qubit allocation for Aer qasm_simulator (31 qubits available):
- Counting register: 15 qubits (phase estimation)
- Work register:    15 qubits (modular arithmetic, supports N up to 2^15 = 32,768)
- Ancilla:           1 qubit  (control/temporary)
- Total:            31 qubits
'''

import numpy as np
from fractions import Fraction
from random import randint

from qiskit_aer import Aer
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFT

from module_scripts.arithmeticModule import \
    gcd_extEucideanAlgorithm, moduloInverse_ExtEuclideanAlgorithm
from module_scripts.rsaModule import printRSA_params

# Qubit configuration (Aer qasm_simulator: 31 qubits available)
COUNTING_QUBITS = 15  # Phase estimation register
WORK_QUBITS     = 15  # Modular arithmetic register (N must fit in 2^WORK_QUBITS = 32,768)
ANCILLA_QUBITS  =  1  # Control/temporary qubit


def extract_period_from_counts(counts, counting_bits, a, N):
    '''
    Extract period from QPE measurement results using continued fractions.
    Classical post-processing step of Shor's algorithm.
    '''
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    for bitstring, count in sorted_counts[:10]:
        try:
            phase = int(bitstring, 2) / (2 ** counting_bits)
            frac = Fraction(phase).limit_denominator(N)
            denominator = frac.denominator

            if denominator > 1 and pow(a, denominator, N) == 1:
                return denominator

            for k in range(1, 10, 2):
                r = k * denominator
                if r > 1 and pow(a, r, N) == 1:
                    return r
        except:
            continue

    return -1


def period(backend, a: int, N: int,
           counting_bits=COUNTING_QUBITS, work_bits=WORK_QUBITS):
    '''
    QPE-based period finding: f(x) = a^x mod N.

    Args:
        backend:       Qiskit backend
        a (int):       Base
        N (int):       Modulus
        counting_bits: Qubits for phase estimation register
        work_bits:     Qubits for modular arithmetic register

    Returns:
        r (int): Period, or -1 if not found
    '''
    try:
        counting_reg  = QuantumRegister(counting_bits, 'counting')
        work_reg      = QuantumRegister(work_bits,     'work')
        ancilla_reg   = QuantumRegister(ANCILLA_QUBITS,'ancilla')
        classical_reg = ClassicalRegister(counting_bits,'measured')

        qc = QuantumCircuit(counting_reg, work_reg, ancilla_reg, classical_reg)

        # Initialise work register to |1⟩
        qc.x(work_reg[0])

        # Hadamard on counting register → equal superposition
        for i in range(counting_bits):
            qc.h(counting_reg[i])

        # Simplified controlled modular exponentiation
        for i in range(min(counting_bits, 5)):
            base = pow(a, 2**i, N)
            if base != 1:
                for j in range(work_bits):
                    if (base >> j) & 1:
                        qc.cx(counting_reg[i], work_reg[j])

        # Inverse QFT on counting register
        qc.append(QFT(counting_bits, inverse=True, do_swaps=True),
                  list(counting_reg))

        qc.measure(counting_reg, classical_reg)

        transpiled_qc = transpile(qc, backend=backend, optimization_level=1)
        counts = backend.run(transpiled_qc, shots=1000).result().get_counts()

        r = extract_period_from_counts(counts, counting_bits, a, N)
        return r if r > 0 else -1

    except Exception as e:
        print(f'  [QPE] Error: {str(e)[:60]}...')
        return -1


def shors_breaker(backend, N, max_attempts=15):
    '''
    QPE-based Shor factoring.

    Args:
        backend:      Qiskit backend
        N:            Modulus to factor
        max_attempts: Maximum random-base attempts

    Returns:
        (p, q): Prime factors of N, or (-1, -1) on failure
    '''
    N = int(N)

    if N % 2 == 0:
        return 2, N // 2

    for _ in range(max_attempts):
        a = randint(2, N - 1)
        _, g = gcd_extEucideanAlgorithm(a, N)

        if g != 1:
            return g, N // g

        r = period(backend, a, N)

        if r <= 0 or r % 2 != 0:
            continue

        x = pow(a, r // 2, N)
        if x == N - 1:
            continue

        _, factor1 = gcd_extEucideanAlgorithm(x + 1, N)
        _, factor2 = gcd_extEucideanAlgorithm(x - 1, N)

        if factor1 not in (1, N):
            return factor1, N // factor1
        if factor2 not in (1, N):
            return factor2, N // factor2

    return -1, -1


def shor_algorithm(pk):
    '''
    QPE-based Shor's algorithm wrapper for RSA key-breaking.

    Args:
        pk: Public key [e, N]

    Returns:
        sk: Secret key [d, N], or None if modulus exceeds QPE capacity
    '''
    print('\n' + '=' * 70)
    print("Shor's Algorithm - Quantum Phase Estimation (QPE)")
    print('=' * 70)

    N = pk[1]
    e = pk[0]

    assert N > 0, 'Input must be positive'

    modulus_bits = N.bit_length()
    if modulus_bits > WORK_QUBITS:
        print(
            f'\n⚠  QPE cannot factor this modulus: {modulus_bits} bits required, '
            f'work register supports only {WORK_QUBITS} bits.\n'
            f'   Reduce input_bits so that N < 2^{WORK_QUBITS} = {2**WORK_QUBITS}.'
        )
        return None

    # Backend
    print('\n[Backend]')
    print('-' * 70)
    for backend in Aer.backends():
        print(f"  • {backend.name:35} ({backend.configuration().num_qubits:2} qubits)")
    backend = Aer.get_backend('qasm_simulator')
    print(f'\n  Selected : {backend.name}')
    print(f'  Modulus  : N = {N}  ({modulus_bits} bits)')
    print(f'  Registers: counting({COUNTING_QUBITS}) + work({WORK_QUBITS}) + ancilla({ANCILLA_QUBITS}) = {COUNTING_QUBITS + WORK_QUBITS + ANCILLA_QUBITS} qubits')

    print('\n[Period Finding via QPE]')
    print('-' * 70)

    p_shor, q_shor = shors_breaker(backend, N, max_attempts=10)

    if p_shor <= 0 or q_shor <= 0:
        print('\n⚠  Factorization failed after all attempts.')
        return [e, N]

    print('\n[Private Key Recovery]')
    print('-' * 70)

    phi_n = (p_shor - 1) * (q_shor - 1)
    d_shor = moduloInverse_ExtEuclideanAlgorithm(e, phi_n)
    sk_shor = [d_shor, N]

    print(f'  ✓ d = {hex(d_shor)}')
    print('\n' + '=' * 70)
    printRSA_params(p_shor, q_shor, N, phi_n, pk, sk_shor)
    print('=' * 70)

    return sk_shor
