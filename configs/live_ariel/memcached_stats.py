#!/server/pylons1.0/bin/python
import sys
import pylibmc

client = pylibmc.Client(sys.argv[1].split(';'), binary=True)
client.behaviors = {"tcp_nodelay": True, "ketama": True}
print client.get_stats()

