#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
import traceback
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: initialize Flask migrate in terminal '$ flask db init'
# See config.py for connection to local postgresql database

# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    country = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    seek_talent = db.Column(db.Boolean, default=False)
    seek_description = db.Column(db.String(500), default='')
    shows = db.relationship('Show', backref='venue', lazy=True)

    def create(self):
      db.session.add(self)
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    @property 
    def upcoming_shows(self):
      upcoming_shows = [show for show in self.shows if show.show_time > datetime.now()] #datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') > now]
      return upcoming_shows
    
    @property
    def num_upcoming_shows(self):
      return len(self.upcoming_shows)

    @property
    def past_shows(self):
      past_shows = [show for show in self.shows if show.show_time < datetime.now()]
      return past_shows
    
    @property
    def num_past_shows(self):
      return len(self.past_shows)

    @property
    def search(self):
      return {
        'id': self.id,
        'name': self.name, 
        'image_link': self.image_link,
      }

    def __repr__(self):
      return f'<Venue: {self.id} - {self.name} - {self.description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))    
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(120), default=' ')
    website = db.Column(db.String(120))
    booked_shows = db.relationship('Show', backref='artist', lazy=True)

    def create(self):
      db.session.add(self)
      db.session.commit()
    
    def update(self):
      db.session.upate(self)

    @property
    def search(self):
      return {
        'id': self.id,
        'name': self.name,
        'image_link': self.image_link,
      }

    @property 
    def upcoming_shows(self):
      upcoming_shows = [show for show in self.booked_shows if show.show_time > datetime.now()]
      return upcoming_shows

    @property
    def past_shows(self):
      past_shows = [show for show in self.booked_shows if show.show_time < datetime.now()]
      return past_shows
    
    @property
    def num_past_shows(self):
      return len(self.past_shows)

    @property
    def num_upcoming_shows(self):
      return len(self.upcoming_shows)

    def __repr__(self):
      return f'<Artist: {self.id} - {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    show_time = db.Column(db.DateTime(), nullable=False)

    def create(self):
      db.session.add(self)
      db.session.commit()

    def __repr__(self):
      return f'<Show: {self.id} - {self.venue_id} - {self.artist_id} / {self.show_time}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------~------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------#


@app.route('/venues')
def venues():

  current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  data = []
  
  area = Venue.query.with_entities(Venue.city, Venue.state, Venue.country).distinct().all() 
  for location in area:
    city = location[0]
    state = location[1]
    country = location[2]
    venues = Venue.query.filter_by(city=city, state=state, country=country).all()
    shows = Venue.num_upcoming_shows

    data.append({
      "city": city,
      "state": state,
      "country": country,
      "venues": venues,
      "shows": shows
      })

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  found_venues = Venue.query.filter(Venue.name.ilike("%" + request.form.get('search_term', '') + "%")).all()
  response = {
    "count": len(found_venues),
    "data": [
      venue.search for venue in found_venues
    ]
  }

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if venue:
    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": True if venue.seek_talent in (True, 't', 'True') else False,
      "seeking_description": venue.seek_description,
      "image_link": venue.image_link if venue.image_link else "",
      "past_shows_count": venue.num_past_shows,
      "upcoming_shows_count": venue.num_upcoming_shows,
    }
  
  past_shows = []
  for show in venue.past_shows:
    artist = Artist.query.get(show.artist_id)
    past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.show_time)
    })
    
  upcoming_shows = []
  for show in venue.upcoming_shows:
    artist = Artist.query.get(show.artist_id)
    upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.show_time)
    })

  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  
  #data = list(filter(lambda d: d['id'] == venue_id, venues))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  try:
    new_venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website=form.website.data,
    )
    Venue.create(new_venue)
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except ValueError: 
    flash('Error occurred. Venue ' + form.name + ' could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    Venue.query.filter_by(id=venue_id).delete()
    try:
      db.session.commit()
      flash("Venue %r has been succesfully deleted from FYYUR" % venue_name)
    except:
      db.session.rollback()
      flash("There was an error, venue %r could not deleted" % venue_name)
    finally:
      db.session.close()

    return redirect(url_for('venues'))
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())
  # TODO: replace with real data returned from querying the database

@app.route('/artists/search', methods=['POST'])
def search_artists():
  found_artists = Artist.query.filter(Artist.name.ilike("%" + request.form.get('search_term', '') + "%")).all()
  response = {
    "count": len(found_artists),
    "data": [
      artist.search for artist in found_artists
    ]
  }

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if artist:
    data={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": True if artist.seeking_venue in (True, 't', 'True') else False,
      "seeking_description":  artist.seeking_description,
      "image_link": artist.image_link if artist.image_link else "",
      "past_shows_count": artist.num_past_shows,
      "upcoming_shows_count": artist.num_upcoming_shows,
    }
  
  past_shows = []
  for show in artist.past_shows:
    venue = Venue.query.get(show.venue_id)
    past_shows.append({
        "venue_id": show.venue_id,
        "venuename": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.show_time)
    })
    
  upcoming_shows = []
  for show in artist.upcoming_shows:
    venue = Venue.query.get(show.venue_id)
    upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.show_time)
    })

  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)

  # TODO: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False  
  artist = Artist.query.get(artist_id)
  original_name = artist.name

  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Artist ' + original_name + ' could not be update.')
  if not error: 
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

  # TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False  
  venue = Venue.query.get(venue_id)
  original_name = venue.name # set original name for error message when update fails

  try: 
    venue.name = request.form['name']
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.country = request.form['country']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.genres = request.form.getlist('genres')
    venue.seek_talent = True if 'seek_talent' in request.form else False 
    venue.seek_description = request.form['seek_description']
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Venue ' + original_name + ' could not be updated.')
  if not error: 
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  try:
    new_artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
    )
    Artist.create(new_artist)
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except ValueError: 
    flash('Error occurred. Artist ' + form.name + ' could not be listed.')

  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])





  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
#  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
#  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')

def shows():
  data = []
  shows = Show.query.all()

  for show in shows:
    data.extend([{
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.show_time.strftime("%m/%d/%Y, %H:%M")
    }])
  return render_template('pages/shows.html', shows=data)
      
  # TODO: replace with real data returned from querying the database


  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)

  try:
    new_show = Show(
      venue_id=form.venue_id.data,
      artist_id=form.artist_id.data,
      show_time=form.start_time.data,
    )
    Show.create(new_show)
    flash('Show was successfully listed!')
  except ValueError: 
    flash('An error occurred. Show could not be listed.')

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/artists/<artist_id>', methods=['DELETE'])







@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
if __name__ == '__main__':
  app.run(debug=True)
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)

