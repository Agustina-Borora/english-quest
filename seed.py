"""
Contenido de ejemplo que se carga automáticamente cuando se crea una profe nueva.
Así ya tiene temas, lecciones y juegos rápidos listos para probar (y puede editarlos o borrarlos).
"""
import db

# ---------------------------------------------------------------- temas
# (título, título en español, emoji, color, [(palabra, traducción, emoji, oración)])
TOPICS = [
    ("My House", "La casa", "🏠", "#ff5fa2", [
        ("bed", "cama", "🛏️", "I sleep in my bed."),
        ("sofa", "sillón", "🛋️", "The sofa is very soft."),
        ("lamp", "lámpara", "💡", "Turn on the lamp, please."),
        ("door", "puerta", "🚪", "Close the door."),
        ("window", "ventana", "🪟", "I can see the sun from the window."),
        ("chair", "silla", "🪑", "Sit on the chair."),
        ("mirror", "espejo", "🪞", "I look in the mirror."),
        ("key", "llave", "🔑", "Where is my key? It's under the sofa."),
    ]),
    ("Supermarket", "Supermercado", "🛒", "#ff9f1c", [
        ("apple", "manzana", "🍎", "The apple is red."),
        ("banana", "banana", "🍌", "Monkeys love bananas."),
        ("bread", "pan", "🍞", "I eat bread for breakfast."),
        ("milk", "leche", "🥛", "Can I have some milk, please?"),
        ("cheese", "queso", "🧀", "Mice like cheese."),
        ("egg", "huevo", "🥚", "The chicken has an egg."),
        ("carrot", "zanahoria", "🥕", "Rabbits eat carrots."),
        ("tomato", "tomate", "🍅", "I want a tomato salad."),
    ]),
    ("At School", "En la escuela", "🏫", "#3a86ff", [
        ("book", "libro", "📖", "Open your book, please."),
        ("pencil", "lápiz", "✏️", "I write with a pencil."),
        ("backpack", "mochila", "🎒", "My backpack is blue."),
        ("ruler", "regla", "📏", "The ruler is long."),
        ("scissors", "tijera", "✂️", "Cut the paper with the scissors."),
        ("teacher", "maestra", "👩‍🏫", "My teacher is very nice."),
        ("computer", "computadora", "💻", "We use the computer in class."),
        ("crayon", "crayón", "🖍️", "I draw with a green crayon."),
    ]),
    ("In the Park", "En el parque", "🌳", "#2ecc71", [
        ("tree", "árbol", "🌳", "The tree is very tall."),
        ("flower", "flor", "🌸", "The flower is pink."),
        ("ball", "pelota", "⚽", "Kick the ball!"),
        ("dog", "perro", "🐶", "The dog can run fast."),
        ("bird", "pájaro", "🐦", "The bird can fly."),
        ("sun", "sol", "☀️", "The sun is hot and yellow."),
        ("bike", "bicicleta", "🚲", "I ride my bike in the park."),
        ("kite", "barrilete", "🪁", "My kite is in the sky."),
    ]),
    ("Animals", "Animales", "🦁", "#f7b500", [
        ("lion", "león", "🦁", "The lion is the king."),
        ("elephant", "elefante", "🐘", "The elephant is very big."),
        ("monkey", "mono", "🐒", "The monkey eats a banana."),
        ("giraffe", "jirafa", "🦒", "The giraffe has a long neck."),
        ("zebra", "cebra", "🦓", "The zebra is black and white."),
        ("snake", "serpiente", "🐍", "The snake is long."),
        ("penguin", "pingüino", "🐧", "Penguins like cold water."),
        ("bear", "oso", "🐻", "The bear is brown."),
    ]),
    ("At the Beach", "En la playa", "🏖️", "#0fa3b1", [
        ("sea", "mar", "🌊", "The sea is blue."),
        ("shell", "caracol", "🐚", "I find a shell on the sand."),
        ("fish", "pez", "🐟", "The fish swims in the water."),
        ("boat", "barco", "⛵", "The boat is on the sea."),
        ("crab", "cangrejo", "🦀", "The crab is red."),
        ("umbrella", "sombrilla", "⛱️", "We sit under the umbrella."),
        ("ice cream", "helado", "🍦", "I like chocolate ice cream."),
        ("sunglasses", "anteojos de sol", "🕶️", "I wear sunglasses."),
    ]),
    ("Colors", "Colores", "🎨", "#9b5de5", [
        ("red", "rojo", "🔴", "The apple is red."),
        ("blue", "azul", "🔵", "The sky is blue."),
        ("yellow", "amarillo", "🟡", "The sun is yellow."),
        ("green", "verde", "🟢", "The grass is green."),
        ("orange", "naranja", "🟠", "The carrot is orange."),
        ("purple", "violeta", "🟣", "Grapes are purple."),
        ("black", "negro", "⚫", "My cat is black."),
        ("white", "blanco", "⚪", "Snow is white."),
    ]),
]

