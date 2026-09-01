"""
Toy Protocol Demonstration: Client-Server Session Validation & Transduction.

Demonstrates Phase 1 core capabilities:
  1. Tokenizing a raw protocol message stream.
  2. DFA protocol sequence verification.
  3. Mealy Machine transduction producing server action codes.
"""

from adaptive_automata.core import State, DFA, MealyMachine
from adaptive_automata.protocol import DelimiterTokenizer


def main() -> None:
    print("==========================================================")
    print("  Adaptive Automata Engine - Phase 1 Toy Protocol Example")
    print("==========================================================\n")

    # 1. Define Automaton States
    s_closed = State("CLOSED", is_initial=True)
    s_syn_sent = State("SYN_SENT")
    s_established = State("ESTABLISHED")
    s_authenticated = State("AUTHENTICATED", is_accepting=True)
    s_terminated = State("TERMINATED", is_accepting=True)

    # 2. Build Protocol Validation DFA
    dfa = DFA[str]("Handshake_Validator")
    dfa.add_transition(s_closed, "SYN", s_syn_sent)
    dfa.add_transition(s_syn_sent, "ACK", s_established)
    dfa.add_transition(s_established, "AUTH", s_authenticated)
    dfa.add_transition(s_authenticated, "FIN", s_terminated)
    dfa.validate()

    # 3. Build Mealy Transducer (Maps protocol symbols to Action Responses)
    mealy = MealyMachine[str, str]("Protocol_Transducer")
    mealy.add_transition(s_closed, "SYN", s_syn_sent, "SEND_SYN_ACK")
    mealy.add_transition(s_syn_sent, "ACK", s_established, "ALLOCATE_SESSION")
    mealy.add_transition(s_established, "AUTH", s_authenticated, "GRANT_TOKEN")
    mealy.add_transition(s_authenticated, "FIN", s_terminated, "CLOSE_SESSION")
    mealy.validate()

    # 4. Input Protocol Stream Tokenization
    raw_stream = "SYN ACK AUTH FIN"
    tokenizer = DelimiterTokenizer(delimiter=" ")
    tokens = tokenizer.tokenize(raw_stream)
    symbol_sequence = [token.token_type for token in tokens]

    print(f"[*] Input Stream: {raw_stream!r}")
    print(f"[*] Parsed Symbols: {symbol_sequence}\n")

    # 5. DFA Verification
    is_accepted, final_dfa_state, trace = dfa.process_sequence(symbol_sequence)
    print(f"[*] DFA Protocol Verification:")
    for src, sym, tgt in trace:
        print(f"    {src.name:<15} --[{sym}]--> {tgt.name}")
    print(f"[+] Final State: {final_dfa_state.name}")
    print(f"[+] Sequence Accepted: {is_accepted}\n")

    # 6. Mealy Transduction
    server_actions, final_mealy_state = mealy.process_sequence(symbol_sequence)
    print(f"[*] Mealy Transduction Output:")
    for (src, sym, tgt, out), action in zip(mealy.execution_trace, server_actions):
        print(f"    {src.name:<15} --[{sym}]--> {tgt.name:<15} => Server Response: '{action}'")
    print(f"[+] Server Action Pipeline Output: {server_actions}")
    print("\n[✓] Phase 1 Formal Protocol Modeling Core executed successfully!")


if __name__ == "__main__":
    main()
