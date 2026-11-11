"""Core simulated QUIC transport and stream multiplexer implementation."""
import time
from typing import Dict, List, Optional

class StreamFrame:
    def __init__(self, stream_id: int, offset: int, data: bytes, fin: bool = False):
        self.stream_id = stream_id
        self.offset = offset
        self.data = data
        self.fin = fin

    def __repr__(self) -> str:
        return f"<StreamFrame id={self.stream_id} offset={self.offset} len={len(self.data)} fin={self.fin}>"

class QUICPacket:
    def __init__(self, packet_number: int, frames: List[StreamFrame]):
        self.packet_number = packet_number
        self.frames = frames
        self.timestamp = time.time()

class StreamState:
    def __init__(self, stream_id: int):
        self.stream_id = stream_id
        self.send_offset = 0
        self.recv_offset = 0
        self.buffer = bytearray()
        self.is_closed = False

class QUICStreamBridge:
    """Manages independent multiplexed streams without head-of-line blocking."""
    
    def __init__(self, max_streams: int = 1024):
        self.max_streams = max_streams
        self.packet_counter = 0
        self.streams: Dict[int, StreamState] = {}
        self.flow_control_credit = 65536

    def open_stream(self, stream_id: int) -> StreamState:
        if stream_id in self.streams:
            return self.streams[stream_id]
        if len(self.streams) >= self.max_streams:
            raise RuntimeError("Maximum concurrent QUIC streams exceeded")
        st = StreamState(stream_id)
        self.streams[stream_id] = st
        return st

    def send_stream_data(self, stream_id: int, data: bytes, fin: bool = False) -> QUICPacket:
        st = self.open_stream(stream_id)
        frame = StreamFrame(stream_id=stream_id, offset=st.send_offset, data=data, fin=fin)
        st.send_offset += len(data)
        if fin:
            st.is_closed = True
        self.packet_counter += 1
        return QUICPacket(self.packet_counter, [frame])

    def receive_packet(self, packet: QUICPacket) -> Dict[int, bytes]:
        """Ingests a packet and assembles stream bytes independently per stream ID."""
        assembled = {}
        for frame in packet.frames:
            st = self.open_stream(frame.stream_id)
            # Simulate independent in-order buffer assembly
            st.buffer.extend(frame.data)
            st.recv_offset += len(frame.data)
            assembled[frame.stream_id] = bytes(frame.data)
            if frame.fin:
                st.is_closed = True
        return assembled
