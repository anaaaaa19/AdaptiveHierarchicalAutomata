"""
Phase 8 Queue Backpressure Stress Test.
"""

from adaptive_automata.deployment.config.settings import BackpressurePolicy
from adaptive_automata.deployment.pipeline.events import RawPacket
from adaptive_automata.deployment.pipeline.queue import BoundedEventQueue


def run_queue_stress_test():
    print("Testing BoundedEventQueue backpressure policies...")
    queue = BoundedEventQueue[RawPacket](max_size=10, policy=BackpressurePolicy.DROP_OLDEST)

    for i in range(25):
        pkt = RawPacket(f"pkt_{i}", "10.0.0.1", 1000+i, "10.0.0.2", 80, "TCP", 0.0, b"TEST", 4)
        queue.put(pkt)

    print(f"Final Queue Size: {queue.qsize()} (Max: 10)")
    print(f"Total Dropped Items: {queue.dropped_count}")
    assert queue.qsize() == 10
    assert queue.dropped_count == 15
    print("Backpressure DROP_OLDEST policy verified successfully.")


if __name__ == "__main__":
    run_queue_stress_test()
