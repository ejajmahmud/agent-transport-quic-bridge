"""CLI for agent-transport-quic-bridge."""
import sys
import argparse
from .bridge import QUICStreamBridge

def main():
    parser = argparse.ArgumentParser(description="Agent Transport QUIC Bridge CLI")
    parser.add_argument("--demo", action="store_true", help="Demonstrate multiplexed stream transmission")
    args = parser.parse_args()

    if args.demo:
        bridge = QUICStreamBridge()
        pkt1 = bridge.send_stream_data(stream_id=1, data=b"Tool output line 1")
        pkt2 = bridge.send_stream_data(stream_id=3, data=b"Parallel telemetry metric")
        print(f"Created Packet 1 on Stream 1: {pkt1.frames[0]}")
        print(f"Created Packet 2 on Stream 3: {pkt2.frames[0]}")
        res = bridge.receive_packet(pkt1)
        print(f"Demuxed stream data: {res}")
    else:
        parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()
