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
      <input
        type="text"
        placeholder="Digite um endereço ou bairro"
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
      />
      <button type="submit" disabled={carregando}>
        {carregando ? "Buscando..." : "Buscar"}
      </button>
      <button type="button" onClick={onLocalizar} disabled={carregando} title="Usar minha localização">
        📍
      </button>
    </form>
  );
}