import uselect
import usocket

# WiFi networks in priority order: the first one that is visible wins.
# secrets.py can define WIFI_NETWORKS = [(ssid, password), ...] or the older
# single WIFI_SSID / WIFI_PASS pair.
try:
    from ventilastation.secrets import WIFI_NETWORKS
except ImportError:
    try:
        from ventilastation.secrets import WIFI_SSID, WIFI_PASS
        WIFI_NETWORKS = [(WIFI_SSID, WIFI_PASS)]
    except ImportError:
        WIFI_NETWORKS = [('ventilastation', 'plagazombie2')]

WIFI_TIMEOUT_MS = 15000  # per network, so a missing network never blocks boot

def _connect_wifi(sta_if):
    # Right after active(True) the first scan often comes back empty: retry a
    # few times, and if it is still empty just try every network in order.
    visible = None
    for _ in range(3):
        try:
            found = sta_if.scan()
        except Exception:
            found = []
        if found:
            visible = set(net[0].decode() for net in found)
            break
        utime.sleep_ms(500)
    for ssid, password in WIFI_NETWORKS:
        if visible is not None and ssid not in visible:
            print("wifi: %s not visible" % ssid)
            continue
        print('connecting to %s' % ssid, end="")
        sta_if.connect(ssid, password)
        start = utime.ticks_ms()
        while not sta_if.isconnected():
            if utime.ticks_diff(utime.ticks_ms(), start) > WIFI_TIMEOUT_MS:
                print(" timeout")
                sta_if.disconnect()
                break
            print(".", end="")
            utime.sleep_ms(333)
        else:
            print()
            return True
    return False

try:
    import network
    import utime

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if sta_if.isconnected() or _connect_wifi(sta_if):
        print('network config:', sta_if.ifconfig())
    else:
        print('wifi: no known network found, continuing without it')
    try:
        network.telnet.start()
    except Exception:
        pass
except Exception as e:
    print("no need to set up wifi", e)

UDP_THIS = "0.0.0.0", 5005
this_addr = usocket.getaddrinfo(*UDP_THIS)[0][-1]

sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
sock.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
sock.bind(this_addr)
sock.listen(10)
sock.setblocking(0)
print("listening on 5005")

poller = uselect.poll()
poller.register(sock, uselect.POLLIN)
conn = None

def receive(bufsize):
    global conn
    retval = None
    for obj, event, *more in poller.ipoll(0, 0):
        if obj is sock:
            if conn:
                conn.close()
                poller.unregister(conn)
            conn, _ = sock.accept()
            conn.setblocking(0)
            poller.register(conn, uselect.POLLIN)
        else:
            try:
                b = obj.read(1)
            except OSError:
                b = None
            if b:
                retval = b
            else:
                obj.close()
                poller.unregister(obj)
                conn = None
    return retval

def send(line, data=b""):
    #print("sending:", line, end="")
    global conn
    if conn:
        try:
            # The socket is non-blocking for input polling, but a single
            # non-blocking write() can truncate a large payload (e.g. an
            # imagestrip), desyncing the receiver's framing. Block here so the
            # whole frame is sent, then restore non-blocking for the poller.
            conn.setblocking(True)
            conn.write(line + b"\n" + data)
            conn.setblocking(False)
        except OSError:
            conn.close()
            poller.unregister(conn)
            conn = None
            # conn, _ = sock.accept()
            # conn.setblocking(0)
            # poller.register(conn, uselect.POLLIN)
