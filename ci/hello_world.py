import sys

import anyio
import dagger
from dagger import dag


async def test():
    cfg = dagger.Config(log_output=sys.stderr)

    async with dagger.connection(cfg):
        python = (
            dag.container()
            # pull container
            .from_("python:3.12-slim-bookworm")
            # get Python version
            .with_exec(["python", "-V"])
        )

        # execute
        version = await python.stdout()

    print(f"Hello from Dagger and {version}")


anyio.run(test)
