from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import Category, Transaction, Base
from database import engine, SessionLocal
from datetime import date

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Create the database tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = next(get_db())
    if db.query(Category).count() == 0:
        # Add default categories
        default_categories = ["Food", "Transportation", "Entertainment", "Utilities", "Other"]
        for category_name in default_categories:
            category = Category(name=category_name)
            db.add(category)
        db.commit()

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    db = next(get_db())
    categories = db.query(Category).all()
    for category in categories:
        transactions = db.query(Transaction).filter(Transaction.category_id == category.id).all()
        category.total = sum(transaction.amount for transaction in transactions)
    return templates.TemplateResponse("index.html", {"request": request, "categories": categories})

@app.get("/add", response_class=HTMLResponse)
async def add_transaction(request: Request):
    db = next(get_db())
    categories = db.query(Category).all()
    current_date = date.today().isoformat()
    return templates.TemplateResponse("add.html", {"request": request, "categories": categories, "current_date": current_date})

@app.post("/add", response_class=HTMLResponse)
async def add_transaction_post(
    request: Request,
    category_id: int = Form(...),
    amount: float = Form(...),
    date: date = Form(...),
    description: str = Form(None)
):
    db = next(get_db())
    transaction = Transaction(category_id=category_id, amount=amount, date=date, description=description)
    db.add(transaction)
    db.commit()
    return await read_root(request)

@app.get("/category/{category_id}", response_class=HTMLResponse)
async def read_category(request: Request, category_id: int):
    db = next(get_db())
    category = db.query(Category).filter(Category.id == category_id).first()
    transactions = db.query(Transaction).filter(Transaction.category_id == category_id).all()
    categories = db.query(Category).all()
    return templates.TemplateResponse("category.html", {"request": request, "category": category, "transactions": transactions, "categories": categories})

@app.post("/delete/{transaction_id}", response_class=HTMLResponse)
async def delete_transaction(request: Request, transaction_id: int):
    db = next(get_db())
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction:
        db.delete(transaction)
        db.commit()
    return await read_root(request)

@app.post("/add_category", response_class=HTMLResponse)
async def add_category_post(request: Request, category_name: str = Form(...)):
    db = next(get_db())
    category = Category(name=category_name)
    db.add(category)
    db.commit()
    return await read_root(request)

@app.post("/delete_category/{category_id}", response_class=HTMLResponse)
async def delete_category_post(request: Request, category_id: int):
    db = next(get_db())
    # Find the "Other" category
    other_category = db.query(Category).filter(Category.name == "Other").first()

    if not other_category:
        other_category = Category(name="Other")
        db.add(other_category)
        db.commit()
        print("Created 'Other' category")

    # Move all transactions to the "Other" category
    transactions = db.query(Transaction).filter(Transaction.category_id == category_id).all()
    print(f"Found {len(transactions)} transactions to move to 'Other' category")
    for transaction in transactions:
        transaction.category_id = other_category.id
        print(f"Moved transaction {transaction.id} to 'Other' category")
    db.commit()  # Commit after moving transactions

    # Delete the category
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        db.delete(category)
        db.commit()  # Commit after deleting the category
        print(f"Deleted category {category.name}")

    return await read_root(request)

@app.post("/change_category/{transaction_id}", response_class=HTMLResponse)
async def change_category_post(request: Request, transaction_id: int, new_category_id: int = Form(...)):
    db = next(get_db())
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction:
        transaction.category_id = new_category_id
        db.commit()
    return await read_root(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)