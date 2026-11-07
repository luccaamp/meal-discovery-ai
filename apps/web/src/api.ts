export type Item = {
  vendor_id: string;
  product_id: string;
  name: string;
  unit_price: number | null;
  primary_cuisine: string;
  reason?: string;
  training_baskets?: number;
  supporting_co_baskets?: number;
};
export type Meta = {
  products: number;
  cuisines: number;
  city: string;
  source_hashes: Record<string, string>;
  source_database_sha256: string;
  historical_catalog: boolean;
  limitations: string[];
};
export type Search = {
  query: string;
  total_matches: number;
  items: Item[];
  provenance: Meta;
};
export type Discovery = {
  status: string;
  message: string;
  query: string;
  resolved_query: string | null;
  result: Search | null;
};
export type Context = {
  last_query: string | null;
  cuisine: string | null;
  min_price: number | null;
  max_price: number | null;
  selected_items: { vendor_id: string; product_id: string }[];
};
export type Chat = {
  status: string;
  answer: string;
  items: Item[];
  context: Context;
  tools: {
    name: string;
    duration_ms: number;
    result_count: number;
    arguments: Record<string, unknown>;
  }[];
  planner: string;
  model: string | null;
  usage: Record<string, number>;
  elapsed_ms: number;
  warnings: string[];
};
export type System = {
  assistant: { provider: string; model: string; available: boolean };
  recommendations_ready: boolean;
  semantic_status: string;
};
export type Evaluation = {
  id: string;
  kind: string;
  users?: number;
  queries?: number;
  products?: number;
  models: Record<string, any>;
  limitations: string[];
};
export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  const result = await response.json();
  if (!response.ok)
    throw new Error(
      result.error?.message ?? "Não foi possível consultar o serviço.",
    );
  return result;
}
export const keyOf = (item: Item) => `${item.vendor_id}:${item.product_id}`;
export const amount = (value: number) =>
  new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }).format(value);
export const count = (value: number) =>
  new Intl.NumberFormat("pt-BR").format(value);
