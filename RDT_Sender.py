import socket
import time

UDP_IP = "127.0.0.1"  # IP address of the receiver
UDP_PORT = 5005       # Port number on which the receiver is listening
BUFFER_SIZE = 8   # Maximum size of the data that can be sent in one packet
TIMEOUT = 5           # Timeout value in seconds

# Write a trial string
data = "This is a receiver message from sender side."

# Create a UDP socket
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

# Send a SYN message to the receiver to establish a connection
syn = "SYN"
sock.sendto(syn.encode(), (UDP_IP, UDP_PORT))

# Wait for a SYN-ACK message from the receiver to confirm the connection
data, addr = sock.recvfrom(BUFFER_SIZE)
if data.decode() == "SYN-ACK":
    # Send an ACK message to confirm the connection
    ack = "ACK"
    sock.sendto(ack.encode(), addr)
    print("Connection established.")

    # Send packets to the receiver and wait for acknowledgements
    start_time = time.time()
    for i in range(0, len(data), BUFFER_SIZE-3):
        # Split the data into packets of size BUFFER_SIZE-3 bytes
        seq_num = i // (BUFFER_SIZE-3) % 2
        payload = data[i:i+(BUFFER_SIZE-3)]
        checksum = sum(payload).to_bytes(2, byteorder="big")
        packet = seq_num.to_bytes(1, byteorder="big") + checksum + payload
        # Send the packet to the receiver
        sock.sendto(packet, addr)
        # Wait for an acknowledgement from the receiver or timeout
        sock.settimeout(TIMEOUT)
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            # If the acknowledgement is not received within the timeout period, resend the packet
            i -= BUFFER_SIZE-3
            continue
        expected_seq_num = (i // (BUFFER_SIZE-3) + 1) % 2
        if int.from_bytes(data, byteorder="big") == expected_seq_num:
            # If the acknowledgement has the correct sequence number, continue sending packets
            continue
        else:
            # If the acknowledgement has the wrong sequence number, resend the previous packet
            i -= BUFFER_SIZE-3
    print("Data successfully sent.")
else:
    # Close the socket if the SYN-ACK message is not received
    sock.close()

