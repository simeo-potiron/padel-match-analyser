# An empty score board
score_board = {
    "format": "",
    "teams": {
        "A": {},
        "B": {}
    },
    "serving": {
        "previous": None,
        "current": None,
        "next": None
    },
    "match": {
        "score": [],
        "sets": {
            "A": 0,
            "B": 0
        },
        "games": {
            "A": 0,
            "B": 0
        },
        "points": {
            "A": 0,
            "B": 0
        },
    },
    "live_stats": {
        "serving": [],
        "points_won": [],
        "match_points": [],
        "break_points": [],
        "breaks": [],
        "events": [],
        "A1": [],
        "A2": [],
        "B1": [],
        "B2": []
    },
    "winner": None
}

# All available formats
formats = {
    "A1": {
        "description": "2 sets de 6 jeux, avec avantages.",
        "sets": 2,
        "games": 6,
        "advantages": True, 
        "super_tb": False,
        "tie_break": 0
    },
    "A2": {
        "description": "2 sets de 6 jeux, sans avantages.",
        "sets": 2,
        "games": 6,
        "advantages": False, 
        "super_tb": False,
        "tie_break": 0
    },
    "B1": {
        "description": "2 sets de 6 jeux, avec avantages. Super TB au 3ème.",
        "sets": 2,
        "games": 6,
        "advantages": True, 
        "super_tb": True,
        "tie_break": 0
    },
    "B2": {
        "description": "2 sets de 6 jeux, sans avantages. Super TB au 3ème.",
        "sets": 2,
        "games": 6,
        "advantages": False, 
        "super_tb": True,
        "tie_break": 0
    },
    "C1": {
        "description": "2 sets de 4 jeux, avec avantages. Super TB au 3ème.",
        "sets": 2,
        "games": 4,
        "advantages": True, 
        "super_tb": True,
        "tie_break": 0
    },
    "C2": {
        "description": "2 sets de 4 jeux, sans avantages. Super TB au 3ème.",
        "sets": 2,
        "games": 4,
        "advantages": False, 
        "super_tb": True,
        "tie_break": 0
    },
    "D1": {
        "description": "1 set de 9 jeux, avec avantages. TB à 8/8.",
        "sets": 1,
        "games": 9,
        "advantages": True, 
        "super_tb": False,
        "tie_break": -1
    },
    "D2": {
        "description": "1 set de 9 jeux, sans avantages. TB à 8/8.",
        "sets": 1,
        "games": 9,
        "advantages": False, 
        "super_tb": False,
        "tie_break": -1
    },
    "E": {
        "description": "Super TB en 10 points.",
        "sets": 1,
        "games": 0,
        "advantages": False,
        "super_tb": True,
        "tie_break": 0
    }
}