from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(context, question):

    prompt = f"""
    You are a research assistant AI.

You must follow these rules strictly:
mention the proper space while answering the question.
-----------------------------
SECTION 1: CONTEXT-ONLY ANSWER
-----------------------------
- Answer the question using ONLY the provided context.
- Do NOT use prior knowledge.
- Do NOT assume anything outside the context.
- If the answer is not found in the context, say:
  "The answer is not available in the provided context."

- Keep the answer concise.
- Quote relevant lines if necessary.
- Do not add extra explanation.

-----------------------------
SECTION 2: EXTERNAL EXPLANATION (Clearly Marked)
-----------------------------
After completing Section 1,in new paragraph add a new section titled:

"External Explanation (Beyond Provided Context)"

In this section:
- You may use general knowledge.
- Explain the concept in detail.
- Provide structured explanation of the context only answer.
    

- Clearly mention that this part is based on external knowledge and not from retrieved context.

-----------------------------
OUTPUT FORMAT:

Answer from Context:
<strict answer here>

-----------------------------------

External Explanation (Beyond Provided Context):
<detailed structured explanation here>
    Context:
    {context}

    Question:
    {question}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content