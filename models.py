#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Imports

from app import db
from datetime import datetime

#  ----------------------------------------------------------------

# TODO: initialize Flask migrate in terminal '$ flask db init'

#  Venues
#  ----------------------------------------------------------------
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

    @property         #get shows planned in future date/time for venue
    def upcoming_shows(self):
      # upcoming_shows = [show for show in self.shows if show.show_time > datetime.now()] #datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') > now]
      # return upcoming_shows

      upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==self.id).filter(Show.show_time>datetime.now()).all()
      upcoming_shows = []

      return upcoming_shows
    
    @property         #count number of planned shows in future date/time for venue
    def num_upcoming_shows(self):
      num_upcoming_shows = len(db.session.query(Show).filter(Show.venue_id == self.id).filter(Show.show_time > datetime.now()).all())
      return num_upcoming_shows

    @property         #get shows at venue which started already or which where in the past
    def past_shows(self):
    #  past_shows = [show for show in self.shows if show.show_time < datetime.now()]
    #  return past_shows
      
      past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==self.id).filter(Show.show_time<datetime.now()).all()
      past_shows = []
      
      return past_shows

    @property         #count number shows at venue which started already or which where in the past
    def num_past_shows(self):
      num_past_shows = len(db.session.query(Show).filter(Show.venue_id == self.id).filter(Show.show_time < datetime.now()).all())
      return num_past_shows


    @property         #search function for venues
    def search(self): 
      return {
        'id': self.id,
        'name': self.name, 
        'image_link': self.image_link,
      }

    def __repr__(self):
      return f'<Venue: {self.id} - {self.name} - {self.description}>'

#  Artists
#  ----------------------------------------------------------------
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

    @property         #search function for venues
    def search(self):
      return {
        'id': self.id,
        'name': self.name,
        'image_link': self.image_link,
      }
    
    @property         #get shows planned in future date/time for artist
    def upcoming_shows(self):
      upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==self.id).filter(Show.show_time>datetime.now()).all()
      upcoming_shows = []

      return upcoming_shows

    @property         #get shows for artist which started already or which where in the past
    def past_shows(self):
      past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==self.id).filter(Show.show_time<datetime.now()).all()
      past_shows = []
      
      return past_shows
    
    @property         #gcount n umber ofshows for artist which started already or which where in the past
    def num_past_shows(self):
      num_past_shows = len(db.session.query(Show).filter(Show.artist_id == self.id).filter(Show.show_time < datetime.now()).all())
      return num_past_shows

    @property         #count number of shows planned in future date/time for artist
    def num_upcoming_shows(self):
      num_upcoming_shows = len(db.session.query(Show).filter(Show.artist_id == self.id).filter(Show.show_time > datetime.now()).all())
      return num_upcoming_shows

    def __repr__(self):
      return f'<Artist: {self.id} - {self.name}>'


#  Shows
#  ----------------------------------------------------------------
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