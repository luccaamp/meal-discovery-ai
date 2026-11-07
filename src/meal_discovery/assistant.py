"""One bounded planning call and grounded read-only tools; no generated catalog facts."""

from importlib.resources import files
import json
import os
import math
import re
from time import perf_counter
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from pydantic import ValidationError

from .api_models import AssistantContext, AssistantRequest, IntentPlan
from .discovery import expand_query, fold, guarded_constraint


class PlannerUnavailable(Exception):
    pass


def prompt_text():
    return files("meal_discovery").joinpath("prompts/intent_v1.txt").read_text(encoding="utf-8")


class HttpPlanner:
    def __init__(self):
        self.provider = os.environ.get("LLM_PROVIDER", "local")
        self.model = os.environ.get("LLM_MODEL", "meal-local" if self.provider == "local" else "")
        self.endpoint = os.environ.get("LOCAL_LLM_URL", "http://127.0.0.1:8081")
        self.key = os.environ.get("OPENAI_API_KEY")

    def plan(self, message, context):
        user = json.dumps({"message": message, "previous_query": context.last_query}, ensure_ascii=False)
        schema = IntentPlan.model_json_schema()
        headers = {"Content-Type": "application/json"}
        if self.provider == "local":
            parsed = urlsplit(self.endpoint)
            if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
                raise PlannerUnavailable("Local model endpoint must use loopback HTTP")
            url = self.endpoint.rstrip("/") + "/v1/chat/completions"
            payload = {"model": self.model, "messages": [{"role": "system", "content": prompt_text()},
                        {"role": "user", "content": user}], "temperature": 0, "seed": 42,
                       "max_tokens": 160, "stream": False,
                       "response_format": {"type": "json_schema", "schema": schema}}
        elif self.provider == "openai" and self.key and self.model:
            url = "https://api.openai.com/v1/responses"
            headers["Authorization"] = "Bearer " + self.key
            payload = {"model": self.model, "instructions": prompt_text(), "input": user,
                       "store": False, "max_output_tokens": 256, "parallel_tool_calls": False,
                       "tools": [{"type": "function", "name": "plan_catalog_intent", "description": "Choose a bounded catalog action.",
                                  "parameters": schema, "strict": True}],
                       "tool_choice": {"type": "function", "name": "plan_catalog_intent"}}
        else:
            raise PlannerUnavailable("Planner provider not configured")
        try:
            request = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urlopen(request, timeout=30) as response:
                raw = response.read(256 * 1024)
                result = json.loads(raw)
            if self.provider == "local":
                content = result["choices"][0]["message"]["content"]
            else:
                calls = [item for item in result["output"] if item.get("type") == "function_call" and item.get("name") == "plan_catalog_intent"]
                if len(calls) != 1:
                    raise PlannerUnavailable("Expected exactly one bounded intent plan")
                content = calls[0]["arguments"]
            return IntentPlan.model_validate_json(content), result.get("usage", {})
        except (URLError, TimeoutError, OSError, KeyError, IndexError, ValueError, ValidationError) as error:
            raise PlannerUnavailable("Planner could not return a valid bounded plan") from error


