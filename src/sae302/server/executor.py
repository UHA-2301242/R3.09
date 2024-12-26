from __future__ import annotations

import abc
import contextlib
import functools
import logging
import os
import shutil
import subprocess
import tempfile
import typing

_log = logging.getLogger(__name__)


class RunReturn:
    code: int
    output: str
    additional_message: str | None

    def __init__(self, code: int, output: str, additional_message: str | None = None):
        self.code = code
        self.output = output
        self.additional_message = additional_message


class BaseExecutor(metaclass=abc.ABCMeta):
    """This base class is used to declare supported job types and how they should execute.
    All child classes must implement the `execute` method, which is used to execute a given script.

    This is not to be used directly.

    Parameters
    ----------
    friendly_name : str
        The friendly name of the executor.
        This will be returned to the user by the server.

    supported_suffixes : list[str]
        List of file suffixes that are supported to be processed by this executor.
        This is used when a file's name is read and we wish to determine which executor supports
        it.

    attempt_executables : list[str]
        A list of command to try to lookup executables for.
        The first executable that is found will be used for further run.
        In case no executables is found, this list will be empty, and thus mean that this executor
        cannot be used.
    """

    friendly_name: typing.ClassVar[str]
    supported_suffixes: typing.ClassVar[list[str]]

    @staticmethod
    def find_executable(commands: str | list[str]) -> str | None:
        """Attempt to find an executable from given commands.
        This method will check if ANY of the commands are available. If one is found, its path is
        returned. It will pass even if one command misses, but another one is found.
        None will be returned if no commands we able to be found in the user's path.

        Parameters
        ----------
        commands : list[str]
            A list of commands to try to find.

        Returns
        -------
        str | None
            The first executable that is found, or None if no executable were found.
        """
        commands = [commands] if isinstance(commands, str) else commands

        for try_exe in commands:
            if executable_path := shutil.which(try_exe):
                return executable_path
        return None

    @staticmethod
    @contextlib.contextmanager
    def content_to_temporary_file(content: str, suffix: str):
        file = tempfile.NamedTemporaryFile(
            suffix=f".{suffix}", delete=False, delete_on_close=False
        )
        _log.debug("Created temporary file at: %s", file.name)
        file.write(content.encode())
        file.close()
        try:
            yield file
        finally:
            os.unlink(file.name)

    @property
    @abc.abstractmethod
    def is_available(self) -> bool:
        """This property must be implemented by child classes.
        Its purpose is to indicate if the executor can be ran. (Dose he have the necessary
        tooling?)
        This method will be called by the ExecutorFactory upon the class's creation.

        Returns
        -------
        bool :
            True if can be ran. Otherwise False.
        """
        raise NotImplementedError("Not implemented")

    @abc.abstractmethod
    def execute(self, file_name: str, file_content: str) -> RunReturn:
        """This method must be implemented by child classes.
        It is used to execute a given script.

        Parameters
        ----------
        file_content : str
            The content of the script to launch. It is up for the child class to write into a
            temporary file for execution/compilation.
            Shall they do so, they should preferably delete the file after execution, or use the
            temporary folder.

        Returns
        -------
        RunReturn
            Code and output of the execution result.

        Raises
        ------
        NotImplementedError :
            Raised when the child class did NOT implement this method.
        Exception :
            Any other exception raised by the child class.
        """
        raise NotImplementedError("Not implemented")


class PythonExecutor(BaseExecutor):
    """Executor for Python code"""

    friendly_name = "Python"
    supported_suffixes = ["py", "pyc", "pyo"]

    @property
    def is_available(self) -> bool:
        return bool(self.find_executable(["python", "python3", "py"]))

    def execute(self, file_name: str, file_content: str) -> RunReturn:
        exec = self.find_executable(["python", "python3", "py"])
        assert exec

        with self.content_to_temporary_file(file_content, "py") as file:
            args = f"{exec} -O {file.name}"
            proc = subprocess.Popen(
                args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )

            output, _ = proc.communicate()
            code = proc.returncode

        return RunReturn(code=code, output=output.decode())


