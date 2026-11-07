import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  Bookmark,
  Check,
  ChevronRight,
  Compass,
  Database,
  FlaskConical,
  Leaf,
  LoaderCircle,
  MessageCircle,
  Search as SearchIcon,
  Send,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  UtensilsCrossed,
  X,
  Info,
  Coffee,
  ChartNoAxesColumnIncreasing,
  ExternalLink,
} from "lucide-react";
import {
  api,
  amount,
  count,
  keyOf,
  type Chat,
  type Context,
  type Discovery,
  type Evaluation,
  type Item,
  type Meta,
  type System,
} from "./api";

type Page = "discover" | "assistant" | "lab";
type Message = { role: "user" | "assistant"; text: string; response?: Chat };
const emptyContext: Context = {
  last_query: null,
  cuisine: null,
  min_price: null,
  max_price: null,
  selected_items: [],
};
const examples = [
  "Arroz com frango",
  "Chá com leite",
  "Pizza de queijo",
  "Café gelado",
];

function CategoryIcon({
  category,
  size = 22,
}: {
  category: string;
  size?: number;
}) {
  return /coffee|tea|drink|juice/.test(category) ? (
    <Coffee size={size} />
  ) : /salad|veget/.test(category) ? (
    <Leaf size={size} />
  ) : (
    <UtensilsCrossed size={size} />
  );
}

