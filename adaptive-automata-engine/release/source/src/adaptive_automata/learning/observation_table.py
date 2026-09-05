"""
Observation Table data structure for Mealy Machine L* learning.

Maintains prefix set S, extended prefix set S . Sigma, suffix set E,
and observation matrix T: (S U S . Sigma) x E -> Gamma*.
Provides closedness checking, consistency checking, and hypothesis construction.
"""

from typing import Generic, Sequence, TypeVar
from adaptive_automata.core.mealy import MealyMachine
from adaptive_automata.core.state import State
from adaptive_automata.protocol.sut import SystemUnderTest

SymbolT = TypeVar("SymbolT")
OutputT = TypeVar("OutputT")


class ObservationTable(Generic[SymbolT, OutputT]):
    """
    Observation Table (S, E, T) for learning Mealy Machines.

    - S: Access prefix set S subset of Sigma*
    - S_dot_Sigma: Extended prefix set (S . Sigma) \\ S
    - E: Distinguishing suffix set E subset of Sigma+
    - T: Observation mapping from (prefix, suffix) to sequence of output symbols Gamma*
    """

    def __init__(self, alphabet: Sequence[SymbolT] | set[SymbolT]) -> None:
        self._alphabet: tuple[SymbolT, ...] = tuple(sorted(alphabet, key=lambda x: str(x)))
        self._S: list[tuple[SymbolT, ...]] = [()]  # Start with empty prefix epsilon
        self._E: list[tuple[SymbolT, ...]] = [(a,) for a in self._alphabet]  # Length-1 suffixes
        self._table: dict[tuple[tuple[SymbolT, ...], tuple[SymbolT, ...]], tuple[OutputT, ...]] = {}

    @property
    def alphabet(self) -> tuple[SymbolT, ...]:
        return self._alphabet

    @property
    def S(self) -> list[tuple[SymbolT, ...]]:
        return list(self._S)

    @property
    def S_dot_Sigma(self) -> list[tuple[SymbolT, ...]]:
        """Extended prefix set (S . Sigma) \\ S."""
        s_set = set(self._S)
        extended: list[tuple[SymbolT, ...]] = []
        for s in self._S:
            for a in self._alphabet:
                p = s + (a,)
                if p not in s_set and p not in extended:
                    extended.append(p)
        return extended

    @property
    def E(self) -> list[tuple[SymbolT, ...]]:
        return list(self._E)

    def get_row(self, prefix: tuple[SymbolT, ...]) -> tuple[tuple[OutputT, ...], ...]:
        """
        Return the observation vector row(prefix) across all suffixes e in E.

        Raises KeyError if any (prefix, e) pair is missing from table.
        """
        return tuple(self._table[(prefix, e)] for e in self._E)

    def update(self, sut: SystemUnderTest[SymbolT, OutputT]) -> int:
        """
        Query the SUT for any missing entries in T: (S U S . Sigma) x E.

        Returns:
            Number of new membership queries executed.
        """
        queries_before = sut.membership_queries_count
        all_prefixes = self._S + self.S_dot_Sigma

        for p in all_prefixes:
            for e in self._E:
                key = (p, e)
                if key not in self._table:
                    # Query full sequence prefix + suffix on SUT
                    full_input = p + e
                    full_output = sut.query(full_input)
                    # Extract suffix outputs generated during execution of suffix e
                    suffix_output = full_output[len(p):]
                    self._table[key] = suffix_output

        return sut.membership_queries_count - queries_before

    def add_prefix(self, prefix: tuple[SymbolT, ...]) -> bool:
        """
        Add a new prefix sequence to S.

        Returns True if prefix was newly added, False if already in S.
        """
        if prefix not in self._S:
            self._S.append(prefix)
            return True
        return False

    def add_suffix(self, suffix: tuple[SymbolT, ...]) -> bool:
        """
        Add a new distinguishing suffix sequence to E.

        Returns True if suffix was newly added, False if already in E.
        """
        if suffix not in self._E:
            self._E.append(suffix)
            return True
        return False

    def find_unclosed_prefix(self) -> tuple[SymbolT, ...] | None:
        """
        Check table closedness.

        A table is closed if for every t in S . Sigma, there exists s in S such that row(t) == row(s).

        Returns:
            Unclosed prefix t in S . Sigma if non-closed, or None if closed.
        """
        s_rows = {self.get_row(s) for s in self._S}
        for t in self.S_dot_Sigma:
            if self.get_row(t) not in s_rows:
                return t
        return None

    def is_closed(self) -> bool:
        """Return True if table is closed."""
        return self.find_unclosed_prefix() is None

    def make_closed(self, sut: SystemUnderTest[SymbolT, OutputT]) -> bool:
        """
        Repeatedly close table by promoting unclosed extended prefixes t in S . Sigma into S.

        Returns True if table was updated/modified, False if already closed.
        """
        modified = False
        while True:
            t = self.find_unclosed_prefix()
            if t is None:
                break
            self.add_prefix(t)
            self.update(sut)
            modified = True
        return modified

    def find_inconsistency(
        self,
    ) -> tuple[tuple[SymbolT, ...], tuple[SymbolT, ...], SymbolT, tuple[SymbolT, ...]] | None:
        """
        Check table consistency.

        A table is consistent if for all s1, s2 in S with row(s1) == row(s2),
        and for all a in Sigma, row(s1 . a) == row(s2 . a).

        Returns:
            Tuple (s1, s2, a, e) identifying the inconsistency, or None if consistent.
        """
        n_s = len(self._S)
        for i in range(n_s):
            s1 = self._S[i]
            r1 = self.get_row(s1)
            for j in range(i + 1, n_s):
                s2 = self._S[j]
                if r1 == self.get_row(s2):
                    for a in self._alphabet:
                        s1_a = s1 + (a,)
                        s2_a = s2 + (a,)
                        r1_a = self.get_row(s1_a)
                        r2_a = self.get_row(s2_a)
                        if r1_a != r2_a:
                            # Find specific suffix e in E that distinguishes s1.a and s2.a
                            for idx, e in enumerate(self._E):
                                if r1_a[idx] != r2_a[idx]:
                                    return (s1, s2, a, e)
        return None

    def is_consistent(self) -> bool:
        """Return True if table is consistent."""
        return self.find_inconsistency() is None

    def make_consistent(self, sut: SystemUnderTest[SymbolT, OutputT]) -> bool:
        """
        Repeatedly make table consistent by identifying distinguishing suffixes a . e and adding to E.

        Returns True if table was modified, False if already consistent.
        """
        modified = False
        while True:
            inconsistency = self.find_inconsistency()
            if inconsistency is None:
                break
            s1, s2, a, e = inconsistency
            distinguishing_suffix = (a,) + e
            if self.add_suffix(distinguishing_suffix):
                self.update(sut)
                modified = True
            else:
                break
        return modified

    def to_mealy_machine(self, name: str = "LearnedMealyHypothesis") -> MealyMachine[SymbolT, OutputT]:
        """
        Construct a Mealy Machine hypothesis from a closed and consistent observation table.

        Formally defines H = (Q, Sigma, Gamma, delta, lambda, q0):
          - States Q: Unique row vectors in { row(s) | s in S }
          - Initial state q0: State corresponding to row(())
          - Transitions delta(row(s), a) = row(s . a)
          - Outputs lambda(row(s), a) = T(s, (a,))[0]

        Raises:
            ValueError: If table is not closed or consistent.
        """
        if not self.is_closed():
            raise ValueError("Cannot construct hypothesis from non-closed observation table.")
        if not self.is_consistent():
            raise ValueError("Cannot construct hypothesis from inconsistent observation table.")

        # Map each unique row vector in S to a distinct State object
        unique_rows: list[tuple[tuple[OutputT, ...], ...]] = []
        row_to_state: dict[tuple[tuple[OutputT, ...], ...], State] = {}

        empty_row = self.get_row(())

        # Assign states
        state_counter = 0
        for s in self._S:
            r = self.get_row(s)
            if r not in row_to_state:
                is_init = (r == empty_row)
                st_name = f"q{state_counter}"
                st = State(st_name, is_initial=is_init)
                row_to_state[r] = st
                unique_rows.append(r)
                state_counter += 1

        mealy = MealyMachine[SymbolT, OutputT](name=name)
        for st in row_to_state.values():
            mealy.add_state(st)

        # Build transition table for each representative state
        for s in self._S:
            src_row = self.get_row(s)
            src_state = row_to_state[src_row]

            for a in self._alphabet:
                s_a = s + (a,)
                target_row = self.get_row(s_a)
                target_state = row_to_state[target_row]

                # Output symbol lambda(q_s, a) comes from T(s, (a,))[0]
                out_symbol = self._table[(s, (a,))][0]
                mealy.add_transition(src_state, a, target_state, out_symbol)

        mealy.validate()
        return mealy

    def __repr__(self) -> str:
        return f"ObservationTable(|S|={len(self._S)}, |S.Sigma|={len(self.S_dot_Sigma)}, |E|={len(self._E)})"