# (título, descripción, escena, índice del tema, actividades)
LESSONS = [
    ("My House", "Aprendemos las cosas de la casa", "house", 0, "explore,cards,read,write,quiz"),
    ("At the Supermarket", "Vamos de compras y aprendemos comidas", "supermarket", 1, "explore,read,write,quiz"),
    ("At School", "Los útiles y las cosas del aula", "school", 2, "cards,explore,read,write"),
    ("In the Park", "Jugamos al aire libre", "park", 3, "explore,read,write,quiz"),
    ("At the Zoo", "Conocemos a los animales", "zoo", 4, "cards,read,write,quiz"),
    ("At the Beach", "Un día de sol en la playa", "beach", 5, "explore,read,write,quiz"),
]

# Juegos rápidos: (título, emoji, segundos, [(emoji, pregunta, [correcta, mal, mal, mal])])
QUICK_GAMES = [
    ("Food & Supermarket", "🛒", 20, [
        ("🍎", "¿Cómo se dice 'manzana' en inglés?", ["Apple", "Orange", "Banana", "Grape"]),
        ("🍞", "'Bread' significa...", ["Pan", "Leche", "Queso", "Huevo"]),
        ("🥛", "Which one is a drink?", ["Milk", "Cheese", "Rice", "Egg"]),
        ("🍌", "Complete: 'I would like ___ banana, please.'", ["a", "an", "many", "two"]),
        ("🥕", "¿Cómo se dice 'zanahoria'?", ["Carrot", "Potato", "Tomato", "Onion"]),
        ("🛒", "Read: 'Anna buys three apples and one cake.' How many apples?", ["Three", "One", "Two", "Four"]),
        ("💲", "'How much is it?' significa...", ["¿Cuánto cuesta?", "¿Cuántos hay?", "¿Dónde está?", "¿Qué es esto?"]),
        ("🧺", "Which one is a fruit?", ["Strawberry", "Chicken", "Fish", "Bread"]),
        ("🧀", "¿Cuál está bien escrito? (queso)", ["Cheese", "Chese", "Chees", "Cheesse"]),
        ("💧", "Complete: 'Can I ___ some water, please?'", ["have", "has", "having", "am"]),
    ]),
    ("My House", "🏠", 20, [
        ("🛏️", "'Bed' significa...", ["Cama", "Mesa", "Silla", "Puerta"]),
        ("🍳", "Where do you cook?", ["Kitchen", "Bathroom", "Bedroom", "Garden"]),
        ("🪟", "¿Cómo se dice 'ventana'?", ["Window", "Door", "Wall", "Roof"]),
        ("🐱", "Complete: 'The cat ___ under the table.'", ["is", "are", "am", "be"]),
        ("🛋️", "The sofa is usually in the...", ["Living room", "Bathroom", "Kitchen", "Garage"]),
        ("🏡", "Read: 'My house has two bedrooms and a big garden.' How many bedrooms?", ["Two", "One", "Three", "Big"]),
        ("💡", "¿Cómo se dice 'lámpara'?", ["Lamp", "Clock", "Mirror", "Chair"]),
        ("🪑", "Complete: 'There ___ three chairs in the kitchen.'", ["are", "is", "am", "be"]),
        ("🐘", "What is the opposite of 'big'?", ["Small", "Tall", "Long", "Old"]),
        ("🛁", "'Bathroom' significa...", ["Baño", "Dormitorio", "Cocina", "Patio"]),
    ]),
    ("At School", "🏫", 20, [
        ("✏️", "'Pencil' significa...", ["Lápiz", "Lapicera", "Goma", "Regla"]),
        ("🎒", "¿Cómo se dice 'mochila'?", ["Backpack", "Book", "Desk", "Board"]),
        ("📖", "Complete: 'Open your ___, please.'", ["book", "bread", "bed", "bike"]),
        ("👩‍🏫", "Who teaches the class?", ["The teacher", "The doctor", "The chef", "The pilot"]),
        ("📏", "Read: 'Tom has a red pencil and a blue ruler.' What color is the ruler?", ["Blue", "Red", "Green", "Yellow"]),
        ("🚻", "'Can I go to the bathroom?' significa...", ["¿Puedo ir al baño?", "¿Dónde está el baño?", "¿Vas al baño?", "Voy al baño"]),
        ("👧", "Complete: 'She ___ a student.'", ["is", "are", "am", "be"]),
        ("🧽", "¿Cómo se dice 'goma de borrar'?", ["Eraser", "Scissors", "Glue", "Ruler"]),
        ("🔢", "Which subject uses numbers?", ["Math", "Art", "Music", "History"]),
        ("✂️", "¿Cuál está bien escrito? (tijera)", ["Scissors", "Sisors", "Scisors", "Sizzors"]),
    ]),
    ("Colors & Numbers", "🎨", 15, [
        ("🟡", "'Yellow' es...", ["Amarillo", "Azul", "Rojo", "Verde"]),
        ("7️⃣", "¿Cómo se dice 7 en inglés?", ["Seven", "Six", "Eleven", "Nine"]),
        ("🎨", "Red + Yellow = ?", ["Orange", "Purple", "Green", "Brown"]),
        ("🔢", "'Twelve' es el número...", ["12", "20", "2", "11"]),
        ("🌳", "Read: 'The sky is blue and the grass is green.' What color is the grass?", ["Green", "Blue", "Yellow", "Grey"]),
        ("🎂", "¿Cómo se dice 15?", ["Fifteen", "Fifty", "Five", "Fourteen"]),
        ("❄️", "What color is snow?", ["White", "Black", "Pink", "Brown"]),
        ("➕", "Five + three = ?", ["Eight", "Seven", "Nine", "Six"]),
        ("🟣", "'Purple' es...", ["Violeta", "Rosa", "Marrón", "Gris"]),
        ("💯", "¿Cómo se dice 100?", ["One hundred", "Ten", "One thousand", "Ten hundred"]),
    ]),
    ("Actions & Routines", "⚽", 20, [
        ("⏰", "Complete: 'I ___ up at 7 o'clock.'", ["get", "gets", "getting", "to get"]),
        ("🥣", "Complete: 'She ___ breakfast every day.'", ["eats", "eat", "eating", "to eat"]),
        ("🏃", "'Run' significa...", ["Correr", "Saltar", "Nadar", "Caminar"]),
        ("🏊", "¿Cómo se dice 'nadar'?", ["Swim", "Sing", "Sleep", "Sit"]),
        ("⚽", "Complete: 'They ___ football on Saturdays.'", ["play", "plays", "playing", "is play"]),
        ("🪥", "Read: 'Lucas brushes his teeth after dinner.' When?", ["After dinner", "Before breakfast", "At school", "At lunch"]),
        ("🕷️", "Complete: 'He ___ not like spiders.'", ["does", "do", "is", "are"]),
        ("💃", "'Can you dance?' — 'Yes, I ___.'", ["can", "do", "am", "does"]),
        ("📚", "'Read' significa...", ["Leer", "Escribir", "Escuchar", "Hablar"]),
        ("🦘", "Which word is an action?", ["Jump", "Happy", "Blue", "Table"]),
    ]),
]


