# -*- coding: utf-8 -*-
#########################################################
# SERVICE : bdaserver.py                                #
#           Python socket server serving devices that   #
#           access using BDA access                     #
#           I. Helwegen 2018                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event, Lock
from select import select
import socket, errno
import Queue
import logging
import os
from json import dumps, loads
from apps import bdauri

#########################################################

####################### GLOBALS #########################

#########################################################

###################### FUNCTIONS ########################

#########################################################

#########################################################
# Class : bdaserver                                     #
#########################################################
class bdaserver(Thread):
    def __init__(self, callback, host="", port=60004, maxclients=20, url="/Domotion", username="", password=""):
        self.callback = callback
        self.logger = logging.getLogger('Domotion.bdaserver')
        self.username = username
        self.password = password
        if not host:
            host = bdauri.find_ip_address()
        
        self.deviceurl = bdauri.BuildURL(host, url)

        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()
        self.recd = Event()
        self.recd.clear()

        # Create a TCP/IP socket
        self.timeout = 1
        self.bufsize = 1024
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(0)
        self.server_address = (host, port)
        self.logger.info('starting up on %s, port %d', self.server_address[0], self.server_address[1])
        #print 'starting up on %s port %s' % self.server_address
        self.server.bind(self.server_address)
        self.server.listen(maxclients)

        self.inputs = [ self.server ]
        self.outputs = [ ]
        self.send_buf = {}
        self.urls = {}
        self.peers = {}
        self.recddata = []
        self.unblockselect = os.pipe()

    def __del__(self):
        self.server.close()
        del self.send_buf

        del self.mutex
        del self.term
        del self.recd
        self.logger.info("finished")
        #print "finished"

    def terminate(self):
        self.term.set()

    def run(self):
        try:
            self.logger.info("running")
            #print "running"

            while (not self.term.isSet()):
                # Wait for at least one of the sockets to be ready for processing
                try:
                    self.mutex.acquire()
                    ioutputs = self.outputs
                    self.mutex.release()
                    inputready, outputready, exceptready = select(self.inputs + [self.unblockselect[0]], ioutputs, self.inputs, self.timeout)
                except:
                    self.mutex.release()
                    continue

                if not (inputready or outputready or exceptready):
                    continue

                # Handle inputs
                for sock in inputready:
                    if sock is self.server:
                        # A "readable" server socket is ready to accept a connection
                        connection = self._connect(sock)
                        if connection:
                            self.logger.info('New connection from %s',str(self.peers[connection]))
                            #print 'New connection from', self.peers[connection]
                            self._addtosendbuf(connection, bdauri.BuildURI(self.deviceurl, "", self.username, self.password))
                    elif sock is self.unblockselect[0]:
                        os.read(self.unblockselect[0], 1)
                    else:
                        data = self._receive(sock)
                        if data:
                            # A readable client socket has data
                            if self._execute(sock, data):
                                self._addtourls(sock, data)
                                #print 'received "%s" from %s' % (data, self.peers[sock])
                            #else:
                                #print "Invalid data"
                        else:
                            # Interpret empty result as closed connection
                            #print 'Closing connection from', self.peers[sock]
                            self.logger.info('Closing connection from %s',str(self.peers[sock]))
                            if sock in outputready:
                                outputready.remove(sock)
                            self._disconnect(sock)

                # Handle outputs
                for sock in outputready:
                    try:
                        next_msg = self.send_buf[sock].get_nowait()
                    except Queue.Empty:
                        self.outputs.remove(sock)
                    else:
                        #%print 'sending "%s" to %s' % (next_msg, self.peers[sock])
                        success = self._send(sock, next_msg)
                        if (not success):
                            self.outputs.remove(sock)
                            continue

                # Handle "exceptional conditions"
                for sock in exceptready:
                    #print 'Handling exceptional condition for', self.peers[sock]
                    self.logger.info('Handling exceptional condition for %s',str(self.peers[sock]))
                    self._disconnect(sock)
                    del self.send_buf[sock]

            self.logger.info("terminating")
            #print "terminating"
        except Exception, e:
            #self.logger.exception(e)
            #print e
            pass

    def _connect(self, sock):
        try:
            connection, client_address = sock.accept()
            connection.setblocking(0)
        except:
            return None, None
        self.inputs.append(connection)
        self.send_buf[connection] = Queue.Queue()
        self.peers[connection] = client_address
        return connection

    def _disconnect(self, sock):
        if sock in self.outputs:
            self.outputs.remove(sock)
        if sock in self.urls:
            self.urls.pop(sock)
        if sock in self.peers:
            self.peers.pop(sock)
        self.inputs.remove(sock)
        sock.close()
        del self.send_buf[sock]

    def _addtosendbuf(self, sock, data):
        self.mutex.acquire()
        if self.send_buf[sock]: 
            self.send_buf[sock].put(data)
            # Add output channel for response
            if sock not in self.outputs:
                self.outputs.append(sock)
        self.mutex.release()

    def _addtourls(self, sock, data):
        if bdauri.IsUri(data):
            self.urls[sock] = bdauri.GetDeviceUrl(data)

    def _receive(self, sock):
        buf = ''
        continue_recv = True
        while continue_recv:
            try:
                recd = sock.recv(self.bufsize)
                buf += recd
                continue_recv = len(recd) > 0
            except socket.error, e:
                if e.errno != errno.EWOULDBLOCK:
                    #print 'Error: %r' % e
                    return None
                continue_recv = False
        return buf

    def _send(self, sock, arg):
        try:
            sock.sendall(arg)
            return True
        except:
            return False

    def Send(self, deviceurl, tag, value):
        rtag = None
        rvalue = None
        self.recd.clear()
        try:
            sock = [k for k, v in self.urls.items() if v == bdauri.PrettyDeviceUrl(deviceurl)][0]
        except:
            sock = None

        if sock:
            self._addtosendbuf(sock, bdauri.BuildURI(self.deviceurl, bdauri.BuildData(tag, value), self.username, self.password))
            os.write(self.unblockselect[1], 'x')
        
            if self.recd.wait(5):
                self.mutex.acquire()
                recddata = self.recddata
                self.mutex.release()
                if recddata[0] == 'STORED':
                    if (recddata[1] == tag) and (recddata[2] == value):
                        rtag = tag
                        rvalue = value
                elif recddata[0] == 'VALUE':
                    if recddata[1] == tag:
                        rtag = tag
                        rvalue = recddata[2]
            else:
                self._disconnect(sock)
        return rtag, rvalue

    def _execute(self, sock, data):
        if bdauri.IsUri(data):
            if not bdauri.TestAuth(data, self.username, self.password):
                return False
            #print "New command from client"
            pdata = bdauri.ParseData(bdauri.GetData(data))
            if pdata[0]:
                tag, value = self.callback(pdata)
                if tag:
                    if pdata[1]: #set
                        self._addtosendbuf(sock, dumps(['STORED', tag, value]))
                    else: #get
                        self._addtosendbuf(sock, dumps(['VALUE', tag, value]))
                else:
                    self._addtosendbuf(sock, dumps(["ERROR", pdata[0], "NULL"]))
        else:
            #print "Response"
            self.mutex.acquire()
            try:
                self.recddata = loads(data)
            except:
                self.recddata = None
            self.mutex.release()
            self.recd.set()

        return True
