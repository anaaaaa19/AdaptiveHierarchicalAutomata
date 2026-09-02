"""
Context-Free Grammar (CFG) and Parsing Engine.

Provides formal Grammar abstractions (Terminals, NonTerminals, ProductionRules)
and a Earley/Chart parser for structural grammar validation of complex protocol messages.
"""

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass(frozen=True, slots=True)
class Terminal:
    """Terminal symbol in a Context-Free Grammar."""
    name: str

    def __repr__(self) -> str:
        return f"'{self.name}'"


@dataclass(frozen=True, slots=True)
class NonTerminal:
    """Non-terminal symbol in a Context-Free Grammar."""
    name: str

    def __repr__(self) -> str:
        return f"<{self.name}>"


Symbol = Terminal | NonTerminal


@dataclass(frozen=True, slots=True)
class ProductionRule:
    """
    Production rule A -> alpha in a Context-Free Grammar.
    """
    head: NonTerminal
    body: tuple[Symbol, ...]

    def __repr__(self) -> str:
        body_str = " ".join(repr(s) for s in self.body) if self.body else "epsilon"
        return f"{self.head} -> {body_str}"


class CFGValidationError(Exception):
    """Raised when Context-Free Grammar configuration is invalid."""
    pass


@dataclass(slots=True)
class Grammar:
    """
    Context-Free Grammar formally defined as G = (V, Sigma, R, S):
      - V: Non-terminal symbols
      - Sigma: Terminal symbols (alphabet)
      - R: Production rules V -> (V U Sigma)*
      - S: Start symbol (S in V)
    """
    start_symbol: NonTerminal
    rules: list[ProductionRule] = field(default_factory=list)
    terminals: set[Terminal] = field(default_factory=set)
    nonterminals: set[NonTerminal] = field(default_factory=set)

    def add_rule(self, head: NonTerminal, body: Sequence[Symbol]) -> None:
        """Add a production rule head -> body to grammar R."""
        self.nonterminals.add(head)
        body_tuple = tuple(body)
        for sym in body_tuple:
            if isinstance(sym, Terminal):
                self.terminals.add(sym)
            elif isinstance(sym, NonTerminal):
                self.nonterminals.add(sym)

        self.rules.append(ProductionRule(head=head, body=body_tuple))

    def validate(self) -> None:
        """Validate Grammar structural integrity."""
        if self.start_symbol not in self.nonterminals:
            raise CFGValidationError(f"Start symbol '{self.start_symbol}' not in non-terminals set.")
        if not self.rules:
            raise CFGValidationError("Grammar must have at least one production rule.")


@dataclass(slots=True)
class CFGParseResult:
    """Result container produced by CFGParser."""
    is_valid: bool
    reason: str
    error_position: int | None = None
    derivation_tree: Any = None


class CFGParser:
    """
    Earley-style Chart Parser for Context-Free Grammars.
    """

    def __init__(self, grammar: Grammar) -> None:
        grammar.validate()
        self.grammar = grammar

    def parse(self, tokens: Sequence[str]) -> CFGParseResult:
        """
        Parse a sequence of terminal token strings against the grammar.

        Returns:
            CFGParseResult indicating whether the token sequence is valid under G.
        """
        if not tokens:
            # Check if start symbol can derive epsilon
            for r in self.grammar.rules:
                if r.head == self.grammar.start_symbol and len(r.body) == 0:
                    return CFGParseResult(is_valid=True, reason="Parsed empty sequence via epsilon rule.")
            return CFGParseResult(is_valid=False, reason="Empty token sequence not accepted.", error_position=0)

        # Earley Chart Data Structure:
        # Chart item: (rule, dot_index, origin_chart_index)
        n = len(tokens)
        chart: list[set[tuple[ProductionRule, int, int]]] = [set() for _ in range(n + 1)]

        # Initialize Chart[0] with start symbol rules
        for rule in self.grammar.rules:
            if rule.head == self.grammar.start_symbol:
                chart[0].add((rule, 0, 0))

        # Earley Algorithm Main Loop
        for i in range(n + 1):
            changed = True
            while changed:
                changed = False
                current_items = list(chart[i])

                for item in current_items:
                    rule, dot, origin = item

                    if dot < len(rule.body):
                        next_sym = rule.body[dot]
                        if isinstance(next_sym, NonTerminal):
                            # Predictor: add rules for next_sym to chart[i]
                            for r in self.grammar.rules:
                                if r.head == next_sym:
                                    new_item = (r, 0, i)
                                    if new_item not in chart[i]:
                                        chart[i].add(new_item)
                                        changed = True
                        elif isinstance(next_sym, Terminal):
                            # Scanner: if i < n and token matches, add to chart[i+1]
                            if i < n and tokens[i] == next_sym.name:
                                new_item = (rule, dot + 1, origin)
                                if new_item not in chart[i + 1]:
                                    chart[i + 1].add(new_item)
                    else:
                        # Completer: rule is complete! Advance items in chart[origin]
                        for orig_item in list(chart[origin]):
                            orig_rule, orig_dot, orig_origin = orig_item
                            if orig_dot < len(orig_rule.body) and orig_rule.body[orig_dot] == rule.head:
                                new_item = (orig_rule, orig_dot + 1, orig_origin)
                                if new_item not in chart[i]:
                                    chart[i].add(new_item)
                                    changed = True

        # Check if start symbol rule completed in chart[n] starting at 0
        for item in chart[n]:
            rule, dot, origin = item
            if rule.head == self.grammar.start_symbol and dot == len(rule.body) and origin == 0:
                return CFGParseResult(
                    is_valid=True,
                    reason=f"Parsed successfully by CFG start symbol <{self.grammar.start_symbol.name}>.",
                    error_position=None,
                )

        # Find furthest position reached in chart
        furthest = 0
        for idx in range(n, -1, -1):
            if chart[idx]:
                furthest = idx
                break

        err_token = tokens[furthest] if furthest < n else "EOF"
        return CFGParseResult(
            is_valid=False,
            reason=f"CFG parse error: unexpected token '{err_token}' at index {furthest}.",
            error_position=furthest,
        )
