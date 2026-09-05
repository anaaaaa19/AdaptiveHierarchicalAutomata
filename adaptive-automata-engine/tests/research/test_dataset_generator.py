"""
Unit tests for Synthetic Dataset Generator determinism, category separation, and schema compliance.
"""

from adaptive_automata.evaluation.dataset import SyntheticDatasetGenerator, DatasetSplit


def test_dataset_generator_determinism():
    gen1 = SyntheticDatasetGenerator(seed=42)
    split1 = gen1.generate_dataset(train_size=100, validation_size=20, test_size=50, seed=42)

    gen2 = SyntheticDatasetGenerator(seed=42)
    split2 = gen2.generate_dataset(train_size=100, validation_size=20, test_size=50, seed=42)

    assert len(split1.train) == 100
    assert len(split1.validation) == 20
    assert len(split1.test) == 50

    # Verify identical sample sequences across runs with same seed
    for s1, s2 in zip(split1.train, split2.train):
        assert s1.sequence == s2.sequence
        assert s1.expected_label == s2.expected_label
        assert s1.category == s2.category


def test_dataset_categories_and_labels():
    gen = SyntheticDatasetGenerator(seed=123)
    split = gen.generate_dataset(train_size=300, validation_size=60, test_size=120, seed=123)

    categories = {s.category for s in split.test}
    labels = {s.expected_label for s in split.test}

    assert "normal" in categories
    assert "legitimate_evolution" in categories
    assert "structural_anomaly" in categories
    assert "poisoning" in categories

    assert "normal" in labels
    assert "anomalous" in labels or "attack" in labels
