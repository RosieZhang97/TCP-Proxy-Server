# coding: utf-8
from socket import *
import sys
import time



#**********************************functions********************************************
def get_client_port_from_arg(argument):
	count = 0
	client_port = ""
	start = "false"
	for x in range(len(argument)):
		if argument[x] == '/': 
			count = count + 1
		if count == 2 and argument[x] == ':':
			start = "true"
		if count == 3:
			break
		if start == "true":
			client_port = client_port + argument[x]
	if len(client_port)!=0 and client_port[len(client_port)-1] == ']':
		return client_port[1:len(client_port)-2]
	else:
		return int(client_port[1:])

		

def get_client_host_from_arg(argument):	
	count = 0
	client_host = ""
	start = "false"
	for x in range(len(argument)):
		if argument[x] == '/': 
			count = count + 1
		if count == 2 :
			start = "true"
		if count == 2 and argument[x] == ':':
			break
		if start == "true":
			client_host = client_host + argument[x]
	if len(client_host)!=0 and client_host[len(client_host)-1] == ']':
		return client_host[1:len(client_host)-2]
	else:
		return client_host[1:]
	


def get_filename_from_arg(argument):
	count = 0
	file_name = ""
	start = "false"
	for x in range(len(argument)):
		if argument[x] == '/': 
			count = count + 1
		if count == 4:
			start = "true"
		if start == "true":
			file_name = file_name + argument[x]
	if len(file_name)!=0 and file_name[len(file_name)-1] == ']':
		return file_name[1:len(file_name)-2]
	else:
		return file_name[1:]



def get_server_host_from_arg(argument):
	count = 0
	host_name = ""
	start = "false"
	for x in range(len(argument)):
		if argument[x] == '/': 
			count = count + 1
		if count == 3:
			start = "true"
		if count == 4:
			break
		if start == "true":
			host_name = host_name + argument[x]
	#host_name = host_name.ignore("www.","",1)
	if len(host_name)!=0 and host_name[len(host_name)-1] == ']':
		return host_name[1:len(host_name)-2]
	else:
		return host_name[1:]




#*********************************************************************************************************************************************
if len(sys.argv) <= 1:
	print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
	sys.exit(2)


# Create a server socket, bind it to a port and start listening
tcp_proxyserver_welcome_socket = socket(AF_INET, SOCK_STREAM)





# Fill in start
tcp_proxyserver_welcome_socket.settimeout(5.0)
#client socket
tcp_client_socket = socket(AF_INET, SOCK_STREAM)
tcp_client_socket.settimeout(5.0)

#ports and hosts
proxyserver_port = 49152

client_host = get_client_host_from_arg(str(sys.argv))
client_port = get_client_port_from_arg(str(sys.argv)) 

#bind
tcp_client_socket.bind((client_host, client_port))
tcp_proxyserver_welcome_socket.bind(('localhost', proxyserver_port))

#start listening
tcp_proxyserver_welcome_socket.listen(1)

#connect the client socket to the proxyserver,ip:localhost, port: 49152
error = tcp_client_socket.connect_ex(('localhost', proxyserver_port))  
# Fill in end






