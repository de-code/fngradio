import asyncio
import logging
import pytest


@pytest.fixture(scope='session', autouse=True)
def setup_logging():
    logging.basicConfig(level='INFO')
    for name in ['tests', 'fngradio']:
        logging.getLogger(name).setLevel('DEBUG')


@pytest.fixture(autouse=True, scope='session')
def ensure_thread_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield
