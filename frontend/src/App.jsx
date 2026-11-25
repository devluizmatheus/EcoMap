import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import {
  Circle,
  CircleMarker,
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  ZoomControl,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";

import Busca from "./components/Busca";
import Filtros from "./components/Filtros";
import ListaPontos from "./components/ListaPontos";
import SeletorRaio, { OPCOES_RAIO } from "./components/SeletorRaio";
import { nomeMaterial } from "./materiais";
import { buscarPontos, geocodificar } from "./services/api";

const JOAO_PESSOA = [-7.1153, -34.861];
const RAIO_PADRAO = 5000; // em metros

// Alfinete numerado, desenhado com HTML e CSS
function criarIcone(numero, ativo) {
  return L.divIcon({
    className: "pin-wrapper",
    html: `<div class="pin ${ativo ? "pin-ativo" : ""}"><span>${numero}</span></div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 39],
    popupAnchor: [0, -36],
  });
}

// Controla os movimentos do mapa
function ControlarMapa({ centro, pontos, raio, selecionado, marcadores }) {
  const mapa = useMap();

  // Depois de cada busca: enquadra os pontos (ou a área toda, se não houver pontos)
  useEffect(() => {
    const desktop = window.innerWidth > 640;
    const margens = {
      paddingTopLeft: desktop ? [420, 40] : [20, 300],
      paddingBottomRight: [40, 40],
      maxZoom: 16,
    };

    if (pontos.length === 0) {
      mapa.fitBounds(L.latLng(centro).toBounds(raio * 2), margens);
      return;
    }
    const limites = L.latLngBounds([centro, ...pontos.map((p) => [p.lat, p.lon])]);
    mapa.fitBounds(limites, margens);
  }, [centro, pontos, raio, mapa]);

  // Quando um ponto é selecionado: voa até ele e abre o popup
  useEffect(() => {
    const ponto = pontos.find((p) => p.id === selecionado);
    if (!ponto) {
      return;
    }
    mapa.flyTo([ponto.lat, ponto.lon], 17, { duration: 0.8 });
    mapa.once("moveend", () => marcadores.current[ponto.id]?.openPopup());
  }, [selecionado, pontos, mapa, marcadores]);

  return null;
}

export default function App() {
  // ---------- Estados ----------
  const [centro, setCentro] = useState(JOAO_PESSOA);
  const [local, setLocal] = useState(null);
  const [minhaPosicao, setMinhaPosicao] = useState(null);
  const [materiais, setMateriais] = useState([]);
  const [raio, setRaio] = useState(RAIO_PADRAO);
  const [pontos, setPontos] = useState([]);
  const [selecionado, setSelecionado] = useState(null);
  const [painelAberto, setPainelAberto] = useState(true);
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState({ texto: "", tipo: "info" });

  const marcadores = useRef({});

  // A próxima opção de raio maior que a atual (ou undefined, se já for a maior)
  const proximoRaio = OPCOES_RAIO.find((opcao) => opcao > raio);

  function mostrar(texto, tipo = "info") {
    setMensagem({ texto, tipo });
  }

  // ---------- Busca os pontos de um lugar já conhecido ----------
  async function carregarPontos(lugar, filtros, raioBusca) {
    setCarregando(true);
    mostrar("");
    try {
      const resposta = await buscarPontos({
        lat: lugar.lat,
        lon: lugar.lon,
        raio: raioBusca,
        materiais: filtros,
      });
      setPontos(resposta.pontos);
      setSelecionado(null);
      if (window.innerWidth <= 640) {
        setPainelAberto(false);
      }
      if (resposta.total === 0) {
        mostrar(`Nenhum ponto de coleta em ${raioBusca / 1000} km.`, "aviso");
      } else {
        mostrar(`${resposta.total} ponto(s) em ${raioBusca / 1000} km de ${lugar.endereco}`);
      }
    } catch (erro) {
      setPontos([]);
      mostrar(erro.message, "erro");
    } finally {
      setCarregando(false);
    }
  }

  // ---------- Busca por endereço digitado ----------
  async function buscar(endereco) {
    setCarregando(true);
    mostrar("");
    try {
      const lugar = await geocodificar(endereco);
      setLocal(lugar);
      setMinhaPosicao(null);
      setCentro([lugar.lat, lugar.lon]);
      await carregarPontos(lugar, materiais, raio);
    } catch (erro) {
      setPontos([]);
      mostrar(erro.message, "erro");
      setCarregando(false);
    }
  }

  // ---------- Busca pela localização atual ----------
  function usarMinhaLocalizacao() {
    if (!navigator.geolocation) {
      mostrar("Seu navegador não permite obter a localização.", "erro");
      return;
    }

    setCarregando(true);
    mostrar("Obtendo sua localização...");

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
        carregarPontos(lugar, materiais, raio);
      },
      (erro) => {
        setCarregando(false);
        const mensagens = {
          1: "Você não permitiu o acesso à localização.",
          2: "Não foi possível descobrir sua localização.",
          3: "Demorou demais para obter sua localização.",
        };
        mostrar(mensagens[erro.code] ?? "Erro ao obter a localização.", "erro");
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  // ---------- Quando os filtros mudam ----------
  function alterarFiltros(novosMateriais) {
    setMateriais(novosMateriais);
    if (local) {
      carregarPontos(local, novosMateriais, raio);
    }
  }

  // ---------- Quando o raio muda ----------
  function alterarRaio(novoRaio) {
    setRaio(novoRaio);
    if (local) {
      carregarPontos(local, materiais, novoRaio);
    }
  }

  // ---------- Selecionar um ponto da lista ----------
  function selecionarPonto(id) {
    setSelecionado(id);
    if (window.innerWidth <= 640) {
      setPainelAberto(false);
    }
  }

  // ---------- Tela ----------
  return (
    <div className="app">
      <MapContainer center={JOAO_PESSOA} zoom={13} zoomControl={false} className="mapa">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ZoomControl position="bottomright" />
        <ControlarMapa
          centro={centro}
          pontos={pontos}
          raio={raio}
          selecionado={selecionado}
          marcadores={marcadores}
        />

        {/* Área da busca */}
        {local && (
          <Circle
            center={[local.lat, local.lon]}
            radius={raio}
            pathOptions={{ color: "#2e7d32", weight: 1, dashArray: "6 6", fillOpacity: 0.04 }}
          />
        )}

        {/* Onde a pessoa está */}
        {minhaPosicao && (
          <CircleMarker
            center={minhaPosicao}
            radius={8}
            pathOptions={{ color: "#ffffff", weight: 3, fillColor: "#1e88e5", fillOpacity: 1 }}
          >
            <Popup>Você está aqui</Popup>
          </CircleMarker>
        )}

        {/* Pontos de reciclagem */}
        {pontos.map((ponto, indice) => (
          <Marker
            key={ponto.id}
            position={[ponto.lat, ponto.lon]}
            icon={criarIcone(indice + 1, ponto.id === selecionado)}
            ref={(marcador) => {
              if (marcador) marcadores.current[ponto.id] = marcador;
            }}
            eventHandlers={{ click: () => setSelecionado(ponto.id) }}
          >
            <Popup>
              <div className="popup">
                <strong>{ponto.nome ?? "Ponto de coleta"}</strong>
                {ponto.endereco && <p>{ponto.endereco}</p>}
                <p>
                  {ponto.materiais.length > 0
                    ? `Aceita: ${ponto.materiais.map(nomeMaterial).join(", ")}`
                    : "Materiais aceitos não informados"}
                </p>
                <div className="popup-rodape">
                  {ponto.distancia_m != null && (
                    <span className="popup-distancia">
                      A {(ponto.distancia_m / 1000).toFixed(1)} km
                    </span>
                  )}
                  <a
                    className="popup-link"
                    href={`https://www.google.com/maps/dir/?api=1&destination=${ponto.lat},${ponto.lon}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Como chegar →
                  </a>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <aside className={painelAberto ? "painel" : "painel recolhido"}>
        <button
          type="button"
          className="alca"
          onClick={() => setPainelAberto(!painelAberto)}
          aria-expanded={painelAberto}
        >
          {painelAberto ? "Recolher ▲" : "Buscar e filtrar ▼"}
        </button>

        <header className="painel-topo">
          <div className="logo" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path d="M5 21c0-8 6-14 15-16-1 9-7 15-15 16z" />
              <path d="M5 21c3-5 6-8 10-11" />
            </svg>
          </div>
          <div>
            <h1>EcoMap</h1>
            <p>Encontre pontos de reciclagem perto de você</p>
          </div>
        </header>

        <Busca onBuscar={buscar} onLocalizar={usarMinhaLocalizacao} carregando={carregando} />

        <section className="secao">
          <h2 className="secao-titulo">Filtrar por material</h2>
          <Filtros selecionados={materiais} onAlterar={alterarFiltros} />
        </section>

        <section className="secao">
          <h2 className="secao-titulo">Distância máxima</h2>
          <SeletorRaio raio={raio} onAlterar={alterarRaio} />
        </section>

        {mensagem.texto && (
          <div className={`status status-${mensagem.tipo}`}>
            <p>{mensagem.texto}</p>
            {mensagem.tipo === "aviso" && proximoRaio && (
              <button
                type="button"
                className="status-acao"
                onClick={() => alterarRaio(proximoRaio)}
                disabled={carregando}
              >
                Ampliar para {proximoRaio / 1000} km
              </button>
            )}
          </div>
        )}

        <ListaPontos pontos={pontos} selecionado={selecionado} onSelecionar={selecionarPonto} />
      </aside>
    </div>
  );
}