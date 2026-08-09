import socket
import threading
import queue

class Udp:
    """
    Multithreaded UDP packet receiver and packet re-assembler designed for high-throughput stream ingestion.
    """
    def __init__(self, ip, port, max_buffers=2):
        """
        :param ip: Interface IP address to bind.
        :param port: Network UDP target port.
        :param max_buffers: Depth of frame output queue.
        """
        self.ip = ip
        self.port = port
        self.max_buffers = max_buffers
        
        self.data_queue = queue.Queue(maxsize=self.max_buffers)
        self.started = False
        self.thread = None
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def start(self):
        """
        Binds target socket and launches the packet receiver thread.
        """
        if self.started:
            return self
        
        try:
            # Bind socket prior to thread startup to avoid race conditions
            self.sock.bind((self.ip, self.port))
            self.sock.settimeout(1.0) # Prevents blocking indefinitely when halting thread
        except Exception as e:
            print(f"[ERROR] Failed to bind to port {self.port}: {e}")
            return self

        self.started = True
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def _update(self):
        """
        Reassembles incoming segmented UDP frames using chunk header metadata.
        
        Packet Protocol Format:
        [0]: Frame Sequence ID
        [1]: Total Packet Count
        [2..3]: Packet Chunk Index (Big Endian)
        [4..5]: Payload Length (Big Endian)
        [6..]: Chunk Raw Payload Data
        """
        assembly = {}
        active_id = None
        
        while self.started:
            try:
                packet, addr = self.sock.recvfrom(2000)

                id = packet[0] 
                total_packets = packet[1]
                packet_index = (packet[2] << 8) | packet[3]
                chunk_size = (packet[4] << 8) | packet[5]
                payload = packet[6:]

                # Reset buffer on new frame sequence ID
                if active_id != id:
                    assembly.clear()
                    active_id = id
                
                assembly[packet_index] = payload
                
                # Check for completed payload frame
                if len(assembly) == total_packets:
                    data = bytearray()
                    for i in range(total_packets):
                        data += assembly[i]

                    # Push reassembled frame payload into thread-safe output queue
                    if self.data_queue.full():
                        try: self.data_queue.get_nowait()
                        except queue.Empty: pass
                    self.data_queue.put(data)
                    
                    assembly.clear()
                    active_id = None

            except socket.timeout:
                continue
            except Exception as e:
                print(f"UDP Packet processing error: {e}")
                assembly.clear()
                active_id = None

    def stop(self):
        """
        Safely halts background network thread and closes open socket descriptor.
        """
        self.started = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        self.sock.close()