while 1:
	#************************ Strat receiving request from the client*****************************
	print('Ready to serve...')
	tcp_proxyserver_client_connection_socket, addr = tcp_proxyserver_welcome_socket.accept()
	tcp_proxyserver_client_connection_socket.settimeout(5.0)
	print('received a connection from:', addr)
	
	#client sends the message


	# Fill in start
	message = "GET "+ "/" + get_filename_from_arg(str(sys.argv)) + " HTTP/1.0" #generate message from command line	
	tcp_client_socket.send(message.encode('utf-8',errors='ignore'))

	#proxy server receives the message
	message = tcp_proxyserver_client_connection_socket.recv(1024).decode('utf-8',errors='ignore')
    # Fill in End
	# Extract the filename from the given message
	print(message)
	print(message.split()[1])
	filename = get_filename_from_arg(str(sys.argv))#message.split()[1].partition("/")[2]
	print(filename)
	fileExist = "false"
	filename_local = filename.replace("/","_")
	filetouse = "/" + filename_local
	print(filetouse)
	
	#***********************try to read from cache for the local filename**********************************
	try:
		# Check wether the file exist in the cache
		f = open(filetouse[1:], "r")                      
		outputdata = f.readlines()                        
		fileExist = "true"
		# ProxyServer finds a cache hit and generates a response message
		tcp_proxyserver_client_connection_socket.send("HTTP/1.0 200 OK\r\n".encode('utf-8',errors='ignore'))            
		tcp_proxyserver_client_connection_socket.send("Content-Type:text/html\r\n".encode('utf-8',errors='ignore'))

        # Fill in start
		received_data_from_proxyserver = tcp_client_socket.recv(1024).decode('utf-8',errors='ignore')
		received_file = open("from_cache_"+filename_local,"w") 
		for x in range(len(outputdata)):
			tcp_proxyserver_client_connection_socket.send(outputdata[x].encode('utf-8',errors='ignore'))
			received_data_from_proxyserver = tcp_client_socket.recv(1024).decode('utf-8',errors='ignore')
			received_file.write(received_data_from_proxyserver)
        # Fill in end
			print('Read from cache')   
		received_file.close()
	# Error handling for file not found in cache

	#************************if file not in cache******************************
	except IOError:
		if fileExist == "false": 
			# Create a socket on the proxyserver
            # Fill in start
			tcp_proxyserver_server_connection_socket = socket(AF_INET, SOCK_STREAM)
            # Fill in end
			hostn = get_server_host_from_arg(str(sys.argv))        
		                                   
			# Connect to the socket to port 80
	        # Fill in start

			error = tcp_proxyserver_server_connection_socket.connect_ex((hostn, 80))

	        # Fill in end


			# Create a temporary file on this socket and ask port 80 for the file requested by the client
			fileobj = tcp_proxyserver_server_connection_socket.makefile("rwb", 0)   
				        

			temp = filename
			if filename!="":
				temp = "/"+filename
			fileobj.write(("GET " + temp  + " HTTP/1.0\r\n" + "Host: " + hostn+"\r\n\r\n").encode('utf-8',errors='ignore'))
			fileobj.flush()
			# Read the response into buffer
	        # Fill in start
			decoded_response=""
			consecutive_new_line = 0
			break_indicator = "false"
			while 1:
				response = tcp_proxyserver_server_connection_socket.recvfrom(1)
				for x in range(len(response)):
					if response[x] != None:
						decoded_response = decoded_response + response[x].decode('utf-8',errors='ignore')
						if response[x].decode('utf-8',errors='ignore') == "\n":
							consecutive_new_line = consecutive_new_line+1
						
						else:
							consecutive_new_line = 0

						if consecutive_new_line == 2:
							break_indicator = "true"
							break
				if break_indicator == "true": 
					break
	        # Fill in end



			# Create a new file in the cache for the requested file. Also send the response in the buffer to client socket and the corresponding file in the cache
			tmpFile = open("./" + filename_local,"w")  
	        # Fill in star
			tcp_proxyserver_server_connection_socket.settimeout(5.0)
			start_time = time.time()
			current_time = start_time
			while current_time-start_time<5: 
				data = tcp_proxyserver_server_connection_socket.recvfrom(1024)
				for x in range(len(data)):
					if data[x] != None:
						tmpFile.write(data[x].decode('utf-8',errors='ignore'))
				current_time = time.time()
			tmpFile.close()
			

			
			#send this temp file to the client
			tcp_proxyserver_client_connection_socket.send("HTTP/1.0 200 OK\r\n".encode('utf-8',errors='ignore'))            
			tcp_proxyserver_client_connection_socket.send("Content-Type:text/html\r\n".encode('utf-8',errors='ignore'))

			received_response_from_proxyserver = tcp_client_socket.recv(1024).decode('utf-8',errors='ignore')
			received_file = open("from_server_"+filename_local,"w") 
			f = open(filename_local, "r")                      
			data = f.readlines()
			for x in range(len(data)):
				tcp_proxyserver_client_connection_socket.send(data[x].encode('utf-8',errors='ignore'))
				received_data_from_proxyserver = tcp_client_socket.recv(1024).decode('utf-8',errors='ignore')
				received_file.write(received_data_from_proxyserver)
			received_file.close()
			f.close()

			                                           
		else:
			# HTTP response message for file not found
            # Fill in start
			tcp_proxyserver_client_connection_socket.send("HTTP/1.1 404 Not found: The requested document does not exist on this server.\r\n")            
			# Fill in end
	# Close the client and the server sockets    
	tcp_proxyserver_client_connection_socket.close() 
# Fill in start
tcp_proxyserver_server_connection_socket.close()
tcp_client_socket.close()
# Fill in end



