"""
Synthetic Protocol Dataset Generator for Reproducible Evaluation.
"""

from dataclasses import dataclass, field
import random
from typing import List, Optional, Tuple


@dataclass
class ProtocolSample:
    sample_id: str
    protocol: str
    sequence: List[str]
    expected_label: str  # "normal", "anomalous", "evolved", "attack", "poisoning"
    category: str  # "normal", "legitimate_evolution", "structural_anomaly", "behavioral_anomaly", "unseen", "poisoning"
    attack_category: Optional[str] = None
    session_id: str = ""
    seed: int = 42


@dataclass
class DatasetSplit:
    train: List[ProtocolSample]
    validation: List[ProtocolSample]
    test: List[ProtocolSample]


class SyntheticDatasetGenerator:
    """Deterministic Synthetic Dataset Generator for Protocol Benchmark Experiments."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def generate_dataset(
        self,
        protocol: str = "toy_protocol",
        train_size: int = 1000,
        validation_size: int = 200,
        test_size: int = 500,
        categories: Optional[List[str]] = None,
        seed: Optional[int] = None,
    ) -> DatasetSplit:
        gen_seed = seed if seed is not None else self.seed
        rng = random.Random(gen_seed)

        if categories is None:
            categories = [
                "normal",
                "legitimate_evolution",
                "structural_anomaly",
                "behavioral_anomaly",
                "unseen",
                "poisoning",
            ]

        # Generate pool for each category
        pool_train: List[ProtocolSample] = []
        pool_val: List[ProtocolSample] = []
        pool_test: List[ProtocolSample] = []

        # Calculate category proportion with ceiling division to meet requested split sizes
        cat_count_train = max(1, (train_size + len(categories) - 1) // len(categories))
        cat_count_val = max(1, (validation_size + len(categories) - 1) // len(categories))
        cat_count_test = max(1, (test_size + len(categories) - 1) // len(categories))

        for cat in categories:
            if cat == "normal":
                pool_train.extend(self._gen_normal(cat_count_train, rng, protocol, gen_seed, "train"))
                pool_val.extend(self._gen_normal(cat_count_val, rng, protocol, gen_seed, "val"))
                pool_test.extend(self._gen_normal(cat_count_test, rng, protocol, gen_seed, "test"))
            elif cat == "legitimate_evolution":
                # Evolved behavior only present in val & test for unseen evolution test
                pool_train.extend(self._gen_normal(cat_count_train, rng, protocol, gen_seed, "train"))
                pool_val.extend(self._gen_evolved(cat_count_val, rng, protocol, gen_seed, "val"))
                pool_test.extend(self._gen_evolved(cat_count_test, rng, protocol, gen_seed, "test"))
            elif cat == "structural_anomaly":
                pool_train.extend(self._gen_normal(cat_count_train, rng, protocol, gen_seed, "train"))
                pool_val.extend(self._gen_structural(cat_count_val, rng, protocol, gen_seed, "val"))
                pool_test.extend(self._gen_structural(cat_count_test, rng, protocol, gen_seed, "test"))
            elif cat == "behavioral_anomaly":
                pool_train.extend(self._gen_normal(cat_count_train, rng, protocol, gen_seed, "train"))
                pool_val.extend(self._gen_behavioral(cat_count_val, rng, protocol, gen_seed, "val"))
                pool_test.extend(self._gen_behavioral(cat_count_test, rng, protocol, gen_seed, "test"))
            elif cat == "unseen":
                # Unseen attacks excluded from training set
                pool_train.extend(self._gen_normal(cat_count_train, rng, protocol, gen_seed, "train"))
                pool_val.extend(self._gen_unseen(cat_count_val, rng, protocol, gen_seed, "val"))
                pool_test.extend(self._gen_unseen(cat_count_test, rng, protocol, gen_seed, "test"))
            elif cat == "poisoning":
                pool_train.extend(self._gen_normal(cat_count_train, rng, protocol, gen_seed, "train"))
                pool_val.extend(self._gen_poisoning(cat_count_val, rng, protocol, gen_seed, "val"))
                pool_test.extend(self._gen_poisoning(cat_count_test, rng, protocol, gen_seed, "test"))

        rng.shuffle(pool_train)
        rng.shuffle(pool_val)
        rng.shuffle(pool_test)

        return DatasetSplit(
            train=pool_train[:train_size],
            validation=pool_val[:validation_size],
            test=pool_test[:test_size],
        )

    def _gen_normal(self, count: int, rng: random.Random, protocol: str, seed: int, split: str) -> List[ProtocolSample]:
        samples = []
        # Normal sequences: HELLO -> AUTH -> REQUEST -> RESPONSE -> LOGOUT
        # or HELLO -> AUTH -> REQ1 -> RESP1 -> REQ2 -> RESP2 -> LOGOUT
        for i in range(count):
            req_count = rng.randint(1, 3)
            seq = ["HELLO", "AUTH"]
            for _ in range(req_count):
                seq.extend(["REQUEST", "RESPONSE"])
            seq.append("LOGOUT")

            samples.append(
                ProtocolSample(
                    sample_id=f"{split}_norm_{i}",
                    protocol=protocol,
                    sequence=seq,
                    expected_label="normal",
                    category="normal",
                    session_id=f"sess_norm_{i}",
                    seed=seed,
                )
            )
        return samples

    def _gen_evolved(self, count: int, rng: random.Random, protocol: str, seed: int, split: str) -> List[ProtocolSample]:
        samples = []
        # Evolved sequences (Protocol v2): HELLO -> AUTH -> CAPABILITIES -> REQUEST -> RESPONSE -> LOGOUT
        for i in range(count):
            req_count = rng.randint(1, 2)
            seq = ["HELLO", "AUTH", "CAPABILITIES"]
            for _ in range(req_count):
                seq.extend(["REQUEST", "RESPONSE"])
            seq.append("LOGOUT")

            samples.append(
                ProtocolSample(
                    sample_id=f"{split}_evolved_{i}",
                    protocol=protocol,
                    sequence=seq,
                    expected_label="evolved",
                    category="legitimate_evolution",
                    session_id=f"sess_evolved_{i}",
                    seed=seed,
                )
            )
        return samples

    def _gen_structural(self, count: int, rng: random.Random, protocol: str, seed: int, split: str) -> List[ProtocolSample]:
        samples = []
        # Structural anomaly: Out of order or unclosed depth (e.g. REQUEST without AUTH or missing LOGOUT)
        templates = [
            ["REQUEST", "RESPONSE", "LOGOUT"],
            ["HELLO", "REQUEST", "LOGOUT"],
            ["AUTH", "HELLO", "LOGOUT"],
            ["HELLO", "AUTH", "RESPONSE"],
        ]
        for i in range(count):
            seq = rng.choice(templates).copy()
            samples.append(
                ProtocolSample(
                    sample_id=f"{split}_struct_{i}",
                    protocol=protocol,
                    sequence=seq,
                    expected_label="anomalous",
                    category="structural_anomaly",
                    attack_category="out_of_order",
                    session_id=f"sess_struct_{i}",
                    seed=seed,
                )
            )
        return samples

    def _gen_behavioral(self, count: int, rng: random.Random, protocol: str, seed: int, split: str) -> List[ProtocolSample]:
        samples = []
        # Behavioral anomaly: Valid syntax, invalid timing/ordering (e.g., repeated LOGOUT, Auth flood)
        templates = [
            ["HELLO", "AUTH", "AUTH", "AUTH", "REQUEST", "RESPONSE", "LOGOUT"],
            ["HELLO", "AUTH", "REQUEST", "RESPONSE", "LOGOUT", "LOGOUT"],
        ]
        for i in range(count):
            seq = rng.choice(templates).copy()
            samples.append(
                ProtocolSample(
                    sample_id=f"{split}_behav_{i}",
                    protocol=protocol,
                    sequence=seq,
                    expected_label="anomalous",
                    category="behavioral_anomaly",
                    attack_category="state_violation",
                    session_id=f"sess_behav_{i}",
                    seed=seed,
                )
            )
        return samples

    def _gen_unseen(self, count: int, rng: random.Random, protocol: str, seed: int, split: str) -> List[ProtocolSample]:
        samples = []
        # Unseen zero-day style attack payload
        templates = [
            ["HELLO", "AUTH", "EXPLOIT_PAYLOAD", "LOGOUT"],
            ["HELLO", "AUTH", "OVERFLOW_BUFFER", "RESPONSE", "LOGOUT"],
        ]
        for i in range(count):
            seq = rng.choice(templates).copy()
            samples.append(
                ProtocolSample(
                    sample_id=f"{split}_unseen_{i}",
                    protocol=protocol,
                    sequence=seq,
                    expected_label="attack",
                    category="unseen",
                    attack_category="zero_day_exploit",
                    session_id=f"sess_unseen_{i}",
                    seed=seed,
                )
            )
        return samples

    def _gen_poisoning(self, count: int, rng: random.Random, protocol: str, seed: int, split: str) -> List[ProtocolSample]:
        samples = []
        # Deliberately injected repeated malicious transition sequence designed to trick naive adaptive engines
        for i in range(count):
            seq = ["HELLO", "AUTH", "MALICIOUS_INJECT", "REQUEST", "RESPONSE", "LOGOUT"]
            samples.append(
                ProtocolSample(
                    sample_id=f"{split}_poison_{i}",
                    protocol=protocol,
                    sequence=seq,
                    expected_label="poisoning",
                    category="poisoning",
                    attack_category="model_poisoning",
                    session_id=f"sess_poison_{i}",
                    seed=seed,
                )
            )
        return samples
