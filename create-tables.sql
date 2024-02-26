CREATE TABLE IF NOT EXISTS game (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    developer TEXT NOT NULL,
    publisher TEXT NOT NULL,
    released_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS staff (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS game_staff (
    game_id TEXT NOT NULL,
    staff_id TEXT NOT NULL,
    PRIMARY KEY (game_id, staff_id),
    FOREIGN KEY (game_id) REFERENCES game(id),
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

CREATE TABLE IF NOT EXISTS monster (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS game_monster (
    game_id TEXT NOT NULL,
    monster_id TEXT NOT NULL,
    PRIMARY KEY (game_id, monster_id),
    FOREIGN KEY (game_id) REFERENCES game(id),
    FOREIGN KEY (monster_id) REFERENCES monster(id)
);

CREATE TABLE IF NOT EXISTS item (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS game_item (
    game_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    PRIMARY KEY (game_id, item_id),
    FOREIGN KEY (game_id) REFERENCES game(id),
    FOREIGN KEY (item_id) REFERENCES item(id)
);



