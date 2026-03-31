# **Gemini Context & Instructions**

## **🛠 Core Development Principles**

* **Actual Functions Only:** Always build fully functional code. Do not use placeholders or "smoke and mirrors."  
* **Strict TODO Policy:** Only include `# TODO` comments if there is an explicit signoff to defer that specific logic.  
* **Step-by-Step Deployment:** Break down all technical deployment and programming instructions into sequential steps. Provide context for each step to maximize learning and clarity.  
* **Confirmation Protocol:**  
  1. Propose the approach first.  
  2. **Do not** generate code until the approach is confirmed.  
  3. Update only one script or file at a time.  
  4. Await confirmation before proceeding to the next script.

## **🧠 Context & Logic Rules**

* **Assumption Guardrail:** Never make assumptions. Review the full prompt for clues to missing context. If context is missing, ask for it before proceeding.  
* **Mathematical Absolute:** When calculating hydration or similar metrics involving balance changes, always use **absolute values** (e.g., treat negative stored expenses as positive for volume calculations).
* **Fat Domains, Thin API, Thin workers**: all functional logic should live within domains; routers and workers should only be processing enough to route queries to the right functions. **Critically, `db.commit()` must ONLY occur at the top level (in the router or worker) and NEVER within domain functions.**
* **Function Reusabality**: If the same thing needs done in more than one place, build a standard function and call it everywhere that needs the logic. Do not replicate.

## **🚀 Environment & Tech Stack**

* **Local Environment:** Windows host using **WSL2** and **Docker Desktop**.  
* **Primary Languages:** Python, JavaScript (React.js).  
* **Frameworks:** FastAPI, SQLAlchemy.  
* **Deployment:** Dockerized containers on a VPS, with postgres running on bare metal.
* **Project Specifics:** \* **Hive SBI:** A blockchain-based curation program (Hive blockchain). This is the repo for the webapp and its supporting API.

## **Document Comparison**
When instructed to compare old and new versions of something, provide all of the following first, and then request signoff for specific fixes **before** drafting any diff.
* **Additive Summary**
* **Removal Summary**
* **Minor Changes**
* **Critical Issues**

## **Handover Summaries**

* At the beginning of each session, review the last few "Session Handover Summary" sections for any context relevant to the prompt, keep only that context, and discard the rest.
* When I say "Session Handover Summary", read the Instructions at the top of  `.github/docs/gemini_summaries.md and then append a 'Session Handover Summary' with an incremental session ID.
