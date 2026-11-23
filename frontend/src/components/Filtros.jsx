import { useEffect, useState } from "react";
import { listarMateriais } from "../services/api";

const NOMES = {
  papel: "Papel",
  plastico: "Plástico",
  vidro: "Vidro",
  metal: "Metal",
  eletronico: "Eletrônico",
};

export default function Filtros({ selecionados, onAlterar }) {
  const [materiais, setMateriais] = useState([]);

  useEffect(() => {
    listarMateriais()
      .then(setMateriais)
      .catch(() => setMateriais(Object.keys(NOMES)));
  }, []);

  function alternar(material) {
    if (selecionados.includes(material)) {
      onAlterar(selecionados.filter((m) => m !== material));
    } else {
      onAlterar([...selecionados, material]);
    }
  }

  return (
    <div className="filtros">
      {materiais.map((material) => (
        <button
          key={material}
          type="button"
          className={selecionados.includes(material) ? "filtro ativo" : "filtro"}
          onClick={() => alternar(material)}
        >
          {NOMES[material] ?? material}
        </button>
      ))}
    </div>
  );
}