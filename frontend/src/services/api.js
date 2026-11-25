const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

async function pedir(caminho, parametros = {}) {
  const url = new URL(caminho, API_URL);

  for (const [chave, valor] of Object.entries(parametros)) {
    if (Array.isArray(valor)) {
      valor.forEach((item) => url.searchParams.append(chave, item));
    } else if (valor !== undefined && valor !== null) {
      url.searchParams.append(chave, valor);
    }
  }

  let resposta;
  try {
    resposta = await fetch(url);
  } catch {
    throw new Error("Não foi possível conectar ao servidor. Verifique sua conexão.");
  }

  const dados = await resposta.json().catch(() => null);

  if (!resposta.ok) {
    throw new Error(dados?.detail ?? "O servidor está indisponível. Tente novamente em instantes.");
  }
  return dados;
}

export function geocodificar(endereco) {
  return pedir("/api/geocodificar", { q: endereco });
}

export function buscarPontos({ lat, lon, raio = 5000, materiais = [] }) {
  return pedir("/api/pontos", { lat, lon, raio, materiais });
}

export function listarMateriais() {
  return pedir("/api/materiais");
}