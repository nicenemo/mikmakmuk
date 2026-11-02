# Network locked out

If you broke the network configuration with the ansible playbooks or otherwise, the following snippets provide suggestions on how to get a connection again so that you can restore your network via playboos again.

## If you want to see all devices 

Run `ip -br link` to get a simple table of interface names:

```bash
ip -br link

```

Look for state **UP** or **UNKNOWN** next to your physical card (ignoring `lo`), then use that interface name in place of `$IFACE`.


## Details including MAC adresses

If you need full details (MAC address, state, and flags):

```bash
ip link
```


## Fixing

Here are the exact commands to assign `192.168.105.2` as fixed to **eno1**:

```bash
# 1. Clear old addresses and set 192.168.105.2
sudo ip addr flush dev eno1
sudo ip addr add 192.168.105.2/24 dev eno1
sudo ip link set eno1 up

# 2. Add default gateway (assuming 192.168.105.1)
sudo ip route add default via 192.168.105.1 dev eno1

# 3. Set temporary DNS
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf

```

### Check Connection

Verify the IP assignment by running:

```bash
ip addr show dev eno1

```
