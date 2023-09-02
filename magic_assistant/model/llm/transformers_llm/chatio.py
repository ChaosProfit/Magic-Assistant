import abc
import re

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live

class ChatIO(abc.ABC):
    @abc.abstractmethod
    def prompt_for_input(self, role: str) -> str:
        """Prompt for input from a role."""

    @abc.abstractmethod
    def prompt_for_output(self, role: str):
        """Prompt for output from a role."""

    @abc.abstractmethod
    def stream_output(self, output_stream, skip_echo_len: int):
        """Stream output."""


class SimpleChatIO(ChatIO):
    def prompt_for_input(self, role) -> str:
        return input(f"{role}: ")

    def prompt_for_output(self, role: str):
        print(f"{role}: ", end="", flush=True)

    def stream_output(self, output_stream, skip_echo_len: int):
        pre = 0
        for outputs in output_stream:
            outputs = outputs[skip_echo_len:].strip()
            outputs = outputs.split(" ")
            now = len(outputs) - 1
            if now > pre:
                print(" ".join(outputs[pre:now]), end=" ", flush=True)
                pre = now
        print(" ".join(outputs[pre:]), flush=True)
        return " ".join(outputs)


class RichChatIO(ChatIO):
    def __init__(self):
        self._prompt_session = PromptSession(history=InMemoryHistory())
        self._completer = WordCompleter(
            words=["!exit", "!reset"], pattern=re.compile("$")
        )
        self._console = Console()

    def prompt_for_input(self, role) -> str:
        self._console.print(f"[bold]{role}:")
        # TODO(suquark): multiline input has some issues. fix it later.
        prompt_input = self._prompt_session.prompt(
            completer=self._completer,
            multiline=False,
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=None,
        )
        self._console.print()
        return prompt_input

    def prompt_for_output(self, role: str):
        self._console.print(f"[bold]{role}:")

    def stream_output(self, output_stream, skip_echo_len: int):
        """Stream output from a role."""
        # TODO(suquark): the console flickers when there is a code block
        #  above it. We need to cut off "live" when a code block is done.

        # Create a Live context for updating the console output
        with Live(console=self._console, refresh_per_second=4) as live:
            # Read lines from the stream
            for outputs in output_stream:
                accumulated_text = outputs[skip_echo_len:]
                if not accumulated_text:
                    continue
                # Render the accumulated text as Markdown
                # NOTE: this is a workaround for the rendering "unstandard markdown"
                #  in rich. The chatbots output treat "\n" as a new line for
                #  better compatibility with real-world text. However, rendering
                #  in markdown would break the format. It is because standard markdown
                #  treat a single "\n" in normal text as a space.
                #  Our workaround is adding two spaces at the end of each line.
                #  This is not a perfect solution, as it would
                #  introduce trailing spaces (only) in code block, but it works well
                #  especially for console output, because in role_play the console does not
                #  care about trailing spaces.
                lines = []
                for line in accumulated_text.splitlines():
                    lines.append(line)
                    if line.startswith("```"):
                        # Code block marker - do not add trailing spaces, as it would
                        #  break the syntax highlighting
                        lines.append("\n")
                    else:
                        lines.append("  \n")
                markdown = Markdown("".join(lines))
                # Update the Live console output
                # live.update(markdown)
        # self._console.print()
        return outputs[skip_echo_len:]

    def decode_output_stream(self, output_stream, skip_echo_len: int):
        """Stream output from a role."""
        # TODO(suquark): the console flickers when there is a code block
        #  above it. We need to cut off "live" when a code block is done.

        # Create a Live context for updating the console output
            # Read lines from the stream
        for outputs in output_stream:
            accumulated_text = outputs[skip_echo_len:]
            if not accumulated_text:
                continue
            # Render the accumulated text as Markdown
            # NOTE: this is a workaround for the rendering "unstandard markdown"
            #  in rich. The chatbots output treat "\n" as a new line for
            #  better compatibility with real-world text. However, rendering
            #  in markdown would break the format. It is because standard markdown
            #  treat a single "\n" in normal text as a space.
            #  Our workaround is adding two spaces at the end of each line.
            #  This is not a perfect solution, as it would
            #  introduce trailing spaces (only) in code block, but it works well
            #  especially for console output, because in role_play the console does not
            #  care about trailing spaces.
            lines = []
            for line in accumulated_text.splitlines():
                lines.append(line)
                if line.startswith("```"):
                    # Code block marker - do not add trailing spaces, as it would
                    #  break the syntax highlighting
                    lines.append("\n")
                else:
                    lines.append("  \n")
            # Update the Live console output
            # live.update(markdown)
        # self._console.print()
        return outputs[skip_echo_len:]
