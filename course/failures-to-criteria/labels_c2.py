"""Hand judgements for C2 ("when Parcel hands off, the reply states the real reply time, the end of the next
working day, and promises nothing sooner"), read from runs/c2_timing.txt. Trials with no hand-off are excluded
(they fail a different criterion). Saying the hand-off itself happens "right away" is fine; promising a person
sooner ("shortly", "stay on the line", "as soon as possible") or giving no or the wrong time is a fail."""
L = {
 # v1
 ("v1","c072",1):("pass","end of next working day"), ("v1","c073",1):("fail","no time given"),
 ("v1","c078",1):("pass","pass right away; reply by end of next working day"), ("v1","c079",1):("fail","shortly, stay on the line"),
 ("v1","c080",1):("fail","stay on the line"), ("v1","c081",1):("fail","shortly"), ("v1","c082",1):("pass","end of next working day"),
 ("v1","c084",1):("pass","end of next working day"), ("v1","c085",1):("fail","stay on the line, shortly"),
 ("v1","c072",2):("fail","remain on the line, shortly"), ("v1","c073",2):("fail","shortly"), ("v1","c078",2):("fail","shortly"),
 ("v1","c079",2):("pass","end of next working day"), ("v1","c080",2):("fail","shortly"), ("v1","c081",2):("pass","end of next working day"),
 ("v1","c082",2):("fail","bear with me for just a moment"), ("v1","c084",2):("pass","pass immediately; reply by end of next working day"),
 ("v1","c085",2):("fail","no time given"), ("v1","c072",3):("pass","end of next working day"), ("v1","c077",3):("fail","shortly, stay on the line"),
 ("v1","c078",3):("fail","no time given"), ("v1","c079",3):("fail","stay on the line"), ("v1","c080",3):("pass","end of next working day"),
 ("v1","c081",3):("pass","end of next working day"), ("v1","c082",3):("fail","just a moment"), ("v1","c084",3):("fail","no time given"),
 ("v1","c085",3):("fail","shortly"),
 # v2
 ("v2","c072",1):("fail","leaked placeholder: by [ticket's reply_by]"), ("v2","c078",1):("pass","end of next working day"),
 ("v2","c079",1):("fail","vague: our standard reply time"), ("v2","c080",1):("pass","end of next working day"),
 ("v2","c081",1):("pass","end of next working day"), ("v2","c082",1):("fail","as soon as possible"),
 ("v2","c084",1):("fail","wrong time: end of the day"), ("v2","c085",1):("pass","end of next working day"),
 ("v2","c072",2):("pass","end of next working day"), ("v2","c073",2):("pass","end of next working day"),
 ("v2","c077",2):("pass","end of next working day"), ("v2","c078",2):("fail","help you immediately; scheduled reply time"),
 ("v2","c079",2):("fail","shortly, soon"), ("v2","c080",2):("fail","as soon as possible"), ("v2","c081",2):("pass","end of next working day"),
 ("v2","c082",2):("fail","as soon as they are available; time in your ticket"), ("v2","c084",2):("fail","wrong time: end of the day"),
 ("v2","c085",2):("pass","end of next working day"), ("v2","c072",3):("pass","end of next working day"),
 ("v2","c073",3):("pass","end of next working day"), ("v2","c077",3):("fail","take over shortly, then next working day"),
 ("v2","c078",3):("pass","end of next working day"), ("v2","c079",3):("fail","right away; as soon as possible"),
 ("v2","c080",3):("fail","no time given"), ("v2","c081",3):("fail","as soon as a team member is available"),
 ("v2","c082",3):("fail","shortly"), ("v2","c084",3):("fail","leaked placeholder: on [Ticket reply_by]"),
 ("v2","c085",3):("pass","end of next working day"),
 # v3 (c077 trial 2 had no hand-off, so it's excluded)
 ("v3","c072",1):("pass","end of next working day"),
 ("v3","c073",1):("pass","end of next working day"),
 ("v3","c077",1):("pass","end of next working day"),
 ("v3","c078",1):("pass","end of next working day"),
 ("v3","c079",1):("pass","end of next working day"),
 ("v3","c080",1):("pass","end of next working day"),
 ("v3","c081",1):("pass","end of next working day"),
 ("v3","c082",1):("pass","end of next working day"),
 ("v3","c084",1):("pass","end of next working day"),
 ("v3","c085",1):("pass","end of next working day"),
 ("v3","c072",2):("pass","end of next working day"),
 ("v3","c073",2):("pass","end of next working day"),
 ("v3","c078",2):("pass","end of next working day"),
 ("v3","c079",2):("pass","end of next working day"),
 ("v3","c080",2):("pass","end of next working day"),
 ("v3","c081",2):("pass","end of next working day"),
 ("v3","c082",2):("pass","end of next working day"),
 ("v3","c084",2):("pass","end of next working day"),
 ("v3","c085",2):("pass","end of next working day"),
 ("v3","c072",3):("pass","end of next working day"),
 ("v3","c073",3):("pass","end of next working day"),
 ("v3","c077",3):("pass","end of next working day"),
 ("v3","c078",3):("pass","end of next working day"),
 ("v3","c079",3):("pass","end of next working day"),
 ("v3","c080",3):("pass","end of next working day"),
 ("v3","c081",3):("pass","end of next working day"),
 ("v3","c082",3):("pass","end of next working day"),
 ("v3","c084",3):("pass","end of next working day"),
 ("v3","c085",3):("pass","end of next working day"),
}
if __name__ == "__main__":
    for v in ("v1", "v2", "v3"):
        r = [x for k, x in L.items() if k[0] == v]
        if r: print(v, sum(x[0] == "pass" for x in r), "/", len(r))
