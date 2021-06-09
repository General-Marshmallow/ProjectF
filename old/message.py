import random

_messages = [
    'Dream big',
    'Leave no stone unturned',
    'And so the adventure begins',
    'If you want it, work for it',
    'If it matters to you, you’ll find a way',
    'Actually, you can',
    'Focus on the good',
    'You are doing great',
    'Focus on the journey, not the destination'
    'You make mistakes. Mistakes don’t make you',
    'If you feel like giving up, look back at how far you’ve come',
    'Let go!',
    'Breathe',
    'Go for it',
    'Keep going',
    'Take it easy',
    'Keep it cool',
    'Don’t rush things',
    'Keep moving forward',
    'The best is yet to come',
]

_messages_alt = [
    'Life is too short to learn German. Oscar Wilde',
    'Why do they put pizza in a square box?',
    'Do crabs think we walk sideways? Bill Murray',
    'Don’t be humble, you’re not that great. Indira Gandhi',
    'I intend to live forever. So far, so good. Steven Wright',
    'My life feels like a test I didn’t study for.',
    'Why is there an expiration date on sour cream? George Carlin',
    'I drive way too fast to worry about cholesterol. Steven Wright',
    'A day without sunshine is like, you know, night. Steve Martin',
    'In heaven, all the interesting people are missing. Friedrich Nietzsche',
    'The last woman I was in was the Statue of Liberty. Woddy Allen',
    'Women want love to be a novel. Men, a short story. Daphne du Maurier',
    'Guests, like fish, begin to smell after three days. Benjamin Franklin',
    'Whoever named it necking is a poor judge of anatomy. Groucho Marx',
    'Change is inevitable – except from a vending machine. Robert C. Gallagher',
    'I bet giraffes don’t even know what farts smell like. Bill Murray',
    'Every novel is a mystery novel if you never finish it.',
    'Why is the slowest traffic of the day called ‘rush hour’?',
    'It’s easy to quit smoking. I’ve done it hundreds of times. Mark Twain',
    'The risk I took was calculated, but man, I am bad at math.',
    'I couldn’t repair your brakes, so I made your horn louder. Steven Wright',
    'Do not read the next sentence. You little rebel, I like you.',
    'Just when I discovered the meaning of life, they changed it. George Carlin',
    'Always borrow money from a pessimist. He won’t expect it back. Oscar Wilde',
    'If truth is beauty, how come no one has their hair done in a library? Lily Tomlin',
    'I love deadlines. I love the whooshing noise they make as they go by. Douglas Adams',
    'I never feel more alone than when I’m trying to put sunscreen on my back. Jimmy Kimmel',
    'The key to eating healthy is not eating any food that has a TV commercial. Mike Birbiglia',
    'I’ve got to keep breathing. It’ll be my worst business mistake if I don’t. Steve Martin',
    'There are three types of people in this world: those who can count, and those who can’t.',
    'The closest a person ever comes to perfection is when he fills out a job application form.'
]


def get_random_message():
    return random.choice(_messages)

