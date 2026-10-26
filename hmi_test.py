"""
hmi_test.py — Modbus test client for the OT Security Lab.

What it does: connects to the OpenPLC controller, READS the tank level,
WRITES a new level (5), then READS the pump coil. No password is ever
asked for — that is the whole point of the demo.

Run it twice:
  1. From the TRUSTED computer (192.168.10.10): it should work.
  2. From the OTHER computer (192.168.10.20): before the firewall rule it
     also works (the problem); after the rule it prints BLOCKED (the fix).

This script auto-detects your pymodbus version, so the common
"unexpected keyword argument 'slave'/'device_id'" error cannot happen.

Use only inside your own lab VMs.
"""

from pymodbus.client import ModbusTcpClient

PLC_IP = "192.168.20.10"   # the OpenPLC machine
PLC_PORT = 502             # Modbus TCP always uses port 502
UNIT_ID = 1                # the Modbus "slave"/"device" id OpenPLC answers on


def unit_kwarg():
    """Different pymodbus versions name the device id differently.
    This finds the right one (device_id / slave / unit) for your version."""
    import inspect
    params = inspect.signature(ModbusTcpClient.read_holding_registers).parameters
    for name in ("device_id", "slave", "unit"):
        if name in params:
            return {name: UNIT_ID}
    return {}   # very old versions take no id at all


def main():
    kw = unit_kwarg()
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

    # If the firewall is blocking us, the connection fails here.
    if not client.connect():
        print("BLOCKED: cannot connect to the PLC at %s:%s" % (PLC_IP, PLC_PORT))
        print("(If this is the untrusted computer AFTER the firewall rule, that is the point.)")
        raise SystemExit(1)

    print("Connected to the PLC. No password was asked for.\n")

    # 1. READ the tank level (holding register 0)
    rr = client.read_holding_registers(address=0, count=1, **kw)
    if rr.isError():
        print("Read error:", rr)
    else:
        print("Tank level now:", rr.registers[0])

    # 2. WRITE a new tank level (set it to 5). This is the dangerous part:
    #    an intruder can make the PLC think the tank is nearly empty.
    wr = client.write_register(address=0, value=5, **kw)
    print("Write result:", "OK" if not wr.isError() else wr)

    # 3. READ the pump coil (coil 0). Because level 5 < 20, the program
    #    should now have switched the pump ON.
    rc = client.read_coils(address=0, count=1, **kw)
    if rc.isError():
        print("Coil read error:", rc)
    else:
        print("Pump is ON?", rc.bits[0])

    client.close()
    print("\nDone. A real HMI would need no password either — that is the vulnerability.")


if __name__ == "__main__":
    main()
