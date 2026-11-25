import { useState } from "react";

export default function Busca({ onBuscar, onLocalizar, carregando }) {
  const [texto, setTexto] = useState("");

  function enviar(evento) {
    evento.preventDefault();
    if (texto.trim().length >= 3) {
      onBuscar(texto.trim());
    }
  }

  return (
    <form className="busca" onSubmit={enviar}>
      <div className="busca-linha">
        <div className="campo">
          <svg className="campo-icone" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="7" />
            <line x1="16.5" y1="16.5" x2="21" y2="21" />
          </svg>
          <input
            type="text"
            placeholder="Digite um endereço ou bairro"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
          />
        </div>
        <button type="submit" className="botao-primario" disabled={carregando}>
          {carregando ? "Buscando..." : "Buscar"}
        </button>
      </div>

      <button
        type="button"
        className="botao-secundario"
        onClick={onLocalizar}
        disabled={carregando}
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="4" />
          <line x1="12" y1="2" x2="12" y2="5" />
          <line x1="12" y1="19" x2="12" y2="22" />
          <line x1="2" y1="12" x2="5" y2="12" />
          <line x1="19" y1="12" x2="22" y2="12" />
        </svg>
        Usar minha localização
      </button>
    </form>
  );
}