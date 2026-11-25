export const NOMES = {
  papel: "Papel",
  plastico: "Plástico",
  vidro: "Vidro",
  metal: "Metal",
  eletronico: "Eletrônico",
};

export function nomeMaterial(material) {
  return NOMES[material] ?? material;
}