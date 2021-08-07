from threading import Thread, Event
from select import select
import socket
import queue
import logging
from json import dumps, loads
from struct import pack, unpack
from engine.localaccess import localaccess
from .basicwebaccess import basicwebaccess
from utilities.memorylog import memorylog
from engine.scripts import scripts

#########################################################
# Class : webserveraccess                               #
#########################################################
class webserveraccess(Thread):
    _errors = {"No error": 0, "Invalid function": 1, "Invalid number of input arguments": 2, "Invalid input argument type": 3,
               "Timout": 4}
    def __init__(self, commandqueue, localaccess, killer, memorylog, scripts, port=10000, maxclients=5):
        self.commandqueue = commandqueue
        self.localaccess = localaccess
        self.killer = killer
        self.memorylog = memorylog
        self.scripts = scripts
        self.logger = logging.getLogger('Domotion.webserveraccess')
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()

        # Create a TCP/IP socket
        self.timeout = 1
        self.bufsize = 1024
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(0)
        self.server_address = ('localhost', port)
        self.logger.info('starting up on %s, port %d', self.server_address[0], self.server_address[1])
        self.server.bind(self.server_address)
        self.server.listen(maxclients)

        self.inputs = [ self.server ]
        self.outputs = [ ]
        self.return_args = {}
        self.memoryloginstances = {}

    def __del__(self):
        self.server.close()
        del self.return_args
        del self.term
        self.logger.info("finished")

    def terminate(self):
        self.term.set()

    def run(self):
        try:
            self.logger.info("running")

            while (not self.term.isSet()):
                # Wait for at least one of the sockets to be ready for processing
                try:
                    inputready, outputready, exceptready = select(self.inputs, self.outputs, self.inputs, self.timeout)
                except:
                    continue

                if not (inputready or outputready or exceptready):
                    continue

                # Handle inputs
                for sock in inputready:

                    if sock is self.server:
                        # A "readable" server socket is ready to accept a connection
                        try:
                            connection, client_address = sock.accept()
                            connection.setblocking(0)
                            self.send(connection,dumps('Domotion'))
                        except:
                            continue
                        self.logger.info('New connection from: %s:%d', client_address[0], client_address[1])
                        self.inputs.append(connection)
                        self.return_args[connection] = queue.Queue()
                        self.memoryloginstances[connection] = self.memorylog.addinstance()

                    else:
                        data = self.receive(sock)
                        if data:
                            # A readable client socket has data
                            #print 'received "%s" from %s' % (data, sock.getpeername())
                            argout = self.execute(data, sock)
                            if argout:
                                self.return_args[sock].put(argout)
                                # Add output channel for response
                                if sock not in self.outputs:
                                    self.outputs.append(sock)
                        else:
                            # Interpret empty result as closed connection
                            self.logger.info('Closing connection from: %s:%d', client_address[0], client_address[1])
                            if sock in self.outputs:
                                self.outputs.remove(sock)
                            if sock in outputready:
                                outputready.remove(sock)
                            self.inputs.remove(sock)
                            sock.close()
                            del self.return_args[sock]
                            self.memorylog.removeinstance(self.memoryloginstances[sock])
                            del self.memoryloginstances[sock]

                # Handle outputs
                for sock in outputready:
                    try:
                        next_msg = self.return_args[sock].get_nowait()
                    except queue.Empty:
                        self.outputs.remove(sock)
                    else:
                        #print 'sending "%s" to %s' % (next_msg, sock.getpeername())
                        success = self.send(sock, next_msg)
                        if (not success):
                            self.outputs.remove(sock)
                            continue

                # Handle "exceptional conditions"
                for sock in exceptready:
                    client_address = sock.getpeername()
                    self.logger.error('Handling exceptional condition for: %s:%d', client_address[0], client_address[1])
                    # Stop listening for input on the connection
                    self.inputs.remove(sock)
                    if sock in self.outputs:
                        self.outputs.remove(sock)
                    sock.close()

                    # Remove message queue
                    del self.return_args[sock]
                    self.memorylog.removeinstance(self.memoryloginstances[sock])
                    del self.memoryloginstances[sock]

            self.logger.info("terminating")
        except Exception as e:
            self.logger.exception(e)

    def receive(self, sock):
        try:
            raw_msglen = self.receivevalue(sock, 4)
            if not raw_msglen:
                return None
            msglen = unpack('>I', raw_msglen)[0]
            # Read the message data
            return self.receivevalue(sock, msglen).decode("utf-8")
        except:
            return None

    def receivevalue(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            if (n- len(data) > self.bufsize):
                packet = sock.recv(self.bufsize)
            else:
                packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def send(self, sock, arg):
        try:
            msg = pack('>I', len(arg)) + bytes(arg,"utf-8")
            sock.sendall(msg)
            return True
        except:
            self.logger.error("Cannot encode input to be sent")
            return False

    def execute(self, arguments, sock):
        try:
            function, argin = loads(arguments)
        except:
            self.logger.error("Cannot decode received input")
            return None

        status = "No error"
        argout = ()

        if (function == 1): # "SetStatusBusy" localaccess.SetStatusBusy
            self.localaccess.SetStatusBusy()
        elif (function == 2): # "Callback" commanqueue.callback
            if (len(argin) < 1):
                status = "Invalid number of input arguments"
            else:
                if (type(argin[0]) != str) and (type(argin[0]) != str):
                    status = "Invalid input argument type"
                else:
                    self.commandqueue.callback(argin[0])
        elif (function == 3): # "BWAset" basicwebaccess.set
            if (len(argin) < 2):
                status = "Invalid number of input arguments"
            else:
                if (type(argin[0]) != str) and (type(argin[0]) != str):
                    status = "Invalid input argument type"
                else:
                    argout = basicwebaccess(self.commandqueue, self.localaccess, self.memorylog).set(argin[0], argin[1])
        elif (function == 4): # "BWAget" basicwebaccess().get
            if (len(argin) < 1):
                status = "Invalid number of input arguments"
            else:
                if (type(argin[0]) != str) and (type(argin[0]) != str):
                    status = "Invalid input argument type"
                else:
                    argout = basicwebaccess(self.commandqueue, self.localaccess, self.memorylog).get(argin[0])
        elif (function == 5): # "Reboot" appkiller.reboot
            self.killer.reboot()
            pass
        elif (function == 6): # "Shutdown" appkiller.shutdown
            self.killer.shutdown()
            pass
        elif (function == 7): # "RestartApp" appkiller.restart_app
            self.killer.restart_app()
            pass
        elif (function == 8): # "RestartAll" appkiller.restart_app
            self.killer.restart_all()
            pass
        elif (function == 9): # "LogReadLines" memorylog.readlines
            argout = self.memorylog.readlines(self.memoryloginstances[sock])
            if (argout == []):
                argout = [""]
        elif (function == 10): # "LogGetLog" memorylog.getvalue
            argout = self.memorylog.getvalue(self.memoryloginstances[sock])
            if (argout == []):
                argout = [""]
        elif (function == 11): # "PutValue" commandqueue.put_id
            if (len(argin) < 2):
                status = "Invalid number of input arguments"
            else:
                if (type(argin[0]) != int):
                    status = "Invalid input argument type"
                else:
                    if (len(argin) >= 3):
                        #commandqueue.put_id("None", int(key), ivalue, (tableid == "controls"))
                        self.commandqueue.put_id("None", argin[0], argin[1], argin[2])
                    else:
                        self.commandqueue.put_id("None", argin[0], argin[1])
        elif (function == 12): # "GetActuatorValues" localaccess.GetActuatorValues
            argout = self.localaccess.GetActuatorValues()
        elif (function == 13): # "GetSensorValues" localaccess.GetSensorValues
            argout = self.localaccess.GetSensorValues()
        elif (function == 14): # "GetTimerValues" localaccess.GetTimerValues
            argout = self.localaccess.GetTimerValues()
        elif (function == 15): # "GetSunRiseSetMod" localaccess.GetSunRiseSetMod
            argout = self.localaccess.GetSunRiseSetMod()
        elif (function == 16): # "SetTimer" localaccess.SetTimer
            if (len(argin) < 2):
                status = "Invalid number of input arguments"
            else:
                if (type(argin[0]) != int) or (type(argin[1]) != int):
                    status = "Invalid input argument type"
                else:
                    argout = self.localaccess.SetTimer(argin[0], argin[1])
        elif (function == 17): # "GetToday" localaccess.GetToday
            argout = self.localaccess.GetToday()
        elif (function == 18): # "BWAget" basicwebaccess().getall
            if (len(argin) < 1):
                status = "Invalid number of input arguments"
            else:
                if (type(argin[0]) != str) and (type(argin[0]) != str):
                    status = "Invalid input argument type"
                else:
                    argout = basicwebaccess(self.commandqueue, self.localaccess, self.memorylog).getall(argin[0])
        elif (function == 19): # "BWAget" basicwebaccess().getinfo
            if (len(argin) < 1):
                status = "Invalid number of input arguments"
            else:
                if (type(argin[0]) != str) and (type(argin[0]) != str):
                    status = "Invalid input argument type"
                else:
                    argout = basicwebaccess(self.commandqueue, self.localaccess, self.memorylog).getinfo(argin[0])
        elif (function == 20): #ScriptsList scripts.list()
            argout = self.scripts.list()
            if (argout == []):
                argout = [""]
        elif (function == 21): #GetScript scripts.get()
            if (len(argin) < 1):
                status = "Invalid number of input arguments"
            else:
                if (type(argin[0]) != str):
                    status = "Invalid input argument type"
                else:
                    argout = self.scripts.get(argin[0])
        elif (function == 22): #SetScript scripts.set()
            if (len(argin) < 1):
                status = "Invalid number of input arguments"
            else:
                if (type(argin[0]) != str) and (type(argin[1]) != str):
                    status = "Invalid input argument type"
                else:
                    argout = self.scripts.set(argin[0], argin[1])
        else: # Error
            status = "Invalid function"
            function = 0

        if (status != "No error"):
            self.logger.error(status)

        return dumps((self._errors[status], function, argout))
