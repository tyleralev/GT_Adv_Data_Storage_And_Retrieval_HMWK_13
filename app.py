#importing dependencies
from flask import Flask, render_template
from flask_pymongo import PyMongo
import scrape_mars

#setting up flask app
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

#can also set it inline with this code
#mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

#creating the main route
@app.route("/")
def index():
    mars = mongo.db.mars.find_one()
    return render_template("index.html", mars=mars)

#creating the scrape route
@app.route("/scrape")
def scrape():
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape_all()
    mars.update({}, mars_data, upsert=True)
    return "Scrapping Successful"

#final part
if __name__ == "__main__":
    app.run()
