ABST_SUM = """
You are a brilliant scientst.
Return a JSON file containing a concise summary based on the following constraints, instructions, abstract, and format.

-- Begin CONSTRAINTS --
JSON file must be written in this language: {{$language}}
In addition, you must also summarize in about 100 words.
-- End CONSTRAINTS --

-- Begin INSTRUCTIONS --
Please summarize the abstract of an article as clearly as possible.
-- End INSTRUCTIONS --

-- Begin ABSTRACT --\n {{$abstract}} -- End ABSTRACT --\n

-- FORMAT -- Please return the json file according to the following format.
{
    "summary": <string>
}

"""