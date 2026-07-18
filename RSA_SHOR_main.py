'''
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 

Project: RSA and Shor's Algorithm
Title: Python implementation of RSA and SHOR
File: RSA_SHOR_main.py
Dependencies: shorModule.py, rsaModule.py, arithmeticModule.py
Author: Avinash M
mail: m.avinash@in.bosch.com
Last Modified Date: 12-11-2024
'''

import os
import time
# import numpy as np

from random import randint
from lorem_text import lorem

# Function imports
from module_scripts.arithmeticModule import naive_Factorize
from module_scripts.rsaModule import generateKeyPairRSA, encryptRSA, decryptRSA
from module_scripts.shorModule import shor_algorithm, WORK_QUBITS, COUNTING_QUBITS, ANCILLA_QUBITS

# Get backend configuration
from qiskit_aer import Aer
backend = Aer.get_backend('qasm_simulator')
available_qubits = backend.configuration().num_qubits

def read_file(filename):

    filepath = os.getcwd()+'\\'+filename
    fileOBJ = open(filepath,'r')
    text = fileOBJ.read()
    fileOBJ.close()

    return text

def write_file(filename, text):

    filepath = os.getcwd()+'\\'+filename
    fileOBJ = open(filepath, 'w')
    fileOBJ.write(text)
    fileOBJ.close()

def get_loremtext(words):

    lorem_paragraph = lorem.words(words)
    return lorem_paragraph

def RunModule_keyGen(input_bits):
    rsa_keypairgen_init = time.time()
    pk, sk = generateKeyPairRSA(input_bits)
    rsa_keypairgen_final = time.time()
    print('------------------')
    print('Timing Report: ')
    print('------------------')
    print('Key Generation: ', format("{:>6.4f} s".format(rsa_keypairgen_final-rsa_keypairgen_init)))
    return pk, sk

def RunModule_Enc(resultDispChoice, loremWords, message, pk):
    
    print("\n========================================")
    print('++++----RSA Encryption Components----++++')
    print('Public Key:', [hex(pk[0]), hex(pk[1])])
    print('Message Digest is a LOREM IPSUM TEXT with %3d words, %3d Bytes' %(loremWords, messageBytes))
    print("========================================\n")
    print('-------------------------')
    print('Message: LOREM IPSUM TEXT')
    print('-------------------------')
    if resultDispChoice:
        print(message)
    else:
        print('<Text Too Large to Print>')
    ### ENCRYPTION

    rsa_enc_init = time.time_ns()
    encMsg = encryptRSA(message, pk)
    rsa_enc_final = time.time_ns()
    
    encString = ''.join(map(lambda x: str(format(x, '0{}x'.format(4))), encMsg))
    print('\n------------------')
    print('Cipher Text: ')
    print('------------------')
    if resultDispChoice:
        print(encString)
    else:
        print('<Text Too Large to Print>')

    print('\n------------------')
    print('Timing Report: ')
    print('------------------')
    print('Encryption: ', format("{:>6.4f} ns".format(rsa_enc_final-rsa_enc_init)))
    return encMsg, encString


def RunModule_Dec(resultDispChoice, loremWords, encString, encMsg, sk):
    ### DECRYPTION

    rsa_dec_init = time.time_ns()
    decMsg = decryptRSA(encMsg, sk)
    rsa_dec_final = time.time_ns()

    decString = ''.join(decMsg)
    cipherBytes = encString.__sizeof__() - [].__sizeof__() - 1

    print("\n========================================")
    print('++++----RSA Decryption Components----++++')
    print('Private Key:', [hex(sk[0]), hex(sk[1])])
    print('Cipher Digest is %3d Bytes' %(cipherBytes))
    print("========================================\n")
    
    print('------------------')
    print('Cipher Text: ')
    print('------------------')
    if resultDispChoice:
        print(encString)
    else:
        print('<Text Too Large to Print>')

    print('\n------------------')
    print('Decrypted Message:')
    print('------------------')
    if resultDispChoice:
        print(decString)
    else:
        print('<Text Too Large to Print>')
        

    print('\n------------------')
    print('Timing Report: ')
    print('------------------')
    print('Decryption: ', format("{:>6.4f} ns".format(rsa_dec_final-rsa_dec_init)))
    return decString

if __name__ == '__main__':

    ### RSA and SHOR's Algorithm
    
    os.system('cls')
    # os.system('python -V')
    loremWords = 20         # Change here for number of words in the LOREM IPSUM TEXT
    message = lorem.words(loremWords)
    txtAscii = [ord(char) for char in message]
    txtArray = ','.join(map(lambda message: str(message), txtAscii))
    messageBytes = message.__sizeof__() - [].__sizeof__() - 1

    print("\n" + "="*70)
    print("RSA KEY BREAKING via QUANTUM PHASE ESTIMATION (QPE)")
    print("="*70)
    print(f"\nBackend: Qiskit Aer qasm_simulator ({available_qubits} qubits available)")
    print(f"\nQubit Allocation:")
    print(f"  • Counting register (phase estimation): {COUNTING_QUBITS} qubits")
    print(f"  • Work register (modular arithmetic): {WORK_QUBITS} qubits → max N < 2^{WORK_QUBITS} = {2**WORK_QUBITS:,}")
    print(f"  • Ancilla qubits: {ANCILLA_QUBITS}")
    print(f"  • Total: {COUNTING_QUBITS + WORK_QUBITS + ANCILLA_QUBITS} qubits")
    print(f"\nSince N = p x q (both {WORK_QUBITS//2}-bit primes), max input_bits = {WORK_QUBITS//2}")
    print(f"(Oversized moduli will fall back to standard RSA key)")
    print("="*70)
    max_input_bits = WORK_QUBITS // 2
    input_bits = int(input(f'Enter input bits for KeyGeneration | (max {max_input_bits}): '))
    if input_bits > max_input_bits:
        print(f'Cannot implement SHOR\'s: input_bits must be <= {max_input_bits}.')
        print(f'(QPE work register supports moduli up to {2**WORK_QUBITS} = 2^{WORK_QUBITS})')
        exit()        


# Key Generation
    pk, sk = RunModule_keyGen(input_bits)
    
    resultDispChoice = True
    if loremWords > 50:
        resultDispChoice = False    

    os.system('pause')

# Encrypt the message
    encMsg, encString = RunModule_Enc(
        resultDispChoice=resultDispChoice, 
        loremWords=loremWords, 
        message=message, 
        pk=pk
        )

# SHOR's Algorithm to factor the modulus and get the private key
        
        
    SHOR_breaker_init = time.time()
    sk_shor = shor_algorithm(pk)
    SHOR_breaker_final = time.time()
    
    print('\n------------------')
    print('Overall Timing Report: ')
    print('------------------')
    print("Total Shor's execution time: ", format("{:>6.4f} s\n".format(SHOR_breaker_final-SHOR_breaker_init)))
    
    print('The Private Key generated by SHOR\'s Algorithm is: ', [hex(sk_shor[0]), hex(sk_shor[1])])
    
# Decrypt the message
    decMsg = RunModule_Dec(
        resultDispChoice=resultDispChoice, 
        loremWords=loremWords, 
        encString=encString, 
        encMsg=encMsg, 
        sk=sk_shor
        )
    print('\nThe original message is same as the decrypted message: ', message == decMsg, end='\n')