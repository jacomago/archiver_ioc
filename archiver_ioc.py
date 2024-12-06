
import asyncio
import time
from p4p.nt import NTScalar
from p4p.server import Server
from p4p.server.thread import SharedPV

def start_server_pv(pv_name: str, pv: SharedPV):
    with Server(providers=[{
        pv_name:pv, # PV name only appears here
    }]) as _server:
        write_to_pv(pv)

def create_pv() -> SharedPV:
    return SharedPV(nt=NTScalar('d'), # scalar double
              initial=0.0)

INTERVAL = 1.0/14.0

def write_to_pv(pv: SharedPV):
    value = 0.0
    while value < 50:
        value += 1.0
        time.sleep(INTERVAL)
        pv.post(value, timestamp=time.time())

async def runner():
    print("start")
    start_server_pv("test_pv", create_pv())
    print("end")
    
asyncio.run(runner())