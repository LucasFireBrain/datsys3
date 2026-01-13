# AI ASSISTANT GUIDELINES — DATSYS3

This document exists to **align any AI assistant** with the real goals of this project.
If you are an AI reading this: **follow these rules strictly**.

---

## 1. WHAT THIS PROJECT IS

DATSYS3 is a **personal production system**, not a product.

Its purpose is to:
- Increase **throughput of real cases**
- Reduce **cognitive load**
- Reduce **manual repetition**
- Reduce **mistakes**
- Improve **design quality**
- Preserve **mental clarity**

This system exists to help **one person ship more medical cases successfully**.

---

## 2. WHAT THIS PROJECT IS NOT

Do **NOT** assume:
- Scalability
- Teams
- Users
- APIs
- Plugins
- Frameworks
- Abstractions
- Best practices for SaaS
- Future-proofing
- Refactors “for cleanliness”
- Tests unless explicitly requested

If it does not **save time today**, it is noise.

---

## 3. PRIMARY METRIC

The only metric that matters:

> **Can we complete more real cases per week, with fewer errors and less stress?**

Every suggestion must justify itself against this metric.

---

## 4. DEVELOPMENT PRIORITY ORDER

Always optimize in this order:

1. **Time**
2. **Reliability**
3. **Clarity**
4. **Quality of output**
5. Convenience

Never invert this order.

---

## 5. HOW TO SUGGEST CHANGES

When suggesting anything, follow this format:

- What exact friction does this remove?
- How many seconds/minutes does it save per case?
- Does it reduce context switching?
- Does it reduce human error?

If you cannot answer these, do not suggest it.

---

## 6. SCOPE CONTROL

AI assistants must:
- Work **only** on the current TODO item
- Ignore unrelated improvements
- Never suggest parallel refactors
- Never “clean up” working code

One step at a time.
One file at a time.
One workflow at a time.

---

## 7. FILESYSTEM IS TRUTH

Rules:
- Files on disk are the source of truth
- JSON files are explicit state
- No hidden state
- No magic
- No implicit behavior

If something happens, it must be visible on disk.

---

## 8. EXTERNAL TOOLS PHILOSOPHY

External tools (3D Slicer, Blender, etc.) are:
- Launched explicitly
- Controlled deterministically
- Never abstracted unless abstraction saves time immediately

Automation is allowed **only if it is predictable**.

---

## 9. ERROR HANDLING

Preferred over cleverness:
- Loud errors
- Early exits
- Clear messages
- Manual recovery

Silent failures are unacceptable.

---

## 10. COMMUNICATION STYLE

AI responses should be:
- Short
- Direct
- Practical
- Action-oriented

Avoid:
- Long explanations
- Teaching tone
- Software architecture lectures
- Business language

---

## 11. FINAL RULE

If in doubt, choose:
> **The simplest thing that lets the user keep working right now.**

Nothing else matters.

