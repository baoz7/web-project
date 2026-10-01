from app.models import Hero, Team, Mission, HeroMissionLink, HeroCreate, HeroPublic, HeroUpdate, TeamCreate, TeamPublic, MissionCreate, MissionPublic
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from sqlmodel import SQLModel, select
from sqlalchemy.exc import IntegrityError

from app.database import engine, SessionDep
from app.models import Hero, Team, HeroCreate, HeroPublic, HeroUpdate, TeamCreate, TeamPublic

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

# --- HERO ENDPOINTS ---

@app.post("/heroes", response_model=HeroPublic, status_code=201)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    # Challenge: Check if team exists before assigning
    if hero_in.team_id is not None:
        team = session.get(Team, hero_in.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@app.get("/heroes", response_model=list[HeroPublic])
def list_heroes(
    session: SessionDep, 
    offset: int = 0, 
    limit: int = Query(default=10, le=100),
    min_age: int | None = None,
    team_id: int | None = None,
    name: str | None = None
):
    query = select(Hero)

    if min_age is not None:
        query = query.where(Hero.age >= min_age)
    if team_id is not None:
        query = query.where(Hero.team_id == team_id)
    if name is not None:
        query = query.where(Hero.name.ilike(f"%{name}%"))
        
    heroes = session.exec(query.offset(offset).limit(limit)).all()
    return heroes

@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    
    if hero_in.team_id is not None:
        team = session.get(Team, hero_in.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
            
    hero_data = hero_in.model_dump(exclude_unset=True)
    hero.sqlmodel_update(hero_data)
    
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()

# --- TEAM ENDPOINTS ---

@app.post("/teams", response_model=TeamPublic, status_code=201)
def create_team(team_in: TeamCreate, session: SessionDep):
    team = Team.model_validate(team_in)
    session.add(team)
    try:
        session.commit()
        session.refresh(team)
        return team
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Team name already exists")

@app.get("/teams", response_model=list[TeamPublic])
def list_teams(session: SessionDep, offset: int = 0, limit: int = Query(default=10, le=100)):
    teams = session.exec(select(Team).offset(offset).limit(limit)).all()
    return teams

@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def read_team_heroes(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.heroes

# --- MISSION ENDPOINTS ---

@app.post("/missions", response_model=MissionPublic, status_code=201)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission

@app.post("/heroes/{hero_id}/missions/{mission_id}", status_code=204)
def assign_mission(hero_id: int, mission_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    mission = session.get(Mission, mission_id)
    if not hero or not mission:
        raise HTTPException(status_code=404, detail="Hero or Mission not found")
    
    # Do nothing if already assigned
    if mission in hero.missions:
        return
        
    hero.missions.append(mission)
    session.add(hero)
    session.commit()

@app.get("/heroes/{hero_id}/missions", response_model=list[MissionPublic])
def read_hero_missions(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero.missions