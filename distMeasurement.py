import socket
from socket import *
import struct
import select
import time
import matplotlib.pyplot as mplot

def main():
	targets = [line.strip() for line in open('targets.txt')]
	output = open('results.txt',"w")
	graph = open('gresults.txt',"w")
	
	for target in targets:
		results = probe(target)
		print results
		if results is not None:
			result_str = "Host: {}\nHops: {}\nRTT: {} ms\n{}".format(target, results[0],results[1], results[2])
			output.write(result_str + "\n")
			graph_str = "{}\t{}\t".format(results[0],results[1])
			graph.write(graph_str + "\n")
		else: 
			output.write("{} timed out".format(target) + "\n\n")

	output.close()
	graph.close()
	graph_results()

def graph_results():
	data = open('gresults.txt',"r")
	hops = []
	rtt = []
	for line in data:
		split = line.split('\t')
		hops.append(split[0])
		rtt.append(split[1])

	mplot.plot(hops,rtt,'r*',linewidth = 5)
	mplot.grid(color='black',linestyle='-', linewidth=1)
	mplot.xlabel('Hops(# of hops)')
	mplot.ylabel('RTT(ms)')
	xmin,xmax = mplot.xlim()
	ymin,ymax = mplot.ylim()
	mplot.xlim((xmin-1,xmax+1))
	mplot.ylim((ymin-5,ymax+5))
	mplot.show()
	

def probe(target):

	timeout = 3.0
	ttl_current = 32
	ttl_top = 0
	ttl_bot = 0
	maxed_out = False
	mined_out = False

	port = 33435
	retry = 10

	for tries in range(retry):
		rec_socket = socket(AF_INET,SOCK_RAW,getprotobyname('icmp'))
		send_socket = socket(AF_INET,SOCK_DGRAM,getprotobyname('udp'))
		send_socket.setsockopt(SOL_IP,IP_TTL,ttl_current)

		rec_socket.settimeout(timeout)
		send_socket.settimeout(timeout)

#		listen = select.select([rec_socket],[],[],10.0)
		
#find appropiate ttl
#		try:
#			if listen[0]:
#				rec_packet,cur_addr = rec_socket.recvfrom(1024)
#				code_type,code = struct.unpack("bb",rec_packet[20:22])
#				if(code_type==11):
#					if(not mined_out):
#						ttl_bot = ttl_current
#						mined_out = True
#					if(maxed_out):
#						ttl_bot = ttl_current
#						ttl_current = (ttl_bot+ttl_top)/2
#					else: ttl_current *= 2
#				elif(code_type==3):
#					if(not maxed_out):
#						ttl_top = ttl_current
#						maxed_out = True
#					if(mined_out):
#						ttl_top = ttl_current
#						ttl_current = (ttl_bot+ttl_top)/2
#					elif(timeout==0):
#						ttl_current /=2
#					else: ttl_current = 4
#				else: 
#					ttl_current *=2
#					if (ttl_current>ttl_top and maxed_out):
#						ttl_top = ttl_current
#			else:
#				ttl_current *=2
#				if (ttl_current>ttl_top and maxed_out):
#						ttl_top = ttl_current
#		except socket.error: print(socket.error)
#		finally:
#			send_socket.close()
#			rec_socket.close()

#For TTL = 32 to start
		try:
			rec_packet = None
			rec_addr = None

			rec_socket.bind(("",port))
			send_time = time.time()
			send_socket.sendto("",(target,port))	
			rec_packet,rec_addr = rec_socket.recvfrom(1500)
			recd_time = time.time()

			ip_long = struct.unpack('!L',rec_packet[44:48])[0]
			ip_target = inet_ntoa(struct.pack('!L',ip_long))
			port_target = struct.unpack("!H",rec_packet[50:52])[0]
			
			header_icmp = rec_packet[20:28]
			icmp_type,icmp_code,icmp_checksum,icmp_ip,icmp_seq = struct.unpack_from("bbHHh",header_icmp)
			
			header_ip = rec_packet[36:40]
			ip_ttl,ip_protocol,ip_checksum = struct.unpack_from("bbH",header_ip)


			hops = ttl_current - ip_ttl +1
			rtt = 1000*(recd_time-send_time)


			if(ip_target == target and port_target == port):
				addr_target = "Target IP: {} Port {}. \n".format(ip_target,port_target)
			else: addr_target = "Target IP and Port were not valid." + "IP: {} Port {}".format(ip_target,port_target)
			
			return hops,rtt,addr_target
			
		except (error,timeout): pass

		finally:
			send_socket.close()
			rec_socket.close()
	else: return None

if __name__ == "__main__":
	main()
