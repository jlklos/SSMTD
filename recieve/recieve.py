import argparse
import sys
import socket


def main():
    parts = listening()
    remake(parts)


# receive program
def listening():
    parts = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # setting up the socket for the listener
        print 'Socket created'
        s.bind(('0.0.0.0', args.port))
        # bind to the port and listen for a computer to connect
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    # start listening on socket port
    s.listen(5)
    print 'Socket now listening'

    conn, addr = s.accept()
    # get address of machine connecting to the HOST
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    l = conn.recv(args.chunk)
    # first packet recieved & loop to get the rest
    while l:
        print "Receiving messages"
        parts.append(l)
        l = conn.recv(args.chunk)
        if not l: break
        # recieve chunks and save them in parts

    print "Done Receiving chunks"
    conn.close()
    # close connection with client

    s.close()
    return parts


# taking parts that were sent and reordering them to create a file
def remake(parts):
    fp = open(args.fileToRec, 'wb')
    # opening the file to receive
    for fileParts in range(len(parts)):
        fp.writelines(parts[fileParts])
        # order and write the parts in the correct order to the file
    fp.close()
    print "Finish remake"
    f = open(args.fileToRec, 'r')
    # open the file so it can read from it
    file_contents = f.read()
    # printing the file
    print(file_contents)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A quick and dirty Mutli-Path TCP using remort ports')
    parser.add_argument('fileToRec', metavar='F', type=str, help='The file to receive from sender')
    parser.add_argument('-b', dest='chunk', type=int, default=4096, help='The size of the blocks that have been split')
    parser.add_argument('-p', dest='port', type=int, default=5185, help='Change the default communication port')
    args = parser.parse_args()
    main()
