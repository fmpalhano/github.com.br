const promptInput = document.getElementById("prompt");
const modelInput = document.getElementById("model");
const outputInput = document.getElementById("output");
const jsonInput = document.getElementById("json");
const convertToggle = document.getElementById("convert");
const logToggle = document.getElementById("log-file");
const statusOutput = document.getElementById("status");
const logOutput = document.getElementById("log");
const runButton = document.getElementById("run-report");
const resetButton = document.getElementById("reset-form");

const defaultPrompt =
  "Relatório de obra com extensão MT, status PEP, execução e registros fotográficos.";

const buildPayload = () => ({
  prompt: promptInput.value || defaultPrompt,
  model: modelInput.value || "gpt-4o-mini",
  output_md: outputInput.value || "relatorio.md",
  output_json: jsonInput.value || "",
  convert_docx: convertToggle.checked,
  log_file: logToggle.checked ? "relatorio.log" : "",
});

const updateStatus = (text, isError = false) => {
  statusOutput.textContent = text;
  statusOutput.style.borderColor = isError
    ? "rgba(248, 113, 113, 0.4)"
    : "rgba(79, 209, 197, 0.25)";
  statusOutput.style.background = isError
    ? "rgba(248, 113, 113, 0.1)"
    : "rgba(79, 209, 197, 0.08)";
};

runButton.addEventListener("click", async () => {
  updateStatus("Processando relatório...");
  logOutput.textContent = "";

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildPayload()),
    });
    const data = await response.json();
    const success = response.ok && data.returncode === 0;
    updateStatus(
      success ? "Relatório gerado com sucesso." : "Falha ao gerar relatório.",
      !success
    );
    logOutput.textContent = [data.stdout, data.stderr].filter(Boolean).join("\n");
  } catch (error) {
    updateStatus("Erro ao conectar com o servidor local.", true);
    logOutput.textContent = String(error);
  }
});

resetButton.addEventListener("click", () => {
  promptInput.value = "";
  modelInput.value = "gpt-4o-mini";
  outputInput.value = "relatorio.md";
  jsonInput.value = "relatorio.json";
  convertToggle.checked = true;
  logToggle.checked = true;
  updateStatus("Aguardando envio.");
  logOutput.textContent = "";
});

promptInput.value = defaultPrompt;
updateStatus("Aguardando envio.");
