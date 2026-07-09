# Copyright 2025 Flower Labs GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Flower command line interface."""

import inspect
from typing import Annotated, Any, Callable, Optional

import click
import typer
import typer.core
from typer.main import get_command

from flwr.common.version import package_version

from .build import build
from .install import install
from .log import log
from .login import login
from .ls import ls
from .new import new
from .run import run
from .stop import stop


def _patch_make_metavar() -> None:
    """Patch Typer/Click metavar handling across Click versions."""
    if "ctx" not in inspect.signature(click.core.Parameter.make_metavar).parameters:
        return

    def _wrap_click_make_metavar(method: Callable[..., str]) -> Callable[..., str]:
        def _patched(self: Any, ctx: Optional[click.Context] = None) -> str:
            if ctx is None:
                ctx = click.Context(click.Command(name=""))
            return method(self, ctx)

        return _patched

    def _wrap_typer_make_metavar(method: Callable[..., str]) -> Callable[..., str]:
        def _patched(  # pylint: disable=unused-argument
            self: Any, ctx: Optional[click.Context] = None
        ) -> str:
            return method(self)

        return _patched

    make_metavar = "make_metavar"
    setattr(
        click.core.Parameter,
        make_metavar,
        _wrap_click_make_metavar(click.core.Parameter.make_metavar),
    )
    setattr(
        click.core.Option,
        make_metavar,
        _wrap_click_make_metavar(click.core.Option.make_metavar),
    )
    setattr(
        click.core.Argument,
        make_metavar,
        _wrap_click_make_metavar(click.core.Argument.make_metavar),
    )
    setattr(
        typer.core.TyperOption,
        make_metavar,
        _wrap_typer_make_metavar(typer.core.TyperOption.make_metavar),
    )
    setattr(
        typer.core.TyperArgument,
        make_metavar,
        _wrap_typer_make_metavar(typer.core.TyperArgument.make_metavar),
    )


_patch_make_metavar()

app = typer.Typer(
    help=typer.style(
        "flwr is the Flower command line interface.",
        fg=typer.colors.BRIGHT_YELLOW,
        bold=True,
    ),
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

app.command()(new)
app.command()(run)
app.command()(build)
app.command()(install)
app.command()(log)
app.command()(ls)
app.command()(stop)
app.command()(login)


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.secho(f"Flower version: {package_version}", fg="blue")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def version_callback(
    _: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = None,
) -> None:
    """Flower command line interface."""


typer_click_object = get_command(app)


if __name__ == "__main__":
    app()
