const promptInput = document.getElementById("prompt");
const modelInput = document.getElementById("model");
const outputInput = document.getElementById("output");
const jsonInput = document.getElementById("json");
const convertToggle = document.getElementById("convert");
const logToggle = document.getElementById("log-file");
const commandOutput = document.getElementById("command");
const copyButton = document.getElementById("copy-command");
const resetButton = document.getElementById("reset-form");

const defaultPrompt =
  "Relatório de obra com extensão MT, status PEP, execução e registros fotográficos.";

const buildCommand = () => {
  const parts = [
    "python generate_report.py",
    `--prompt \"${(promptInput.value || defaultPrompt).replace(/\"/g, "'")}\"`,
    `--model ${modelInput.value || "gpt-4o-mini"}`,
    `--output-md ${outputInput.value || "relatorio.md"}`,
  ];

  if (jsonInput.value) {
    parts.push(`--output-json ${jsonInput.value}`);
  }

  if (convertToggle.checked) {
    parts.push("--convert-docx");
  }

  if (logToggle.checked) {
    parts.push("--log-file relatorio.log");
  }

  return parts.join(" \\\n  ");
};

const updateCommand = () => {
  commandOutput.textContent = buildCommand();
};

[promptInput, modelInput, outputInput, jsonInput, convertToggle, logToggle].forEach(
  (element) => {
    element.addEventListener("input", updateCommand);
    element.addEventListener("change", updateCommand);
  }
);

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(commandOutput.textContent);
    copyButton.textContent = "Copiado!";
    setTimeout(() => {
      copyButton.textContent = "Copiar comando";
    }, 1600);
  } catch {
    copyButton.textContent = "Falha ao copiar";
  }
});

resetButton.addEventListener("click", () => {
  promptInput.value = "";
  modelInput.value = "gpt-4o-mini";
  outputInput.value = "relatorio.md";
  jsonInput.value = "relatorio.json";
  convertToggle.checked = true;
  logToggle.checked = true;
  updateCommand();
});

promptInput.value = defaultPrompt;
updateCommand();
