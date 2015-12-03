from socket import *
import sys
import struct
import time
import select

#Constants
TTL_START = 32  # max TTL for the probe to start at.
TIMEOUT = 2.0   # number of seconds for a the socket to timeout.
RETRIES = 7     # max number of retries allowed.

def main():
    input_file = open("targets.txt")
    output_file = open("result.txt", "w")

    output_file.write("Name: Andrew Hwang\n" + "EECS 325 Project 2\n" + "\n")

    target_hosts = input_file.read().splitlines()

    # Iterates throuth the list of target hosts from the target.txt file.
    for host in target_hosts:
        # probes the destination host by its name.
        result = probe(gethostbyname(host))
        if result is not None:
            output_result = "Host: {}\nHops: {}\nRTT: {} ms\n{}".format(host, result[0], result[1], result[2])
            print output_result
            output_file.write(output_result + "\n")
        else:
            output_result = "Host: {}\nHost timed out.\n".format(host)
            print output_result
            output_file.write(output_result + "\n")

    input_file.close()
    output_file.close()

def probe(IP_address):
    ttl = TTL_START
    port = 33434 # specify unlikely port to listen for.

    # Use every retry until a result is returned or the number of retries runs out.
    for retry in xrange(RETRIES):
        # the sending socket uses a UDP protocol to probe.
        send_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        # the receiving socket uses a ICMP protocol to listen for a reply.
        recv_socket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)

        # change the TTL field in the header.
        send_socket.setsockopt(SOL_IP, IP_TTL, ttl)

        # set the timeout for both sockets.
        send_socket.settimeout(TIMEOUT)
        recv_socket.settimeout(TIMEOUT)

        try:
            # bind the port to the receivng socket for listening.
            recv_socket.bind(("", port))
            # send to the specified IP address and port number.
            send_socket.sendto("", (IP_address, port))
            sent_time = time.time()

            recv_packet = recv_address = None

            # select blocksize to read, which we set to 1500 MTU.
            recv_packet, recv_address = recv_socket.recvfrom(1500)
            recvd_time = time.time()
            print "Packet Recieved."

            # the ICMP header is within range from 20 to 28 bytes of the packet.
            icmp_header = recv_packet[20:28]
            icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq = struct.unpack_from("bbHHh", icmp_header)

            # the IP header is within the range from 36 to 40 bytes of the packet.
            ip_header = recv_packet[36:40]
            ip_ttl, ip_protocol, ip_checksum = struct.unpack_from("bbH", ip_header)

            # the number of hops is difference of the intial ttl and the ip header ttl plus one.
            number_hops = ttl - ip_ttl + 1
            rtt = 1000*(recvd_time - sent_time) # multiply by 1000 for ms.

            # retreiving the destination IP and destingation port from the packet.
            long_ip = struct.unpack('!L', recv_packet[44:48])[0]
            dest_ip = inet_ntoa(struct.pack('!L', long_ip))
            dest_port = struct.unpack("!H", recv_packet[50:52])[0]

            print "Destination IP: {}\nDestination Port: {}".format(dest_ip, dest_port)

            # Verify if the destination IP and port from the packet match with the destination IP and port that was sent.
            verified = None
            if dest_ip == IP_address and dest_port == port:
                # verify if the ICMP type and code match the specified conditions.
                if icmp_type == 3 and icmp_code == 3:
                    verified = "The Destination IP address: {} and port number: {} match.\n".format(dest_ip, dest_port)
                else:
                    verified = "The ICMP type {} and code {} were incorrect.\n".format(icmp_type, icmp_code)
            else:
                verified = "The Destination IP address and port number do not match.\n"

            # Return the tuple of hops, RTT, and verification.
            return number_hops, rtt, verified

        # loop through again if a timeout or error occurs.
        except (timeout, error):
            pass
        finally:
            send_socket.close()
            recv_socket.close()
    else:
        return None


if __name__ == "__main__":
    main()
