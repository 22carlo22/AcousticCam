import socket
import threading
import queue
from typing import Optional

class TcpClient:
    """Multithreaded TCP stream receiver designed for framed packet ingestion.

    Connects to an ESP32 TCP server and unpacks 2-byte length-prefixed payloads 
    into a thread-safe queue.
    """

    def __init__(self, ip: str, port: int, max_buffers: int = 2):
        """Initializes TCP client connection parameters and data queues.

        Args:
            ip (str): Target TCP Server IP address.
            port (int): Target TCP port number.
            max_buffers (int, optional): Depth of frame output queue. Defaults to 2.
        """
        self.ip = ip
        self.port = port
        self.max_buffers = max_buffers
        
        # Output queue bounded to prevent latency buildup under heavy processing load
        self.data_queue: queue.Queue = queue.Queue(maxsize=self.max_buffers)
        self.started = False
        self.thread: Optional[threading.Thread] = None
        
        self.sock: Optional[socket.socket] = None

    def start(self) -> 'TcpClient':
        """Establishes connection to TCP server and launches background receiver thread.

        Returns:
            TcpClient: Self reference for method chaining.
        """
        if self.started:
            return self
        
        try:
            # Create a TCP IPv4 socket (SOCK_STREAM)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Timeout prevents blocking indefinitely on socket read/connect calls
            self.sock.settimeout(2.0) 
            self.sock.connect((self.ip, self.port))
        except Exception as e:
            print(f"[ERROR] Failed to connect to {self.ip}:{self.port}: {e}")
            if self.sock:
                self.sock.close()
            return self

        self.started = True
        # Spawn background daemon worker for uninterrupted packet ingestion
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        return self

    def _read_exact(self, num_bytes: int) -> Optional[bytes]:
        """Reads EXACTLY num_bytes from the TCP stream, assembling fragmented chunks.

        Args:
            num_bytes (int): Total number of bytes required to form a complete packet block.

        Returns:
            Optional[bytes]: Fully assembled byte payload, or None if connection breaks/times out.
        """
        data = bytearray()
        while len(data) < num_bytes and self.started:
            try:
                # Request remaining bytes needed to reach target length
                packet = self.sock.recv(num_bytes - len(data))
                if not packet:
                    # Connection closed cleanly by remote host
                    return None
                data.extend(packet)
            except socket.timeout:
                # Loop back and retry read if still running
                continue
            except Exception as e:
                print(f"[ERROR] Socket read failed: {e}")
                return None
        return bytes(data)

    def _update(self):
        """Worker loop parsing incoming TCP stream using a 2-byte length header protocol:

        Header format:
            [0..1]: Payload Length (16-bit Big Endian)
            [2..]: Raw Payload Data
        """
        while self.started:
            try:
                # 1. Read the 2-byte Big Endian length header
                header = self._read_exact(2)
                if header is None:
                    break

                # Extract 16-bit integer length from header bytes
                payload_len = (header[0] << 8) | header[1]

                # 2. Read the full payload frame matching payload_len
                payload = self._read_exact(payload_len)
                if payload is None:
                    break

                # 3. Push complete payload into thread-safe output queue (drop oldest frame if full)
                if self.data_queue.full():
                    try: 
                        self.data_queue.get_nowait()
                    except queue.Empty: 
                        pass
                self.data_queue.put(payload)

            except Exception as e:
                print(f"[ERROR] TCP Stream processing error: {e}")
                break

        self.started = False

    def stop(self):
        """Safely halts background worker thread and closes active socket connection."""
        self.started = False
        if self.sock:
            try:
                # Shutdown both read and write halves of the socket descriptor
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            self.sock.close()

        # Wait for worker thread termination
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)