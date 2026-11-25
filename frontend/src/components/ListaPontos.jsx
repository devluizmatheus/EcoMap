import { nomeMaterial } from "../materiais";

export default function ListaPontos({ pontos, selecionado, onSelecionar }) {
  if (pontos.length === 0) {
    return null;
  }

  return (
    <section className="secao">
      <h2 className="secao-titulo">Pontos próximos</h2>
      <ol className="lista">
        {pontos.map((ponto, indice) => (
          <li key={ponto.id}>
            <button
              type="button"
              className={ponto.id === selecionado ? "item ativo" : "item"}
              onClick={() => onSelecionar(ponto.id)}
            >
              <span className="item-numero">{indice + 1}</span>
              <span className="item-info">
                <strong>{ponto.nome ?? "Ponto de coleta"}</strong>
                {ponto.endereco && <span className="item-endereco">{ponto.endereco}</span>}
                <span className="item-tags">
                  {ponto.distancia_m != null && (
                    <span className="tag tag-distancia">
                      {(ponto.distancia_m / 1000).toFixed(1)} km
                    </span>
                  )}
                  {ponto.materiais.map((material) => (
                    <span key={material} className="tag">
                      {nomeMaterial(material)}
                    </span>
                  ))}
                </span>
              </span>
            </button>
          </li>
        ))}
      </ol>
    </section>
  );
}