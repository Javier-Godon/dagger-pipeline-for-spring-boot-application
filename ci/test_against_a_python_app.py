import sys

import anyio
import dagger
from dagger import dag


async def test():
    cfg = dagger.Config(log_output=sys.stderr)
    async with dagger.Connection(cfg):
        # get reference to the local project
        src = dag.host().directory(".")

        python = (
            dag.container().from_("python:3.12-slim-bookworm")
            # mount cloned repository into image
            .with_directory("/src", src)
            # set current working directory for next commands
            .with_workdir("/src")
            # install test dependencies
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            # run tests
            .with_exec(["pytest", "tests"])
        )

        # execute
        await python.sync()

    print("Tests succeeded!")


anyio.run(test)