class JavaExecutor(BaseExecutor):
    """Executor for Java code"""

    friendly_name = "Java"
    supported_suffixes = ["java"]

    @property
    def is_available(self) -> bool:
        return bool(self.find_executable("java"))

    def execute(self, file_name: str, file_content: str) -> RunReturn:
        exec = self.find_executable("java")
        assert exec

        with self.content_to_temporary_file(file_content, "java") as file:
            args = f"{exec} {file.name}"
            proc = subprocess.Popen(
                args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            output, _ = proc.communicate()
            code = proc.returncode

        return RunReturn(code=code, output=output.decode())


class CppExecutor(BaseExecutor):
    """Executor for C++ code"""

    friendly_name = "C++"
    supported_suffixes = ["cpp", "hpp"]

    @property
    def is_available(self) -> bool:
        return bool(self.find_executable("g++"))

    def execute(self, file_name: str, file_content: str) -> RunReturn:
        exec = self.find_executable("gcc")
        assert exec

        with self.content_to_temporary_file(file_content, "c") as file:
            output_file = f"{file.name}.out"
            compilation = subprocess.Popen(
                f"g++ -o {output_file} {file.name}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            compilation.wait()

            if compilation.returncode != 0:
                output, _ = compilation.communicate()
                return RunReturn(code=compilation.returncode, output=output.decode())

            proc = subprocess.Popen(
                f"{output_file}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            output, _ = proc.communicate()
            code = proc.returncode

        return RunReturn(code=code, output=output.decode())


class CExecutor(BaseExecutor):
    """Executor for C code"""

    friendly_name = "C"
    supported_suffixes = ["c", "h"]

    @property
    def is_available(self) -> bool:
        return bool(self.find_executable("gcc"))

    def execute(self, file_name: str, file_content: str) -> RunReturn:
        exec = self.find_executable("gcc")
        assert exec

        with self.content_to_temporary_file(file_content, "c") as file:
            output_file = f"{file.name}.out"
            compilation = subprocess.Popen(
                f"gcc -o {output_file} {file.name}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            compilation.wait()

            if compilation.returncode != 0:
                output, _ = compilation.communicate()
                return RunReturn(code=compilation.returncode, output=output.decode())

            proc = subprocess.Popen(
                f"{output_file}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            output, _ = proc.communicate()
            code = proc.returncode

        return RunReturn(code=code, output=output.decode())


class ExecutorFactory:
    """This class takes care of picking the right executor to use.
    It's also used to determine which executor are available and which aren't.

    As such, this class is the main interaction the user have with.
    """

    @functools.cached_property
    def all_executors(self) -> typing.Generator[type[BaseExecutor], None, None]:
        """Returns all executors that have been created and can be used.
        This method does NOT check whether they can be used or not.
        This simply return a list of all subclasses of :py:class:`BaseExecutor`.

        Yields
        ------
        typing.Generator[type[BaseExecutor], None, None]
            The list of executors
        """
        yield from BaseExecutor.__subclasses__()

    @functools.cached_property
    def available_executors(self) -> typing.Iterable[type[BaseExecutor]]:
        """Return a list of available executors.

        Returns
        -------
        typing.Iterable[type[BaseExecutor]]
            The list of available executors.
        """
        return [
            executor[0]
            for executor in self._determine_available_executors().items()
            if executor[1]
        ]

    def all_executors_availability(self) -> dict[type[BaseExecutor], bool]:
        """Return a list of all available executors.
        The boolean indicates whether or not the executor is available.

        Returns
        -------
        dict[type[BaseExecutor], bool]
            The list of executor, and their availability as a boolean.
        """
        return self._determine_available_executors()

    def _determine_available_executors(self) -> dict[type[BaseExecutor], bool]:
        availability: dict[type[BaseExecutor], bool] = {
            executor: bool(executor.is_available) for executor in self.all_executors
        }
        return availability

    def find_executor(
        self,
        *,
        friendly_name: str | None = None,
        supported_suffixes: list[str] | None = None,
    ) -> type[BaseExecutor] | None:
        """Attempt to find an executor based on its friendly name and supported suffixes.

        Parameters
        ----------
        friendly_name : str | None, optional
            Friendly name to match with, if given, by default None
        supported_suffixes : list[str] | None, optional
            Suffixes to match with, if given, by default None

        Returns
        -------
        type[BaseExecutor] | None
            The found executor that must be used to execute the given script.
            Returns none if no executor was found

        Raises
        ------
        ValueError
            Raised when either ``friendly_name`` or ``supported_suffixes`` arguments are not given.
        """
        if not friendly_name and (not supported_suffixes):
            raise RuntimeError("No arguments are given, yet at least one is required.")

        for executor in self.available_executors:
            if executor.friendly_name == friendly_name:
                return executor
            if supported_suffixes and any(
                suffix in executor.supported_suffixes for suffix in supported_suffixes
            ):
                return executor