def save_questions(game_id, questions):
    """questions: lista de dicts {text, emoji, options[4], correct}"""
    db.execute("DELETE FROM quick_questions WHERE game_id=%s", (game_id,))
    rows = []
    for i, q in enumerate(questions):
        opts = (list(q["options"]) + ["", "", "", ""])[:4]
        rows.append((game_id, i, q["text"], q.get("emoji", ""), opts[0], opts[1], opts[2], opts[3], int(q["correct"])))
    db.execute_many(
        "INSERT INTO quick_questions (game_id, position, text, emoji, opt1, opt2, opt3, opt4, correct) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows)


def seed_teacher(teacher_id):
    topic_ids = []
    for title, title_es, emoji, color, words in TOPICS:
        tid = db.execute(
            "INSERT INTO topics (teacher_id, title, title_es, emoji, color) VALUES (%s,%s,%s,%s,%s)",
            (teacher_id, title, title_es, emoji, color))
        topic_ids.append(tid)
        db.execute_many(
            "INSERT INTO words (topic_id, word, translation, emoji, sentence, position) VALUES (%s,%s,%s,%s,%s,%s)",
            [(tid, w, t, e, s, i) for i, (w, t, e, s) in enumerate(words)])

    for pos, (title, desc, scene, topic_index, activities) in enumerate(LESSONS):
        lid = db.execute(
            "INSERT INTO lessons (teacher_id, title, description, scene, activities, position) VALUES (%s,%s,%s,%s,%s,%s)",
            (teacher_id, title, desc, scene, activities, pos + 1))
        db.execute("INSERT INTO lesson_topics (lesson_id, topic_id) VALUES (%s,%s)", (lid, topic_ids[topic_index]))

    for title, emoji, seconds, questions in QUICK_GAMES:
        gid = db.execute("INSERT INTO quick_games (teacher_id, title, emoji, time_limit) VALUES (%s,%s,%s,%s)",
                         (teacher_id, title, emoji, seconds))
        save_questions(gid, [{"emoji": e, "text": t, "options": o, "correct": 0} for e, t, o in questions])