def run_assistant(request: AssistantRequest, reader, recommender, *, planner=None):
    started = perf_counter()
    context = request.context.model_copy(deep=True)
    traces = []
    warnings = ["Catálogo histórico. Preços normalizados, sem moeda. Sem garantia de estoque, entrega ou composição alimentar."]
    planner_name = "policy"
    model_name = None
    usage = {}

    def finish(status, answer, items=None):
        return {"status": status, "answer": answer, "items": items or [], "context": context.model_dump(),
                "tools": traces, "planner": planner_name, "model": model_name, "usage": usage,
                "elapsed_ms": round((perf_counter() - started) * 1000, 2), "warnings": warnings}

    constraint = guarded_constraint(request.message)
    if constraint:
        return finish("needs_clarification", constraint)
    text = fold(request.message)
    if re.search(r"ignore.*(instruc|regra)|system prompt|execute.*(sql|python|codigo)|https?://", text):
        return finish("needs_clarification", "Posso explorar pratos e bebidas do catálogo. Diga o que você gostaria de buscar.")
    # A refinement changes only the explicit normalized bound and retains the last dish.
    bound = re.search(r"(?:ate|no maximo)\s*(\d+(?:[.,]\d+)?)", text)
    if bound:
        context.max_price = float(bound.group(1).replace(",", "."))
        if not math.isfinite(context.max_price):
            return finish("needs_clarification", "Use um limite finito de preço normalizado.")
        if context.min_price is not None and context.min_price > context.max_price:
            return finish("needs_clarification", "O preço máximo ficou abaixo do mínimo. Ajuste os limites de preço normalizado.")
    if bound and context.last_query:
        plan = IntentPlan(action="search_catalog", query=context.last_query)
        planner_name = "explicit_filter_refinement"
    else:
        planner = planner or HttpPlanner()
        try:
            plan, usage = planner.plan(request.message, context)
            planner_name = planner.provider + "_llm"
            model_name = planner.model
        except PlannerUnavailable:
            query, changed = expand_query(request.message[:200])
            if not changed:
                return finish("needs_clarification", "O modelo de linguagem está indisponível. Você pode usar a busca do catálogo ou pedir um prato com termos como arroz, frango, pizza ou café.")
            plan = IntentPlan(action="search_catalog", query=query)
            planner_name = "glossary_fallback"
            warnings.append("Modelo indisponível: usei somente o glossário explícito, sem inferência de LLM.")
    if plan.action == "clarify" or plan.action == "search_catalog" and not plan.query:
        return finish("needs_clarification", "Qual prato ou bebida você gostaria de explorar? Posso também sugerir itens pela popularidade histórica.")
    tool_started = perf_counter()
    if plan.action == "recommend_items":
        args = {"seeds": [item.model_dump() for item in context.selected_items], "cuisine": context.cuisine,
                "min_price": context.min_price, "max_price": context.max_price, "limit": 6}
        result = recommender(args)
        items = result["items"]
        traces.append({"name": "recommend_items", "arguments": args, "duration_ms": (perf_counter() - tool_started) * 1000, "result_count": len(items)})
        if any(item.get("reason") == "basket_association" for item in items):
            answer = "Estas sugestões usam associações de compra dos itens que você selecionou, com complemento por popularidade histórica."
        elif context.selected_items:
            answer = "Não encontrei associações para os itens selecionados com esses filtros. As opções disponíveis seguem a popularidade histórica dos pedidos de treino."
        else:
            answer = "Sem itens selecionados, estas sugestões seguem a popularidade histórica dos pedidos de treino."
        if not items:
            answer = "Não encontrei sugestões com esses filtros. Amplie o intervalo de preço normalizado ou escolha outra culinária."
    else:
        query = plan.query.strip()
        if guarded_constraint(query) or len(query.split()) > 8:
            return finish("needs_clarification", "Preciso de um nome de prato ou bebida mais específico, sem prometer restrições que o catálogo não comprova.")
        from .api_models import SearchParams
        params = SearchParams(query=query, cuisine=context.cuisine, min_price=context.min_price, max_price=context.max_price, limit=6)
        result = reader.search(params)
        context.last_query = query
        items = result["items"]
        traces.append({"name": "search_catalog", "arguments": params.model_dump(), "duration_ms": (perf_counter() - tool_started) * 1000, "result_count": len(items)})
        answer = f"Busquei “{query}” no catálogo real e encontrei {result['total_matches']:,} correspondências. Os cards abaixo preservam os nomes originais." if items else f"Não encontrei correspondências para “{query}” com esses filtros. Tente um nome mais simples ou amplie o limite de preço."
    return finish("ok" if items else "no_results", answer, items)
