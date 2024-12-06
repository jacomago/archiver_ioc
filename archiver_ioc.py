
import asyncio
from dataclasses import dataclass
import time
from p4p.nt import NTScalar
from p4p.server import Server
from p4p.server.thread import SharedPV

@dataclass
class WritingOptions():
    maximum: float
    init: float
    increment: float
    interval: float

@dataclass
class ExamplePV:
    shared_pv: SharedPV
    options: WritingOptions

async def start_server_pv(pvs: dict[str, ExamplePV]):
    with Server(providers=[{pv_name: pv.shared_pv for pv_name, pv in pvs.items()}]) as _server:
        await write_to_pvs(pvs)

def pv_name(base_name: str, option: WritingOptions) -> str:
    return f"{base_name}:{int(option.interval)}HZ"

def create_pvs(base_name: str, options: list[WritingOptions]) -> dict[str, ExamplePV]:
    return {pv_name(base_name, option): ExamplePV(create_pv(), option) for option in options}

def create_pv() -> SharedPV:
    return SharedPV(nt=NTScalar('d'), # scalar double
              initial=0.0)

async def write_to_pvs(pvs: dict[str, ExamplePV]):
    writeables = [write_to_pv(pv_options) for pv_options in pvs.values()]
    await asyncio.gather(*writeables)


async def write_to_pv(pv: ExamplePV):
    value = pv.options.init
    while value < pv.options.maximum:
        value += pv.options.increment
        await asyncio.sleep(1.0/pv.options.interval)
        pv.shared_pv.post(value, timestamp=time.time())

async def runner():
    print("start")
    await start_server_pv(create_pvs("ARCH", [WritingOptions(30 * 14, 1.0, 1.0, 14.0), WritingOptions(30, 1.0,1.0, 1.0)]))
    print("end")
    
asyncio.run(runner())