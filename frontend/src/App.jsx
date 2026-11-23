import { useEffect, useState } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";

import Busca from "./components/Busca";
import Filtros from "./components/Filtros";
import { buscarPontos, geocodificar } from "./services/api";

const JOAO_PESSOA = [-7.1153, -34.861];

function Recentralizar({ centro }) {
  const mapa = useMap();
  useEffect(() => {
    mapa.setView(centro, 14);
  }, [centro, mapa]);
  return null;
}

export default function App() {
  // ---------- Estados ----------
  const [centro, setCentro] = useState(JOAO_PESSOA);
  const [local, setLocal] = useState(null);
  const [minhaPosicao, setMinhaPosicao] = useState(null);
  const [materiais, setMateriais] = useState([]);
  const [pontos, setPontos] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState("");

  // ---------- Busca os pontos de um lugar já conhecido ----------
  async function carregarPontos(lugar, filtros) {
    setCarregando(true);
    setMensagem("");
    try {
      const resposta = await buscarPontos({
        lat: lugar.lat,
        lon: lugar.lon,
        materiais: filtros,
      });
      setPontos(resposta.pontos);
      setMensagem(
        resposta.total === 0
          ? "Nenhum ponto de coleta encontrado com esses filtros."
          : `${resposta.total} ponto(s) encontrado(s) perto de ${lugar.endereco}`
      );
    } catch (erro) {
      setPontos([]);
      setMensagem(erro.message);
    } finally {
      setCarregando(false);
    }
  }

  // ---------- Busca por endereço digitado ----------
  async function buscar(endereco) {
    setCarregando(true);
    setMensagem("");
    try {
      const lugar = await geocodificar(endereco);
      setLocal(lugar);
      setMinhaPosicao(null);
      setCentro([lugar.lat, lugar.lon]);
      await carregarPontos(lugar, materiais);
    } catch (erro) {
      setPontos([]);
      setMensagem(erro.message);
      setCarregando(false);
    }
  }

  // ---------- Busca pela localização atual ----------
  function usarMinhaLocalizacao() {
    if (!navigator.geolocation) {
      setMensagem("Seu navegador não permite obter a localização.");
      return;
    }

    setCarregando(true);
    setMensagem("Obtendo sua localização...");

    navigator.geolocation.getCurrentPosition(
      (posicao) => {
        const lugar = {
          lat: posicao.coords.latitude,
          lon: posicao.coords.longitude,
          endereco: "sua localização",
        };
        setMinhaPosicao([lugar.lat, lugar.lon]);
        setLocal(lugar);
        setCentro([lugar.lat, lugar.lon]);
        carregarPontos(lugar, materiais);
      },
      (erro) => {
        setCarregando(false);
        const mensagens = {
          1: "Você não permitiu o acesso à localização.",
          2: "Não foi possível descobrir sua localização.",
          3: "Demorou demais para obter sua localização.",
        };
        setMensagem(mensagens[erro.code] ?? "Erro ao obter a localização.");
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  // ---------- Quando os filtros mudam ----------
  function alterarFiltros(novosMateriais) {
    setMateriais(novosMateriais);
    if (local) {
      carregarPontos(local, novosMateriais);
    }
  }

  // ---------- Tela ----------
  return (
    <div className="app">
      <header className="cabecalho">
        <h1>EcoMap</h1>
        <Busca onBuscar={buscar} onLocalizar={usarMinhaLocalizacao} carregando={carregando} />
        <Filtros selecionados={materiais} onAlterar={alterarFiltros} />
        {mensagem && <p className="mensagem">{mensagem}</p>}
      </header>

      <MapContainer center={JOAO_PESSOA} zoom={13} className="mapa">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Recentralizar centro={centro} />

        {minhaPosicao && (
          <CircleMarker
            center={minhaPosicao}
            radius={8}
            pathOptions={{ color: "#1565c0", fillColor: "#1e88e5", fillOpacity: 1 }}
          >
            <Popup>Você está aqui</Popup>
          </CircleMarker>
        )}

        {pontos.map((ponto) => (
          <CircleMarker
            key={ponto.id}
            center={[ponto.lat, ponto.lon]}
            radius={10}
            pathOptions={{ color: "#2e7d32", fillOpacity: 0.7 }}
          >
            <Popup>
              <strong>{ponto.nome ?? "Ponto de coleta"}</strong>
              {ponto.endereco && <p>{ponto.endereco}</p>}
              <p>
                {ponto.materiais.length > 0
                  ? `Aceita: ${ponto.materiais.join(", ")}`
                  : "Materiais aceitos não informados"}
              </p>
              {ponto.distancia_m != null && (
                <p>A {(ponto.distancia_m / 1000).toFixed(1)} km</p>
              )}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}