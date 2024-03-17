import sys

import anyio
import dagger
from dagger import dag


async def main():
    # check for Docker Hub registry credentials in host environment
    # for var in ["DOCKERHUB_USERNAME", "DOCKERHUB_PASSWORD"]:
    #     if var not in os.environ:
    #         msg = f"{var} environment variable must be set"
    #         raise OSError(msg)

    # initialize Dagger client
    cfg = dagger.Config(log_output=sys.stderr)
    async with (dagger.connection(cfg)):
        # username = os.environ["DOCKERHUB_USERNAME"]
        # set registry password as secret for Dagger pipeline
        # password = dag.set_secret("password", os.environ["DOCKERHUB_PASSWORD"])

        # create a cache volume for Maven downloads
        maven_cache = dag.cache_volume("maven-cache")

        # get reference to source code directory
        source = dag.host().directory("grpc-kafka-stream-video-server", exclude=["ci", ".venv"])


        # create database service container for application unit tests
        mariadb = (
            dag.container()
            .from_("mariadb:10.11.2")
            .with_env_variable("MARIADB_USER", "petclinic")
            .with_env_variable("MARIADB_PASSWORD", "petclinic")
            .with_env_variable("MARIADB_DATABASE", "petclinic")
            .with_env_variable("MARIADB_ROOT_PASSWORD", "root")
            .with_exposed_port(3306)
            .as_service()
        )

        # use maven:3.9 container
        # mount cache and source code volumes
        # set working directory
        app = (
            dag.container()
            .from_("maven:3.9-eclipse-temurin-20")
            .with_mounted_cache("/root/.m2", maven_cache)
            .with_mounted_directory("/app", source)
            .with_workdir("/app")
        )

        # define binding between
        # application and service containers
        # define JDBC URL for tests
        # test, build and package application as JAR
        build = (
            app.with_service_binding("db", mariadb)
            .with_env_variable(
                "MYSQL_URL",
                "jdbc:mysql://petclinic:petclinic@db/petclinic",
            )
            .with_exec(["mvn", "-Dspring.profiles.active=mysql", "clean", "package"])
        )

        # use eclipse alpine container as base
        # copy JAR files from builder
        # set entrypoint and database profile
        deploy = (
            dag.container()
            .from_("eclipse-temurin:20-alpine")
            .with_directory("/app", build.directory("./target"))
            .with_entrypoint(
                [
                    "java",
                    "-jar",
                    "-Dspring.profiles.active=mysql",
                    "/app/grpc-kafka-stream-video-server-0.0.1-SNAPSHOT.jar",
                ]
            )
        )

        # await deploy.directory

        username = 'pepito'
        password = dag.set_secret("password", 'password')
        # publish image to registry
        address = await deploy.with_registry_auth(
            "docker.io", username, password
        )
        # ).publish(f"{username}/myapp")

        # username = 'pepito'
        # password = dag.set_secret("password", 'password')
        # # publish image to registry
        # address = await deploy.with_registry_auth(
        #     "docker.io", username, password
        # ).publish(f"{username}/myapp")

        # print image address
        # print(f"Image published at: {address}")


anyio.run(main)
