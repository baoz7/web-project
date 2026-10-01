# Answers - Lab Week 09

## Part 1

? Question 1. For each of the four statements, which constraint blocked it and why?

1. `INSERT INTO team... 'Avengers'`: Blocked by the UNIQUE constraint on the `name` column (because the team 'Avengers' already exists).
2. `INSERT INTO hero... 99`: Blocked by the FOREIGN KEY constraint on the `team_id` column (because there is no team with id = 99 in the team table).
3. `INSERT INTO hero (age) VALUES (30)`: Blocked by the NOT NULL constraint on the `name` column (because the required data for the name column is missing).
4. `DELETE FROM team WHERE id=1`: Blocked by the FOREIGN KEY constraint (because the team with id=1 is being referenced by heroes in the hero table; the team cannot be deleted until the heroes belonging to it are handled).

? Question 2. The relationship team -> hero is one-to-many. Why is the foreign key on hero and not on team?

- Because a team can contain many heroes. If the foreign key were placed in the `team` table, a team row could only store the id of a single hero. By placing it in the `hero` table, multiple different hero rows can point to the same `team_id`.

? Question 3. Sketch the tables you need for missions (many-to-many)

Need to create an additional link table to connect them:

- `mission` table: `id` (Primary Key), `name` (VARCHAR).
- `hero_mission_link` table: `hero_id` (Foreign Key), `mission_id` (Foreign Key). The primary key of this table will be a composite key combining (`hero_id`, `mission_id`).

? Question 4. Why read the URL from an environment variable instead of writing it in database.py? Give two reasons

1. Security: To avoid hardcoding sensitive credentials (like passwords) directly into the source code, which could be exposed if the code is shared or pushed to GitHub

2. Flexibility: It allows the application to connect to different databases (e.g., a local one for testing and a live one for production) simply by changing the environment environment, without having to rewrite any code

? Question 5. Why is id typed int | None with default=None, when every row in the database has an id?

- Because before the object is saved to the database for the first time, it does not have an ID yet (the database generates it). Setting it to `None` allows us to create the object in Python without causing a validation error.

? Question 6. Which attributes of Hero become columns, and which one does not? What is back_populates for?

- `id`, `name`, `age`, `team_id`, and `secret_name` become columns in the database.
- The `team` attribute (the Relationship) does NOT become a column.
- `back_populates` tells SQLModel how the tables are linked, ensuring that when you update the relationship on one side (e.g., adding a hero to a team), the other side is automatically updated in Python.

? Question 7. Compare the CREATE TABLE hero printed by SQLAlchemy with the one you wrote by hand in Part 1.

- SQLAlchemy automatically adds index constraints (because we set `index=True` in the models), explicitly names the primary keys, and dynamically handles `NOT NULL` constraints based on whether we allowed `None` in Pydantic.

? Question 8. Stop and restart the server. Is CREATE TABLE printed again? Why? What does create_all do when a table already exists?

- Yes, the engine still checks. However, `create_all` is safe—if it detects the tables already exist in the database, it simply skips creating them and does nothing.

? Question 9. create_all only knows about models that have been imported. Which line in main.py makes sure Hero and Team are registered?

- The line: `from app.models import Hero, Team`

? Question 10. Comment out session.commit() in create_hero and create a hero. What does the response look like, and is the row in the database? What does add() do on its own, and why do we need refresh()?

- Without `commit()`, the API response might look successful but the row is NOT actually saved in the PostgreSQL database
- `add()` only stages the object in the current session memory.
- `commit()` executes the transaction to save it to the database permanently.
- `refresh()` fetches the newly generated data (like the auto-incrementing `id` that the database assigns) back into the Python object.

? Question 11. Which SQL statement does echo=True print for PATCH with body {"age": 17}? Does it update every column or only age? Why?

