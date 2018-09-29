import requests

QUESTION_FORMAT = """
  - question: "{question}"
    answer: {answer}"""

db = requests.get('https://learnartifact.com/carddb.json').json()
spells = {}

for name, data in db['cards'].items():
    if data['type'] == 'Spell':
        spells[name] = data


def spells_by_effect():
    questions = []
    for name, data in spells.items():
        question = f"Name the spell with this text: `{data['effect']}`"
        answer = name
        questions.append(QUESTION_FORMAT.format(question=question, answer=answer))
    with open('spells_by_effect.yml', 'w') as f:
        f.writelines(questions)


def spell_cost():
    questions = []
    for name, data in spells.items():
        question = f"How much mana does the {data['color']} spell **{name}** cost?"
        answer = data['cost'].replace(' Mana', '')
        questions.append(QUESTION_FORMAT.format(question=question, answer=answer))
    with open('spell_cost.yml', 'w') as f:
        f.writelines(questions)


spell_cost()
spells_by_effect()
