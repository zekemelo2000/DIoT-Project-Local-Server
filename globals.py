# globals.py
from typing import Optional

from zeroconf.asyncio import AsyncZeroconf

# This file holds shared variables so other files don't have to import each other.
mdns_bus: Optional[AsyncZeroconf] = None