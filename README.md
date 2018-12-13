# Stream Splitting Demo

Our system relies on intermediate bouncer hosts to break up the stream between multiple routes.

![Arch](images/arch.png)

Ideally this would be implimented as a kernel module and would be effectively transparent to the user.  Furthermore it woiuld be more ideal if this were implmented by abusing TCP TTL and packet size, which would allow for disprate routing paths without the need for explicit intermediate bouncer hosts.

## Usage

### `receive.py`

The receiver should be set up on whatever host you would like to receive.

### `bouncer.py`

The bouncer should be set up on hosts in geographicly disprate areas to force divergent paths.  The `hosts` list in `bouncer.py` should be populated with the final endpoint and/or other bouncers. Running the bouncer is as follows `python bouncer.py <port>`.

### `sender.py`

The sender should be ran on the machine with the data you wish to send.  The `remoteHosts` list be populated with the IP addresses of the remote bouncer hosts.  To run the sender, `python sender.py <file>`.  Optinally the size of the chuncks the data will be broken into can be set using `-b`.