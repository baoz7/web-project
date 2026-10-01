from sqlmodel import Session, select, SQLModel
from app.database import engine
from app.models import Hero, Team, Mission

def seed():
    # 1. Create tables if they don't exist
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # 2. Check if there is already at least one team
        if session.exec(select(Team)).first():
            print("Database is already seeded!")
            return
            
        print("Seeding database...")
        
        # 3. Create 2 Missions
        mission1 = Mission(title="Battle of Sokovia")
        mission2 = Mission(title="Infinity War")
        
        # 4. Create 2 Teams
        avengers = Team(name="Avengers", headquarters="New York")
        xmen = Team(name="X-Men", headquarters="Westchester")
        
        # 5. Create 5 Heroes and assign them to teams and missions via relationships
        h1 = Hero(name="Tony", age=45, secret_name="Iron Man", team=avengers, missions=[mission1, mission2])
        h2 = Hero(name="Natasha", age=35, secret_name="Black Widow", team=avengers, missions=[mission1])
        h3 = Hero(name="Logan", age=150, secret_name="Wolverine", team=xmen, missions=[mission2])
        h4 = Hero(name="Peter", age=16, secret_name="Spider-Man", team=avengers, missions=[])
        h5 = Hero(name="Ororo", age=30, secret_name="Storm", team=xmen, missions=[])
        
        # Adding the heroes automatically adds their associated teams and missions
        session.add_all([h1, h2, h3, h4, h5])
        session.commit()
        
        print("Seeding complete!")

if __name__ == "__main__":
    seed()