"""
Postprocessing Module (for LLM Output):

Responsibilities:
Takes the raw output from the LLM.
Performs any necessary cleaning (e.g., removing boilerplate text the LLM might add, fixing minor formatting issues).
Could also involve extracting structured information if the LLM was prompted to produce it.
Formats the final answer for presentation to the user.
Why it's needed: To ensure the final answer is clean, presentable, and directly usable.
"""