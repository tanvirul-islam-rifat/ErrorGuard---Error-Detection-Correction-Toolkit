# ErrorGuard — Error Detection & Correction Toolkit

A command-line tool that implements the four core error control mechanisms from the Data Link layer — **Parity Check**, **Checksum**, **CRC**, and **Hamming Code** — with full step-by-step working shown for every operation, plus interactive error simulation to demonstrate what each method catches and what it misses.

> CSE320 is a pure theory course with no coding component. This project computationally implements the error detection and correction mechanisms studied in Week 11 of the course syllabus.

Built as a course project for **CSE320 – Data Communications** at BRAC University.

---

## The Real-World Problem

Every byte transferred over a network passes through error detection before being accepted. The Data Link layer protects all communication using exactly these four mechanisms. ErrorGuard makes that process visible, interactive, and testable.

---

## Modules

### 1. Parity Check
Appends a single redundant bit to make the total count of 1s even or odd. Demonstrates the **two-bit blind spot** — flipping two bits cancels out and parity incorrectly passes.

### 2. Checksum (Internet Checksum)
Divides data into 8-bit blocks, sums them with carry wraparound, and appends the 1s complement. Shows binary addition step by step including each carry rollover.

### 3. CRC — Cyclic Redundancy Check
Full modulo-2 binary division shown step by step — XOR at each step, bring down next bit — with any user-specified generator polynomial.

```
Data            : 11010011101100
Generator       : 1011  (degree 3)
Data + 3 zeros  : 11010011101100000

Step 1: 1101  XOR 1011 -> 0110  Bring down -> 1100
Step 2: 1100  XOR 1011 -> 0111  Bring down -> 1110
...
CRC remainder (FCS) : 100
Transmitted frame   : 11010011101100100
```

### 4. Hamming Code — Error Correction
Inserts parity bits at power-of-2 positions. Computes syndrome value to pinpoint the exact error bit position and corrects it automatically.

```
Data: 1011  ->  Hamming frame: 0110011

Error at position 3  ->  Received: 0100011
Syndrome: C1=1, C2=1, C4=0  ->  Syndrome = 3
Error at position 3! Correcting...
Recovered data: 1011  -- MATCH
```

### 5. Comparison Table
Side-by-side summary: overhead, detection capability, and correction capability for all four methods.

---

## How to Run

```bash
git clone https://github.com/YourGitHubUsername/errorguard-error-detection.git
cd errorguard-error-detection
python3 errorguard.py
```

No external libraries required.

---

## Project Structure

```
errorguard-error-detection/
├── errorguard.py    # All four modules + CLI menu
└── README.md
```

---

## Technical Architecture

- **Language:** Python 3.x
- **Paradigm:** Modular procedural design — each error control method is an independent callable module
- **External Libraries:** None — all arithmetic implemented from scratch
- **Interface:** Command Line Interface (CLI) with interactive error simulation per module

## Core Engineering Practices Demonstrated

- **Modulo-2 Binary Division from Scratch:** CRC division implemented bit-by-bit using XOR and bring-down logic — matching exactly how hardware CRC circuits operate, with no library functions
- **Syndrome-Based Error Localization:** Hamming correction uses the syndrome value (binary sum of failed parity check positions) to pinpoint the exact error bit — the same algorithm used in ECC RAM modules
- **1s Complement Arithmetic with Carry Wraparound:** Checksum implements the internet checksum algorithm with end-around carry, correctly handling sums that overflow 8 bits
- **Interactive Error Injection:** Every module lets the user flip specific bits mid-transmission to test detection limits — including parity's two-bit blind spot and CRC's burst error resilience — making each method's limitations tangible rather than abstract
- **Comparative Analysis Built In:** The comparison module explicitly surfaces the overhead vs. capability trade-off across all four methods, demonstrating why different network layers choose different mechanisms

## Author

**Md. Tanvirul Islam Rifat**

* **GitHub:** [@tanvirul-islam-rifat](https://github.com/tanvirul-islam-rifat)
* **LinkedIn:** [Tanvirul Islam Rifat](https://www.linkedin.com/in/tanvirul-islam-rifat)
