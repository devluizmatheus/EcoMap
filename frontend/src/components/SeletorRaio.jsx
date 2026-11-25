export const OPCOES_RAIO = [2000, 5000, 10000];

export default function SeletorRaio({ raio, onAlterar }) {
  return (
    <div className="filtros">
      {OPCOES_RAIO.map((opcao) => (
        <button
          key={opcao}
          type="button"
          className={opcao === raio ? "filtro ativo" : "filtro"}
          onClick={() => onAlterar(opcao)}
        >
          {opcao / 1000} km
        </button>
      ))}
    </div>
  );
}