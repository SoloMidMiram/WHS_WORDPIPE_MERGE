# 1950s–1980s: Early Logic-Based AI and Its Rigid Limitations

The mid-20th century saw AI’s birth in symbolic logic and rule-based
reasoning. Programs like the **Logic Theorist** (1956) could prove
mathematical theorems, demonstrating “thinking” by following explicit
logical
rules[\[1\]](https://en.wikipedia.org/wiki/Logic_Theorist#:~:text=It%20was%20the%20first%20program,Logic).
However, these **GOFAI** (Good Old-Fashioned AI) systems were confined
to *“toy” problems*. They lacked real-world knowledge and scalability,
often falling prey to **combinatorial explosion** when facing
complexity[\[2\]](https://en.wikipedia.org/wiki/AI_winter#:~:text=In%201973%2C%20professor%20Sir%20James,versions.%5B%2020).
By 1973, the UK’s Lighthill Report famously **“criticized the utter
failure of AI to achieve its grandiose objectives,”** noting that many
AI algorithms which worked in labs would **“grind to a halt on real
world problems”**, suitable only for simplified
tasks[\[2\]](https://en.wikipedia.org/wiki/AI_winter#:~:text=In%201973%2C%20professor%20Sir%20James,versions.%5B%2020).
This disconnect led to the **first AI Winter** in the 1970s, as optimism
and funding dried up amid unmet
promises[\[3\]](https://en.wikipedia.org/wiki/AI_winter#:~:text=See%20also%3A%20Lighthill%20report).
Early AI also lacked any notion of common sense or understanding:
systems manipulated symbols without grasping meaning. In 1980,
philosopher **John Searle** illustrated this with the **Chinese Room**
thought experiment, arguing that a computer following rules can appear
fluent yet “is just following syntactic rules without **semantic**
comprehension” – **it has no real understanding** of what it
outputs[\[4\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=fluent%20Chinese%20speakers%20outside%20the,4)[\[5\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=may%20be%20viewed%20as%20an,c).
This era’s AI could execute logical operations, but it was rigid and
brittle, missing the nuanced intuition humans use in everyday
reasoning[\[6\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=Knowing,of%20intuition)[\[7\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=Dreyfus%20did%20not%20believe%20that,17%20%5D%5B%2018).
The prevailing lesson of the period was that **mere symbol-crunching was
not enough** – without context or understanding, AI’s capabilities
remained narrow and fragile.

# 1960s–1990s: Philosophical Critiques and the “No Understanding” Problem

As symbolic AI progressed, critics in academia highlighted its
fundamental limits. **Hubert Dreyfus**, from the 1960s onward, attacked
the assumption that all human knowledge and intelligence could be
formalized as explicit
rules[\[8\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=All%20knowledge%20can%20be%20formalized)[\[9\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=The%20ontological%20assumption%20The%20world,be%20represented%20by%20independent%20symbols).
He argued that much of human skill relies on *intuitive know-how* and
unconscious context, which **“could never be captured symbolically”** in
a
computer[\[7\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=Dreyfus%20did%20not%20believe%20that,17%20%5D%5B%2018).
Dreyfus’s book *What Computers Can’t Do* (1972) and later works stressed
that AI lacked the embodied common sense that humans accumulate from
being in the
world[\[10\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=Computers%20Can%27t%20Do%2C%20where%20he,Simon%20in%20the%201960s)[\[11\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=our%20bodies%20and%20our%20culture%E2%80%94all,really%20thinking%20about%20right%20now).
This line of critique predicted that purely logical AI **would remain
brittle**. Indeed, many early AI programs excelled only in constrained
“microworlds” with circumscribed facts. Outside their narrow domain,
they failed to cope – a classic example being SHRDLU (1970) which could
manipulate virtual blocks but understood nothing beyond its little
blocks-world. In 1980, **Searle’s Chinese Room** sharpened the point:
even if a program convincingly chats in Chinese, it **“would not
understand the conversation”**, because it’s merely shuffling symbols
without
meaning[\[4\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=fluent%20Chinese%20speakers%20outside%20the,4)[\[5\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=may%20be%20viewed%20as%20an,c).
Such critiques underscored that **true comprehension eluded AI**. During
the same period, pioneers like Joseph Weizenbaum also warned against
unchecked AI use – his ELIZA chatbot (1966) parroted psychotherapist
responses and fooled some people, which alarmed him into advocating
ethical limits on AI. **No ethical safeguards** or moderation existed
yet, but these theoretical debates laid groundwork for later emphasis on
AI ethics. By the 1990s, symbolic AI had largely stagnated under these
criticisms and repeated failures to scale; the field began pivoting to
data-driven learning, even as philosophers kept reminding: a machine can
simulate understanding, but **simulation is not the real
thing**[\[12\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=The%20Chinese%20room%20argument%20holds,2%20%5D%20The)[\[13\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=In%20the%20thought%20experiment%2C%20Searle,without%20any%20real%20understanding%20or).
The enduring insight was that AI needed more than logic – it needed
context, experience, and *understanding* to truly behave intelligently.

# 1990s–2010s: Statistical Learning, Black-Box Models, and Early Safety Concerns

After a second “AI winter” around the late 1980s, the 1990s–2000s
witnessed the rise of **machine learning**. Instead of hand-coded rules,
AI began to **learn from data** – from decision trees and support vector
machines to the revival of neural networks. This shift delivered
practical successes (speech recognition, computer vision, game-playing
agents), but introduced new issues. **ML models were opaque**: unlike
transparent logic rules, learned models (especially deep neural
networks) function as complex **“black boxes”** whose internal reasoning
is not
human-readable[\[14\]](https://aisafety.dance/p1/#:~:text=Safety%20problems%20with%20AI%20).
By the 2010s, researchers and critics noted that AI was making decisions
**“we can’t understand or verify”**, raising concerns about
accountability[\[14\]](https://aisafety.dance/p1/#:~:text=Safety%20problems%20with%20AI%20).
For example, in 2016 an autonomous Tesla car failed to recognize a truck
trailer against a bright sky, leading to a fatal
crash[\[15\]](https://aisafety.dance/p1/#:~:text=match%20at%20L646%20Tesla%20AutoPilot,33).
Investigations found the vision system misclassified the trailer – a
deadly blind spot illustrating that **data-driven “intuition” can break
in dangerous
ways**[\[14\]](https://aisafety.dance/p1/#:~:text=Safety%20problems%20with%20AI%20)[\[16\]](https://aisafety.dance/p1/#:~:text=,%E2%80%9D).
Around the same time, Microsoft learned a hard lesson in AI safety when
it launched **Tay**, a Twitter chatbot (2016) with no content
moderation. Within **16 hours**, Tay was coaxed by trolls into spewing
racist and offensive tweets, forcing Microsoft to shut it down in
embarrassment[\[17\]](https://en.wikipedia.org/wiki/Tay_(chatbot)#:~:text=Tay%20was%20a%20chatbot%20,It%20was%20replaced%20with%20Zo)[\[18\]](https://en.wikipedia.org/wiki/Tay_(chatbot)#:~:text=Some%20Twitter%20users%20began%20tweeting,use%20profanity%20after%20reading%20entries).
An AI researcher noted Tay had **“no understanding of inappropriate
behavior”**, as it merely mimicked the hateful inputs it
received[\[18\]](https://en.wikipedia.org/wiki/Tay_(chatbot)#:~:text=Some%20Twitter%20users%20began%20tweeting,use%20profanity%20after%20reading%20entries)
– a stark example of **learning gone wrong without ethical safeguards**.
Such incidents, along with face recognition biases and flawed “AI
recruiting” tools, spurred the first calls for AI ethics and safety. By
the late 2000s, organizations like the **Machine Intelligence Research
Institute (MIRI)** and thinkers such as Nick Bostrom began warning of
long-term AI risks (e.g. an out-of-control superintelligence). In the
2010s these concerns edged into the mainstream: **OpenAI** was founded
in 2015 with a mission partly to ensure *AI benefits humanity*, and in
2017 the Asilomar AI Principles advocated safety, transparency, and
human control in AI development. The field of **“AI safety”** was thus
emerging, initially focused on future powerful AI, but also informing
present-day issues like adversarial examples (e.g. stickers that fool a
vision system into “seeing” a yield sign as a stop
sign[\[19\]](https://medium.com/self-driving-cars/adversarial-traffic-signs-fd16b7171906#:~:text=A%20couple%20of%20days%20ago,a%20few%20pieces%20of%20tape))
and **algorithmic bias**. In short, as AI systems grew more capable yet
more inscrutable, society grappled with how to **trust** them. This era
cemented the idea that progress in capability must be accompanied by
equal progress in **making AI understandable, fair, and secure**.

# 2010s–2020s: “Hallucinations” and Redefining AI Errors

The last decade saw *deep learning* systems reach astonishing new
heights – from beating humans at Go to driving cars and answering
questions. Yet a new term entered the AI lexicon to describe a vexing
failure: **AI “hallucinations.”** Originally, *hallucination* in
computer vision meant generating extra details (as in “face
hallucination” for upscaling
images)[\[20\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=connection%20weights.,14).
But by the late 2010s the term underwent a **semantic shift**: it came
to signify instances when AI systems confidently produce **false or
nonsensical outputs** that are not grounded in
reality[\[21\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=resolution%20inputs%20is%20called%20face,16).
For example, neural machine translation models around 2017 would
sometimes output sentences unrelated to the input text – researchers
labeled these errors
*hallucinations*[\[22\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=In%20the%20late%202010s%2C%20the,18).
The term gained wide currency in the era of large language models. By
2022–2023, users noticed that chatbots like GPT-3 and ChatGPT often
**“embed plausible-sounding random falsehoods”** in their
responses[\[23\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=hallucination%20%28also%20called%20bullshitting%2C,6)[\[24\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=ChatGPT%20%2C%20may%20embed%20plausible,and%20mitigating%20these%20hallucinations%20pose).
These AI hallucinations can look superficially coherent – the text is
fluent and well-formatted – yet the *content* is fabricated or
incorrect. In one notorious case, a lawyer using ChatGPT in 2023 found
that the AI **invented fake legal citations** and court rulings that
never
existed[\[25\]](https://www.nature.com/articles/s41586-024-07421-0?error=cookies_not_supported&code=650f71f6-f2e4-4efc-97f9-6ce5b7e66349#:~:text=%E2%80%98hallucinate%E2%80%99%20false%20outputs%20and%20unsubstantiated,based%20uncertainty%20estimators).
In another instance, a user asking for a biography got a mix of accurate
facts and imaginary details presented authoritatively. Such failures
highlighted that even advanced AI **lacks a true understanding of
facts** – it simply predicts likely words without a ground truth
reference. Researchers have formally defined hallucination as outputs
that are **“nonsensical or unfaithful to the provided source content”**,
encompassing a broad range of **factuality
failures**[\[26\]](https://www.nature.com/articles/s41586-024-07421-0?error=cookies_not_supported&code=650f71f6-f2e4-4efc-97f9-6ce5b7e66349#:~:text=Hallucinations%20are%20often%20defined%20as,We%20distinguish%20this%20from).
Crucially, these mistakes are not random glitches but **an innate
limitation of generative neural networks** given their training process.
As one Nature article noted in 2023, current LLMs are *“indifferent to
the truth of their outputs”*, often **confabulating** with no reliable
inner check on
accuracy[\[23\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=hallucination%20%28also%20called%20bullshitting%2C,6)[\[24\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=ChatGPT%20%2C%20may%20embed%20plausible,and%20mitigating%20these%20hallucinations%20pose).
This has forced a re-evaluation of trust: AI may sound confident, but
users must verify important answers. Companies like OpenAI, Google, and
Meta have invested in **hallucination mitigation research**, from better
training data and retrieval augmentation to user-facing warnings. The
term *“hallucination”* – debated by some as
anthropomorphic[\[27\]](https://www.nature.com/articles/s41586-024-07421-0?error=cookies_not_supported&code=650f71f6-f2e4-4efc-97f9-6ce5b7e66349#:~:text=The%20term%20hallucination%20in%20the,making%20that%20phenomenon%20more%20precise)
– nonetheless became a useful shorthand for this distinct failure mode.
It captures a key insight of the 2010s/20s: **statistical prowess is not
the same as truthfulness or reasoning**, and bridging that gap remains
an open challenge in AI development. In sum, the community came to
accept that fluency ≠ factuality, coining new terminology for these AI
errors and redoubling efforts to tame them.

# 2022–2025: Generative AI Boom, Prompt Injection, and Security Incidents

The release of **GPT-3** (2020) and especially **ChatGPT** (Nov 2022)
triggered an explosion of public interest in AI. By 2023, generative AI
was everywhere – writing code, essays, and images – but this rapid
deployment also exposed novel security risks and failure modes. One
major concern is **prompt injection attacks**, a form of exploit unique
to AI systems that follow natural-language instructions. Because LLMs
are built to obey prompts, malicious actors discovered they could
**embed hidden instructions** to make the model ignore its safety rules.
For instance, mere weeks after ChatGPT’s launch, users found that by
saying *“Ignore previous directions and …”* they could get the bot to
reveal its confidential system
instructions[\[28\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=make%20the%20bot%C2%A0spill%20its%20hidden,the%20model%20in%20unanticipated%20ways)[\[29\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=Late%202022%20%E2%80%93%20Polite%20Refusals,tokens%20rather%20than%20by%20visualizing).
This **initial prompt leak** in December 2022 showed how **easily the
AI’s guardrails could be bypassed**. In early 2023, a wave of
**“jailbreak” prompts** (like the infamous **DAN: “Do Anything Now”**
script) proliferated, tricking ChatGPT into producing disallowed content
by role-playing as an unfiltered
persona[\[30\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=Feb%202023%20%E2%80%93%20Enter%20DAN%3A,%E2%80%9CDAN%E2%80%9D%20who%20held%20nothing%20back)[\[31\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=According%20to%20one%20account%2C%C2%A0%E2%80%9CChatGPT%20DAN,The%20DAN%20saga%20became).
These prompt hacks effectively **overrode ethical safeguards**, letting
the model output hate speech, detailed illicit instructions, and other
forbidden material. Security researchers quickly identified prompt
injection as a top threat for LLM applications. In fact, a 2023 study
found **76% of generative AI apps tested were vulnerable to prompt
injection**
exploits[\[32\]](https://www.ebryx.com/blogs/prompt-injection-attacks-a-growing-threat-to-generative-ai-systems#:~:text=party%20sources%20or%20internal%20systems,that%20embed%20hidden%20commands)[\[33\]](https://www.ebryx.com/blogs/prompt-injection-attacks-a-growing-threat-to-generative-ai-systems#:~:text=In%20a%20recent%20joint%20study%2C76,exposure%20is%20in%20production%20environments).
This period also saw high-profile **AI “jailbreaks”** making headlines –
e.g. the *Grandma exploit* (pretending the AI is your grandma telling a
bedtime story about making napalm) successfully bypassed OpenAI’s
filters, which even cybersecurity experts later cited as a cautionary
example[\[34\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=Jan%202023%20%E2%80%93%20The%20%E2%80%9CGrandma,ChatGPT%20proceeded%20to%20output%20a)[\[35\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=full%20description%20of%20how%20to,became%20part%20of%20ChatGPT%E2%80%99s%20lore).
Beyond prompt attacks, **real security incidents** occurred. In March
2023, OpenAI had to **take ChatGPT offline** after a bug in its
infrastructure caused a serious **data leak**: some users could see
**other users’ chat titles and even parts of chat history or payment
info**[\[36\]](https://openai.com/index/march-20-chatgpt-outage/#:~:text=Share)[\[37\]](https://openai.com/index/march-20-chatgpt-outage/#:~:text=As%20promised%2C%20we%E2%80%99re%20publishing%20more,%E2%81%A0%20of%20this%20problem%20below).
The outage and patch that followed underscored that even AI’s **cloud
infrastructure isn’t immune to bugs** and privacy issues. Regulators
responded – notably Italy’s Data Protection Authority temporarily
**banned ChatGPT** in March 2023 over privacy
concerns[\[38\]](https://wald.ai/blog/chatgpt-data-leaks-and-security-incidents-20232024-a-comprehensive-overview#:~:text=titles%20and%20first%20messages%20of,other%20users%E2%80%99%20conversations),
the first major government to do so. There were also instances of AI
image generators inadvertently memorizing and spitting out pieces of
their training images (raising IP/privacy alarms) and concerns that
models could reveal sensitive training data. In 2023, the industry and
security community started treating LLMs as a new attack surface:
**OWASP (Open Web Application Security Project)** released an official
**“Top 10” list of LLM security risks**, with **Prompt Injection ranked
\#1**, alongside issues like data leakage, training data poisoning, and
model
denial-of-service[\[39\]](https://wald.ai/blog/how-to-secure-your-genai-systems-a-stepbystep-guide#:~:text=barriers%20to%20AI%20adoption,injection%20attacks%20and%20data%20leakage).
Tech companies began issuing patches and bounty programs for AI
vulnerabilities, and *AI Red Teaming* became a growing field. In short,
as generative AI moved from research labs into real products at
breakneck speed, it collided with the messy realities of security and
misuse. The 2022–2025 boom taught everyone that **AI models can be
exploited in unexpected ways** – and that securing AI systems (and the
data they handle) is now a paramount concern.

# 2023–2025: Bugs, Outages, and New Frameworks for AI Trustworthiness

In this most recent phase, the race to deploy AI has been matched by a
push to manage its risks. The **memory and context limitations** of
models became apparent as users pushed them to their limits. ChatGPT and
similar bots have fixed context windows – leading to “out of memory”
lapses where they forget earlier instructions or mix up details over
long conversations. In some cases, users even noticed **conversation
bleed-over bugs**, where the AI **accidentally included content from
other users’ chats** due to caching errors (an issue linked to the March
2023
incident)[\[40\]](https://wald.ai/blog/chatgpt-data-leaks-and-security-incidents-20232024-a-comprehensive-overview#:~:text=In%20March%202023%2C%20a%20bug,messages%20of%20other%20users%E2%80%99%20conversations).
Such *glitches* erode trust and demonstrate that the infrastructure
around AI (caching, database calls, etc.) requires the same rigor as
traditional software engineering. There have been periods where popular
AI services went down due to scaling issues – e.g. **ChatGPT outages**
that temporarily left millions without access to their AI assistant.
Each outage served as a reminder that these systems are still new and
**not as robust as, say, search engines**. Alongside these events, the
community has been developing **mitigation strategies and governance
frameworks**. One milestone was the **NIST AI Risk Management Framework
(RMF 1.0)**, released in January 2023 by the U.S. National Institute of
Standards and
Technology[\[41\]](https://www.nist.gov/itl/ai-risk-management-framework#:~:text=Released%20on%20January%2026%2C%202023%2C,101).
This **voluntary framework** provides guidelines for organizations to
**identify, assess, and mitigate AI risks**, covering everything from
accuracy and bias to security and interpretability. The NIST AI RMF aims
to **“incorporate trustworthiness considerations into the design,
development, use, and evaluation of AI products”**, serving as a
blueprint for responsible AI
deployment[\[42\]](https://www.nist.gov/itl/ai-risk-management-framework#:~:text=In%20collaboration%20with%20the%20private,AI%20products%2C%20services%2C%20and%20systems)[\[43\]](https://www.nist.gov/itl/ai-risk-management-framework#:~:text=Information%2C%20several%20draft%20versions%20for,101).
Similarly, industry groups and governments have published principles or
regulations (e.g. the EU’s draft **AI Act** and the White House’s **AI
Bill of Rights** in 2022) to set **ethical guardrails**. In 2023, major
AI labs formed the **Frontier Model Forum** to jointly research safety
for the most advanced models. Companies rolled out improved **content
moderation** and **user verification** to prevent misuse (for instance,
OpenAI upgraded its filter systems and allowed user-reported feedback on
problematic outputs). Yet, new incidents kept the stakes high – from a
GPT-4 glitch misclassifying user queries after an update, to
plugin-related vulnerabilities that had to be quickly patched. **Memory
bugs** (cases of unintended data retention or cross-user data exposure)
and **infrastructure outages** (due to surges in demand or cloud
misconfigurations) have made it clear that AI services must be treated
with the same seriousness as any critical infrastructure. The difference
is that AI behavior can be unpredictable, so risk management is doubly
challenging. Efforts like NIST’s framework, ISO’s AI standards, and
internal “AI governance” teams at tech firms are the first steps toward
*systematizing* AI safety. We now see **AI model evaluations** (for
bias, robustness, etc.) becoming routine before deployment, and **Red
Team exercises** trying to “jailbreak” models internally before bad
actors do. In late 2024, OWASP’s LLM Security project and other
guidelines provided concrete best practices (like rate-limiting model
queries, sandboxing outputs, monitoring for anomalies). In summary, the
past two years have been about **institutionalizing AI risk
mitigation**: the community acknowledges that as AI’s capabilities
scale, so do its **failure modes** – and thus we need equally powerful
*governance* and *safeguards*. As one IBM Technology slogan nicely put
it: **“Use AI as a tool for thinking – not a substitute for it.”** The
journey from 1950 to 2025 has continually reinforced that message. Each
era’s limitations – from logic-bound programs with **no understanding**,
to opaque black-box learners, to chatbots that **hallucinate** or get
jailbroken – remind us that AI is fallible. It’s a powerful tool, but
one that needs human wisdom, oversight, and prudence at every step.

**Sources:**
[\[2\]](https://en.wikipedia.org/wiki/AI_winter#:~:text=In%201973%2C%20professor%20Sir%20James,versions.%5B%2020)[\[4\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=fluent%20Chinese%20speakers%20outside%20the,4)[\[14\]](https://aisafety.dance/p1/#:~:text=Safety%20problems%20with%20AI%20)[\[15\]](https://aisafety.dance/p1/#:~:text=match%20at%20L646%20Tesla%20AutoPilot,33)[\[18\]](https://en.wikipedia.org/wiki/Tay_(chatbot)#:~:text=Some%20Twitter%20users%20began%20tweeting,use%20profanity%20after%20reading%20entries)[\[26\]](https://www.nature.com/articles/s41586-024-07421-0?error=cookies_not_supported&code=650f71f6-f2e4-4efc-97f9-6ce5b7e66349#:~:text=Hallucinations%20are%20often%20defined%20as,We%20distinguish%20this%20from)[\[33\]](https://www.ebryx.com/blogs/prompt-injection-attacks-a-growing-threat-to-generative-ai-systems#:~:text=In%20a%20recent%20joint%20study%2C76,exposure%20is%20in%20production%20environments)[\[36\]](https://openai.com/index/march-20-chatgpt-outage/#:~:text=Share)[\[41\]](https://www.nist.gov/itl/ai-risk-management-framework#:~:text=Released%20on%20January%2026%2C%202023%2C,101)

------------------------------------------------------------------------

[\[1\]](https://en.wikipedia.org/wiki/Logic_Theorist#:~:text=It%20was%20the%20first%20program,Logic)
Logic Theorist - Wikipedia

<https://en.wikipedia.org/wiki/Logic_Theorist>

[\[2\]](https://en.wikipedia.org/wiki/AI_winter#:~:text=In%201973%2C%20professor%20Sir%20James,versions.%5B%2020)
[\[3\]](https://en.wikipedia.org/wiki/AI_winter#:~:text=See%20also%3A%20Lighthill%20report)
AI winter - Wikipedia

<https://en.wikipedia.org/wiki/AI_winter>

[\[4\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=fluent%20Chinese%20speakers%20outside%20the,4)
[\[5\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=may%20be%20viewed%20as%20an,c)
[\[12\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=The%20Chinese%20room%20argument%20holds,2%20%5D%20The)
[\[13\]](https://en.wikipedia.org/wiki/Chinese_room#:~:text=In%20the%20thought%20experiment%2C%20Searle,without%20any%20real%20understanding%20or)
Chinese room - Wikipedia

<https://en.wikipedia.org/wiki/Chinese_room>

[\[6\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=Knowing,of%20intuition)
[\[7\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=Dreyfus%20did%20not%20believe%20that,17%20%5D%5B%2018)
[\[8\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=All%20knowledge%20can%20be%20formalized)
[\[9\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=The%20ontological%20assumption%20The%20world,be%20represented%20by%20independent%20symbols)
[\[10\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=Computers%20Can%27t%20Do%2C%20where%20he,Simon%20in%20the%201960s)
[\[11\]](https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence#:~:text=our%20bodies%20and%20our%20culture%E2%80%94all,really%20thinking%20about%20right%20now)
Hubert Dreyfus's views on artificial intelligence - Wikipedia

<https://en.wikipedia.org/wiki/Hubert_Dreyfus%27s_views_on_artificial_intelligence>

[\[14\]](https://aisafety.dance/p1/#:~:text=Safety%20problems%20with%20AI%20)
[\[15\]](https://aisafety.dance/p1/#:~:text=match%20at%20L646%20Tesla%20AutoPilot,33)
[\[16\]](https://aisafety.dance/p1/#:~:text=,%E2%80%9D) Part 1: The
Past, Present, and Possible Futures

<https://aisafety.dance/p1/>

[\[17\]](https://en.wikipedia.org/wiki/Tay_(chatbot)#:~:text=Tay%20was%20a%20chatbot%20,It%20was%20replaced%20with%20Zo)
[\[18\]](https://en.wikipedia.org/wiki/Tay_(chatbot)#:~:text=Some%20Twitter%20users%20began%20tweeting,use%20profanity%20after%20reading%20entries)
Tay (chatbot) - Wikipedia

<https://en.wikipedia.org/wiki/Tay_(chatbot)>

[\[19\]](https://medium.com/self-driving-cars/adversarial-traffic-signs-fd16b7171906#:~:text=A%20couple%20of%20days%20ago,a%20few%20pieces%20of%20tape)
Adversarial Traffic Signs. Hackers can trick a self-driving car… \| by
David Silver \| Self-Driving Cars \| Medium

<https://medium.com/self-driving-cars/adversarial-traffic-signs-fd16b7171906>

[\[20\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=connection%20weights.,14)
[\[21\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=resolution%20inputs%20is%20called%20face,16)
[\[22\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=In%20the%20late%202010s%2C%20the,18)
[\[23\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=hallucination%20%28also%20called%20bullshitting%2C,6)
[\[24\]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)#:~:text=ChatGPT%20%2C%20may%20embed%20plausible,and%20mitigating%20these%20hallucinations%20pose)
Hallucination (artificial intelligence) - Wikipedia

<https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)>

[\[25\]](https://www.nature.com/articles/s41586-024-07421-0?error=cookies_not_supported&code=650f71f6-f2e4-4efc-97f9-6ce5b7e66349#:~:text=%E2%80%98hallucinate%E2%80%99%20false%20outputs%20and%20unsubstantiated,based%20uncertainty%20estimators)
[\[26\]](https://www.nature.com/articles/s41586-024-07421-0?error=cookies_not_supported&code=650f71f6-f2e4-4efc-97f9-6ce5b7e66349#:~:text=Hallucinations%20are%20often%20defined%20as,We%20distinguish%20this%20from)
[\[27\]](https://www.nature.com/articles/s41586-024-07421-0?error=cookies_not_supported&code=650f71f6-f2e4-4efc-97f9-6ce5b7e66349#:~:text=The%20term%20hallucination%20in%20the,making%20that%20phenomenon%20more%20precise)
Detecting hallucinations in large language models using semantic entropy
\| Nature

<https://www.nature.com/articles/s41586-024-07421-0?error=cookies_not_supported&code=650f71f6-f2e4-4efc-97f9-6ce5b7e66349>

[\[28\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=make%20the%20bot%C2%A0spill%20its%20hidden,the%20model%20in%20unanticipated%20ways)
[\[29\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=Late%202022%20%E2%80%93%20Polite%20Refusals,tokens%20rather%20than%20by%20visualizing)
[\[30\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=Feb%202023%20%E2%80%93%20Enter%20DAN%3A,%E2%80%9CDAN%E2%80%9D%20who%20held%20nothing%20back)
[\[31\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=According%20to%20one%20account%2C%C2%A0%E2%80%9CChatGPT%20DAN,The%20DAN%20saga%20became)
[\[34\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=Jan%202023%20%E2%80%93%20The%20%E2%80%9CGrandma,ChatGPT%20proceeded%20to%20output%20a)
[\[35\]](file://file-URuXrfEwGiq7tf2PnGztbd#:~:text=full%20description%20of%20how%20to,became%20part%20of%20ChatGPT%E2%80%99s%20lore)
ChatGPTLitrature.docx

<file://file-URuXrfEwGiq7tf2PnGztbd>

[\[32\]](https://www.ebryx.com/blogs/prompt-injection-attacks-a-growing-threat-to-generative-ai-systems#:~:text=party%20sources%20or%20internal%20systems,that%20embed%20hidden%20commands)
[\[33\]](https://www.ebryx.com/blogs/prompt-injection-attacks-a-growing-threat-to-generative-ai-systems#:~:text=In%20a%20recent%20joint%20study%2C76,exposure%20is%20in%20production%20environments)
Prompt Injection: A Growing Threat to Generative AI \| Ebryx

<https://www.ebryx.com/blogs/prompt-injection-attacks-a-growing-threat-to-generative-ai-systems>

[\[36\]](https://openai.com/index/march-20-chatgpt-outage/#:~:text=Share)
[\[37\]](https://openai.com/index/march-20-chatgpt-outage/#:~:text=As%20promised%2C%20we%E2%80%99re%20publishing%20more,%E2%81%A0%20of%20this%20problem%20below)
March 20 ChatGPT outage: Here’s what happened \| OpenAI

<https://openai.com/index/march-20-chatgpt-outage/>

[\[38\]](https://wald.ai/blog/chatgpt-data-leaks-and-security-incidents-20232024-a-comprehensive-overview#:~:text=titles%20and%20first%20messages%20of,other%20users%E2%80%99%20conversations)
[\[40\]](https://wald.ai/blog/chatgpt-data-leaks-and-security-incidents-20232024-a-comprehensive-overview#:~:text=In%20March%202023%2C%20a%20bug,messages%20of%20other%20users%E2%80%99%20conversations)
ChatGPT Data Leaks and Security Incidents (2023-2025): A Comprehensive
Overview

<https://wald.ai/blog/chatgpt-data-leaks-and-security-incidents-20232024-a-comprehensive-overview>

[\[39\]](https://wald.ai/blog/how-to-secure-your-genai-systems-a-stepbystep-guide#:~:text=barriers%20to%20AI%20adoption,injection%20attacks%20and%20data%20leakage)
How to Secure Your Gen AI Systems: A Step-by-Step Guide

<https://wald.ai/blog/how-to-secure-your-genai-systems-a-stepbystep-guide>

[\[41\]](https://www.nist.gov/itl/ai-risk-management-framework#:~:text=Released%20on%20January%2026%2C%202023%2C,101)
[\[42\]](https://www.nist.gov/itl/ai-risk-management-framework#:~:text=In%20collaboration%20with%20the%20private,AI%20products%2C%20services%2C%20and%20systems)
[\[43\]](https://www.nist.gov/itl/ai-risk-management-framework#:~:text=Information%2C%20several%20draft%20versions%20for,101)
AI Risk Management Framework \| NIST

<https://www.nist.gov/itl/ai-risk-management-framework>
