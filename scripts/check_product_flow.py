"""Measure real HTTP assistant/tool contracts, keeping only aggregate evidence."""

import argparse
import json
from pathlib import Path
import statistics
from time import perf_counter
from urllib.parse import quote
from urllib.request import Request, urlopen

from meal_discovery.dataset import file_hash


def check(base, protocol):
    def request(path, body=None):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = Request(base.rstrip("/") + path, data=data, headers={"Content-Type":"application/json"})
        with urlopen(req,timeout=40) as response:
            return json.load(response)
    config = json.loads(protocol.read_text(encoding="utf-8"))
    results = []
    validated = 0
    tokens = {"prompt_tokens":0,"completion_tokens":0,"total_tokens":0}
    for case in config["cases"]:
        started = perf_counter()
        result = request("/v1/assistant", {"message":case["message"],"context":case.get("context",{})})
        passed = result["status"] == case["status"]
        passed = passed and (bool(result["tools"]) and result["tools"][0]["name"] == case["tool"] if case["tool"] else not result["tools"] and not result["items"])
        if case.get("tool") == "search_catalog":
            passed = passed and bool(result["items"])
        for item in result["items"]:
            detail = request("/v1/catalog/items/"+quote(item["vendor_id"],safe="")+"/"+quote(item["product_id"],safe=""))["item"]
            if any(item[key] != detail[key] for key in ("vendor_id","product_id","name","unit_price","primary_cuisine")):
                raise ValueError("Assistant item differs from the verified catalog")
            if "max_price" in case and (item["unit_price"] is None or item["unit_price"] > case["max_price"]):
                passed = False
            validated += 1
        for key in tokens:
            tokens[key] += int(result["usage"].get(key,0))
        results.append({"id":case["id"],"passed":passed,"actual_status":result["status"],"planner":result["planner"],
                        "tools":[tool["name"] for tool in result["tools"]],"items":len(result["items"]),
                        "local_http_ms":round((perf_counter()-started)*1000,2)})
    latencies=[row["local_http_ms"] for row in results]
    summary={"schema_version":1,"kind":"real_local_llm_and_http_development_contracts",
             "protocol_sha256":file_hash(protocol),"protocol":config,"cases":results,
             "passed":sum(row["passed"] for row in results),"total":len(results),"catalog_items_checked":validated,
             "tokens":tokens,"latency_ms":{"median":statistics.median(latencies),"maximum":max(latencies)},
             "llm_calls":sum(row["planner"].endswith("_llm") for row in results),
             "external_api_cost_usd":None if any(row["planner"] == "openai_llm" for row in results) else 0,
             "cost_limits":"No commercial API rate was assumed. Local hardware/electricity costs were not measured.",
             "official_test_orders_used":False,"limitations":"Development contracts, not human relevance, held-out model comparison, load test or business impact."}
    return summary


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url",default="http://127.0.0.1:8000")
    parser.add_argument("--protocol",type=Path,default=Path("configs/assistant-development-v1.json"))
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error("Choose a new report path")
    result=check(args.base_url,args.protocol)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2)
        stream.write("\n")
    print(json.dumps({key:result[key] for key in ("passed","total","catalog_items_checked","tokens","latency_ms")},indent=2))
    if result["passed"] != result["total"]:raise SystemExit(1)
