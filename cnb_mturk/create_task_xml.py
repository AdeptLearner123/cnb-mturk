from xml.dom import minidom

def create_task_xml(word_pairs):
    with open("question_form.xml", "r") as file:
        question_form = file.read()
    
    question_xmls = [ create_pair_xml(i, word1, word2) for i, (word1, word2) in enumerate(word_pairs) ]
    question_xmls = "\n".join(question_xmls)
    question_form = question_form.replace("$QUESTIONS", question_xmls)
    return question_form


def create_pair_xml(i, word1, word2):
    with open("question.xml", "r") as file:
        question_xml = file.read()
    question_xml = question_xml.replace("$TITLE", f"Pair {i}: {word1}, {word2}")
    question_xml = question_xml.replace("$CLUE_IDENTIFIER", f"pair_{i}_clue")
    question_xml = question_xml.replace("$EXPLANATION_1_IDENTIFIER", f"pair_{i}_explanation1")
    question_xml = question_xml.replace("$EXPLANATION_1_LABEL", f"Explanation for why {word1} is related to this clue:")
    question_xml = question_xml.replace("$EXPLANATION_2_IDENTIFIER", f"pair_{i}_explanation2")
    question_xml = question_xml.replace("$EXPLANATION_2_LABEL", f"Explanation for why {word2} is related to this clue:")
    return question_xml