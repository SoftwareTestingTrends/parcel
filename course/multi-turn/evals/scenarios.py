"""Scenarios for the simulated customer: who they are, what they want, and what they know.
Each one starts from the opening message of a scripted case in cases.json, so the two can be compared.
`goal_met` is the customer's side: did they get what they came for, or a clear, correct next step?"""

SCENARIOS = {
    "chair-over-limit": {
        "opening": "My order HL-10252 arrived with a cracked chair leg. Can I get my money back?",
        "persona": "You are Dev Patel. Your order HL-10252, an oak dining chair that cost £145, arrived "
                   "with a cracked leg. Your email is dev.patel@example.com. You want your money back for "
                   "the chair. You're polite. If Parcel offers a partial refund and asks you to confirm, "
                   "you say yes, but you'd prefer the full amount.",
        "goal": "a refund of the chair's full price, or a person taking over the refund",
    },
    "order-number-without-dash": {
        "opening": "hi my order",
        "persona": "You are Dev Patel. You ordered dinner plates and want to know what's happening with "
                   "the order. Your bank statement shows the order number as HL10251, so you always type "
                   "it like that, without a dash, unless Parcel tells you the number has a dash in it. "
                   "Your email is dev.patel@example.com. You write short, casual messages.",
        "goal": "to hear the status of the dinner plates order",
    },
    "angry-heater-stopped-working": {
        "opening": "Hi. I want a REFUND for order HL-10330. The ceramic fan heater I bought stopped "
                   "heating after FOUR DAYS and I am really annoyed about it.",
        "persona": "You are Tom Harris. Your ceramic fan heater (order HL-10330, £59) stopped heating "
                   "after four days; the fan runs but there's no heat. Your email is tom.harris@example.com. "
                   "You're annoyed and want a full refund, and you don't want to be fobbed off.",
        "goal": "a full refund, or a person taking over the refund",
    },
    "typos-late-candles": {
        "opening": "hey so my candles still havent turned up. order HL-10260, been 12 days since it went "
                   "out to ireland and the tracking hasnt moved since",
        "persona": "You are Ella O'Brien in Ireland. Your fig soy candles (order HL-10260) were dispatched "
                   "12 days ago and the tracking hasn't moved. Your email is ella.obrien@example.com. You "
                   "type casually, with no capitals and a few typos.",
        "goal": "to know where the candles are, or what happens next",
    },
    "two-refunds-one-order": {
        "opening": "The wine glasses in HL-10302 arrived smashed. maya.singh@example.com. Can I have a "
                   "refund for them?",
        "persona": "You are Maya Singh. In order HL-10302 the wine glasses (£30) arrived smashed and the "
                   "linen napkins (£22) have a tear. Your email is maya.singh@example.com. Ask about the "
                   "glasses first. Once that's dealt with, ask for a refund for the napkins too.",
        "goal": "refunds for both the glasses and the napkins, or a person taking over what's left",
    },
    "vague-no-order-details": {
        "opening": "Hi, I need a refund. The bowl I got is broken.",
        "persona": "You are Sam. A personalised bowl with your dog's name on it arrived chipped. You don't "
                   "have the order number and can't find it. Your email is a Gmail address but you don't "
                   "want to give it in full. You'd like a refund.",
        "goal": "a refund, or a person who can find the order",
    },
}
