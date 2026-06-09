# 🚀 Copilot CLI

Copilot CLI is a command-line interface for interacting with GitHub Copilot's chat functionality. This tool allows users to send prompts to Copilot, specify models, and perform predefined actions.

## Features

- Send custom prompts to GitHub Copilot.
- Specify different models for chat completion.
- Use system prompts to guide the conversation.
- Perform predefined actions with customizable commands.
- Output responses to stdout or handle them with custom callbacks.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/rachartier/copilot-cli.git
    cd copilot-cli
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. **You need need to already be connected to GitHub Copilot by VsCode, Neovim or any other IDE that supports Copilot.**

## Usage

To use the Copilot CLI, run the `copilot-cli.py` script with the desired arguments:

```sh
python copilot-cli.py --prompt "Your prompt here" --model "gpt-5-mini"
```

### Arguments

- `--path`: Path to run the action in (default: `.`).
- `--prompt`: Prompt to send to Copilot Chat.
- `--model`: Model to use for the chat (default: `gpt-5-mini` in copilot mode, `qwen3.5:4b` in ollama mode).
- `--system_prompt`: System prompt to send to Copilot Chat.
- `--action`: Action to perform (choices are defined in `ActionManager`).
- `--mode`: Backend to use, `copilot` (default) or `ollama`.
- `--ollama-host`: Ollama server host in `ollama` mode (default: `http://localhost:11434`, overridable via the `OLLAMA_HOST` env var).

### Example

```sh
python copilot-cli.py --prompt "Explain the concept of recursion"
```

#### Actions
```sh
python copilot-cli.py --action "gitignore" --prompt "Write a gitignore for Python" --path "/path/to/project"
```

#### Ollama mode

Run against a local [Ollama](https://ollama.com/) server instead of GitHub Copilot. The `--model`
must name a model you have already pulled locally; action-defined Copilot models are ignored in this
mode.

```sh
python copilot-cli.py --mode ollama --model llama3.1 --prompt "Explain the concept of recursion"
```

## Extras

### Adding copilot-cli to LazyGit

In `~/.config/lazygit/config.yml` add the following snippets:
```yaml
customCommands:
  - key: "<c-a>" # ctrl + a
    description: "Generate commit message"
    context: "files"
    loadingText: "Generating commit message..."
    subprocess: true
    prompts:
      - type: "menuFromCommand"
        title: "Copilot AI Convention Commit"
        key: "Msg"
        command: copilot-cli --action "lazygit-conventional-commit" --path "."
        filter: '^(?P<number>\d+):\s(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?:\s(?P<message>.+)$'
        valueFormat: "{{ .type }}{{ if .scope }}({{ .scope }}){{ end }}: {{ .message }}"
        labelFormat: "{{ .type | red }}{{ if .scope }}({{ .scope }}){{ end }}: {{ .message | green }}"
      - type: "menu"
        key: "Confirm"
        title: "Confirm/Edit commit message"
        options:
          - name: "Commit"
            value: "commit"
          - name: "Edit"
            value: "edit"
    command: >
      {{- if eq .Form.Confirm "commit" -}}
        git commit -m '{{.Form.Msg}}'
      {{- else if eq .Form.Confirm "edit" -}}
        git commit -e -m '{{.Form.Msg}}'
      {{- else -}}
        echo "Commit cancelled" && exit 0
      {{- end -}}
```
It will enable generations of commits messages for staged changed when you press `<CTRL-A>`.

## Acknowledgements

- [GitHub Copilot](https://github.com/features/copilot)

