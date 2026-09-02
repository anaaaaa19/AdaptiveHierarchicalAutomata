"""Unit and integration tests for Hierarchical Formal Analysis Engine."""

import pytest
from adaptive_automata.core import (
    State,
    MealyMachine,
    PushdownAutomaton,
    StackOp,
    Grammar,
    Terminal,
    NonTerminal,
    CFGParser,
)
from adaptive_automata.models import ModelSource, VersionedProtocolModel
from adaptive_automata.learning import ConfidenceLevel, TransitionMetadata
from adaptive_automata.analysis import (
    DeviationEvent,
    EscalationController,
    AnalysisLevel,
    AnalysisStatus,
    HierarchicalAnalyzer,
)


def test_hierarchical_analyzer_fast_path_success():
    s0 = State("q0", is_initial=True)
    s1 = State("q1")

    mealy = MealyMachine[str, str]("FastPathMealy")
    mealy.add_transition(s0, "SYN", s1, "SEND_SYN_ACK")
    mealy.validate()

    meta = {
        ("q0", "SYN"): TransitionMetadata("q0", "SYN", "q1", "SEND_SYN_ACK", 10, 1.0, ConfidenceLevel.ACTIVE_VERIFIED)
    }

    model = VersionedProtocolModel[str, str](
        model_id="TestFastPath",
        version="v1.0.0",
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
        transition_metadata=meta,
    )

    analyzer = HierarchicalAnalyzer(fast_path_model=model)
    res = analyzer.analyze_sequence(["SYN"])

    assert res.status == AnalysisStatus.KNOWN
    assert res.level_used == AnalysisLevel.DFA_MEALY
    assert res.state == "q1"


def test_hierarchical_analyzer_pda_escalation():
    s0 = State("q0", is_initial=True)
    mealy = MealyMachine[str, str]("FastPathMealy")
    mealy.add_state(s0)
    mealy.validate()

    model = VersionedProtocolModel[str, str](
        model_id="TestFastPath",
        version="v1.0.0",
        source=ModelSource.PASSIVE_INFERENCE,
        mealy_machine=mealy,
    )

    # Build PDA for container matching
    p_s0 = State("p0", is_initial=True)
    p_s1 = State("p1")
    p_s2 = State("p2", is_accepting=True)

    pda = PushdownAutomaton[str, str]("ContainerPDA", initial_stack_symbol="$")
    pda.add_transition(p_s0, "OPEN_BLOCK", "$", p_s1, op=StackOp.PUSH, push_symbols=["B"])
    pda.add_transition(p_s1, "CLOSE_BLOCK", "B", p_s2, op=StackOp.POP, pop_count=1)
    pda.validate()

    analyzer = HierarchicalAnalyzer(fast_path_model=model, pda=pda)
    res = analyzer.analyze_sequence(["OPEN_BLOCK", "CLOSE_BLOCK"])

    assert res.status == AnalysisStatus.NOVEL_BUT_VALID
    assert res.level_used == AnalysisLevel.PDA
    assert res.state == "p2"


def test_hierarchical_analyzer_cfg_escalation():
    s0 = State("q0", is_initial=True)
    mealy = MealyMachine[str, str]("FastPathMealy")
    mealy.add_state(s0)
    mealy.validate()

    model = VersionedProtocolModel[str, str](
        model_id="TestFastPath",
        version="v1.0.0",
        source=ModelSource.PASSIVE_INFERENCE,
        mealy_machine=mealy,
    )

    # CFG grammar: S -> 'HEADER' 'BODY'
    S = NonTerminal("S")
    t_h = Terminal("HEADER")
    t_b = Terminal("BODY")

    g = Grammar(start_symbol=S)
    g.add_rule(S, [t_h, t_b])
    g.validate()

    cfg_parser = CFGParser(g)

    analyzer = HierarchicalAnalyzer(fast_path_model=model, cfg_parser=cfg_parser)
    res = analyzer.analyze_sequence(["HEADER", "BODY"])

    assert res.status == AnalysisStatus.NOVEL_BUT_VALID
    assert res.level_used == AnalysisLevel.CFG


def test_hierarchical_analyzer_unknown_deviation():
    s0 = State("q0", is_initial=True)
    mealy = MealyMachine[str, str]("FastPathMealy")
    mealy.add_state(s0)
    mealy.validate()

    model = VersionedProtocolModel[str, str](
        model_id="TestFastPath",
        version="v1.0.0",
        source=ModelSource.PASSIVE_INFERENCE,
        mealy_machine=mealy,
    )

    analyzer = HierarchicalAnalyzer(fast_path_model=model)
    res = analyzer.analyze_sequence(["UNKNOWN_CMD"])

    assert res.status == AnalysisStatus.UNKNOWN
    assert res.level_used == AnalysisLevel.UNRESOLVED
