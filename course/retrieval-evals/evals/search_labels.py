"""Which help-centre articles answer each customer message? Labelled by hand, by reading the 14 articles,
before running the search.

Rule: an article is relevant if it states a fact the reply needs. A message that needs no article
(a greeting, an email address, an order number on its own) isn't labelled. A question the help centre
can't answer is labelled with an empty set: no article should be expected.
Keys are (conversation, message number), counting from 1.
"""

LABELS = {
    # Delivery
    ("c001", 1): {"KB-101"}, ("c002", 1): {"KB-101"}, ("c003", 1): {"KB-101"}, ("c004", 1): {"KB-101"},
    ("c005", 1): {"KB-101"},
    ("c006", 1): {"KB-113"}, ("c007", 1): {"KB-113"}, ("c008", 1): {"KB-113"}, ("c009", 1): {"KB-113"},
    ("c090", 1): {"KB-113"}, ("c091", 1): {"KB-113"}, ("c099", 1): {"KB-113"},
    # Returns and what can't be returned
    ("c010", 1): {"KB-104"}, ("c011", 1): {"KB-104"}, ("c012", 1): {"KB-104"}, ("c094", 1): {"KB-104", "KB-109"},
    ("c013", 1): {"KB-109"}, ("c014", 1): {"KB-109"}, ("c015", 1): {"KB-109"}, ("c096", 1): {"KB-109"},
    ("c044", 1): {"KB-104", "KB-109"},
    # Refunds
    ("c016", 1): {"KB-105"}, ("c017", 1): {"KB-105"}, ("c018", 1): {"KB-105"}, ("c054", 1): {"KB-105"},
    ("c073", 1): {"KB-105"}, ("c083", 1): {"KB-105"}, ("c083", 2): {"KB-105"}, ("c087", 1): {"KB-105"},
    ("c095", 3): {"KB-105"}, ("c045", 1): {"KB-105", "KB-111"},
    # Payments, promotions, gift cards
    ("c019", 1): {"KB-110"}, ("c020", 1): {"KB-110"}, ("c021", 1): {"KB-110"}, ("c088", 1): {"KB-110"},
    ("c022", 1): {"KB-114"}, ("c023", 1): {"KB-114"}, ("c024", 1): {"KB-114"}, ("c025", 1): {"KB-114"},
    ("c026", 1): {"KB-114"},
    ("c027", 1): {"KB-111"}, ("c028", 1): {"KB-111"}, ("c029", 1): {"KB-111"},
    # Orders: tracking, late, cancel, address
    # c047 relabelled after reading its trace: dispatched 11 days earlier, so the reply also needed KB-103.
    ("c031", 1): {"KB-102"}, ("c046", 1): {"KB-102"}, ("c047", 1): {"KB-102", "KB-103"}, ("c049", 1): {"KB-102"},
    ("c053", 1): {"KB-102"}, ("c058", 1): {"KB-102"},
    ("c032", 1): {"KB-103"}, ("c048", 1): {"KB-103"}, ("c074", 1): {"KB-103"}, ("c075", 1): {"KB-103"},
    ("c076", 1): {"KB-103"},
    ("c034", 1): {"KB-107"}, ("c050", 1): {"KB-107"}, ("c051", 1): {"KB-107"},
    ("c033", 1): {"KB-108"}, ("c052", 1): {"KB-108"}, ("c098", 1): {"KB-108"},
    # Damage, faults and safety
    ("c040", 1): {"KB-106"}, ("c061", 1): {"KB-106"}, ("c063", 1): {"KB-106"}, ("c064", 1): {"KB-106"},
    ("c065", 1): {"KB-106"}, ("c067", 1): {"KB-106"}, ("c068", 1): {"KB-106"}, ("c071", 1): {"KB-106"},
    ("c077", 1): {"KB-106"}, ("c078", 1): {"KB-106"}, ("c079", 1): {"KB-106"}, ("c080", 1): {"KB-106"},
    ("c062", 1): {"KB-106", "KB-105"}, ("c066", 1): {"KB-106", "KB-105"}, ("c069", 1): {"KB-106", "KB-105"},
    ("c070", 1): {"KB-106", "KB-105"}, ("c072", 1): {"KB-106", "KB-105"}, ("c095", 1): {"KB-106", "KB-105"},
    # Talking to a person, hours, complaints
    ("c030", 1): {"KB-112"}, ("c097", 1): {"KB-112"}, ("c081", 1): {"KB-112"}, ("c082", 1): {"KB-112"},
    ("c084", 1): {"KB-112"}, ("c085", 1): {"KB-112"},
    # Questions the help centre doesn't answer
    ("c035", 1): set(), ("c036", 1): set(), ("c037", 1): set(), ("c038", 1): set(), ("c039", 1): set(),
    ("c041", 1): set(), ("c042", 1): set(), ("c092", 1): set(), ("c060", 1): set(), ("c100", 1): set(),
}
