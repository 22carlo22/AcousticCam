import cv2
import socket
import numpy as np
import threading
import queue

class UdpStreamServer:
    """
    Reads the video stream from the esp via UDP protocol
    """
    def __init__(self, ip, port, max_buffers=2):
        self.ip = ip
        self.port = port
        self.max_buffers = max_buffers
        
        self.frame_queue = queue.Queue(maxsize=self.max_buffers)
        self.started = False
        self.thread = None
        
        # Configure a standard UDP network socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def start(self):
        if self.started:
            return self
        
        try:
            self.sock.bind((self.ip, self.port))
            # Set a timeout so the socket loop doesn't block forever on closing
            self.sock.settimeout(1.0) 
        except Exception as e:
            print(f"Could not bind UDP socket to port {self.port}: {e}")
            return self

        self.started = True
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def _update(self):
        frame_assembly = {}
        active_frame_id = None
        
        while self.started:
            try:
                packet, addr = self.sock.recvfrom(2000)
                if len(packet) < 6: # Expecting at least 6 bytes now
                    continue
                
                # Unpack our updated 6-byte header
                frame_id = packet[0]
                total_packets = packet[1]
                packet_index = (packet[2] << 8) | packet[3]
                chunk_size = (packet[4] << 8) | packet[5]
                payload = packet[6:]
                
                # --- BOUNDARY SANITIZATION ENGINE ---
                # If this packet belongs to a brand new frame signature sequence
                if active_frame_id != frame_id:
                    # Clear out the old incomplete frame snippets instantly
                    frame_assembly.clear()
                    active_frame_id = frame_id
                
                frame_assembly[packet_index] = payload
                
                # Verify structural completion
                if len(frame_assembly) == total_packets:
                    is_frame_complete = True
                    full_frame_bytes = bytearray()
                    
                    for i in range(total_packets):
                        if i in frame_assembly:
                            full_frame_bytes += frame_assembly[i]
                        else:
                            is_frame_complete = False
                            break
                    
                    if is_frame_complete:
                        frame = cv2.imdecode(np.frombuffer(full_frame_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if frame is not None:
                            if self.frame_queue.full():
                                try: self.frame_queue.get_nowait()
                                except queue.Empty: pass
                            self.frame_queue.put(frame)
                    
                    # Clean out structures for subsequent updates
                    frame_assembly.clear()
                    active_frame_id = None

            except socket.timeout:
                continue
            except Exception as e:
                print(f"UDP Packet processing error: {e}")
                frame_assembly.clear()
                active_frame_id = None

    def stop(self):
        self.started = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        self.sock.close()
