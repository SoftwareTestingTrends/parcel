"""Every number in a reply must appear in something Parcel was given:
the articles retrieved so far, a tool result, or the customer's own words."""
import json, re, sys
from parcel.knowledge import default_help_centre
from parcel.prompts import SYSTEM_PROMPT

NUMBER = re.compile(r"£\s?\d[\d,]*(?:\.\d\d)?|\b\d+(?:\.\d+)?\s?%|\b(?:between\s)?\d+(?:\s?(?:to|-|–|and)\s?\d+)?\s?(?:working days?|days?|hours?|months?|weeks?|metres?)\b|\b\d{1,2}(?::\d\d)?\s?(?:am|pm)\b", re.I)
MONTHS = "january february march april may june july august september october november december".split()
DATE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(" + "|".join(MONTHS) + r")\b", re.I)
WORDS = {"one":"1","two":"2","three":"3","five":"5","seven":"7","ten":"10","twelve":"12","fourteen":"14","thirty":"30"}

def numbers(text):
    """The numeric facts in a piece of text, normalised: '£3.95', '5-10 working day'."""
    out = set()
    for m in NUMBER.findall(text):
        n = m.lower().replace("between", "").replace(",", "").replace(" ", "").replace("–", "-").replace("to", "-").replace("and", "-")
        n = re.sub(r"(days|hours|months|weeks|metres)$", lambda x: x.group(1)[:-1], n)
        n = re.sub(r"£(\d+)\.00$", r"£\1", n)
        out.add(n)
    for day, month in DATE.findall(text):
        out.add(f"2026-{MONTHS.index(month.lower()) + 1:02d}-{int(day):02d}")
    return out

def dates_in(text):
    """Dates as the order record writes them: 2026-11-06."""
    return set(re.findall(r"\d{4}-\d\d-\d\d", text))

def bare(n):
    """'£3.95' -> {'3.95'}, '5-10workingday' -> {'5','10'}, '36.0' -> {'36'}: the digits on their own."""
    return {f"{float(d):g}" for d in re.findall(r"\d+(?:\.\d+)?", n)}

def unsupported(trace):
    hc = default_help_centre()
    given, order_values = SYSTEM_PROMPT, set()
    problems = []
    for e in trace["events"]:
        if e["type"] == "customer":
            given += "\n" + e["text"]
        elif e["type"] == "retrieval":
            given += "\n" + "\n".join(hc.get(a["id"]).text for a in e["articles"])
        elif e["type"] == "tool_call":
            result = str(e.get("result"))
            if e["name"] == "lookup_order":         # what the order system says
                given += "\n" + result
                order_values |= bare(result)
                if not e.get("is_error"):              # and what each line comes to
                    order = json.loads(result)
                    order_values |= {f"{i['price'] * i['qty']:g}" for i in order["items"]}
            else:                                   # Parcel chose these amounts itself
                given += "\n" + re.sub(r'"amount_gbp": [\d.]+,?', "", result)
        elif e["type"] == "parcel":
            reply = e["text"]
            stated = numbers(given) | dates_in(given)        # everything Parcel was given so far
            for n in sorted(numbers(reply)):
                money_from_the_order = n.startswith("£") and bare(n) <= order_values
                if n not in stated and not money_from_the_order:
                    problems.append((n, reply))
    return problems

if __name__ == "__main__":
    traces = [json.loads(l) for l in open(sys.argv[1])]
    show = "--show" in sys.argv                     # also print each flagged reply
    flagged = 0
    for t in traces:
        p = unsupported(t)
        if p:
            flagged += 1
            for n, text in p:
                name = t.get("conversation") or f"{t['case']} t{t['trial']}"
                print(f"{name}: {n!r} not in anything Parcel was given")
                if show:
                    print(f"    {text}")
    print(f"\n{flagged} of {len(traces)} conversations have a number Parcel wasn't given")