export default function App() {
  const [page, setPage] = useState<Page>("discover");
  useEffect(() => {
    window.scrollTo(0, 0);
    document.getElementById("main")?.focus({ preventScroll: true });
  }, [page]);
  const [meta, setMeta] = useState<Meta | null>(null),
    [system, setSystem] = useState<System | null>(null);
  const [cuisines, setCuisines] = useState<
    { name: string; products: number }[]
  >([]);
  const [reports, setReports] = useState<Evaluation[]>([]);
  const [query, setQuery] = useState("arroz com frango"),
    [cuisine, setCuisine] = useState("");
  const [min, setMin] = useState(""),
    [max, setMax] = useState("");
  const [discovery, setDiscovery] = useState<Discovery | null>(null),
    [loading, setLoading] = useState(false),
    [error, setError] = useState("");
  const [selected, setSelected] = useState<Item[]>([]),
    [detail, setDetail] = useState<Item | null>(null);
  const [recommendations, setRecommendations] = useState<Item[]>([]),
    [recLoading, setRecLoading] = useState(false),
    [recError, setRecError] = useState("");
  const [messages, setMessages] = useState<Message[]>([]),
    [draft, setDraft] = useState(""),
    [chatLoading, setChatLoading] = useState(false);
  const [context, setContext] = useState<Context>(emptyContext);
  const dialog = useRef<HTMLDialogElement>(null),
    chatEnd = useRef<HTMLDivElement>(null),
    searchSequence = useRef(0);
  useEffect(() => {
    Promise.all([
      api<Meta>("/v1/catalog/meta"),
      api<{ cuisines: { name: string; products: number }[] }>(
        "/v1/catalog/cuisines",
      ),
      api<System>("/v1/system"),
      api<{ reports: Evaluation[] }>("/v1/evaluations"),
    ])
      .then(([m, c, s, e]) => {
        setMeta(m);
        setCuisines(c.cuisines);
        setSystem(s);
        setReports(e.reports);
      })
      .catch(() =>
        setError(
          "O catálogo está indisponível. Confira se a API e os dados oficiais foram preparados.",
        ),
      );
    search("arroz com frango");
  }, []);
  useEffect(() => {
    if (detail) dialog.current?.showModal();
    else dialog.current?.close();
  }, [detail]);
  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, chatLoading]);
  function filters() {
    if (min !== "" && max !== "" && Number(min) > Number(max))
      throw new Error("O preço mínimo deve ser menor ou igual ao máximo.");
    return {
      cuisine: cuisine || null,
      min_price: min === "" ? null : Number(min),
      max_price: max === "" ? null : Number(max),
    };
  }
  async function search(value = query) {
    const seq = ++searchSequence.current;
    setLoading(true);
    setError("");
    setDiscovery(null);
    try {
      const f = filters();
      const params = new URLSearchParams({ query: value, limit: "12" });
      Object.entries(f).forEach(([key, v]) => {
        if (v !== null) params.set(key, String(v));
      });
      const data = await api<Discovery>("/v1/discovery/search?" + params);
      if (seq === searchSequence.current) {
        setDiscovery(data);
        setQuery(value);
      }
    } catch (e) {
      if (seq === searchSequence.current)
        setError(e instanceof Error ? e.message : "Falha ao buscar.");
    } finally {
      if (seq === searchSequence.current) setLoading(false);
    }
  }
  function toggle(item: Item) {
    setSelected((current) =>
      current.some((value) => keyOf(value) === keyOf(item))
        ? current.filter((value) => keyOf(value) !== keyOf(item))
        : current.length < 5
          ? [...current, item]
          : current,
    );
  }
  async function recommend() {
    setRecLoading(true);
    setRecError("");
    try {
      const result = await api<{ items: Item[] }>("/v1/recommendations", {
        method: "POST",
        body: JSON.stringify({
          seeds: selected.map(({ vendor_id, product_id }) => ({
            vendor_id,
            product_id,
          })),
          ...filters(),
          limit: 6,
        }),
      });
      setRecommendations(result.items);
    } catch (e) {
      setRecError(e instanceof Error ? e.message : "Falha ao recomendar.");
    } finally {
      setRecLoading(false);
    }
  }
  async function chat(value = draft) {
    if (!value.trim() || chatLoading) return;
    setDraft("");
    setMessages((current) => [...current, { role: "user", text: value }]);
    setChatLoading(true);
    try {
      const result = await api<Chat>("/v1/assistant", {
        method: "POST",
        body: JSON.stringify({
          message: value,
          context: {
            ...context,
            ...filters(),
            selected_items: selected.map(({ vendor_id, product_id }) => ({
              vendor_id,
              product_id,
            })),
          },
        }),
      });
      setContext(result.context);
      if (result.context.max_price !== null)
        setMax(String(result.context.max_price));
      setMessages((current) => [
        ...current,
        { role: "assistant", text: result.answer, response: result },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: "Não consegui concluir esta consulta. O catálogo não foi substituído por exemplos. Tente novamente ou use a busca.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  }
  function card(item: Item, index: number, compact = false) {
    const saved = selected.some((value) => keyOf(value) === keyOf(item));
    return (
      <article
        className={"food-card " + (compact ? "compact" : "")}
        key={keyOf(item)}
      >
        <div className={"card-art art-" + (index % 4)} aria-hidden="true">
          <span className="art-rings" />
          <CategoryIcon
            category={item.primary_cuisine}
            size={compact ? 28 : 42}
          />
          <span className="art-caption">{item.primary_cuisine}</span>
        </div>
        <div className="card-body">
          <div className="card-category">{item.primary_cuisine}</div>
          <h3>{item.name}</h3>
          <p className="price">
            {item.unit_price === null ? (
              "Preço não informado"
            ) : (
              <>
                {amount(item.unit_price)} <span>u.n.</span>
              </>
            )}
          </p>
          {item.reason && (
            <p className="reason">
              {item.reason === "basket_association"
                ? "Associação em cestas reais"
                : "Popularidade histórica"}
            </p>
          )}
          <div className="card-bottom">
            <button className="text-button" onClick={() => setDetail(item)}>
              Ver evidências <ArrowUpRight size={15} />
            </button>
            <button
              className={"save-button " + (saved ? "saved" : "")}
              title={
                saved
                  ? "Remover da seleção"
                  : selected.length >= 5
                    ? "Limite de cinco itens selecionados"
                    : "Selecionar como referência"
              }
              aria-label={
                saved ? `Remover ${item.name}` : `Selecionar ${item.name}`
              }
              aria-pressed={saved}
              disabled={!saved && selected.length >= 5}
              onClick={() => toggle(item)}
            >
              {saved ? <Check size={17} /> : <Bookmark size={17} />}
            </button>
          </div>
        </div>
      </article>
    );
  }
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        Pular para o conteúdo
      </a>
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setPage("discover");
          }}
          aria-label="Mesa, início"
        >
          <span className="brand-symbol">
            <UtensilsCrossed size={23} />
          </span>
          mesa<span className="brand-dot">.</span>
        </a>
        <span className="brand-subtitle">DESCUBRA COM CONTEXTO</span>
        <nav aria-label="Navegação principal">
          {(
            [
              { id: "discover", label: "Explorar", icon: Compass },
              { id: "assistant", label: "Assistente", icon: Sparkles },
              { id: "lab", label: "Laboratório", icon: FlaskConical },
            ] as const
          ).map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={page === id ? "nav-active" : ""}
              aria-label={label}
              aria-current={page === id ? "page" : undefined}
              onClick={() => setPage(id)}
            >
              <Icon size={19} />
              <span>{label}</span>
              {page === id && <span className="nav-dot" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-selection">
          <div>
            <Bookmark size={16} /> SUA SELEÇÃO <span>{selected.length}/5</span>
          </div>
          {selected.length ? (
            <>
              <ul>
                {selected.map((item) => (
                  <li key={keyOf(item)}>
                    <span>{item.name}</span>
                    <button
                      onClick={() => toggle(item)}
                      aria-label={`Remover ${item.name}`}
                    >
                      <X size={13} />
                    </button>
                  </li>
                ))}
              </ul>
              <p>Itens escolhidos por você para orientar sugestões.</p>
            </>
          ) : (
            <p>
              Marque itens do catálogo para descobrir combinações relacionadas.
            </p>
          )}
        </div>
        <div className="sidebar-bottom">
          <span className="dataset-dot" /> Dados reais, escolhas informadas
          <p>Um projeto independente de IA.</p>
          <a
            href="https://github.com/luccaamp/meal-discovery-ai"
            target="_blank"
            rel="noreferrer"
          >
            Código & metodologia <ExternalLink size={13} />
          </a>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <span className="breadcrumb">
            Mesa <ChevronRight size={13} />
            {page === "discover"
              ? "Explorar o catálogo"
              : page === "assistant"
                ? "Conversa com contexto"
                : "Métodos & resultados"}
          </span>
          <div className="historical-pill">
            <span /> Singapura <span className="pill-divider">/</span> Catálogo
            histórico
          </div>
        </header>
        <main id="main" tabIndex={-1}>
          {page === "discover" && (
            <>
              <section className="hero">
                <div className="eyebrow">
                  <span /> EXPLORAÇÃO COM EVIDÊNCIAS
                </div>
                <h1>
                  Uma boa escolha
                  <br />
                  começa <em>aqui.</em>
                </h1>
                <p>
                  Encontre seu próximo prato entre opções reais.
                  <br className="desktop-break" /> Explore, refine e descubra o
                  contexto de cada sugestão.
                </p>
                <div className="hero-illustration" aria-hidden="true">
                  <div className="plate">
                    <div className="plate-inner">
                      <Leaf size={76} strokeWidth={1} />
                    </div>
                  </div>
                  <span className="floating-label">
                    <Sparkles size={14} /> Curiosidade à mesa
                  </span>
                  <span className="small-orbit" />
                </div>
              </section>
              <section className="search-section" aria-label="Busca e filtros">
                <form
                  className="search-box"
                  onSubmit={(e: FormEvent) => {
                    e.preventDefault();
                    search();
                  }}
                >
                  <SearchIcon size={23} />
                  <label className="sr-only" htmlFor="query">
                    O que você quer encontrar?
                  </label>
                  <input
                    id="query"
                    maxLength={200}
                    required
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Um prato, uma bebida, uma vontade…"
                  />
                  <button
                    className="primary"
                    aria-label="Explorar catálogo"
                    disabled={loading}
                  >
                    {loading ? (
                      <LoaderCircle className="spin" size={19} />
                    ) : (
                      <>
                        Explorar <ArrowRight size={18} />
                      </>
                    )}
                  </button>
                </form>
                <div className="query-chips">
                  <span>Experimente</span>
                  {examples.map((example) => (
                    <button key={example} onClick={() => search(example)}>
                      {example}
                      <ArrowUpRight size={12} />
                    </button>
                  ))}
                </div>
                <div className="filter-row">
                  <span className="filter-label">
                    <SlidersHorizontal size={16} /> Refine sua busca
                  </span>
                  <label>
                    <span className="sr-only">Culinária</span>
                    <select
                      value={cuisine}
                      onChange={(e) => setCuisine(e.target.value)}
                    >
                      <option value="">Todas as culinárias</option>
                      {cuisines.map((value) => (
                        <option key={value.name} value={value.name}>
                          {value.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="price-filter">
                    Mín.{" "}
                    <input
                      type="number"
                      step="any"
                      min="0"
                      value={min}
                      onChange={(e) => setMin(e.target.value)}
                      placeholder="—"
                      aria-label="Preço mínimo normalizado"
                    />
                  </label>
                  <label className="price-filter">
                    Máx.{" "}
                    <input
                      type="number"
                      step="any"
                      min="0"
                      value={max}
                      onChange={(e) => setMax(e.target.value)}
                      placeholder="—"
                      aria-label="Preço máximo normalizado"
                    />
                  </label>
                  <button className="apply-filter" onClick={() => search()}>
                    Aplicar
                  </button>
                  {(cuisine || min || max) && (
                    <button
                      className="clear-filter"
                      onClick={() => {
                        setCuisine("");
                        setMin("");
                        setMax("");
                      }}
                    >
                      Limpar filtros
                    </button>
                  )}
                </div>
                <p className="filter-note">
                  <Info size={12} /> Preços em unidades normalizadas (u.n.), sem
                  moeda ou conversão para reais.
                </p>
              </section>
              <section aria-labelledby="results-title">
                <div className="section-heading">
                  <div>
                    <span className="eyebrow">DO CATÁLOGO PARA VOCÊ</span>
                    <h2 id="results-title">
                      Explore possibilidades
                      <span className="count-label">
                        {discovery?.result
                          ? count(discovery.result.total_matches) +
                            " resultados"
                          : "Catálogo real"}
                      </span>
                    </h2>
                  </div>
                  <span className="ranking-label">
                    Ordenação por relevância textual
                  </span>
                </div>
                {error && (
                  <div role="alert" className="notice error">
                    <Info size={18} />
                    {error}
                  </div>
                )}
                {loading ? (
                  <div className="loading-state" role="status">
                    <LoaderCircle size={24} className="spin" />
                    <span>Consultando o catálogo real…</span>
                  </div>
                ) : discovery?.status === "needs_clarification" ? (
                  <div className="empty-state">
                    <ShieldCheck size={32} />
                    <h3>Vamos esclarecer essa preferência</h3>
                    <p>{discovery.message}</p>
                  </div>
                ) : discovery?.result?.items.length ? (
                  <>
                    <div className="resolved-query">
                      Busca realizada por{" "}
                      <strong>{discovery.resolved_query}</strong>
                      <span>Vocabulário PT → EN explícito</span>
                    </div>
                    <div className="results-grid">
                      {discovery.result.items.map((item, index) =>
                        card(item, index),
                      )}
                    </div>
                  </>
                ) : (
                  !error && (
                    <div className="empty-state">
                      <SearchIcon size={32} />
                      <h3>Nenhuma correspondência por aqui</h3>
                      <p>
                        Tente outro nome ou amplie os filtros. Não preenchemos
                        resultados com itens inventados.
                      </p>
                    </div>
                  )
                )}
              </section>
              <section className="recommend-section">
                <div className="section-heading">
                  <div>
                    <span className="eyebrow">CONTEXTO QUE APROXIMA</span>
                    <h2>
                      {selected.length
                        ? "A partir da sua seleção"
                        : "O que aparece nas cestas"}
                    </h2>
                    <p>
                      {selected.length
                        ? recommendations.length &&
                          recommendations.every(
                            (item) => item.reason === "historical_popularity",
                          )
                          ? "Sem associações para a seleção atual; estas opções seguem popularidade histórica."
                          : "Associações observadas em pedidos reais, sem histórico pessoal inventado."
                        : "Explore itens pela popularidade nos pedidos históricos de treino."}
                    </p>
                  </div>
                  <button
                    className="secondary"
                    onClick={recommend}
                    disabled={recLoading}
                  >
                    {recLoading ? (
                      <LoaderCircle size={16} className="spin" />
                    ) : (
                      <Sparkles size={16} />
                    )}{" "}
                    Descobrir sugestões
                  </button>
                </div>
                {recError && (
                  <div role="alert" className="notice error">
                    {recError}
                  </div>
                )}
                {recommendations.length > 0 && (
                  <div className="results-grid">
                    {recommendations.map((item, index) => card(item, index))}
                  </div>
                )}
              </section>
              <section className="assistant-banner">
                <div className="banner-icon">
                  <MessageCircle size={25} />
                </div>
                <div>
                  <h3>Uma vontade difícil de descrever?</h3>
                  <p>
                    Converse para explorar pratos e ajustar suas preferências.
                  </p>
                </div>
                <button onClick={() => setPage("assistant")}>
                  Vamos conversar <ArrowUpRight size={18} />
                </button>
              </section>
            </>
          )}
          {page === "assistant" && (
            <section className="assistant-page">
              <div className="eyebrow">
                <Sparkles size={13} /> CONVERSA COM CONTEXTO
              </div>
              <h1>
                Conte sua <em>vontade.</em>
              </h1>
              <p className="page-intro">
                A IA interpreta seu pedido. As ferramentas consultam o catálogo.
                <br />
                Os resultados mantêm a evidência à vista.
              </p>
              <div className="assistant-status">
                <span
                  className={
                    system?.assistant.available ? "online-dot" : "offline-dot"
                  }
                />
                {system?.assistant.available
                  ? "Qwen local conectado"
                  : "Modo essencial · glossário disponível"}
                <span>Sem memória pessoal persistida</span>
              </div>
              <div className="conversation" aria-live="polite">
                {!messages.length && (
                  <div className="chat-welcome">
                    <div className="chat-mark">
                      <Sparkles size={28} />
                    </div>
                    <h2>Por onde começamos?</h2>
                    <p>
                      Peça um prato ou explore sugestões. Depois refine o preço
                      em unidades normalizadas.
                    </p>
                    <div className="chat-examples">
                      {[
                        "Quero arroz com frango",
                        "Quero chá com leite",
                        "Recomende algo",
                      ].map((value) => (
                        <button key={value} onClick={() => chat(value)}>
                          {value}
                          <ArrowUpRight size={15} />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={"message message-" + message.role}
                  >
                    <div className="message-label">
                      {message.role === "user" ? "VOCÊ" : "MESA · ASSISTENTE"}
                    </div>
                    <p>{message.text}</p>
                    {message.response && (
                      <>
                        <div className="chat-results">
                          {message.response.items.map((item, i) =>
                            card(item, i, true),
                          )}
                        </div>
                        <details className="tool-details">
                          <summary>
                            <ShieldCheck size={14} /> Como encontrei estas
                            opções <ChevronRight size={14} />
                          </summary>
                          <p>
                            Planejador: {message.response.planner}{" "}
                            {message.response.model &&
                              "· " + message.response.model}
                          </p>
                          {message.response.tools.map((tool, i) => (
                            <p key={i}>
                              {tool.name === "search_catalog"
                                ? "Busca no catálogo"
                                : "Recomendação por cestas"}{" "}
                              · {tool.result_count} itens ·{" "}
                              {Math.round(tool.duration_ms)} ms
                            </p>
                          ))}
                          <p>
                            Resposta em{" "}
                            {Math.round(message.response.elapsed_ms)} ms. Fatos
                            dos produtos vêm das ferramentas; o modelo não cria
                            itens.
                          </p>
                          <p>
                            Tokens informados:{" "}
                            {message.response.usage.total_tokens ??
                              "não informado"}
                            .
                            {message.response.planner === "local_llm" &&
                              " Inferência local, sem cobrança de API. Custo de hardware não medido."}
                          </p>
                        </details>
                      </>
                    )}
                  </div>
                ))}
                {chatLoading && (
                  <div className="chat-thinking" role="status">
                    <LoaderCircle size={18} className="spin" /> Interpretando e
                    consultando as evidências…
                  </div>
                )}
                <div ref={chatEnd} />
              </div>
              <form
                className="chat-composer"
                onSubmit={(e) => {
                  e.preventDefault();
                  chat();
                }}
              >
                <label htmlFor="chat-input" className="sr-only">
                  Mensagem para o assistente
                </label>
                <input
                  id="chat-input"
                  required
                  maxLength={1000}
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  placeholder="Ex.: quero uma bebida de chá com leite"
                />
                <button
                  className="primary"
                  aria-label="Enviar mensagem"
                  disabled={chatLoading || !draft.trim()}
                >
                  <Send size={19} />
                </button>
              </form>
              <p className="chat-footnote">
                <ShieldCheck size={13} /> O catálogo não comprova ingredientes,
                alérgenos ou disponibilidade atual.
              </p>
            </section>
          )}
          {page === "lab" && (
            <section className="lab-page">
              <div className="eyebrow">
                <FlaskConical size={14} /> LABORATÓRIO ABERTO
              </div>
              <h1>
                Mais evidência.
                <br />
                <em>Menos suposição.</em>
              </h1>
              <p className="page-intro">
                Resultados reais, métodos explícitos e espaço para os erros.
                <br />
                Nenhuma métrica abaixo comprova impacto comercial.
              </p>
              <div className="metric-grid">
                <div>
                  <Database size={20} />
                  <strong>{meta ? count(meta.products) : "—"}</strong>
                  <span>produtos no catálogo lexical</span>
                </div>
                <div>
                  <CategoryIcon category="salad" />
                  <strong>{meta?.cuisines ?? "—"}</strong>
                  <span>culinárias cadastradas</span>
                </div>
                <div>
                  <ShieldCheck size={20} />
                  <strong>Separado</strong>
                  <span>teste oficial, ainda sem avaliação</span>
                </div>
              </div>
              {reports.map((report) => (
                <article className="experiment" key={report.id}>
                  <div className="experiment-header">
                    <span className="experiment-number">
                      {report.id === "recommendation" ? "01" : "02"}
                    </span>
                    <div>
                      <span className="eyebrow">
                        {report.id === "recommendation"
                          ? "PREVISÃO DA PRÓXIMA CESTA"
                          : "RECUPERAÇÃO · PILOTO EXPERIMENTAL"}
                      </span>
                      <h2>
                        {report.id === "recommendation"
                          ? "Recomendação com referências"
                          : "Quando o significado ainda não basta"}
                      </h2>
                    </div>
                    <ChartNoAxesColumnIncreasing size={26} />
                  </div>
                  <p>
                    {report.id === "recommendation"
                      ? `Validação temporal interna com ${count(report.users ?? 0)} clientes. Treino até o dia 61; validação nos dias 62–75.`
                      : `${count(report.products ?? 0)} produtos, ${report.queries} consultas de desenvolvimento. Rótulos automáticos por regras de nomes, sem revisão humana.`}
                  </p>
                  <div className="model-bars">
                    {Object.entries(report.models).map(([name, values]) => {
                      const value =
                        report.id === "recommendation"
                          ? values.ndcg
                          : values.all.ndcg;
                      const labels: Record<string, string> = {
                        popularity: "Popularidade",
                        repeat: "Repetição pessoal",
                        basket_cosine: "Similaridade por cesta",
                        lexical: "Busca lexical",
                        semantic: "Embeddings E5",
                        hybrid: "Busca híbrida",
                      };
                      return (
                        <div className="model-row" key={name}>
                          <span>{labels[name] ?? name}</span>
                          <div className="bar-track">
                            <span
                              style={{ width: Math.max(value, 0) * 100 + "%" }}
                            />
                          </div>
                          <strong>{value.toFixed(4)}</strong>
                        </div>
                      );
                    })}
                  </div>
                  <p className="chart-caption">
                    NDCG@10 ·{" "}
                    {report.id === "recommendation"
                      ? "média por cliente"
                      : "proxy com rótulos fracos, não relevância julgada"}
                  </p>
                  <div className="experiment-note">
                    <Info size={17} />
                    <p>
                      {report.id === "recommendation"
                        ? "Repetição foi a melhor referência medida. Clientes sem histórico usam popularidade como alternativa."
                        : "O piloto semântico não superou a busca lexical na média deste proxy e ainda erra em português. Não foi promovido para a busca do produto."}
                    </p>
                  </div>
                  <details>
                    <summary>Limitações e método</summary>
                    <ul>
                      {report.limitations.map((text, index) => (
                        <li key={index}>{text}</li>
                      ))}
                    </ul>
                  </details>
                </article>
              ))}
              {!reports.length && (
                <div className="empty-state">
                  Os relatórios ainda não estão disponíveis neste ambiente.
                </div>
              )}
              <div className="method-footer">
                <Database size={21} />
                <div>
                  <h3>Procedência faz parte da experiência</h3>
                  <p>
                    Delivery Hero · Singapura · catálogo histórico. Arquivos
                    verificados por SHA-256. Preços normalizados e
                    estabelecimentos anonimizados.
                  </p>
                  <a
                    href="https://github.com/luccaamp/meal-discovery-ai/tree/main/docs"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Ler metodologia no GitHub <ArrowUpRight size={14} />
                  </a>
                </div>
              </div>
            </section>
          )}
          <footer className="page-footer">
            <span>
              mesa. <span>Dados reais. Contexto à vista.</span>
            </span>
            <p>
              Projeto independente de portfólio · sem vínculo com iFood ou
              Delivery Hero
            </p>
          </footer>
        </main>
      </div>
      <dialog
        aria-labelledby="detail-title"
        ref={dialog}
        onCancel={() => setDetail(null)}
        onClick={(e) => {
          if (e.target === dialog.current) setDetail(null);
        }}
      >
        <div className="detail-content">
          {detail && (
            <>
              <button
                className="dialog-close"
                onClick={() => setDetail(null)}
                aria-label="Fechar detalhes"
              >
                <X size={20} />
              </button>
              <span className="eyebrow">EVIDÊNCIA DO CATÁLOGO</span>
              <h2 id="detail-title">{detail.name}</h2>
              <p className="detail-category">
                <CategoryIcon category={detail.primary_cuisine} />
                {detail.primary_cuisine}
              </p>
              <dl>
                <div>
                  <dt>Preço normalizado</dt>
                  <dd>
                    {detail.unit_price === null
                      ? "Não informado"
                      : amount(detail.unit_price) + " u.n."}
                  </dd>
                </div>
                <div>
                  <dt>Origem</dt>
                  <dd>Delivery Hero · Singapura</dd>
                </div>
                <div>
                  <dt>Estado dos dados</dt>
                  <dd>Catálogo histórico</dd>
                </div>
                <div>
                  <dt>Vendedor anonimizado</dt>
                  <dd className="mono">{detail.vendor_id}</dd>
                </div>
                <div>
                  <dt>Produto</dt>
                  <dd className="mono">{detail.product_id}</dd>
                </div>
                {detail.training_baskets !== undefined && (
                  <div>
                    <dt>Presença em cestas de treino</dt>
                    <dd>{count(detail.training_baskets)}</dd>
                  </div>
                )}
              </dl>
              <div className="notice">
                <ShieldCheck size={19} />
                <p>
                  Nome, culinária e preço foram preservados da base real. Não há
                  confirmação de ingredientes, alérgenos, estoque ou entrega. O
                  desenho dos cards é gráfico, não uma foto do prato.
                </p>
              </div>
              <button
                className="primary detail-select"
                onClick={() => toggle(detail)}
              >
                {selected.some((item) => keyOf(item) === keyOf(detail)) ? (
                  <>
                    <Check size={16} /> Item selecionado
                  </>
                ) : (
                  <>
                    <Bookmark size={16} /> Usar como referência
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </dialog>
    </div>
  );
}
