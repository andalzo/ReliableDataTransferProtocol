import socket
import time

UDP_IP = "127.0.0.1"  # IP address of the receiver
UDP_PORT = 5005       # Port number on which the receiver is listening
BUFFER_SIZE = 8    # Maximum size of the data that can be received in one packet
TIMEOUT = 5           # Timeout value in seconds

# Create a UDP socket
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

# Bind the socket to the IP address and port number
sock.bind((UDP_IP, UDP_PORT))

# Wait for a SYN message from the sender to establish a connection
data, addr = sock.recvfrom(BUFFER_SIZE)
if data.decode() == "SYN":
    # Send a SYN-ACK message to confirm the connection
    syn_ack = "SYN-ACK"
    sock.sendto(syn_ack.encode(), addr)

    # Wait for an ACK message from the sender to confirm the connection
    data, addr = sock.recvfrom(BUFFER_SIZE)
    if data.decode() == "ACK":
        print("Connection established.")
        last_received_seq_num = -1
        start_time = time.time()
        while True:
            # Receive a packet from the sender
            sock.settimeout(TIMEOUT)
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                # If no packet is received within the timeout period, close the socket and end the program
                print("Connection timed out.")
                sock.close()
                break
            seq_num = int.from_bytes(data[0:1], byteorder="big")
            checksum = int.from_bytes(data[1:3], byteorder="big")
            payload = data[3:]
            # Check if the packet has the correct sequence number and checksum
            if seq_num == (last_received_seq_num + 1) % 2 and checksum == sum(payload):
                print(f"The segment with sequence number {seq_num} is received correctly.")
                # Send an acknowledgement to the sender
                ack = seq_num.to_bytes(1, byteorder="big")
                sock.sendto(ack, addr)
                print(f"The acknowledgement with sequence number {seq_num} is sent.")
                last_received_seq_num = seq_num
                # Write the received data to a file
                print(payload.decode())
            else:
                # Send an acknowledgement for the previous packet to the sender
                print(f"The segment with sequence number {seq_num} is  not received correctly. The last"
                      f"segment's acknowledgement is sent.")
                ack = last_received_seq_num.to_bytes(1, byteorder="big")
                sock.sendto(ack, addr)
        print("Data reception complete.")
    else:
        # Close the socket if the ACK message is not received
        sock.close()
else:
    # Close the socket if the SYN message is not received
    sock.close()
