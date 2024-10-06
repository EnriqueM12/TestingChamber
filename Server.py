# server.py
import socket
import cv2
import pickle
import struct
import time

# Set up the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 3000))  # Bind to all interfaces on port 8080
server_socket.listen(1)
print("Waiting for a connection...")

conn, addr = server_socket.accept()
print(f"Connected to: {addr}")

# Capture video from the webcam
cap = cv2.VideoCapture(0)

a0 = float(conn.recv(1024).decode())
f0 = time.time()
conn.sendall(str(f0).encode())
a1 = float(conn.recv(1024).decode())
f1 = time.time()
w, h = (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
conn.sendall(pickle.dumps((w, h)))
print(f1 - f0, a1)
begin = f0

while True:
    print('h ')
    ret, frame = cap.read()
    t = time.time() - begin
    if not ret:
        break

    # Serialize the frame
    data = pickle.dumps([t, frame])
    # Send the length of the frame first
    message_size = struct.pack("L", len(data))  # Use 'Q' for 64-bit if necessary
    conn.sendall(message_size + data)

cap.release()
conn.close()
server_socket.close()

