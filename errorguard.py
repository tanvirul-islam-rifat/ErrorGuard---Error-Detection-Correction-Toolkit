"""
ErrorGuard — Error Detection & Correction Toolkit
Implements four core error detection/correction mechanisms from the
Data Link layer: Parity Check, Checksum, CRC (Cyclic Redundancy Check),
and Hamming Code. Each method shows full step-by-step working, introduces
errors, and demonstrates whether the method detects or corrects them.

CSE320 is a pure theory course with no coding component. This project
computationally implements the error control mechanisms studied in Week 11.

Course: CSE320 - Data Communications
"""


# ═══════════════════════════════════════════════════════
# UTILITY HELPERS
# ═══════════════════════════════════════════════════════

def get_binary_input(prompt):
    while True:
        val = input(prompt).strip().replace(" ", "")
        if all(c in "01" for c in val) and len(val) > 0:
            return val
        print("  Please enter a valid binary string (only 0s and 1s).")


def get_int(prompt, min_val=1, max_val=9999):
    while True:
        try:
            val = int(input(prompt).strip())
            if min_val <= val <= max_val:
                return val
            print(f"  Enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("  Invalid input.")


def introduce_error(data):
    print(f"\n  Current data: {data}")
    pos = get_int(f"  Flip which bit? (1 = leftmost, {len(data)} = rightmost): ", 1, len(data))
    corrupted = list(data)
    corrupted[pos - 1] = "1" if corrupted[pos - 1] == "0" else "0"
    corrupted = "".join(corrupted)
    print(f"  Corrupted data: {corrupted}  (bit {pos} flipped)")
    return corrupted


def section(title):
    print("\n" + "-" * 54)
    print(f"  {title}")
    print("-" * 54)


# ═══════════════════════════════════════════════════════
# 1. PARITY CHECK
# ═══════════════════════════════════════════════════════

def parity_check():
    section("PARITY CHECK")
    print("  Parity adds 1 extra bit so the total number of 1s")
    print("  is even (even parity) or odd (odd parity).")
    print("  Detects: single-bit errors  |  Corrects: nothing\n")

    data = get_binary_input("  Enter data bits: ")
    print("  1. Even Parity\n  2. Odd Parity")
    choice = input("  Choice (1/2): ").strip()
    even = (choice != "2")
    parity_name = "Even" if even else "Odd"

    ones = data.count("1")
    print(f"\n  Data           : {data}")
    print(f"  Number of 1s   : {ones}")

    if even:
        parity_bit = "0" if ones % 2 == 0 else "1"
        print(f"  Even parity: total 1s must be even.")
    else:
        parity_bit = "0" if ones % 2 == 1 else "1"
        print(f"  Odd parity: total 1s must be odd.")
    print(f"  Current 1s = {ones} -> parity bit = {parity_bit}")

    transmitted = data + parity_bit
    print(f"\n  Transmitted frame : {transmitted}  (data + parity bit)")

    print("\n  -- Error Simulation --")
    print("  1. Check without error")
    print("  2. Introduce a single-bit error")
    print("  3. Introduce a two-bit error (parity blind spot)")
    sim = input("  Choice (1/2/3): ").strip()

    if sim == "2":
        received = introduce_error(transmitted)
    elif sim == "3":
        received = introduce_error(transmitted)
        received = introduce_error(received)
    else:
        received = transmitted

    received_ones = received.count("1")
    print(f"\n  Received frame : {received}")
    print(f"  Number of 1s   : {received_ones}")

    valid = (received_ones % 2 == 0) if even else (received_ones % 2 == 1)

    if valid:
        if received == transmitted:
            print("  Parity check   : PASS -- no error detected (correct)")
        else:
            print("  Parity check   : PASS -- but data IS corrupted!")
            print("  -> Two-bit errors cancel out. Parity CANNOT detect even-number bit flips.")
    else:
        print("  Parity check   : FAIL -- ERROR DETECTED!")
        print("  -> Receiver knows something went wrong but cannot fix it.")


# ═══════════════════════════════════════════════════════
# 2. CHECKSUM
# ═══════════════════════════════════════════════════════

def checksum():
    section("CHECKSUM (Internet Checksum)")
    print("  Divides data into 8-bit blocks, sums them in binary,")
    print("  and appends the 1s complement as the checksum.")
    print("  Detects: most errors  |  Corrects: nothing\n")

    print("  Enter 8-bit binary segments (type 'done' when finished).")
    segments = []
    while True:
        raw = input(f"  Segment {len(segments)+1}: ").strip().replace(" ", "")
        if raw.lower() == "done":
            if len(segments) < 2:
                print("  Need at least 2 segments.")
                continue
            break
        if len(raw) != 8 or not all(c in "01" for c in raw):
            print("  Please enter exactly 8 binary digits.")
            continue
        segments.append(raw)

    print(f"\n  Segments:")
    for i, s in enumerate(segments, 1):
        print(f"    Block {i}: {s}  (decimal: {int(s, 2)})")

    total = 0
    print(f"\n  Binary addition with carry wraparound:")
    for i, s in enumerate(segments):
        total += int(s, 2)
        while total > 0xFF:
            total = (total & 0xFF) + (total >> 8)
        print(f"    After block {i+1}: {format(total, '08b')}  ({total})")

    checksum_val = (~total) & 0xFF
    checksum_bits = format(checksum_val, "08b")
    print(f"\n  Sum             : {format(total, '08b')}  ({total})")
    print(f"  1s complement   : {checksum_bits}  ({checksum_val})  <- checksum")
    print(f"  Transmitted     : {' '.join(segments)} | {checksum_bits}")

    print("\n  -- Receiver Verification --")
    sim = input("  Simulate error? (y/n): ").strip().lower()
    if sim == "y":
        full = "".join(segments + [checksum_bits])
        corrupted_full = introduce_error(full)
        received_blocks = [corrupted_full[i:i+8] for i in range(0, len(corrupted_full), 8)]
    else:
        received_blocks = segments + [checksum_bits]

    print(f"\n  Received blocks: {' '.join(received_blocks)}")
    verify_total = 0
    for b in received_blocks:
        verify_total += int(b, 2)
        while verify_total > 0xFF:
            verify_total = (verify_total & 0xFF) + (verify_total >> 8)

    verify_complement = (~verify_total) & 0xFF
    print(f"  Sum of all (incl. checksum): {format(verify_total, '08b')}")
    print(f"  1s complement: {format(verify_complement, '08b')}")

    if verify_complement == 0:
        print("\n  Checksum: PASS -- no error detected")
    else:
        print("\n  Checksum: FAIL -- ERROR DETECTED!")
        print("  -> Result is not 00000000. Frame discarded.")


# ═══════════════════════════════════════════════════════
# 3. CRC
# ═══════════════════════════════════════════════════════

def crc():
    section("CRC -- CYCLIC REDUNDANCY CHECK")
    print("  Treats data as a polynomial divided by a generator.")
    print("  The remainder (FCS) is appended to the frame.")
    print("  Detects: burst errors very reliably  |  Corrects: nothing\n")

    data = get_binary_input("  Enter data bits (dividend): ")
    generator = get_binary_input("  Enter generator polynomial (e.g. 1011): ")
    r = len(generator) - 1
    padded = data + "0" * r

    print(f"\n  Data            : {data}")
    print(f"  Generator       : {generator}  (degree {r})")
    print(f"  Data + {r} zeros : {padded}")

    def xor(a, b):
        return "".join("0" if a[i] == b[i] else "1" for i in range(len(b)))

    def mod2_divide(dividend, divisor, show_steps=True):
        dv = len(divisor)
        remainder = dividend[:dv]
        if show_steps:
            print(f"\n  Step-by-step modulo-2 division:")
            print(f"  {'─'*40}")
        step = 1
        for i in range(dv, len(dividend) + 1):
            if show_steps:
                print(f"  Step {step}: {remainder}")
            if remainder[0] == "1":
                result = xor(remainder, divisor)
                if show_steps:
                    print(f"         XOR {divisor} -> {result}")
            else:
                result = xor(remainder, "0" * dv)
                if show_steps:
                    print(f"         XOR {'0'*dv} -> {result}  (leading 0)")
            if i < len(dividend):
                remainder = result[1:] + dividend[i]
                if show_steps:
                    print(f"         Bring down -> {remainder}")
            else:
                remainder = result[1:]
            step += 1
        return remainder.zfill(r)

    remainder = mod2_divide(padded, generator)
    crc_frame = data + remainder
    print(f"\n  CRC remainder (FCS) : {remainder}")
    print(f"  Transmitted frame   : {crc_frame}")

    print("\n  -- Receiver Verification --")
    sim = input("  Simulate error? (y/n): ").strip().lower()
    received = introduce_error(crc_frame) if sim == "y" else crc_frame

    print(f"\n  Received: {received}")
    check_remainder = mod2_divide(received, generator, show_steps=False)
    print(f"  Remainder after division: {check_remainder}")

    if all(c == "0" for c in check_remainder):
        if received == crc_frame:
            print("  CRC: PASS -- remainder is zero, no error detected")
        else:
            print("  CRC: PASS -- but data corrupted (extremely rare miss)")
    else:
        print(f"  CRC: FAIL -- remainder {check_remainder} != 0 -- ERROR DETECTED!")
        print("  -> Receiver requests retransmission.")


# ═══════════════════════════════════════════════════════
# 4. HAMMING CODE
# ═══════════════════════════════════════════════════════

def hamming_code():
    section("HAMMING CODE -- ERROR CORRECTION")
    print("  Inserts parity bits at power-of-2 positions.")
    print("  Detects: 2-bit errors  |  Corrects: single-bit errors\n")

    data = get_binary_input("  Enter data bits (e.g. 1011): ")
    m = len(data)

    r = 0
    while (2 ** r) < (m + r + 1):
        r += 1
    total_bits = m + r

    print(f"\n  Data bits (m)   : {m}")
    print(f"  Parity bits (r) : {r}  (2^{r}={2**r} >= {m+r+1})")
    print(f"  Total bits      : {total_bits}")
    print(f"  Parity positions: {[2**i for i in range(r)]}")

    parity_positions = {2**i for i in range(r)}
    frame = ["_"] * (total_bits + 1)

    data_idx = 0
    print(f"\n  Placing bits:")
    for pos in range(1, total_bits + 1):
        if pos not in parity_positions:
            frame[pos] = data[data_idx]
            print(f"    Position {pos:2d}: data '{data[data_idx]}'")
            data_idx += 1
        else:
            print(f"    Position {pos:2d}: parity (TBD)")

    print(f"\n  Calculating parity bits (even parity):")
    for i in range(r):
        p_pos = 2 ** i
        covered = [pos for pos in range(1, total_bits + 1) if pos & p_pos]
        covered_vals = [frame[pos] for pos in covered if frame[pos] != "_"]
        ones = covered_vals.count("1")
        parity = "0" if ones % 2 == 0 else "1"
        frame[p_pos] = parity
        print(f"    P{p_pos}: covers {covered} -> values {covered_vals} -> ones={ones} -> P{p_pos}={parity}")

    hamming_frame = "".join(frame[1:])
    print(f"\n  Hamming frame: {hamming_frame}")

    print("\n  -- Error Detection & Correction --")
    sim = input("  Simulate single-bit error? (y/n): ").strip().lower()
    received = introduce_error(hamming_frame) if sim == "y" else hamming_frame

    print(f"\n  Received: {received}")
    received_frame = ["_"] + list(received)

    print(f"\n  Syndrome calculation:")
    syndrome = 0
    for i in range(r):
        p_pos = 2 ** i
        covered = [pos for pos in range(1, total_bits + 1) if pos & p_pos]
        covered_vals = [received_frame[pos] for pos in covered]
        ones = covered_vals.count("1")
        check_bit = 0 if ones % 2 == 0 else 1
        syndrome += check_bit * p_pos
        print(f"    C{p_pos}: positions {covered} -> ones={ones} -> bit={check_bit}")

    print(f"\n  Syndrome: {syndrome}")
    if syndrome == 0:
        print("  No error detected. Data received correctly.")
    else:
        print(f"  Error at bit position {syndrome}!")
        corrected = list(received)
        corrected[syndrome - 1] = "1" if corrected[syndrome - 1] == "0" else "0"
        corrected_str = "".join(corrected)
        print(f"  Corrected frame: {corrected_str}")
        recovered = "".join(corrected_str[pos-1] for pos in range(1, total_bits+1)
                            if pos not in parity_positions)
        print(f"  Recovered data : {recovered}")
        print(f"  Original data  : {data}")
        print(f"  Match: {'YES -- successfully corrected!' if recovered == data else 'NO -- correction failed'}")


# ═══════════════════════════════════════════════════════
# 5. COMPARISON
# ═══════════════════════════════════════════════════════

def show_comparison():
    section("ERROR CONTROL METHODS -- COMPARISON")
    print(f"  {'Method':<18}{'Overhead':<14}{'Detects':<30}{'Corrects'}")
    print("  " + "-" * 74)
    rows = [
        ("Parity Check",  "1 bit",        "Single-bit errors only",        "Cannot correct"),
        ("Checksum",      "8-16 bits",    "Most errors (some blind spots)", "Cannot correct"),
        ("CRC",           "r bits",       "Burst errors very reliably",     "Cannot correct"),
        ("Hamming Code",  "r parity bits","Single & double-bit errors",     "Single-bit errors"),
    ]
    for name, oh, det, cor in rows:
        print(f"  {name:<18}{oh:<14}{det:<30}{cor}")
    print()
    print("  Key insight: Detection methods (Parity, Checksum, CRC) are used")
    print("  with ARQ retransmission. Correction (Hamming) is used where")
    print("  retransmission is too costly (e.g. deep-space communication).")


# ═══════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════

def main():
    while True:
        print("\n" + "=" * 54)
        print("    ErrorGuard -- Error Detection & Correction")
        print("=" * 54)
        print("  1. Parity Check")
        print("  2. Checksum (Internet Checksum)")
        print("  3. CRC -- Cyclic Redundancy Check")
        print("  4. Hamming Code (Error Correction)")
        print("  5. Comparison of All Methods")
        print("  0. Exit")
        print("=" * 54)
        choice = input("  Choose a module: ").strip()

        if choice == "1":
            parity_check()
        elif choice == "2":
            checksum()
        elif choice == "3":
            crc()
        elif choice == "4":
            hamming_code()
        elif choice == "5":
            show_comparison()
        elif choice == "0":
            print("\n  Goodbye!\n")
            break
        else:
            print("  Invalid choice. Enter 0-5.")


if __name__ == "__main__":
    main()
