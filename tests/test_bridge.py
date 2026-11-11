"""Unit tests for agent-transport-quic-bridge."""
import unittest
from agent_transport_quic_bridge.bridge import QUICStreamBridge

class TestQUICStreamBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = QUICStreamBridge(max_streams=10)

    def test_independent_multiplexing(self):
        pkt1 = self.bridge.send_stream_data(1, b"Hello from stream 1")
        pkt2 = self.bridge.send_stream_data(2, b"Hello from stream 2", fin=True)

        res1 = self.bridge.receive_packet(pkt1)
        res2 = self.bridge.receive_packet(pkt2)

        self.assertIn(1, res1)
        self.assertEqual(res1[1], b"Hello from stream 1")
        self.assertIn(2, res2)
        self.assertTrue(self.bridge.streams[2].is_closed)

    def test_max_streams_limit(self):
        bridge = QUICStreamBridge(max_streams=2)
        bridge.open_stream(1)
        bridge.open_stream(2)
        with self.assertRaises(RuntimeError):
            bridge.open_stream(3)
