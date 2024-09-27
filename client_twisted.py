# client_twisted.py
from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver
from threading import Thread
import sys

HOST = '127.0.0.1'
PORT = 65432

class GameClientProtocol(LineReceiver):
    delimiter = b'\n'

    def connectionMade(self):
        print("Connected to the server.")
        print("Type 'help' to see available commands.")

    def lineReceived(self, line):
        message = line.decode().strip()
        print(message)

    def sendCommand(self, command):
        self.sendLine(command.encode())

class GameClientFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        self.protocol_instance = GameClientProtocol()
        return self.protocol_instance

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed.")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost.")
        reactor.stop()

def read_input(factory):
    while True:
        try:
            command = sys.stdin.readline()
            if not command:
                break
            command = command.strip()
            if command.lower() == "exit":
                reactor.callFromThread(reactor.stop)
                break
            factory.protocol_instance.sendCommand(command)
        except EOFError:
            break

def main():
    factory = GameClientFactory()
    reactor.connectTCP(HOST, PORT, factory)

    # เริ่ม Thread สำหรับรับอินพุตจากผู้ใช้
    input_thread = Thread(target=read_input, args=(factory,))
    input_thread.daemon = True
    input_thread.start()

    reactor.run()

if __name__ == "__main__":
    main()
