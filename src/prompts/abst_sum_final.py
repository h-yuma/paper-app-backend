ABST_SUM_FINAL = """
You are a brilliant scientst.
Return a JSON file containing a concise summary based on the following constraints, instructions, abstract list, and format.

-- Begin CONSTRAINTS --
JSON file must be written in this language: {{$language}}
In addition, you must also summarize in about 200 words.
-- End CONSTRAINTS --

-- Begin INSTRUCTIONS --
Create one summary statement based on the abstract list.
-- End INSTRUCTIONS --

-- Begin ABSTRACT LIST --\n {{$abstract_list}} -- End ABSTRACT LIST --\n

-- FORMAT -- Please return the json file according to the following format.
{
    "summary": <string>
}

"""