- It prints an `UPDATE` statement that only updates the `age` column. This is because we use `hero_in.model_dump(exclude_unset=True)`, which tells Pydantic to ignore any fields the client didn't explicitly send, preventing us from overwriting existing data with `None`.

? Question 12. Look at the JSON returned by GET /heroes/{id}. Is secret_name there? Which line of code is responsible?

- No, `secret_name` is not there. The line `response_model=HeroPublic` in the endpoint decorator (`@app.get(...)`) is responsible for this. It filters out any fields that are not defined in the `HeroPublic` schema before sending the JSON to the client.

? Question 13. Call GET /heroes?min_age=18&team_id=1 and copy the SELECT printed by echo=True. Where do the values 18 and 1 appear? Why is this safe against SQL injection?

- The values 18 and 1 do not appear directly in the raw SQL string; instead, you see placeholders (like `%(age_1)s` or `$1`, `$2`). This is safe against SQL injection because parameterized queries separate the SQL logic from the user data, preventing malicious input from altering the SQL command.

? Question 14. Why filter in the database instead of `[h for h in session.exec(select(Hero)).all() if h.age >= 18]`?

- Filtering in Python requires fetching every single row from the database table and loading it into server memory, which is extremely slow and wastes RAM. Filtering in the database uses indexed SQL checks, which is highly optimized and only sends the necessary data back to Python.

? Question 15. On restart, create_all did create mission and heromissionlink. In Part 4 it did nothing for hero. What is the rule?

- The rule is that `SQLModel.metadata.create_all(engine)` only creates tables that do _not_ already exist in the database. In Part 4, the `hero` table already existed from our manual SQL commands, so it was skipped. On this restart, `mission` and `heromissionlink` did not exist yet, so SQLAlchemy safely created them.

? Question 16. You never set team_id in the seed script. Read the echo=True output: in which order were the INSERT s executed, and how did hero.team_id get its value?

- SQLAlchemy handles the insertion order automatically based on the relationships. It first executed `INSERT` statements for the `team` and `mission` tables to let PostgreSQL generate their primary keys. Once those IDs were created, SQLAlchemy fetched them back into Python and automatically used them to populate the `team_id` column when generating the `INSERT` statements for the `hero` and `heromissionlink` tables.

? Question 17. Is there a power column? Now call GET /heroes. What happens and why? Why is "drop all tables and run create_all again" not an acceptable fix in production?

- No, there is no `power` column in the database yet.
- Calling `GET /heroes` causes an Internal Server Error (500). This happens because the SQLModel Python code tries to query the `power` column, but PostgreSQL throws an error because the column does not exist.
- "Drop all tables and run `create_all` again" is not acceptable in production because dropping tables deletes all of your live user data. We need a way to alter the existing schema without losing the data inside it.

? Question 18. Copy the bodies of upgrade() and downgrade(). What does each one do?

- `upgrade()`: `op.add_column('hero', sa.Column('power', sqlmodel.sql.sqltypes.AutoString(), nullable=True))`. This safely adds the new `power` column to the existing database table when the migration is applied.
- `downgrade()`: `op.drop_column('hero', 'power')`. This removes the `power` column if we ever need to undo (roll back) this migration.

? Question 19. Where does Alembic store "which revision this database is at"? (Hint: \dt.) Why should the migrations/ folder be committed to Git?

- Alembic stores this in a special database table it creates called `alembic_version`. The `migrations/` folder must be committed to Git so that other developers on your team (or the production server) have the exact same history of scripts to upgrade their databases to match yours.

? Question 20. Rename secret_name to alias in the model and run revision --autogenerate (do not apply it). What did Alembic generate? Why is that dangerous for existing data, and how would you fix the script?

- Alembic generated a script that drops the `secret_name` column and adds a brand new `alias` column. This is incredibly dangerous because dropping the column permanently deletes all the existing secret names from the database! To fix it, you would manually edit the generated migration script to use `op.alter_column('hero', 'secret_name', new_column_name='alias')` instead of dropping and adding.
