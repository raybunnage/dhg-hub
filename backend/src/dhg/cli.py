import click
from flask.cli import with_appcontext, AppGroup
import pytest
import os
from dotenv import load_dotenv

test_cli = AppGroup("test", help="Testing commands.")


def load_env_file(env_name):
    """Load the appropriate .env file."""
    if env_name == "test":
        load_dotenv(".env.test", override=True)
    else:
        load_dotenv(override=True)


def register_commands(app):
    """Register Flask CLI commands."""

    @test_cli.command("run")
    @click.option(
        "--coverage/--no-coverage", default=False, help="Run tests with coverage."
    )
    @click.option(
        "--env", default="test", help="Environment to run tests in (test, dev)"
    )
    def test(coverage, env):
        """Run the tests."""
        # Load appropriate environment variables
        load_env_file(env)

        # Ensure PYTHONPATH includes the project root
        os.environ["PYTHONPATH"] = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../")
        )

        click.echo(f"Running tests in {env} environment...")
        click.echo(f"PYTHONPATH: {os.environ['PYTHONPATH']}")

        # Build pytest arguments
        args = ["backend/tests", "-v"]

        if coverage:
            args.extend(["--cov=backend/src", "--cov-report=term-missing"])

        # Clear caches before running tests
        click.echo("Clearing caches...")
        os.system('find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null')
        os.system('find . -type f -name "*.pyc" -delete 2>/dev/null')
        os.system("rm -rf .pytest_cache 2>/dev/null")

        # Run the tests
        click.echo("Running tests...")
        result = pytest.main(args)

        if result == 0:
            click.echo("All tests passed! 🎉")
        else:
            click.echo("Tests failed! 😢")
            exit(1)

    # Register the test command group
    app.cli.add_command(test_cli)
